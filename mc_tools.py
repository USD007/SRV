#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from future import standard_library
from builtins import str
from builtins import range
from builtins import object
from dbg_handler import DbgHandler
standard_library.install_aliases()

OPT_CTEMP = 0
OPT_MC_TOOL = 255

OPT_TEXT_DICT = {
    OPT_CTEMP: 'ctemp',
    OPT_MC_TOOL: 'intern',
}


def InitWorker():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def ParseFiles(sourceroot, filelist, filelist_dict, options, stop, debug_queue,maps_curves_search_lst=None, idx=0, debug=0, profile=False,
               profile_step='', profile_path='.'):
    pr = {}
    if profile:
        import cProfile
        for opt_id in OPT_TEXT_DICT:
            pr[opt_id] = None
        pr[OPT_MC_TOOL] = cProfile.Profile()
        pr[OPT_MC_TOOL].enable()
    
    def activate_profile(opt_id):
        if profile:
            if pr[opt_id] is None:
                pr[opt_id] = cProfile.Profile()
            pr[OPT_MC_TOOL].disable()
            pr[opt_id].enable()
        
    def deactivate_profile(opt_id):
        if profile:
            if pr[opt_id] is not None:
                pr[opt_id].disable()
                pr[OPT_MC_TOOL].enable()
                
    filename = ''

    def send_status(dbg_inst, count):
        if debug_queue is None:
            dbg_inst.send(None, {'SUBTASK_COUNT': count})

    import traceback
    import sys
    import os
    os.path.sep = '/'

    import time
    time_last = [time.time()]

    def add_time():
        tmp = time_last[0]
        time_last[0] = time.time()
        return time_last[0] - tmp

    # init results container
    results = {}
    for opt in options[0]:
        results[opt] = {}

    # create debug instance dictionary with main debug instance
    dbg = {}
    opt_now = OPT_MC_TOOL
    dbg[opt_now] = DbgHandler('MC PARSER %s' % str(idx), debug, debug_queue_sender=debug_queue)

    try:
        output_path = None
        opt_re_search = None
        ospsrvlist = []
        # init workers
        if OPT_CTEMP in options[0]:
            opt_now = OPT_CTEMP
            dbg[opt_now] = DbgHandler('C_PARSER_%s' % str(idx), debug, debug_queue_sender=debug_queue)

            gcc_path, gcc_exec, gcc_env, include_paths, std_flags, my_flags, my_opt = options[0][OPT_CTEMP]
            # mmi6kor : OSP 
            ospsrvlist = options[1]

            output = False

            if 'output' in my_opt:
                if my_opt['output'] is None:
                    output = True
                else:
                    output_path = my_opt['output'][0]
                    output_ext = my_opt['output'][1]
                    output = True

            opt_re_search_ret = None
            if 're_search' in my_opt:
                opt_re_search = my_opt['re_search']
                if 're_search_ret' in my_opt:
                    opt_re_search_ret = my_opt['re_search_ret']

        # start working
        opt_now = OPT_MC_TOOL
        filename_count = 0
        while True:
            opt_now = OPT_MC_TOOL
            if len(filelist) > 0:
                try:
                    filesize, filename = filelist.pop()
                except:
                    continue
            else:
                break
            try:
                if (OPT_CTEMP in options[0]) and (filelist_dict[filename][0] == OPT_CTEMP):
                    # COMPILER
                    opt_now = OPT_CTEMP
                    path = filelist_dict[filename][1]
                    gcc_path_file, gcc_exec_file = gcc_path, gcc_exec
                    use_compiler_flags, use_include_paths = std_flags, include_paths
                    if len(filelist_dict[filename]) > 3:
                        options_file = filelist_dict[filename][3]
                        if 'include_only' in options_file:
                            include_only = options_file['include_only']
                        else:
                            include_only = []
                        if 'remove_line_descriptor' in options_file:
                            remove_line_descriptor = options_file['remove_line_descriptor']
                        else:
                            remove_line_descriptor = False
                        if 'gcc' in options_file:
                            gcc_path_file, gcc_exec_file = options_file['gcc']
                        if 'own_compiler_args' in options_file:
                            use_compiler_flags = options_file['own_compiler_args']
                        if 'own_include_paths' in options_file:
                            use_include_paths = options_file['own_include_paths']

                    from gcc_tools import resolve_macros
                    raw_data, raw_data_cleaned, command_used, search_result, err, ifile_time, clean_time = \
                        resolve_macros(path, filename, gcc_path_file, gcc_exec_file, gcc_env, use_include_paths,
                                       use_compiler_flags, my_flags, ospsrvlist, cwd=sourceroot,
                                       include_only=include_only, remove_line_descriptor=remove_line_descriptor,
                                       re_search=opt_re_search, re_search_ret=opt_re_search_ret, dbg=dbg[opt_now], maps_curves_search_lst=maps_curves_search_lst)
                    data = None

                    if output:
                        if output_path is None:
                            data = raw_data
                        else:
                            base = os.path.splitext(filename)[0]
                            from windows_tools import write_file
                            if raw_data_cleaned is not None:
                                write_file(raw_data_cleaned, path=os.path.join(sourceroot, output_path + "/debug_results/", 'cleaned_ifile'),
                                           filename='.'.join((base, output_ext)), date_time_stamp=False,
                                           access_binary=True, dbg=dbg[opt_now])
                            # 26112018 Supress the Uncleaned Folder
                            # if raw_data is not None:
                            #     write_file(raw_data, root=sourceroot, path=os.path.join(output_path, 'not_cleaned'),
                            #                filename='.'.join((base, output_ext)), date_time_stamp=False,
                            #                access_binary=True, dbg=dbg[opt_now])
                    results[OPT_CTEMP][filename] = [len(raw_data), data, command_used, search_result, err,
                                                    add_time(), ifile_time, clean_time]

            except KeyboardInterrupt as e:
                raise e
            except MemoryError as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, '\n', traceback.print_tb(exc_traceback))  # CHK_IGNORE
                dbg[opt_now].send_exception(traceback, sys, e, filename=filename, no_break=True)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, '\n', traceback.print_tb(exc_traceback))  # CHK_IGNORE
                dbg[opt_now].send_exception(traceback, sys, e, filename=filename, no_break=True)
                break

            filename_count += 1
            send_status(dbg[opt_now], filename_count)

            if stop.is_set():
                break

    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        dbg[opt_now].send_exception(traceback, sys, e, filename=filename, no_break=True)
        
    if stop.is_set():
        results = None

    if profile:
        from windows_tools import write_file
        sortby = 'cumulative'
        try:
            import pstats
            import io
            for opt_id in pr:
                if pr[opt_id] is None:
                    continue
                s = io.StringIO()
                filename = '%s_%s_proc_%d.log' % (OPT_TEXT_DICT[opt_id], profile_step, idx)
                ps = pstats.Stats(pr[opt_id], stream=s).sort_stats(sortby)
                ps.print_stats()
                write_file(s.getvalue(), path=os.path.join(sourceroot, profile_path), filename=filename, date_time_stamp=False)
                s.close()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(e, '\n', traceback.print_tb(exc_traceback))  # CHK_IGNORE

    return results


