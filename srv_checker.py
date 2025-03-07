#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
source scanner for service routines

all registered c files in db3 file will be processed
swb build flags will be added from swb config referenced in medc ini file
"""

# Importing the Module
import traceback
import sys
import os.path
import re
import tempfile
from time import time
from datetime import datetime
import os
import psutil
from version import VERSION
from general import TOOLNAME, ALM_MSG
from multiprocessing import freeze_support
from configs import to_conf_file, from_conf_file, create_regex_list, get_default_config, serviceLibraryList
from fetchunc import FetchUNC
from argparse import ArgumentParser as ArgParser
from dbg_handler import DbgHandler
from about import *
from errorcodes import ErrHandler
from excelwriter import ExcelWriter
from gcc_tools import get_include_paths
from mc_tools import MCParser
import mc_tools as mc_tools
from windows_tools import is_unc_path,sleep,write_file,multiprocess_workaround
from general import flatlist
from helpers import version_split, version_check
from datetime import datetime
from srvchecker_logger import LoggerDisp

# ------------------------------------------------------------------------------
# Main Class Srvchecker
# ------------------------------------------------------------------------------
class SrvChecker:
    """
    Usage   : Main Class srvchecker

    Syntax  : sc = SrvChecker()

    Example : sc = SrvChecker(root=root, add_flags=add_flags, outputpath=output_path, no_clean=not clean_content,
                            path_select=None, src_file_list=input_src_files, compilerpath=options.compiler,
                            excludepaths=options.exclude, search_list=search_list, dep_search_list=dep_search_list,
                            search_return=search_return, search_cs=case_sense, cpu=int(options.cpu),
                            log_search_file=options.log, no_write=not options.ifiles,
                            ulf=ulf, ulf_key='SCAN', nc=options.no_counter, debug=0, debug_log=options.debug)

    """
    import re
    cmp_version = re.compile(r'^[A-Za-z]\:.*?(\d+\.\d+\.\d+).*?[/\\]bin')

    swb_options = {'IGNORE_UNSUPPORTED_SWB_BUILD': True, }

    # ------------------------------------------------------------------------------
    # Constructor for the class
    # ------------------------------------------------------------------------------
    def __init__(self, outputpath='_srvchecker', root=None, prj=None, add_flags='', no_clean=False,
                 store_results=False, no_write=False, src_file_list=None, cpu=0, excludepaths=None,
                 search_list=None, dep_search_list=None, search_return=None, search_cs=False, compilerpath=None,
                 log_search_file=True, ulf=None, ulf_key=None, nc=False, debug=0, debug_log=False, maps_curves_search_lst=None):

        self.debug = debug
        self.dbg = DbgHandler(self.__class__.__name__, debug)
        self.ulf = ulf
        self.ulf_key = ulf_key
        self.cpu = cpu
        self.nc = nc
        self.root = root
        self.prj = prj

        self.sourcefile_num = 0



        # outputpath for external tools '_gen/swb/filegroup/cc_temps'
        self.outputpath = outputpath
        self.outputfilepaths = None
        self.search_results = []

        # load project
        if self.root is not None:
            # checking root directory
            if not os.path.exists(self.root):
                self.dbg.out(1, 'root directory %s not found' % self.root)
                return

            if ulf is None:
                self.dbg.out(3, 'loading swb project folder ...')

            self.swb_config = self.prj.parse_swb_config(self.root, self.prj.get_prjcfgname())
        else:
            self.dbg.out(1, 'no project found in root directory %s' % self.root)
            return

        search_mdgb_usecase = False
        if type(search_list) is dict:
            search_mdgb_usecase = True

        # create search regex list
        if dep_search_list is not None:
            res = self.check_dep(dep_search_list)
            if not search_mdgb_usecase:
                search_list += res
            else:
                   search_list["NON_ADAPTER"] += res

        self.srv_search_list = search_list
        self.re_search, self.re_search_ret = None, None

        # added this logic for ICE
        if search_list is not None:
            if search_mdgb_usecase:
                search_list = self.srv_search_list["NON_ADAPTER"] + self.srv_search_list["ADAPTER"]

            if search_cs:
                self.re_search = self.re.compile(b'|'.join(search_list))
                if search_return is not None:
                    self.re_search_ret = self.re.compile(search_return.encode())
            else:  # Ignores Case
                self.re_search = self.re.compile(b'|'.join(search_list), self.re.I)
                if search_return is not None:
                    self.re_search_ret = self.re.compile(search_return.encode(), self.re.I)
            self.search_list = search_list
        else:
            self.search_list = None

        # store user compiler flags
        self.myflags = add_flags

        # create output path
        self.outputpath = outputpath
        if not os.path.exists(self.outputpath):
            try:
                os.makedirs(self.outputpath)
            except:
                if ulf is None:
                    self.dbg.send('No access for creating file. '
                                  'Please check your permissions in folder %s.' % self.outputpath,
                                  {'FATAL': None})
                else:
                    ulf.msg(ulf_key, 'NO_PERMISSION', ft=self.outputpath)

        # create exclude path regex
        if (excludepaths is not None) and len(excludepaths):
            excludepaths = excludepaths.replace('\\', '/')
            self.excludepaths = []
            for ep in excludepaths.split(';'):
                tmp_ = [re.compile('^%s' % x.replace('?', '.?').replace('*', r'.*'), flags=re.I) for x in ep.split('/')]
                self.excludepaths.append((tmp_, len(tmp_)))
            self.exclude_cache = {}
        else:
            self.excludepaths = None

        # get gcc compiler information and standard include paths
        self.gcc_path, self.gcc_exec = os.path.split(compilerpath)
        # self.gcc_env = self.prj.get_compiler_license()
        self.gcc_env = {}
        self.gcc_env.update(os.environ)
        # __, self.gcc_exec = get_gcc_configs(self.root, gcc_path = self.gcc_path)
        self.include_paths = get_include_paths(self.root)

        data_paths = ['makeout/damos/gen_files', 'tmp/include/data', '_gen/swb/include/data',
                      '_gen/swb/filegroup/includes/data', '_gen/swb/damos/gen_files']
        for data_path in data_paths:
            new_data_path = './' + data_path
            if new_data_path in self.include_paths:
                files_lst = []
                new_data_path1 = new_data_path.replace('.', '')
                for root, dirs, files in os.walk(self.root + new_data_path1):
                    if root==self.root + new_data_path1:
                        for file in files:
                            files_lst.append(file)
                self.include_paths.remove(new_data_path)
                out_data_path=os.path.join(output_path,"data").replace('\\','/')
                self.include_paths.append(out_data_path)
                try:
                    if not os.path.exists(out_data_path):
                        os.makedirs(out_data_path)
                    else:
                        for file1 in os.listdir(out_data_path):
                            file_path = os.path.join(out_data_path, file1)
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                    from shutil import copy
                    for file in files_lst:
                        import io
                        with io.open(os.path.join(self.root + new_data_path1,file), 'r', newline='\n') as F:
                            alldata=F.read()
                            all_data_str = ''.join(alldata)
                            all_data_byte=all_data_str.encode('utf-8')
                        all_data_search_lst=self.re_search.findall(all_data_byte)
                        all_data_search_lst = set(all_data_search_lst)
                        def check_for_srv(data):
                            if type(data) is list:
                                data = ' '.join(data)
                            for tmp in all_data_search_lst:
                                srvFunc = tmp.decode()
                                if srvFunc in data:
                                    return True
                            return False
                        if not len(all_data_search_lst) == 0:
                            with open(os.path.join(out_data_path, file), 'w') as F1:
                                inside_block = False
                                store_lst = []
                                for data in all_data_byte.split(b'\n'):
                                    data.strip()
                                    data = data.decode()
                                    if data.startswith('#') and data[-2:-1] == '\\':
                                        store_lst.append(data)
                                        inside_block = True
                                        continue

                                    elif inside_block and data.strip()[0:1] != '#':
                                        store_lst.append(data)
                                        continue
                                    elif data.startswith('#') and inside_block:  # check for non srv
                                        if check_for_srv(store_lst):
                                            store_lst = []  # removing stored things
                                            inside_block = False
                                            if not check_for_srv(data):
                                                F1.write(data)
                                        else:
                                            for each in store_lst:
                                                F1.write(each)
                                            store_lst=[]
                                            F1.write(data)

                                    elif data.startswith('#'):
                                        if check_for_srv(data):
                                            continue
                                        else:
                                            inside_block = False
                                            F1.write(data)
                                    else:
                                        F1.write(data)

                        else:
                            copy(os.path.join(self.root + new_data_path1, file), out_data_path)
                except Exception as e:
                    dbg_error = dbgh.get_exception(traceback, sys, e)
                    ulf.msg('ALL', 'TOOLERROR', ulfmsg=dbg_error)

        # mmi6kor 29102018 (Removed the Warning)-----------------------------------------------
        # if self.prj.is_swb():
        #    ulf.msg(ulf_key, 'UC1_PVER_SWB')
        # mmi6kor 29102018 (Removed the Warning)-----------------------------------------------
        if ulf is not None:
            ulf.msg(ulf_key, 'UC1_INCPATH', ft='\n' + '\n'.join(self.include_paths))

        # This Variable is used to store to read the cfile full path in the build_cmd.log
        self.c_filepaths = {}

        # set environment variable (for tricore-gcc v4)
        if ('RLM_PATH' in self.gcc_env) and ('PATH' in self.gcc_env):
            self.gcc_env['PATH'] = ';'.join((self.gcc_env['PATH'], self.gcc_env['RLM_PATH']))

        # get include paths
        if not self.include_paths:
            if ulf is not None:
                ulf.msg(ulf_key, 'NO_INCLUDE_FILES')
            else:
                self.dbg.out(1, 'No source files to scan in the PVER.')

        if ulf is not None:
            ulf.msg(ulf_key, 'GCC_VERSION', ft=self.gcc_path)
        else:
            self.dbg.out(3, 'using gcc version: %s.' % self.gcc_path)

        self.results = None
        self.ctemps = None
        self.alm_msg = ''

        if self.prj.get_pvernature() == 'MIC':
            self.alm_msg = ALM_MSG + '\n\n'
        if ulf is not None:
            ulf.msg(ulf_key, 'IFILE_START')
        else:
            self.dbg.out(4, 'IFILE_START')
        ifile_starttime = datetime.now()
        self.create_i_files(no_clean=no_clean, store_results=store_results, no_write=no_write,
                            log_search_file=log_search_file, src_file_list=src_file_list, debug_log=debug_log,maps_curves_search_lst=maps_curves_search_lst)
        if ulf is not None:
            ulf.msg(ulf_key, 'IFILE_END')
        else:
            self.dbg.out(4, 'IFILE_END')
        endtime_print(ulf, ifile_starttime, ulf_key, 'i file generation', debug=True)

    def check_dep(self, searchlist):

        result = []
        cache_dep = {}
        for search_str, deps in searchlist:
            for lws_obj, ver_chk in deps:
                if (lws_obj + ver_chk) in cache_dep:
                    if cache_dep[lws_obj + ver_chk]:
                        continue
                    else:
                        # not met
                        break
                class_name, cont_name = lws_obj.split(':') 
                ver, rev = self.prj.getsrvversion(cont_name)
                used_version_obj = version_split(ver, rev)
                if version_check(used_version_obj, ver_chk):
                    cache_dep[lws_obj + ver_chk] = True
                    continue
                else:
                    cache_dep[lws_obj + ver_chk] = False
                    # not met
                    break
            else:
                # no break > append this string
                result.append(search_str)
        return result

    def get_flags_compiler_version(self, compiler_path, use_version=None):
        version_attrib = self.cmp_version.search(compiler_path)
        if version_attrib is not None:
            version_attrib = version_attrib.group(1).split('.')[:2]
            if (use_version is not None) and (int(version_attrib[0]) != use_version):
                version_attrib[0] = '-D__GNUC__=%s' % str(use_version[0])
                version_attrib[1] = '-D__GNUC_MINOR__=%s' % str(use_version[1])
            else:
                version_attrib[0] = '-D__GNUC__=%s' % version_attrib[0]
                version_attrib[1] = '-D__GNUC_MINOR__=%s' % version_attrib[1]
        else:
            version_attrib = []
        return version_attrib

    def is_path_excluded(self, path):
        if self.excludepaths is None:
            return False
        if path in self.exclude_cache:
            return self.exclude_cache[path]
        path_splitted = path.split('/')
        for ep, depth in self.excludepaths:
            for idx, tmp_ in enumerate(path_splitted):
                if idx >= depth:
                    self.exclude_cache[path] = True
                    return True
                if ep[idx].search(tmp_) is None:
                    break
            else:
                self.exclude_cache[path] = True
                return True
        self.exclude_cache[path] = False
        return False

    @staticmethod
    def clean_args(compiler_args):
        new_args, include_paths = [], []
        skip_next = True                        #act9kor changed to true
        for arg in list(compiler_args):
            if skip_next:                       # act9kor todo always stays false need changes
                skip_next = False
                if not arg.startswith('-'):
                    continue
            if arg.startswith(('-MF', '-o', '-m', '-x')):
                skip_next = True
                continue
            elif arg.lower().startswith(('-iqoute', '-i-', '-mmd')):
                # GCC 4/3
                continue
            elif arg.lower().startswith('-f'):
                continue
            elif arg.lower().endswith('.c'):
                # input file to be ignored
                continue
            elif arg.startswith('-I'):
                # include path
                include_paths.append(arg[2:])
            else:
                new_args.append(arg)
        return new_args, include_paths

    def get_compiler_flags(self):
        if 'ADD_FLAGS' in self.swb_config:
            tmp_ = self.swb_config['ADD_FLAGS'].strip()
        elif 'COMPILER_ADD_FLAGS' in self.swb_config:
            tmp_ = self.swb_config['COMPILER_ADD_FLAGS'].strip()
        else:
            return ''
        if tmp_.startswith('"') and tmp_.endswith('"'):
            return [x.strip() for x in tmp_[1:-1].split(' ')]
        return tmp_

    def create_i_files(self, no_clean=False, store_results=False, no_write=False,
                       log_search_file=True, src_file_list=None, debug_log=False,maps_curves_search_lst=None ):



        if not no_write:
            opts = {'output': [self.outputpath, 'i'],
                    're_search_ret': self.re_search_ret,
                    're_search': self.re_search, }
        else:
            opts = {'re_search_ret': self.re_search_ret,
                    're_search': self.re_search, }

        if src_file_list is None:
            src_file_list = self.prj.getsrclist(ulf)
            src_file_list = list(src_file_list)

        excluded_c_files_list = self.prj.exclude_files(src_file_list)
        raw_filelist, notavailablelist = self.prj.readfilelist(src_file_list)

        # collect registered c source filelist
        c_filelist_dict = {}

        excluded_paths = {}
        for i, file_attr in enumerate(raw_filelist):
            c_path, c_file = file_attr[0]
            if self.is_path_excluded(c_path.lower().replace('\\', '/')):
                if c_path not in excluded_paths:
                    excluded_paths[c_path] = 1
                else:
                    excluded_paths[c_path] += 1
                raw_filelist[i].append('excluded')
                continue

            if not c_file.upper().endswith('.C'):
                # filter wrong registered SWSRC > which not end with '.c'
                raw_filelist[i].append('excluded')
                continue

            raw_filelist[i].append('included')
            # checks if path is equal to the input_file path
            c_size = file_attr[1]
            # include only files for code output
            options_file = {}

            if not no_clean:
                options_file['include_only'] = [c_file.lower()]
                # _msg.h, _dat.h files
                self.add_genereated_files(c_file.lower(), options_file['include_only'])
            else:
                options_file['include_only'] = []

            c_filelist_dict[c_file] = [mc_tools.OPT_CTEMP, c_path, c_size, options_file]

        # mmi6kor : 12102018 - Added to print the list extracted for analysis
        if debug_log:
            rawfiles_print = flatlist(raw_filelist)
            # Adding the Header and also Adding Not available list
            rawfiles_print = ['sep=,', 'BC Name, File Name,Size in (KB),Scan'] + rawfiles_print + notavailablelist + excluded_c_files_list
            from windows_tools import write_file
            write_file('\n'.join(rawfiles_print), path=self.outputpath + "/debug_results/", filename='scanned_filelist.csv',
                       date_time_stamp=False, access_binary=False, dbg=self.dbg)

        if not len(c_filelist_dict):
            return

        cmp_flags = self.clean_args(list(self.get_compiler_flags()))[0]
        cmp_flags.insert(0, '-DGNU=1')
        if self.prj.get_pverbuild() == 'MDGB' or self.prj.get_pverbuild() == 'PMB':
            tmp_flags = self.get_flags_compiler_version(self.gcc_path, use_version=(4, 6))
        else:
            tmp_flags = self.get_flags_compiler_version(self.gcc_path)
        cmp_flags = tmp_flags + cmp_flags

        start = time()

        # read ospfile
        ospsrvlist = readospcontent(self.root, self.search_list)

        # Passing the Argument to MC Parser
        c_options = [{mc_tools.OPT_CTEMP: [self.gcc_path, self.gcc_exec, self.gcc_env, self.include_paths, cmp_flags,
                                           self.myflags, opts]}, ospsrvlist]
        if self.ulf is not None:
            self.ulf.msg(self.ulf_key, 'CREATING_I', ft=len(c_filelist_dict))
        else:
            self.dbg.out(3, 'scanning %d relevant source files ...' % (len(c_filelist_dict)))

        self.sourcefile_num = len(c_filelist_dict)
        self.ctemps = MCParser(nc=self.nc, debug=0)
        self.ctemps.parse(self.root, c_filelist_dict, c_options, prc=self.cpu, clip_filesize=100000, maps_curves_search_lst=maps_curves_search_lst)

        if log_search_file:
            log_cmds = []
            if mc_tools.OPT_CTEMP in self.ctemps.results:
                for file_name in sorted(list(self.ctemps.results[mc_tools.OPT_CTEMP]), key=lambda x: x.strip().lower()):
                    log_cmds.append(self.ctemps.results[mc_tools.OPT_CTEMP][file_name][1])
            from windows_tools import write_file
            write_file(self.alm_msg + '\n'.join(log_cmds), path=self.outputpath + "/debug_results/",
                       filename='srvchecker_build_cmds.log', date_time_stamp=False, access_binary=False, dbg=self.dbg)

        ct_stderr = 0
        print_stderr = []

        if self.search_list is not None:
            count_srv = 0
            count_direct=0

            log_search = ['>>>Search results:']
            srv_used_lst=set([])
            possible_direct_usage=set([])
            if mc_tools.OPT_CTEMP in self.ctemps.results:
                for file_name in sorted(list(self.ctemps.results[mc_tools.OPT_CTEMP]), key=lambda x: x.strip().lower()):
                    # get search result for each file
                    search_result = self.ctemps.results[mc_tools.OPT_CTEMP][file_name][2]
                    stderr = self.ctemps.results[mc_tools.OPT_CTEMP][file_name][3]
                    if stderr is not None:
                        # mmi6kor:111018: Writing the Compiler Error Log information
                        print_stderr.append(file_name + ":\n" + str(stderr) + "\n")
                        ct_stderr += 1
                        if (self.ulf is not None) and (self.ulf_key is not None):
                            self.ulf.msg(self.ulf_key, 'GCC_COMPERR', ft=stderr, filename=file_name, stdout=False)

                    for tmp_c_path, tmp_c_filename, srv_found, found_unkown ,line_no_start, line_no_end, osp_status in search_result:
                        for each_found in srv_found:             #labels found with srv
                            srv_used_lst.add('>'+((each_found[1]).lstrip('_')))
                        for each_found in found_unkown:         #labels found without srv possible direct access
                           possible_direct_usage.add('>'+((each_found[1]).lstrip('_')))
                        self.search_results.append((tmp_c_path, tmp_c_filename, srv_found, found_unkown,
                                                line_no_start, line_no_end, osp_status))


            log_search += ['']

            log_search += ['>>>%d matches found for affected maps and curves with srv functions' % (len(srv_used_lst))] + ['']
            log_search.extend(srv_used_lst)
            log_search += ['>>>%d matches found for posible affected maps and curves with outer function usage' % (len(possible_direct_usage))] + ['']
            log_search.extend(possible_direct_usage)
            log_search += ['>>>RegEx used:'] + [x.decode() for x in self.search_list] + ['']
            if len(excluded_paths):
                log_search += ['>>>paths ignored:']
                for path in sorted(list(excluded_paths.keys()), key=lambda x: x.strip().lower()):
                    log_search += ['%s (%d c files)' % (path, excluded_paths[path])]
                log_search += ['']

            if log_search_file:
                from windows_tools import write_file
                write_file(self.alm_msg + '\n'.join(log_search), path=self.outputpath + "/debug_results/", filename='search_result.log',
                           date_time_stamp=True, access_binary=False, dbg=self.dbg)

        if store_results:
            self.results = self.ctemps.results

        if ct_stderr:
            if debug_log:
                from windows_tools import write_file
                # mmi6kor:111018: Writing the Compiler Error Log information
                write_file(self.alm_msg + '\n'.join(print_stderr), path=self.outputpath + "/debug_results/",
                           filename='compiler_error_result.log', date_time_stamp=True, access_binary=False,
                           dbg=self.dbg)

            if self.ulf is not None:
                self.ulf.msg(self.ulf_key, 'GCC_COMPERR_I', ft=ct_stderr)
            else:
                self.dbg.out(2, 'in %d files precompiler error detected' % ct_stderr)

        amount = self.ctemps.bytecnt / 1024.0 / 1024.0
        time_consume = time() - start
        performance = amount / time_consume
        if self.ulf is not None:
            self.ulf.msg(self.ulf_key, 'CREATED_I', ft=(amount, time_consume, performance))
            # Only for testing.
            # Not possible to get the ifile generation time and cleaning time in multiprocessing environment.
            # if debug_log:
            #     # AIR6KOR: write i file generation time and total time taken for cleaning it
            #     self.ulf.msg(self.ulf_key, 'IFILE_TIME', ft=self.ctemps.get_ifile_creation_time())
            #     self.ulf.msg(self.ulf_key, 'IFILECLEAN_TIME', ft=self.ctemps.get_cleaning_ifile_time())
        else:
            self.dbg.out(3, '%.1fMB done in %3.1f seconds (%.1fMB/s).' % (amount, time_consume, performance))

    def get_search_results(self):
        return self.search_results

    @staticmethod
    def add_genereated_files(src_file, target_list, add_ext=None):
        add_ext_i=[]            # act9kor todo changes done
        if add_ext is None:
            add_ext_i= ['_msg.h', '_dat.h']
        else:
            add_ext_i=add_ext+['_msg.h', '_dat.h']
        tmp = os.path.splitext(src_file)[0]
        for ext in add_ext_i:
            target_list.append(tmp + ext)
        return


    def get_search_string(self):
        if self.re_search is not None:
            return self.re_search.pattern.decode()
        return ''

    def get_srv_search_list(self):
        return self.srv_search_list

    def get_sourcefile_num(self):
        return self.sourcefile_num


# ------------------------------------------------------------------------------

# Also found from windows_tools.py in multiprocess_workaround function
# PyInstaller workaround when GUI calls SRVChecker
# Module multiprocessing is organized differently in Python 3.4+
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking


# AIR6KOR: Optimized code
def check_filepath_arg(filepath_arg, default_fn, outputpath, ulf_=None, ulf_key=None, create_file=True):

    def return_path_or_file(path_name, file_name):
        if len(path_name.strip()):
            if not os.path.exists(path_name):
                try:
                    os.makedirs(path_name)
                except PermissionError:
                    if ulf_ is not None:
                        ulf_.msg(ulf_key, 'NO_PERMISSION', ft=path_name)
            return os.path.join(path_name, file_name)
        return file_name  # Only file name given, without file path - YET

    if filepath_arg is not None:
        if create_file:
            # check if given path is actually a file path or just a path
            if os.path.isfile(filepath_arg):
                path_use, file_use = os.path.split(filepath_arg)
            else:
                path_use, file_use = filepath_arg, default_fn
                if file_use is None:
                    return None

            if not len(path_use) and not len(filepath_arg):  # Only if given path empty. - YET
                path_use = outputpath

            return return_path_or_file(path_use, file_use)

        # check only if exists
        if os.path.exists(filepath_arg):
            return filepath_arg
    return None


def get_root_path(path,ulf,output_path,ignore_unc_path=True):
    # try to get project root path by instancing swb_project for each path

    from windows_tools import is_unc_path

    unc_path = is_unc_path(path)

    if (not ignore_unc_path) and unc_path:
        return None, None, True

    from pveranalyze import PverAnalyze
    ulf.msg(None, 'PVER_VALIDATION')
    prj = PverAnalyze(path,output_path)

    if not prj.checkpverproperties():
        # not a project path
        return None, prj, unc_path

    return path, prj, unc_path


def get_passed_options(opts, parsr):
    # returns list of passed options and default option values
    opts_used = opts.__dict__
    opts_default = {}
    opts_passed = {}
    for opt_key in opts_used:
        opts_default[opt_key] = parsr.get_default(opt_key)
        if opts_default[opt_key] != opts_used[opt_key]:
            opts_passed[opt_key] = opts_used[opt_key]
    opts_passed = ['%s=%s' % (k, opts_passed[k]) for k in sorted(opts_passed.keys())]
    opts_default = ['%s=%s' % (k, opts_default[k]) for k in sorted(opts_default.keys())]
    return opts_passed, opts_default


# ------------------------------------------------------------------------------
# Adjust the process priority
# ------------------------------------------------------------------------------
def adjust_process_priority(set_prio):
    """
    Usage   : Adjust the process Priority (controllable using the command line option --prio)

    Syntax  : adjust_process_priority(set_prio)
              set_prio : low(default), idle, parent, normal

    Example : adjust_process_priority('low')

    """

    prio_dict = {
        'low': psutil.BELOW_NORMAL_PRIORITY_CLASS,
        'idle': psutil.IDLE_PRIORITY_CLASS,
        'parent': None,
        'normal': psutil.NORMAL_PRIORITY_CLASS,
    }
    if set_prio not in prio_dict:
        return False
    set_prio = prio_dict[set_prio]
    if set_prio is not None:
        psutil.Process().nice(set_prio)
    return True


# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Set the endian Mode
# ------------------------------------------------------------------------------

def get_endian_mode(useendian):
    """
    Usage   : Set the Endian mode
              (controllable using the command line option --endian)

    Syntax  : get_endian_mode(useendian)
              useendian : auto(default), little , big}

    Example : get_endian_mode('auto')

    """

    endian_dict = {
        'auto': None,
        'little': True,
        'big': False,
    }
    if useendian not in endian_dict:
        return None, False
    return endian_dict[useendian], True


# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Get the search list
# ------------------------------------------------------------------------------
def get_search_list(input_searchfile):
    """
    Usage   : Replace internal srv function list with given list
              (controllable using the command line option --search)

    Syntax  : get_search_list(input_searchfile)
              input_searchfile : input srv list file name

    Example : get_search_list('C:/PVER/srvlist.lst')

    """

    # read file
    with open(input_searchfile, 'r') as F:
        input_src_files_raw = [x.split(';')[0] for x in F.readlines()]
        input_src_files_raw = [x.split(',')[0] for x in input_src_files_raw]
        input_src_files_raw = [x.strip() for x in input_src_files_raw]
    # remove header
    if len(input_src_files_raw):
        if input_src_files_raw[0].upper().startswith('FUNC'):
            try:
                input_src_files_raw = input_src_files_raw[1:]
            except:
                input_src_files_raw = []            #this line is not accessible
    return input_src_files_raw


# ------------------------------------------------------------------------------

def get_source_path_info(input_srclst, given_root, ulf_,output_path):
    # read input_src.lst
    with open(input_srclst, 'r') as F:
        input_src_files_raw = [x.strip() for x in F.readlines()]

    ulf_.msg(None, 'INPUTSRCREAD', ft=input_srclst)

    if not input_src_files_raw:
        ulf_.msg(None, 'SRCNOFILES')
    # try to get project path using first file listed
    src_path, src_filename = os.path.split(input_src_files_raw[0])
    input_srcfiles = ""
    if os.path.isabs(src_path):
        # if not src_path.startswith(given_root):
        #     ulf_.msg(None, 'MISMATCH_ROOT')
        # absolute filepaths are used in list > detect project by checking first file path listed
        rt, prj, is_uncpath = get_root_path(given_root,ulf_,output_path)
        if rt is not None:
            # input_srcfiles = [os.path.relpath(x, start=rt) for x in input_src_files_raw]
            input_srcfiles = input_src_files_raw
        else:
            ulf_.msg(None, 'SRCNOPRJABS')
    else:
        # relative filepath is used in list
        rt, prj, is_uncpath = get_root_path(given_root,ulf_,output_path)
        if rt is not None:
            input_srcfiles = input_src_files_raw
        else:
            ulf_.msg(None, 'SRCNOPRJREL')
    # check if listed source files exists
    # if not all([os.path.exists(os.path.join(rt, x)) for x in input_srcfiles]):
    #     ulf_.msg(None, 'SRCNOTFOUND')
    return input_srcfiles, rt, prj, is_uncpath


def write_impact_file(ulf_key, impactlst_args, labelsimpact, ulf_, headerinfo='', ismic=False,
                      sort_list=True, osp_correction_list=None, impacted=None, whitelist_labels=None):

    impact_lst_ = check_filepath_arg(*impactlst_args[0], **impactlst_args[1], ulf_=ulf_, ulf_key=ulf_key)
    impact_path_, impact_fn = os.path.split(impact_lst_)
    # AIR6KOR: Checks if srv_checker.lst contains lists that will be corrected in OSP
    if osp_correction_list is not None:
        labelsimpact, sort_list = get_osp_string(labelsimpact, osp_correction_list)
    if whitelist_labels is not None:
        labelsimpact, sort_list = get_whitelist_string(labelsimpact, whitelist_labels)
    if sort_list:
        labelsimpact = sorted(list(labelsimpact))
    almmsg = ''
    if ismic:
        almmsg = '<!-- ' + ALM_MSG + ' -->\n\n'
    write_file(headerinfo + almmsg + '\n'.join(labelsimpact), path=impact_path_, filename=impact_fn,
               date_time_stamp=False)

    impact_hexfilename = os.path.split(impact_lst_)[1]
    if impacted is not None and not impacted:
        ulf_.msg(ulf_key, 'UC2_NOTAFFECTED', ft=impact_hexfilename)

    ulf_.msg(ulf_key, 'WRITEFILE', ft=(impact_fn, impact_path_))

    if impacted is not None and impacted:
        labels_len = len(labelsimpact)
        if '\n<!--Project specific Maps/curves analyzed and approved from project department head-->' in labelsimpact:
            labels_len -=1
        ulf_.msg(ulf_key, 'UC2_AFFECTED', ft=(labels_len, impact_hexfilename))

    return impact_lst_


def get_osp_string(labelsimpact, osp_correction_list):
    # AIR6KOR: If <!--Assumed this is Corrected in OSP--> is present in srvchecker_scan.lst
    # Write values separately in the file.
    labelsimpact_tmp = set(labelsimpact)
    if len(osp_correction_list):
        osp_correction_list = osp_correction_list & labelsimpact_tmp
        if len(osp_correction_list):
            impacted_label = []
            labelsimpact_tmp = labelsimpact_tmp ^ osp_correction_list
            if len(labelsimpact_tmp):
                impacted_label += sorted(list(labelsimpact_tmp))
                return impacted_label, False  # False if list is sorted
    return labelsimpact_tmp, True  # True for not sorted


def get_whitelist_string(labelsimpact, whitelist_dict):
    labelsimpact_tmp = set(labelsimpact)
    if whitelist_dict:
        whitelist = set(whitelist_dict.keys())
        whitelist_labels = whitelist & labelsimpact_tmp
        if len(whitelist_labels):
            impacted_label = []
            labelsimpact_tmp = labelsimpact_tmp ^ whitelist_labels
            if len(labelsimpact_tmp):
                impacted_label += sorted(list(labelsimpact_tmp))
            if len(whitelist_labels):
                impacted_label.append("\n<!--Project specific Maps/curves analyzed and approved from project department head-->")
                impacted_label += sorted([whitelist_dict[wht_labels] for wht_labels in whitelist_labels])
            return impacted_label, False  # False if list is sorted
    return labelsimpact_tmp, True  # True for not sorted


# mmi6kor : Reading the OSP File 02112018
def readospcontent(prj_root, searchlist):
    # Joining the content
    searchsrv = b'|'.join(searchlist)
    searchsrv = searchsrv.decode("utf-8")
    # seacrhospsrv = re.compile(r'' + '(' + searchsrv + ')')
    ospsrvfunction = []
    osppath = ""
    ignorelines = re.compile(r'^\s*#')
    allospfilename = prj_root + "/_gen/swb/filegroup/src_lists/all_osp_files.lst"

    if os.path.exists(allospfilename):
        with open(allospfilename, "r") as F:
            allospfilecont = F.readlines()

        # Reading the content and check this ospfile exists
        for row, data in enumerate(allospfilecont):
            if data.find('dgs_ipofunctions_sstreduction_inca_fix.osp') > 0:
                osppath = prj_root + '/' + allospfilecont[row]
                osppath = osppath.strip()
                break

        # Search OSP file exists
        if osppath != "" and os.path.exists(osppath):
            cleanedosp = []
            with open(osppath, "r") as F:
                ospfilecont = F.readlines()

            for row, data in enumerate(ospfilecont):
                if ignorelines.search(data) is None:
                    cleanedosp.append(data)

            cleanedosp = "".join(cleanedosp)
            ospmatch = list(map(lambda x: x.group(), re.finditer(searchsrv, cleanedosp)))
            ospsrvfunction = list(set(ospmatch))

    return ospsrvfunction


def checkrelativepath(rt, path):
    if not os.path.isabs(path) and rt:
        return os.path.join(rt, path)
    elif not os.path.isabs(path) and not rt:
        return None
    else:
        return path
# --------------------------------------------------------------------------------


def old_files_backup(outputpath, backup,ulf,input_lst=False):
    '''
    :param outputpath:is the path location where files that need to be backedup
    :param backup:True/False
    :param input_lst:if srvchecker_scan.lst path is present in backup file it will be copied to output path
    :return:
    1. LoggerDisp object 'srv_log' will be returned
    2. if any mentioned files found in output path will be taken backup by creating a folder with date and time of now
    3. if backup is false also returns LoggerDisp object
    4. if any .xlsx file in path is open it ensures to close
    '''


    valid_backup_files = (
        # Muliple/Single Hex File
        'wrong_hexfilespath.lst',

        # other output results
        'affected_items.lst',
        'srvchecker_scan.lst',

        # ulf files
        'srvchecker_scan.ulf',
        'affected_items.ulf',
        'srvchecker_impact.ulf',

        # calprm_results.xlsx
        'calprm_results.xlsx',

        # Log excel
        'srvchecker_log.xlsx',

        # / debug_results / scanned_filelist.csv
        # / debug_results / search_result.log
        # / debug_results / compiler_error_result.log
        # / debug_results / srvchecker_build_cmds.log
        'debug_results',

        # Ending with srvchecker_impact.lst and srvchecker_impact.ulf
        'srvchecker_impact.ulf',
        'srvchecker_impact.lst'
    )
    if not backup:
        return None

    files = os.listdir(outputpath)
    create_backup_folder = False
    backup_path = ''
    if files:
        for f in files:
            if f.endswith(valid_backup_files):
                from shutil import move as move_oldfiles, copy
                if not create_backup_folder:
                    from datetime import datetime
                    td = datetime.now()
                    time_stamp = '%d%02d%02d_%02d%02d%02d' % (td.year, td.month, td.day,
                                                              td.hour, td.minute, td.second)
                    backup_path = os.path.join(outputpath, '_srvchecker_backup_' + time_stamp)
                    if not os.path.exists(backup_path):
                        os.makedirs(backup_path)
                    create_backup_folder = True
                    if 'srvchecker.log' in files:

                        move_oldfiles(os.path.join(outputpath, 'srvchecker.log'), backup_path)  
                    ulf.update_logger(srv_logger)
                    ulf.msg(None, 'BACKING_UP', ft=outputpath)

                try:
                    if f.endswith(".xlsx"):
                        from general import ensure_excel_closed
                        ensure_excel_closed(f)
                    if input_lst and f == 'srvchecker_scan.lst':
                        copy(os.path.join(outputpath, f), backup_path)
                    else:
                        move_oldfiles(os.path.join(outputpath, f), backup_path)
                except:
                    pass
                    # DOUBT
                    # dbg.send(2, 'File "%s" is opened.' % f)
    if create_backup_folder:
        ulf.msg(None, 'BACKUP_COMPLETED', ft=outputpath)

    return True


def prepare_output_path(outputpath):
    if not os.path.exists(outputpath):
        try:
            os.makedirs(outputpath)
            return True
        except:
            sleep()
            if not os.path.exists(outputpath):
                try:
                    os.makedirs(outputpath)
                    return True
                except:
                    return False
    return True


def endtime_print(ulf,starttime, ulf_key, key, debug=False):
    endtime = datetime.now()
    elapsedtime = (endtime - starttime).total_seconds()
    if ulf is not None:
        if debug:
            ulf.msg(ulf_key, 'TIME_TAKEN_DEBUG', ft=(key, elapsedtime))
        else:
            ulf.msg(ulf_key, 'TIME_TAKEN_INFO', ft=(key, elapsedtime))


def validate_and_get_source_path_info(white_lst, ulf):
    header = "<!--Project specific Maps/curves analyzed and approved from project department head-->"
    count = 1
    whitelist_labels_ = dict()
    with open(white_lst, 'r') as F:
        for line_no, line_entry in enumerate(F.readlines()):
            line_entry = line_entry.strip()
            line_no = line_no + 1
            if line_entry:
                if count == 1:
                    if header not in line_entry:
                        ulf.msg(None, 'WHITELST_DISCARDED', ft=white_lst)
                        break
                    count = 0
                    continue
                whitelist_entries_parameter = line_entry.split(',', 1)
                if len(whitelist_entries_parameter) != 2:
                    ulf.msg(None, 'INVALID_ENTRY', ft=(line_no, line_entry))
                    continue
                else:
                    label_name, reason = whitelist_entries_parameter
                    if not label_name.strip():
                        ulf.msg(None, 'INVALID_ENTRY', ft=(line_no, line_entry))
                    else:
                        reason = reason.split(":")
                        if len(reason)==2:
                            if (reason[0].strip().lower() == "reason") and reason[1].strip():
                                whitelist_labels_[label_name.strip()] = line_entry
                            else:
                                ulf.msg(None, 'INVALID_ENTRY', ft=(line_no, line_entry))
                        else:
                            ulf.msg(None, 'INVALID_ENTRY', ft=(line_no, line_entry))
    return whitelist_labels_

def buggy_input_lst(input_lst):
    srv_version=""
    from srvCheckerBuggyVersions import buggy_versions
    version = re.compile(r'srvchecker\s*v(\d+\.\d+\.\d+)')
    with open(input_lst, 'r') as F:
        file_content=F.read()
        version_search = version.search(file_content)
        if version_search is not None:
            srv_version = version_search.group(1)
            if srv_version in buggy_versions:
                return True, srv_version
    return False, srv_version


def listOfCurvesAndMaps(prjt,ulf):
    A2LMergerToolbaseexecpath = "C:/toolbase/a2lmerger/test52_4.4.0/a2lmerger.cmd"
    mapNcurve_str = None
    boundary = br'\b'

    a2LPath = prjt.getA2LFilePath()
    a2LMerger_path=os.path.join(prjt.output,'A2LMerger_output')
    output_possibly = os.path.join(a2LMerger_path, "affected_items.lst")
    output_log = os.path.join(a2LMerger_path, "A2LMergerUser.log")
    output_ulf = os.path.join(a2LMerger_path, "A2LMerger.ulf")
    output_toolLog = os.path.join(a2LMerger_path, "A2LMergerTool.log")
    try:
        if not os.path.exists(a2LMerger_path):
            os.makedirs(a2LMerger_path)
        else:
            for file1 in os.listdir(a2LMerger_path):
                file_path = os.path.join(a2LMerger_path, file1)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
    except:
        pass

    try:
        import subprocess
        calltxec = subprocess.Popen([A2LMergerToolbaseexecpath, '--MA2L', a2LPath, '--possibly_affected_items', output_possibly, '--log', output_log, '--ulflog', output_ulf,'--toollog',output_toolLog],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = calltxec.communicate()
        p_status = calltxec.wait()

        # If executed successfully
        if calltxec.returncode == 0:
            with open(output_possibly, 'r') as F:
                elemnts_lst = set()
                for line_no, line_entry in enumerate(F.readlines()):
                    line_entry = line_entry.strip()
                    if line_entry:
                        affected_list_parameters = line_entry.split(',')
                        if len(affected_list_parameters) == 3:
                            map_label_name = affected_list_parameters[0]
                            if map_label_name.strip():
                                elemnts_lst.add("_"+ map_label_name.strip())
                            else:
                                ulf.msg(None, 'INVALID_ENTRY', ft=(line_no, line_entry))
                        else:
                            ulf.msg(None, 'INVALID_ENTRY', ft=(line_no, line_entry))
                            continue
                ele_lst = [boundary + x.encode() + boundary for x in elemnts_lst]
            import re
            mapNcurve_str = re.compile(b'|'.join(ele_lst))
        return mapNcurve_str

    except:
        pass

def collecting_the_options_from_user(*args,**kwargs):
    usage = "%(prog)s -r prj_root_path [-h] ..."
    parser = ArgParser(description="SrvChecker - Tool to check srvLib guidelines", usage=usage)
    parser.add_argument("-r", "--root", default="", metavar="DIR", help="Project root folder")
    parser.add_argument("-o", "--output-path", default="", metavar="DIR", help="Output result path")
    parser.add_argument("-c", "--compiler", default=r"C:\toolbase\hightec\cd_v3.4.5.14\bin\tricore-gcc.exe",
                        metavar="FILE",
                        help="Specify compiler path, else default hightec compiler cd_v3.4.5.14 will be considered")
    parser.add_argument("-a", "--affected-list", default="", metavar="FILE", help="Possibly affected list - "
                                                                                  "Only works with MDGB PVER!")
    parser.add_argument("--output-affected-ulf", default="",
                        help="output ulf (affected labels) filepath - MDGB usecase")
    parser.add_argument("-x", "--exclude", default="(srv*|eos*|epos*)", help="Exclude paths with given regex")
    parser.add_argument("--output-lst", default="", help="srvchecker scan list output filepath")
    parser.add_argument("--output-ulf", default="", help="srvchecker scan  ulf output filepath")
    parser.add_argument("--output-impact-lst", default="", help="output list (impacted labels) filepath")
    parser.add_argument("--output-impact-ulf", default="", help="output ulf (impacted labels) filepath")
    parser.add_argument("--no-scan", action="store_true", default=False, help="disables scanning source files")
    parser.add_argument("--force-scan", action="store_true", default=False, help="forces scanning source files")
    parser.add_argument("--debug", action="store_true", default=False, help="Outputs debugging files")
    parser.add_argument("--a2l", default="", help="axispoints reduction check: A2L filepath")
    parser.add_argument("--hex", default="", help="axispoints reduction check: calibrated HEX filepath"
                                                  " or path to list of hex files.")
    parser.add_argument("--endian", default="auto", type=lambda s: s.lower(),help="set endian {auto(default)|little|big}")
    parser.add_argument("--input-src-lst", default="", help="input *.c files to be scanned")
    parser.add_argument("--search", default="", help="replace internal srv function list with given list")
    parser.add_argument("--input-lst", default="", help="compare reduced labels in HEX&A2L against this list")
    parser.add_argument("--temp-folder", default=tempfile.gettempdir() + r"\_srvchecker",
                        help="temp folder used for fetching files from a UNC path")
    parser.add_argument("--conf-filepath", default=r"", help="use configuration file")
    parser.add_argument("--get-conf-file", action="store_true", default=False, help="output internal scan config")
    parser.add_argument('--cpu', default='-1', help='adjusts core count: all cores - n (<0), all cores (=0),'
                                                    ' n cores (>0) (default=-1)')
    parser.add_argument('--prio', default='low', type=lambda s: s.lower(),
                        help='adjusts process priority (low(default), idle, normal, parent)')
    parser.add_argument('--no-counter', action="store_true", default=False, help="disables filecounter output "
                                                                                 "during scanning/fetching")
    parser.add_argument("-q", "--quiet", action="store_true", default=False, help="be quiet ...")
    parser.add_argument("--about", action="store_true", default=False, help="show about dialog")
    parser.add_argument("--log", action="store_true", default=False, help="outputs log files except i files")
    parser.add_argument("--ifiles", action="store_true", default=False, help="outputs i files")
    parser.add_argument("--no-backup", action="store_true", default=False,
                        help="backs up old srvchecker generated files")
    parser.add_argument("-w", "--whitelist", default="", metavar="FILE",
                        help="list of maps/curves analysed and approved from project department head under different heading in impact.lst file")

    options = parser.parse_args()

    return options,parser


def initiating_the_errorhandler_and_dbghandler(options_passed, options_default, options,start_time):
    # configure debug handler
    dbg = 3
    if options.quiet:
        dbg = 0
    dbgh_instance = DbgHandler('', dbg)
    ulf = ErrHandler(timestamp=False, msg_category='serviceCheck', ti='DGS_Coding_Guideline_SRVCHK', usedbg=dbgh_instance,
                     debug=options.debug)
    ulf.add_on_creation('OPTIONS',
                        ulfmsg='options passed: ' + '; '.join(options_passed) + ' options default: ' + '; '.join(
                            options_default))
    ulf.update_start_time(start_time)

    return dbgh_instance, ulf


def validating_and_taking_actions_wrt_to_options(options):
    # About
    if options.about:
        print_about()
        # normal exit
        sys.exit(0)
    # 07112018 : If debug is enabled ifiles creation will also will be enabled
    if options.debug:
        options.ifiles = True

def validaing_output_path(options,dbgh,ulf,backup_needed):
    root = options.root
    output_path = options.output_path
    if not output_path:
        dbgh.send('Output path is mandatory. Use option --output-path to specify path.', {})
        sys.exit(-1)
    else:
        output_path = checkrelativepath(root, output_path)
        if output_path is None:
            dbgh.send('--output-path is relative. Provide PVER path or an absolute path as input.', {})
            sys.exit(-1)
        else:
            if prepare_output_path(output_path):
                lst_check = False
                if options.input_lst:
                    input_lst_path = os.path.split(options.input_lst)[0]
                    if os.path.abspath(input_lst_path) == os.path.abspath(output_path):
                        lst_check = True                                                        #TODO act9kor even if we are sending true for lst_check it is taking as false
                old_files_backup(output_path, backup_needed,ulf,input_lst=lst_check)
            else:
                dbgh.send('ERROR: Output path cannot be created.', {})
                sys.exit(-1)

    return output_path

def validate_root_path(options,ulf_):
    root = options.root
    root_exists = True
    if root:
        if not os.path.isabs(root):
            ulf_.msg(None, 'ROOTRELATIVE')
        elif not os.path.exists(root):
            ulf_.msg(None, 'PVER_NOT_FOUND', ft=root)
        return root


def initializing_xl_writer(ulf_,output_path_,options_passed_,options_default_):
    xl_writer = ExcelWriter(output_path_, ''.join(options_passed_), ' '.join(options_default_))
    ulf_.set_xl_writer(xl_writer)
    return xl_writer


def initializing_srv_logger(ulf_,outputpath_):
    srv_logger_instance = LoggerDisp(outputpath_)
    ulf_.update_logger(srv_logger_instance)
    return srv_logger_instance


def validate_input_wrt_usecase(root_,options_,ulf_):
    ''' validates the iniput given by user based on use cases'''
    input_lst = options_.input_lst
# -------check_no_options_given
    if not root_ and not input_lst and not options_.input_src_lst and not options_.a2l and not options_.hex:
        ulf_.msg(None, 'NOOPTIONS')
# -------either input_lst or root not both
    if root_ and input_lst:
        ulf_.msg(None, 'UC1_NOROOT_NOINPUTLST')
    # elif not output_path:
    #     ulf.msg(None, 'NOOUTPUTPATH')
# ------with force scan root is needed
    if options_.force_scan and not root_:
        ulf_.msg(None, 'FORCESCAN')


def validate_input_lst_and_buggy_version(ulf_,root_,options_):
    '''checks for input_lst path validation on success checks for report generated version'''
    input_lst_ = checkrelativepath(root_, options_.input_lst)
    if input_lst_ is None:
        ulf_.msg(None, 'RELATIVEPATH', ft='--input-lst')
    buggy_vers, version=buggy_input_lst(input_lst_)
    if buggy_vers:
        input_lst_ = None
        HELP_URL = 'https://connect.bosch.com/blogs/Service_Library_PS-EC/entry/Srvchecker_Warnings?lang=en_us'
        ulf_.msg(None, 'BUGGY_INPUTLIST_FILE', ft=(version,HELP_URL))
    return input_lst_


def validate_whitelist(root_,output_path_,options_,ulf_):
    whitelist_labels_ = None
    if options_.whitelist:
        white_list = checkrelativepath(root_, options_.whitelist)
        if white_list is None:
            ulf_.msg(None, 'RELATIVEPATH', ft='--whitelist')
        white_lst = check_filepath_arg(white_list, None, output_path_, create_file=False)
        if white_lst is None:
            ulf_.msg(None, 'INPUTWHITELSTNOTPRESENT', ft=options_.whitelist)
        else:
            whitelist_labels_ = validate_and_get_source_path_info(white_lst, ulf_)
            return whitelist_labels_
    else:
        return whitelist_labels_

def validate_output_lst(root_,options_,ulf_,backup_needed_):
    output_lst_ = ''
    if options_.output_lst:
        output_lst_ = checkrelativepath(root_, options_.output_lst)
        if output_lst_ is None:
            ulf.msg(None, 'RELATIVEPATH', ft='--output-lst')
        else:
            if os.path.exists(output_lst_) and not os.path.isfile(output_lst_):
                old_files_backup(output_lst_, backup_needed_,ulf_)
    return output_lst_


def validate_output_affected_ulf(root_,options_,ulf_,backup_needed_):
    output_affected_ulf = checkrelativepath(root_, options_.output_affected_ulf)
    if output_affected_ulf is None:
        ulf_.msg(None, 'RELATIVEPATH', ft='--output-affected-ulf')
    else:
        if os.path.exists(output_affected_ulf):
            old_files_backup(output_affected_ulf, backup_needed_,ulf_)


def validating_output_ulf(root_,options_, ulf_,backup_needed_):
    output_ulf = checkrelativepath(root_, options_.output_ulf)
    if output_ulf is None:
        ulf_.msg(None, 'RELATIVEPATH', ft='--output-ulf')
    else:
        if os.path.exists(output_ulf):
            old_files_backup(output_ulf, backup_needed_,ulf_)
    return output_ulf


def validate_output_impact_ulf(root_,options_, ulf_,backup_needed_):
    output_impact_ulf = checkrelativepath(root_, options_.output_impact_ulf)
    if output_impact_ulf is None:
        ulf_.msg(None, 'RELATIVEPATH', ft='--output-impact-ulf')
    else:
        if os.path.exists(output_impact_ulf):
            old_files_backup(output_impact_ulf, backup_needed_,ulf_)
    return output_impact_ulf


def validate_output_impact_lst(root_,options_, ulf_,backup_needed_):
    output_impact_lst = checkrelativepath(root_, options_.output_impact_lst)
    if output_impact_lst is None:
        ulf_.msg(None, 'RELATIVEPATH', ft='--output-impact-lst')
    else:
        if os.path.exists(output_impact_lst):
            old_files_backup(output_impact_lst, backup_needed_,ulf_)
    return output_impact_lst

def validate_all_paths(root,output_path,options,ulf,backup_needed):
    # -------------------------------input_list---like--srvchecker_scan.lst--------------
    if options.input_lst:
        input_lst=validate_input_lst_and_buggy_version(ulf_=ulf,root_=root,options_=options)
    else:
        input_lst = None
    # ------------------------------whitelist----------------------------------------------
    if options.whitelist:
        whitelist_labels=validate_whitelist(root_=root,output_path_=output_path,options_=options,ulf_=ulf)
    else:
        whitelist_labels=None
    # -----------------------------output_lst---------------------------------------------
    if options.output_lst:
        output_lst=validate_output_lst(root_=root, options_=options, ulf_=ulf, backup_needed_=backup_needed)
    else:
        output_lst=''
    # -----------------------------output_affected_ulf---------------------------
    if options.output_affected_ulf:
        output_affected_ulf=validate_output_affected_ulf(root_=root,options_=options, ulf_=ulf, backup_needed_=backup_needed)
    else:
        output_affected_ulf=''
    # -----------------------------output_ulf----------------------------------
    if options.output_ulf:
        output_ulf=validating_output_ulf(root_=root,options_=options, ulf_=ulf, backup_needed_=backup_needed)
    else:
        output_ulf = ''
    # -----------------------------output_impact_ulf-------------------------------------
    if options.output_impact_ulf:
        output_impact_ulf=validate_output_impact_ulf(root_=root,options_=options, ulf_=ulf, backup_needed_=backup_needed)
    else:
        output_impact_ulf=''
    # -----------------------------output_impact_lst-------------------------------------
    if options.output_impact_lst:
        output_impact_lst=validate_output_impact_lst(root_=root,options_=options, ulf_=ulf, backup_needed_=backup_needed)
    else:
        output_impact_lst=''

    return input_lst,whitelist_labels,output_lst,output_affected_ulf,output_ulf,output_impact_ulf,output_impact_lst


# --------------------------------------------------------------------------------
# Calls the Main Function
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    # --------------------------------------------------------------------------------
    #                           initializing the Srvchecker tool
    # --------------------------------------------------------------------------------
    multiprocess_workaround()
    freeze_support()
    # --------------------------------------------------------------------------------
    #                           Parser Options from user
    # --------------------------------------------------------------------------------
    options,parser=collecting_the_options_from_user()
    options_passed, options_default = get_passed_options(options, parser)
    # --------------------------------------------------------------------------------
    #                   initializing error handlers and start time
    # --------------------------------------------------------------------------------
    starttime = datetime.now()
    dbgh,ulf=initiating_the_errorhandler_and_dbghandler(options_passed, options_default, options,starttime)
    validating_and_taking_actions_wrt_to_options(options)
    #----------------------------------------------------------------------------------
    #                          VALIDATION STARTS
    #----------------------------------------------------------------------------------
    backup_needed = True if not options.no_backup else False
    root=validate_root_path(options,ulf_=ulf)
    output_path = validaing_output_path(options, dbgh, ulf,backup_needed)

    # ---------------initializing_srv_logger_creates_srvchecker.log_file_in_outputpath--
    srv_logger_instance=initializing_srv_logger(ulf_=ulf,outputpath_=output_path)

    # -------------initailizing_xl_writer---- creates the srvchecker_log.xlsx file in output
    xl_writer=initializing_xl_writer(ulf_=ulf,output_path_=output_path,options_passed_=options_passed,options_default_=options_default)

    if ulf is not None:
        ulf.msg(None, 'ARTIFACTS_VALIDATION_START')
    else:
        dbgh.out(4, 'ARTIFACTS_VALIDATION_START')
    # ------------------------------------validate_input_wrt_usecase---------------------
    validate_input_wrt_usecase(root_=root, options_=options)

    #------------------------------------validate_all_remaining_paths------------------------
    input_lst, whitelist_labels, output_lst, output_affected_ulf, output_ulf, output_impact_ulf, output_impact_lst=\
    validate_all_paths(root, output_path, options, ulf, backup_needed)

    #-------------------------------------





    # adjust priority
    if not adjust_process_priority(options.prio):
        ulf.msg(None, 'UNKNWONPRIO')




    use_endian, endian_ok = get_endian_mode(options.endian)
    if not endian_ok:
        ulf.msg(None, 'UNKNWONENDIAN')







    if not options.a2l and not options.hex:
        ulf.msg(None, 'UC2_NOA2LHEX')






    now = datetime.now()
    headerinfoimpact = '<!-- File Generated: ' + now.strftime(
        "%d-%m-%Y %H:%M:%S") + ' -->\n' + '<!-- Tool: ' + TOOLNAME + ' v' + VERSION + ' -->\n\n'

    zeroimpact = ["<!-- No issues found in the hex file during the scanning. -->"]



    try:
        # create configuration file if needed
        if options.get_conf_file:
            filename = to_conf_file(output_path)
            ulf.msg(None, 'CONFCREATED', ft=filename)

        # get search list
        if len(options.search):
            in_search_file = checkrelativepath(root, options.search)
            if in_search_file is None:
                ulf.msg(None, 'RELATIVEPATH', ft='--search')
            input_search_file = check_filepath_arg(in_search_file, None, output_path, create_file=False)
            if input_search_file is None:
                ulf.msg(None, 'UC1_INPUTSEARCH', ft=options.search)
            search_replace = get_search_list(input_search_file)
            # check if empty
            if not len(search_replace):
                ulf.msg(None, 'UC1_INPUTEMPTY', ft=options.search)
            ulf.msg(None, 'UC1_INPUTUSE', ft=options.search)
        else:
            search_replace = None

        # ------------------------------------------------------------------------------
        # Read from the src List File Provided or Check the PVER
        # ------------------------------------------------------------------------------

        # get input source file list
        input_src_files = None
        is_unc_path = False
        prjt = None
        if len(options.input_src_lst):
            if not root:
                ulf.msg(None, 'ROOTMANDATORY')
            in_src_lst = checkrelativepath(root, options.input_src_lst)
            if in_src_lst is None:
                ulf.msg(None, 'RELATIVEPATH', ft='--input-src-lst')
            input_src_lst = check_filepath_arg(in_src_lst, None, output_path, create_file=False)
            if input_src_lst is None:
                ulf.msg(None, 'INPUTSRCERR', ft=options.input_src_lst)
            if not os.path.exists(input_src_lst):
                ulf.msg(None, 'INPUTSRCLSTNOTPRESENT', ft=options.input_src_lst)
            input_src_files, root, prjt, is_unc_path = get_source_path_info(input_src_lst, root, ulf,output_path)
        elif root:
            if os.path.isfile(root):  # If input is a file.
                ulf.msg(None, 'WRONGROOT')

            # check project pver root path
            root, prjt, is_unc_path = get_root_path(root,ulf,output_path)

        def remove_uncfiles():
            from general import unc_to_local_path
            if os.path.exists(unc_to_local_path):
                import shutil
                shutil.rmtree(unc_to_local_path)

        if root is None:
            if is_unc_path:
                remove_uncfiles()
            ulf.msg('ALL', 'UC1_INVALIDPVER')
        elif root:
            success = prjt.successfulvalidation(options)
            if is_unc_path:
                remove_uncfiles()
            if not success:
                ulf.msg('ALL', 'UC1_NOPVER')
            ulf.msg(None, 'PVER_SUCCESS', ft=(prjt.get_pverbuild(), prjt.get_pvernature()))

        is_mic = False
        alm_msg = ''
        if prjt is not None and prjt.get_pvernature() == 'MIC':
            is_mic = True
            alm_msg = '<!-- ' + ALM_MSG + ' -->\n\n'
            xl_writer.set_is_mic(is_mic)

        # get config
        use_config = None
        if len(options.conf_filepath):
            conf_path = checkrelativepath(root, options.conf_filepath)
            if conf_path is None:
                ulf.msg(None, 'RELATIVEPATH', ft='--conf-filepath')
            use_config = from_conf_file(conf_path)
            if use_config is None:
                ulf.msg(None, 'CONF_FAILED', ft=options.conf_filepath)

        ap_mapcurve_diff_labels = set([])
        a2l_filepath = ""
        hex_filepath = ""
        input_hex_ext = ''
        hexfiles = set()
        wrong_hexfiles = set()
        impact_lst_args = ()
        impact_multiple_hex = {}
        non_impacted_hex = {}
        impact_worksheet_num = 1

        # AIR6KOR: 'srvchecker_impact.ulf' is created only to record fatal errors.
        def create_impactfatalulf(ulf_key, format_str):
            # first get/create ulf filepath for output message
            impactulf = check_filepath_arg(output_impact_ulf, 'srvchecker_impact.ulf',
                                           output_path, create_file=True, ulf_=ulf, ulf_key=None)
            ulf.create('IMPACT', impactulf, TOOLNAME, VERSION)
            ulf.msg('IMPACT', ulf_key, ft=format_str)

        # check if a2l and hex is given
        if len(options.a2l) or len(options.hex):
            # comparing axispoints in A2L and HEX file -> use case scenario 2

            # check if both files are given and valid
            if len(options.a2l) and len(options.hex):
                a2l_filepath = options.a2l
                hex_filepath = options.hex

                from general import hex_extensions

                input_hex_ext = os.path.splitext(hex_filepath)[1].lower()
                if input_hex_ext not in hex_extensions and input_hex_ext != '.lst':
                    create_impactfatalulf('UC2_WRONGHEXINPUT', hex_filepath)
                    # create_impactfatalulf('UC2_WRONGHEXINPUT', hex_filepath, hex_extensions)

                a2l_filepath = checkrelativepath(root, a2l_filepath)
                if a2l_filepath is None:
                    create_impactfatalulf('RELATIVEPATH', format_str='A2L')
                if not os.path.exists(a2l_filepath):
                    create_impactfatalulf('UC2_NOA2L', a2l_filepath)

                hex_filepath = checkrelativepath(root, hex_filepath)
                if hex_filepath is None:
                    create_impactfatalulf('RELATIVEPATH', format_str='Hex')
                if not os.path.exists(hex_filepath):
                    if input_hex_ext not in hex_extensions:
                        create_impactfatalulf('UC2_NOHEX', hex_filepath)
                    else:
                        create_impactfatalulf('UC2_NOHEXLIST', hex_filepath)

                if input_hex_ext in hex_extensions:
                    hexfiles.add(hex_filepath)
                else:
                    with open(hex_filepath, 'r') as Fl:                         
                        for hex_file_line in Fl.read().splitlines():
                            hex_file_line = hex_file_line.strip()
                            if hex_file_line:
                                if os.path.splitext(hex_file_line)[1].lower() in hex_extensions:
                                    hex_file_name = checkrelativepath(root, hex_file_line)
                                    if hex_file_name is None:
                                        create_impactfatalulf('RELATIVEHEXPATH', format_str=(hex_filepath, hex_file_line))
                                    if not os.path.exists(hex_file_name):
                                        wrong_hexfiles.add(hex_file_line)
                                        continue
                                    hexfiles.add(hex_file_name)
                                else:
                                    wrong_hexfiles.add(hex_file_line)

                    if len(wrong_hexfiles):
                        xl_writer.set_wrong_hexfilespath(wrong_hexfiles)
                        if len(hexfiles):
                            filename = 'wrong_hexfilespath.lst'
                            write_file('\n'.join(wrong_hexfiles), path=output_path, filename=filename,
                                       date_time_stamp=False)
                            create_impactfatalulf('UC2_WRONGHEXFILESPATH', (len(wrong_hexfiles), hex_filepath,
                                                                            os.path.join(output_path, filename)))
                        else:
                            create_impactfatalulf('UC2_ALLHEXPATHWRONG', hex_filepath)
                    else:
                        if not len(hexfiles):
                            create_impactfatalulf('UC2_HEXFILELISTEMPTY', hex_filepath)
                        else:
                            xl_writer.set_input_hexfile(True)
            else:
                create_impactfatalulf('UC2_NOA2LHEX', None)

            # check if input lst file from previous scan is given
            input_lst = check_filepath_arg(input_lst, None, output_path, create_file=False)
            if (input_lst is None) and len(options.input_lst):
                # input lst is given, but could not be found
                create_impactfatalulf('UC2_INPUT', options.input_lst)
        if ulf is not None:
            ulf.msg(None, 'ARTIFACTS_VALIDATION_END')
        else:
            dbgh.out(4, 'ARTIFACTS_VALIDATION_END')
        endtime_print(ulf, starttime, None, 'Artifacts analysis',debug=True)

        if len(options.a2l) and len(options.hex):
            # a2l hex is given > check for reduced axis points in hex
            from axispoints import AxisPoints
            ap = AxisPoints(use_endian=use_endian)
            ap.load_a2l(a2l_filepath, filter_type={'CURVE', 'MAP'})
            from calprm_excelwriter import CalprmExcelWriter
            calprm_output_path = output_path if not output_impact_ulf else output_impact_ulf
            calprm_xl_writer = CalprmExcelWriter(calprm_output_path)

            print_val = True
            for hex_file in hexfiles:
                hex_filename = os.path.split(hex_file)[1]
                hexfile_prefix = os.path.splitext(hex_filename)[0] + '_'
                impact_ulfkey = 'IMPACT' + hexfile_prefix[:-1]
                impact_ulf = check_filepath_arg(output_impact_ulf, hexfile_prefix + 'srvchecker_impact.ulf',
                                                output_path, create_file=True, ulf_=ulf, ulf_key=None)
                ulf.create(impact_ulfkey, impact_ulf, TOOLNAME, VERSION)

                # AIR6KOR: A2L file already loaded once above
                ulf.msg(impact_ulfkey, 'UC2_A2L_OK', print_val=print_val)
                print_val = False
                ap.load_hex(hex_file)  # DOUBT - Wrong hex format
                ulf.msg(impact_ulfkey, 'UC2_HEX_OK', ft=hex_filename)

                impact_lst_args = ((output_impact_lst, hexfile_prefix + 'srvchecker_impact.lst',
                                    output_path), {'create_file': True})
                # get labels with reduced axispoints
                cal_axispoints = ap.get_axis_len(different_only=True)
                # log little/big endian
                ulf.msg(impact_ulfkey, 'UC2_ENDIAN', ft='Little' if ap.little_endian else 'Big')

                # Creating the Calprm Worksheets for each hexfile provide
                # if options.log:
                ap.create_log_file(cal_axispoints, calprm_xl_writer, filename=hexfile_prefix[:-1])
                # mmi6kor 12102018
                ulf.msg(impact_ulfkey, 'WRITEFILEONE', ft=(hexfile_prefix[:-1], os.path.join(calprm_output_path,
                                                                                             'calprm_results.xlsx')))

                ap_mapcurve_diff_count = 0
                for cal_type in list(cal_axispoints.keys()):
                    ap_mapcurve_diff_count += len(cal_axispoints[cal_type])
                    ap_mapcurve_diff_labels |= set(list(cal_axispoints[cal_type].keys()))

                if ap_mapcurve_diff_count:
                    # reduced labels found
                    ulf.msg(impact_ulfkey, 'UC2_REDUCED', ft=(ap_mapcurve_diff_count, hexfile_prefix))
                    if not (options.no_scan and (input_lst is None)):
                        impact_multiple_hex[impact_ulfkey] = {'labels': ap_mapcurve_diff_labels}
                        impact_multiple_hex[impact_ulfkey].update({'list_path': impact_lst_args})
                else:
                    xl_writer.add_worksheet('impact_' + str(impact_worksheet_num), hexfile_prefix[:-1] + '.hex')
                    impact_worksheet_num += 1
                    # create zero impact list
                    # nothing reduced
                    non_impacted_hex[impact_ulfkey] = impact_lst_args

            calprm_xl_writer.close_workbook()

            if input_lst is None and not root:
                std_out = True  # Print on stdout when 'True'
                for impacted_key in impact_multiple_hex:
                    xl_writer.add_worksheet('impact_' + str(impact_worksheet_num), impacted_key[6:] + '.hex')
                    ulf.msg(impacted_key, 'PVERLSTCONFIGURE', stdout=std_out)
                    std_out = False
                for non_impacted_key in non_impacted_hex:
                    write_impact_file(non_impacted_key, non_impacted_hex[non_impacted_key], zeroimpact,
                                      ulf, headerinfoimpact, ismic=is_mic, whitelist_labels=whitelist_labels)

                if impact_multiple_hex:
                    ulf.msg('ALL', 'OK')

            # Note : After this it will go to the end of file no further lines will get executed
            if len(impact_multiple_hex):  # If even one hex file has impacted item
                if options.no_scan and (input_lst is None):
                    std_out = True
                    for impacted_key in impact_multiple_hex:
                        xl_writer.add_worksheet('impact_' + str(impact_worksheet_num), impacted_key[6:] + '.hex')
                        ulf.msg(impacted_key, 'UC2_SCAN_NEEDED', stdout=std_out)
                        std_out = False

                    for non_impacted_key in non_impacted_hex:
                        write_impact_file(non_impacted_key, non_impacted_hex[non_impacted_key], zeroimpact,
                                          ulf, headerinfoimpact, ismic=is_mic, whitelist_labels=whitelist_labels)
                    if is_mic:
                        ulf.msg('ALL', 'ALM_WARNING')
                    ulf.msg('ALL', 'OK')
            else:
                if not options.force_scan:
                    if is_mic:
                        ulf.msg('ALL', 'ALM_WARNING')
                    std_out = True
                    for non_impacted_key in non_impacted_hex:
                        ulf.msg(non_impacted_key, 'UC2_NOSCAN', stdout=std_out)
                        std_out = False
                        write_impact_file(non_impacted_key, non_impacted_hex[non_impacted_key], zeroimpact,
                                          ulf, headerinfoimpact, ismic=is_mic, whitelist_labels=whitelist_labels)
                    ulf.msg('ALL', 'OK')
                else:
                    std_out = True
                    for non_impacted_key in non_impacted_hex:
                        ulf.msg(non_impacted_key, 'UC2_SCAN', stdout=std_out)
                        std_out = False

        # AIR6KOR - list of invalid calls that are assumed to be corrected in OSP
        osp_correction_lst = set()
        if input_lst is None:
            # i file scanner (use case scenario 1)
            # get output filepaths for i file scanner
            scan_ulf = check_filepath_arg(output_ulf, 'srvchecker_scan.ulf', output_path,
                                          create_file=True, ulf_=ulf, ulf_key=None)
            ulf.create('SCAN', scan_ulf, TOOLNAME, VERSION)

            if is_unc_path:
                ulf.msg(None, 'UC1_UNCPATH_WARN')
                f = FetchUNC(root, destpath=options.temp_folder, exclude_paths=['_log'],
                             include_files_in_path=['_gen,filelist_gen_*.txt', 'mak,*.xml', ],
                             include_filematch=['*.c', '*.mwa', 'build_cmds.log', '*.db3', '*.ini', '*.h', '*.d',
                                                '*.mic', '*.lst', 'swbuild_config.xml', '*.mak', 'dgs_ipofunctions_sstreduction_inca_fix.osp'],
                             ulf=ulf, ulf_key=None, nc=options.no_counter, debug=0)
                f.get_filelist()
                f.copy_tree()
                # reload project from the local copied path
                root, prjt, tmp_is_unc_path = get_root_path(options.temp_folder,ulf,output_path)  # TODO - Check if get_root_path is required again
                if root is None:
                    ulf.msg('ALL', 'UC1_UNCPATH_FAIL')

            scan_lst = check_filepath_arg(output_lst, 'srvchecker_scan.lst', output_path,
                                          create_file=True, ulf_=ulf, ulf_key='SCAN')

            if is_unc_path:
                ulf.msg('SCAN', 'UC1_UNCPATH_WARN', stdout=False)

            build_system = prjt.get_pverbuildnature()
            if build_system is not None:
                build_system = build_system.upper()

            # AIR6KOR: Support for MDGB use case
            # From possibly_affected_items.lst populate "affected_items.lst"
            mdgb_usecase = False
            affected_list_path = None
            affected_list = "."
            if options.affected_list:
                if build_system == "LWS_MDGB":
                    mdgb_usecase = True
                    affected_ulf = check_filepath_arg(output_affected_ulf, 'affected_items.ulf',
                                                      output_path, create_file=True, ulf_=ulf, ulf_key=None)
                    ulf.create('AFFECTED', affected_ulf, TOOLNAME, VERSION)

                    from configs import from_conf_file
                    prefix = ''
                    if sys.executable.endswith("srvchecker.exe"):
                        prefix = os.path.dirname(sys.executable)

                    srv_list_path = os.path.join(prefix, "config/srv_ipo.lst")
                    srv_list_path1 = os.path.join(prefix, r"D:/srvchecker_new/src/config/serviceCheckLibraryList.lst")
                    if os.path.exists(srv_list_path):
                        use_config = from_conf_file(srv_list_path)
                        ulf.msg('AFFECTED', 'UC3_SRVIPOLIST_OK', ft=prefix + "/config")
                    elif os.path.exists(srv_list_path1):
                        use_config = from_conf_file(srv_list_path1)
                        ulf.msg('AFFECTED', 'UC3_SRVIPOLIST_OK', ft=prefix + "/config")
                    else:
                        ulf.msg('AFFECTED', 'UC3_NOSRVIPOLIST', ft=prefix + "/config")

                    affected_list = os.path.join(root, options.affected_list)
                    affected_list_path = check_filepath_arg(affected_list, None, output_path, create_file=False)
                    if affected_list_path is None:
                        ulf.msg('AFFECTED', 'UC3_NOPOSSIBILYAFFECTEDLIST', ft=options.affected_list)
                else:
                    ulf.msg('SCAN', 'UC3_AFFECTEDLIST_DGSB')
                    ulf.msg('AFFECTED', 'UC3_AFFECTEDLIST_DGSB')

            srvListFound=serviceLibraryList()
            if srvListFound:
                ulf.msg(None, 'UC3_SRVIPOLIST_OK', ft="config")
            else:
                ulf.msg(None, 'UC3_NOSRVIPOLIST', ft="config")
				
            # create regex list
            search_list, dep_search_list, search_return, add_flags, description, ulf_label_found_desc, \
                ulf_label_found_reduced_desc, case_sense, clean_content, wiki = \
                create_regex_list(configs=use_config, build_env=build_system, search_replace=search_replace)

            maps_curves_search_lst=listOfCurvesAndMaps(prjt,ulf)
            sc = SrvChecker(root=root, add_flags=add_flags, outputpath=output_path, prj=prjt,
                            no_clean=not clean_content, src_file_list=input_src_files,
                            compilerpath=options.compiler, excludepaths=options.exclude, search_list=search_list,
                            dep_search_list=dep_search_list, search_return=search_return, search_cs=case_sense,
                            cpu=int(options.cpu), log_search_file=options.log, no_write=not options.ifiles, ulf=ulf,
                            ulf_key='SCAN', nc=options.no_counter, debug=0, debug_log=options.debug, maps_curves_search_lst=maps_curves_search_lst)
            label_list = sc.get_search_results()
            xl_writer.set_sourcefile_num(sc.get_sourcefile_num())

            # AIR6KOR: MDGB usecase
            if mdgb_usecase:
                from ice_usecase import parse_affected_list, print_impacted_file
                start_time = time()

                xl_writer.add_worksheet('affected_items')

                affected_lst = parse_affected_list(affected_list_path, ulf, affected_list, ulf_key='AFFECTED')
                # Invalid calls list along with maps or curve values
                srv_searchlst = sc.get_srv_search_list()
                affected_items = print_impacted_file(affected_lst, srv_searchlst, ulf=ulf,
                                                     ulf_key='AFFECTED', search_results=label_list,
                                                     ulf_label_found_desc=ulf_label_found_desc,
                                                     wiki=wiki, xl_writer=xl_writer)
                aff_filename = "affected_items.lst"
                write_file(affected_items, path=output_path, filename=aff_filename, date_time_stamp=False)
                ulf.msg('AFFECTED', 'UC3_AFFECTEDITEMSCREATED', ft=output_path)
                ulf.msg('AFFECTED', 'UC3_AFFECTEDLISTTIME', ft=time() - start_time)

            labels_not_allowed_srv = set([])
            labels_not_allowed_unkown = set([])
            labels_not_allowed = set([])

            # mmi6kor 02112018
            osp_labels_not_allowed_srv = set([])
            osp_labels_not_allowed_un = set([])
            ulf.msg('SCAN', 'UC1_REGEX_INFO', ft=sc.get_search_string())
            scan_worksheet_name = 'srvchecker_scan'
            xl_writer.add_worksheet(scan_worksheet_name)
            all_disc=set([])
            desc=''
            for cpath, cfilename, srv_used_lst, posible_direct_usage_lst, line_number_start, line_number_end, ospstatus in label_list:
                if ulf_label_found_desc is not None:
                    if line_number_start is not None:
                        if line_number_end is None:
                            line_number = '%s..EOF' % line_number_start
                        else:
                            line_number = '%s..%s' % (line_number_start, line_number_end)
                    else:
                        line_number = 'unknown'
                    for each in [srv_used_lst,posible_direct_usage_lst]:
                        for each_l in each:
                            func = str(each_l[0])
                            label = str(each_l[1]).lstrip('_')
                            if func!='unknown':
                                desc = ulf_label_found_desc['DESC'].format(
                                        **{'PATH': cpath, 'FILE': cfilename, 'FUNC':func, 'LABEL':label, 'LINE': line_number,'WIKI': wiki})
                            else:
                                desc =f'Direct call done in {cpath} of source file {cfilename} at (line:{line_number}), to access {label} '
                            all_disc.add((desc,label,func,cpath,cfilename,line_number_start,ospstatus))

                for each_label in srv_used_lst:
                    if each_label[1].strip():
                        labels_not_allowed_srv.add(str(each_label[1]).lstrip('_'))
                        if ospstatus:
                            osp_labels_not_allowed_srv.add(str(each_label[1]).lstrip('_'))
                for each in  posible_direct_usage_lst:
                    if each[1].strip():
                        labels_not_allowed_unkown.add(str(each[1]).lstrip('_'))
                        if ospstatus:
                            osp_labels_not_allowed_un.add(str(each[1]).lstrip('_'))
            for desc,label,func,cpath,cfilename,line_number_start,ospstatus in all_disc:
                sn = ulf_label_found_desc['SHORTNAME']
                if ospstatus:
                    descr = desc + " (Assumed corrected maps and curves due to usage of " \
                                   "dgs_ipofunctions_sstreduction_inca_fix.osp in the PVER)"
                xl_writer.add_tablecontents(scan_worksheet_name, [sn, label, desc, wiki])
                ulf['SCAN'].add(1, sn, desc, os.path.join(cpath, cfilename),
                                col_number='0',
                                line_number=line_number_start,
                                wiki=wiki)

            if len(labels_not_allowed_srv):
                ulf.msg('SCAN', 'UC1_DIRECTCALL_WITH_SRV', ft=len(labels_not_allowed_srv))
            if len(labels_not_allowed_unkown):
                ulf.msg('SCAN', 'UC1_DIRECTCALL_WITH_UNKOWN', ft=len(labels_not_allowed_unkown))
            else:
                ulf.msg('SCAN', 'UC1_NODIRECTCALL')
            labels_not_allowed_scan_srv=''
            labels_not_allowed_scan_un=''
            # write scan list file
            scan_lst_path, scan_lst_fn = os.path.split(scan_lst)
            # osp and non-osp
            ospremoved_srv = labels_not_allowed_srv ^ osp_labels_not_allowed_srv
            ospremoved_un=labels_not_allowed_unkown ^ osp_labels_not_allowed_un
            if len(osp_labels_not_allowed_srv) > 0 or len(osp_labels_not_allowed_un) > 0:
                labels_not_allowed_scan ='<--Labels accessed with the srv function-->'+\
                                            '\n'.join(sorted(list(ospremoved_srv))) +\
                                         '<--Labels found with unknown function--> \n'+\
                                           '\n'.join(sorted(list(ospremoved_un)))+\
                                          '''\n<!-- Assumed corrected maps and curves due to usage of 
                                          dgs_ipofunctions_sstreduction_inca_fix.osp in the PVER -->\n\n''' + \
                                         '<--Labels accessed with the srv function-->' + \
                                         '\n'.join(sorted(list(osp_labels_not_allowed_srv)))+ \
                                         '<--Labels found with unknown function--> \n' + \
                                         '\n'.join(sorted(list(osp_labels_not_allowed_un)))

                # Passing this argument to Impact (as scan.lst wont be read during PVER, A2L, HEX options)
                osp_correction_lst = list(osp_labels_not_allowed_srv.add(osp_labels_not_allowed_un))
            else:
                labels_not_allowed_scan_srv = '\n'.join(sorted(list(labels_not_allowed_srv)))
                labels_not_allowed_scan_un = '\n'.join(sorted(list(labels_not_allowed_unkown)))
            srv_msg=''
            if len(labels_not_allowed_scan_srv)>0:
                srv_msg ='\n<--- Labels Found which are accesed by srv functions --->\n'
            # unknown_msg = '\n<--- Affected Labels Found With unknown functions --->\n'
            write_file(headerinfoimpact + alm_msg + '\n'+labels_not_allowed_scan_un+'\n'+srv_msg +labels_not_allowed_scan_srv, path=scan_lst_path,
                       filename=scan_lst_fn, date_time_stamp=False)
            ulf.msg('SCAN', 'WRITEFILE', ft=(scan_lst_fn, scan_lst_path))
        else:
            if options.affected_list:
                ulf.msg('SCAN', 'UC3_AFFECTEDLIST_NOPVER')
                ulf.msg('AFFECTED', 'UC3_AFFECTEDLIST_NOPVER')
            # read input.lst
            with open(input_lst, 'r') as Fl:
                tmp = Fl.read()
            labels_not_allowed = set()
            b_osp_correction_scope = False
            for x in tmp.splitlines():
                x = x.strip()
                if len(x):
                    if x.find("inca_fix.osp") > 0:
                        b_osp_correction_scope = True
                        continue
                    elif x.startswith("<!--"):
                        continue
                    labels_not_allowed.add(x)
                    if b_osp_correction_scope:
                        osp_correction_lst.add(x)

            # Any additional parameter in gcc_tools resolve macros function, needs to be added accordingly here
            label_list = [(None, None, None, x, None, None, None) for x in sorted(list(labels_not_allowed))]
            # create regex list
            ulf_label_found_reduced_desc = get_default_config('ULF_LABEL_FOUND_REDUCED_DESC', configs=use_config)
            wiki = get_default_config('WIKI', configs=use_config)
            print_val = True
            for impact_ulf_key in impact_multiple_hex:  # TODO
                if re.search(r'^(<!|\s*$)', tmp) is None and re.search(r'[^\w_\r\n]', tmp) is not None:
                    # unwanted characters found in input list file; warning output
                    ulf.msg(impact_ulf_key, 'UC2_INPUTLSTW', ft=input_lst, print_val=print_val)
                else:
                    ulf.msg(impact_ulf_key, 'UC2_INPUTLST', ft=input_lst, print_val=print_val)
                print_val = False

        if len(options.a2l) and len(options.hex):

            for non_impacted_key in non_impacted_hex:
                write_impact_file(non_impacted_key, non_impacted_hex[non_impacted_key], zeroimpact,
                                  ulf, headerinfoimpact, ismic=is_mic, impacted=False,
                                  whitelist_labels=whitelist_labels)

            for impact_ulf_key in impact_multiple_hex:
                # get impacted labels
                labels_impact = labels_not_allowed & impact_multiple_hex[impact_ulf_key]['labels']
                # write impact list file if a2l and hex are passed
                impact_lst_args = impact_multiple_hex[impact_ulf_key]['list_path']
                IMPACT_ULF_KEY = impact_ulf_key  # ULF key 'IMPACT' for single/multiple hex files
                impact_hexfile_name = IMPACT_ULF_KEY[6:]  # Get filename by removing 'IMPACT' from key.
                impact_worksheet_name = 'impact_'+str(impact_worksheet_num)
                xl_writer.add_worksheet(impact_worksheet_name, hexname=impact_hexfile_name+'.hex')
                impact_worksheet_num += 1

                if labels_impact:

                    # AIR6KOR: OSP correction list is sent along with impacted list
                    impact_lst = write_impact_file(IMPACT_ULF_KEY, impact_lst_args, labels_impact, ulf,
                                                   headerinfoimpact, ismic=is_mic,
                                                   osp_correction_list=osp_correction_lst, impacted=True,
                                                   whitelist_labels=whitelist_labels)

                    # project affected
                    if ulf_label_found_reduced_desc is not None:
                        for cpath, cfilename, result_re, label, line_number_start, line_number_end, ospstatus in label_list:
                            if not ospstatus:
                                if label not in labels_impact:
                                    continue
                                if line_number_start is not None:
                                    if line_number_end is None:
                                        line_number = '%s..EOF' % line_number_start
                                    else:
                                        line_number = '%s..%s' % (line_number_start, line_number_end)
                                else:
                                    line_number = 'unknown'
                                descr = ulf_label_found_reduced_desc['DESC'].format(
                                    **{'PATH': cpath, 'FILE': cfilename, 'FUNC': result_re, 'LABEL': label,
                                       'LINE': line_number, 'WIKI': wiki})
                                sn = ulf_label_found_reduced_desc['SHORTNAME']
                                if cpath is None:
                                    impact_path = a2l_filepath
                                else:
                                    impact_path = os.path.join(cpath, cfilename)

                                # line_number_end to be not considered
                                xl_writer.add_tablecontents(impact_worksheet_name, [sn, label, descr, wiki])
                                ulf[IMPACT_ULF_KEY].add(1, sn, descr, impact_path, col_number='0',
                                                        line_number=line_number_start, wiki=wiki)

                # If All conditions are blank write not affected. If labels_not_allowed too.
                else:
                    impact_lst = write_impact_file(IMPACT_ULF_KEY, impact_lst_args, zeroimpact,
                                                   ulf, headerinfoimpact, ismic=is_mic, impacted=False,
                                                   whitelist_labels=whitelist_labels)

        if is_mic:
            ulf.msg('ALL', 'ALM_WARNING')

    except KeyboardInterrupt as e:
        # USER INTERRUPT
        ulf.msg('ALL', 'USERBREAK')
    except Exception as e:
        # TOOL ERROR
        dbg_error = dbgh.get_exception(traceback, sys, e)
        ulf.msg('ALL', 'TOOLERROR', ulfmsg=dbg_error)

    ulf.msg('ALL', 'OK')