class MCParser(object):

    def __init__(self, nc=False, debug=0, profile=False, profile_path='.',
                 profile_step=''):
        self.debug = debug
        self.dbg = DbgHandler(self.__class__.__name__, debug)
        self.results = {}
        self.results_time = {}
        self.profile = profile
        self.profile_path = profile_path
        self.profile_step = profile_step
        self.nc = nc
        self.options = {}
        self.bytecnt = 0
        self.ifile_time = []
        self.clean_ifile_time = []

    def FetchResults(self, results):
        if results is not None:
            for opt in results:
                if opt == OPT_CTEMP:

                    if self.results[opt] is None:
                        self.results[opt] = {}
                        # self.results_time[opt] = {}

                    for filename in results[opt]:
                        self.bytecnt += results[opt][filename][0]
                        self.results_time[opt][filename] = results[opt][filename][5]
                        self.ifile_time.append(results[opt][filename][6])
                        self.clean_ifile_time.append(results[opt][filename][7])
                        self.results[OPT_CTEMP][filename] = (results[opt][filename][1], results[opt][filename][2],
                                                             results[opt][filename][3], results[opt][filename][4])
    # function not called from anywhere
    def get_time_results(self):
        """
        returns csv string
        """
        result = [';'.join(['filename', 'time_used [ms]', 'opt'])]
        filename_dict = {}
        for opt in self.results_time:
            for filename in self.results_time[opt]:
                filename_dict[filename] = (OPT_TEXT_DICT[opt], self.results_time[opt][filename])
        for filename in sorted(filename_dict.keys()):
            opt, time_used = filename_dict[filename]
            result.append(';'.join([filename, '%d' % int(time_used * 1000), opt]))
        return '\n'.join(result)

    # function not called from anywhere
    def get_ifile_creation_time(self):
        """
        Returns the total time taken for i file generation.
        """
        return sum(self.ifile_time)

    # function not called from anywhere
    def get_cleaning_ifile_time(self):
        """
        Returns the total time taken for cleaning i files.
        """
        return sum(self.clean_ifile_time)

    def parse(self, root, filelist_dict, options, prc=0, clip_filesize=None,maps_curves_search_lst=None):

        from multiprocessing import cpu_count, Pool, Manager

        import time

        for opt in options[0]:
            self.results[opt] = None
            self.results_time[opt] = {}

        filenamecnt = len(filelist_dict)

        if filenamecnt == 0:
            self.dbg.out(1, 'no files passed.')
            return True

        self.dbg.out(4, 'start parsing %d files.' % filenamecnt)

        if prc > 0:
            max_prc = prc
            if max_prc > 12:
                max_prc = 12
        else:
            max_prc = cpu_count()
            if max_prc > 12:
                max_prc = 12
            if prc < 0:
                max_prc += prc
        if max_prc < 1:
            max_prc = 1

        self.options = options

        filelist = []
        for filename in filelist_dict:
            # opt = filelist_dict[filename][0]
            # path = filelist_dict[filename][1]
            size = filelist_dict[filename][2]
            if size == 0:
                self.dbg.out(1, 'zero filesize for %s' % filename)
            if clip_filesize is not None:
                if size > clip_filesize:
                    size = clip_filesize
            filelist.append([size, filename])

        filelist.sort(key=lambda x: x[0], reverse=False)

        self.bytecnt = 0
        manager = Manager()
        if max_prc > 1:
            pool = Pool(processes=max_prc, initializer=InitWorker)
            filelist = manager.list(filelist)

        debug_queue = manager.Queue()
        stop = manager.Event()
        self.dbg.send(None, {'SUBTASK_COUNT_MAX': len(filelist)})

        self.dbg.queue_set_receiver(debug_queue)
        try:
            for idx in range(max_prc):
                if max_prc > 1:
                    pool.apply_async(
                        ParseFiles, (root, filelist, filelist_dict, options, stop, debug_queue, maps_curves_search_lst),
                        {
                         'debug': self.debug,
                         'idx': idx,
                         'profile': self.profile,
                         'profile_path': self.profile_path,
                         'profile_step': self.profile_step,
                         },
                        callback=self.FetchResults)
                else:
                    idx = 0
                    self.FetchResults(
                        ParseFiles(root, filelist, filelist_dict, options, stop, None,maps_curves_search_lst=maps_curves_search_lst **{
                            'debug': self.debug,
                            'idx': idx,
                            'profile': self.profile,
                            'profile_path': self.profile_path,
                            'profile_step': self.profile_step,
                        }))
            if max_prc > 1:
                pool.close()

                time_used = 0.0
                while True:
                    filecount = filenamecnt - len(filelist)
                    # forward dbg status/messages
                    self.dbg.queue_get_receiver()
                    if not self.nc:
                        self.dbg.send('\r%d files left     ' % (len(filelist)), {'SUBTASK_COUNT': filecount}, end='')
                    if self.dbg.break_tasks():
                        # if break is requested terminate processes
                        stop.set()
                        break
                    if not sum([x.is_alive() for x in pool._pool]):
                        break
                    time.sleep(0.2)
                    time_used += 0.2

                if not self.nc:
                    self.dbg.send('\r                     \r', None, end='')
                if stop.is_set():
                    pool.join()
                    self.dbg.queue_get_receiver()
                    self.dbg.queue_close_receiver()
                else:
                    pool.join()

        except KeyboardInterrupt as e:
            self.dbg.queue_get_receiver()
            self.dbg.queue_close_receiver()
            if max_prc > 1:
                try:
                    pool.terminate()
                except:
                    pass
            if not self.nc:
                self.dbg.send('', None)
            self.dbg.send(None, {'SUBTASK_BREAK': None})
            raise e
        except Exception as e:
            self.dbg.queue_get_receiver()
            self.dbg.queue_close_receiver()
            if max_prc > 1:
                try:
                    pool.terminate()
                except:
                    pass
            if not self.nc:
                self.dbg.send('', None)
            self.dbg.send(None, {'SUBTASK_BREAK': None})
            raise e
        else:
            if self.dbg.break_tasks():
                self.dbg.send(None, {'SUBTASK_BREAK': None})
                return False
            else:
                self.dbg.send(None, {'SUBTASK_COUNT_END': None})
                self.dbg.queue_get_receiver()
                self.dbg.queue_close_receiver()

        return True
