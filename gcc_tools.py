# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re

nestor_inc_path = ['ASW/_include', 'CDRV/_include', 'CORE/_include', 'PROJECT/_include', 'makeout/core/gen_files',
                   'makeout/mcop', 'makeout/damos/gen_files', ]
clearcase_inc_path = ['tmp/include', ]
swb_inc_path = ['_gen/swb/core/headers', '_gen/swb/headers', '_gen/swb/core/gen_files', '_gen/swb/damos/gen_files',
                '_gen/swb/include/src', '_gen/swb/include/corecfg', '_gen/swb/include/data', '_gen/swb/include/mcop', ]
lws_mic_pmb_inc_path = ['_gen/swb/filegroup/includes', '_gen/swb/filegroup/src_files']

include_path = set(nestor_inc_path + clearcase_inc_path + swb_inc_path + lws_mic_pmb_inc_path)


def get_gcc_configs(gcc_path=None):
    import os
    os.path.sep = '/'

    def get_gcc_path(toolbase_path='c:/toolbase'):

        import re

        if os.path.exists('/'.join((toolbase_path, 'hightec'))):
            cd_paths = []
            for cd_path in os.listdir('/'.join((toolbase_path, 'hightec'))):
                if re.search(r'^cd_v(\d+)\.(\d+)\.(\d+)\.(\d+)(?:\Z|_(\d+)\Z)', cd_path):
                    cd_paths.append(cd_path)
            cd_paths.sort()
            return os.path.join(os.path.join(toolbase_path, 'hightec'), cd_paths[-1])
        else:
            return '.'

    def get_gcc_exec(gcc_path_, version_batch_file='version.bat', gcc_exec_std='bin/tricore-gcc.exe'):
        if os.path.exists(gcc_path_):
            import re
            try:
                with open(os.path.join(gcc_path_, version_batch_file), "r") as F:
                    version_batch = F.read()
                gcc_exec = re.search(r'echo\s+###GCC###\s*>>\s*versions\.txt\s*([\\\w\-\+_]+)', version_batch)
                if gcc_exec is not None:
                    return '.'.join((gcc_exec.group(1), 'exe'))
            except:
                if os.path.exists(os.path.join(gcc_path_, gcc_exec_std)):
                    return gcc_exec_std
                return None

        else:
            return None

    if gcc_path is None:
        gcc_path = get_gcc_path()

    return gcc_path, get_gcc_exec(gcc_path)


def get_include_paths(prj_root):
    import os.path
    gen_inc_path = include_path

    def get_new_path(new_path):
        if new_path.startswith('/'):
            return '.' + new_path
        elif new_path.startswith('.'):
            return new_path
        else:
            return './' + new_path

    if os.path.exists(prj_root):
        result = []
        prj_root_l = prj_root.lower().replace('\\', '/')
        for inc_path in gen_inc_path:
            gen_inc_path_abs = os.path.join(prj_root_l, inc_path)
            if os.path.exists(gen_inc_path_abs):
                folder_lists = [subfolder_name for subfolder_name in os.listdir(gen_inc_path_abs)
                                if os.path.isdir(os.path.join(gen_inc_path_abs, subfolder_name))]
                for sub_name in folder_lists:
                    result.append(get_new_path(os.path.join(inc_path, sub_name).replace('\\', '/').strip()))
                else:
                    if not folder_lists:
                        result.append(get_new_path(os.path.join(inc_path).replace('\\', '/').strip()))
        return result
    else:
        return ['.']


class ReGcc:
    import re
    emptylines = re.compile(rb"$\s*^", flags=re.MULTILINE)
    line_descr = re.compile(rb'^#\s(\d+)\s\"(.*?)\"\s?(\d+)?')
    line_descriptor = re.compile(rb"(^|[\r\n])#\s+(\d+).*?(?=[\r\n])")

from configs import func_matcher
def resolve_macros(c_path, c_filename, gcc_path, gcc_exec, gcc_env, include_paths, std_flags, my_flags,
                   ospsrvlist, cwd='.', include_only=None, remove_line_descriptor=False, re_search=None,
                   re_search_ret=None, re_serach_ret_max_chars=1000, get_line_number=True, dbg=None, maps_curves_search_lst=None):
    from time import time
    if include_only is None:
        include_only = []

    ifile_starttime = time()
    if gcc_path is None:
        import os.path
        os.path.sep = '/'
        gcc_path, gcc_exec = get_gcc_configs(os.path.realpath(os.path.curdir()))
    from subprocess import Popen, PIPE
    import os
    os.path.sep = '/'
    command = r'%s -x c -E %s %s -I- %s %s/%s' % (os.path.join(gcc_path, gcc_exec), ' '.join(std_flags), my_flags,
                                                  ' '.join(['-I%s' % x for x in include_paths]), c_path, c_filename)

    p = Popen(command, stdout=PIPE, stderr=PIPE, env=gcc_env, cwd=cwd)
    # mmi6kor 25102018
    stdout, stderr = p.communicate()
    ifile_totaltime = time() - ifile_starttime

    clean_starttime = time()
    # remove empty lines
    stdout = ReGcc.emptylines.sub(b'', stdout)
    excludepattern = re.compile('^srv\w+')
    stdout_new = []
    add_lines = False
    for line_str in stdout.splitlines():
        match = ReGcc.line_descr.search(line_str)
        if match is not None:
            # line descriptor found
            filename = os.path.basename(match.group(2)).lower().strip().decode()
            add_lines = False if excludepattern.search(filename) else True
        # add include instead if marked as first time if in c file
        else:
            if add_lines:
                stdout_new.append(line_str)
    stdout_cleaned = b'\n'.join(stdout_new)
    if remove_line_descriptor:
        stdout = ReGcc.line_descriptor.sub(b'', stdout)
    clean_totaltime = time() - clean_starttime

    if re_search is not None:
        search_result=[]
        endpf = 0
        startpf=0
        ospfound = False
        result_found=[]
        mc_srv_found=[]
        posible_directaccess=[]
        # searching for maps and curves
        ret_val, line_number_start, line_number_end = [], None, None
        for tmp in maps_curves_search_lst.finditer(stdout_cleaned):
            m_or_c_result = tmp.group(0).decode()
            if result_found in ospsrvlist:
                ospfound = True
            mc_start = tmp.start()
            mc_end = tmp.end()
            point = [0 if mc_start <= re_serach_ret_max_chars else mc_start - re_serach_ret_max_chars]
            text_for_search=stdout_cleaned[point[0]:mc_end+1]
            text_for_search=b' '.join((text_for_search.split(b' '))[-1::-1])
            func=func_matcher(text_for_search)
            if func!=None:
                mc_srv_found.append((func[0][0].decode(),m_or_c_result))
            elif func is None:
                acces = str((stdout_cleaned[mc_start - 2:mc_end]).decode()).strip()
                acces1=str((stdout_cleaned[mc_start - 1:mc_end]).decode()).strip()
                if acces.startswith('->') or acces1.startswith('.'):
                    posible_directaccess.append(('unknown',m_or_c_result))


            if get_line_number:
                for tmpline in reversed(stdout_cleaned[:endpf].splitlines()):
                    match_line = ReGcc.line_descr.search(tmpline)
                    if match_line is not None:
                        line_number_start = match_line.group(1).decode()
                        break
                for tmpline in stdout_cleaned[endpf:].splitlines():
                    match_line = ReGcc.line_descr.search(tmpline)
                    if match_line is not None:
                        line_number_end = match_line.group(1).decode()
                        break
        result_found.extend(mc_srv_found)                       #map_curve with srv
        ret_val.extend(posible_directaccess)                    #map_curve without srv-possible direct use

        search_result.append((c_path, c_filename, result_found, ret_val,
                          line_number_start, line_number_end, ospfound))
    else:
        search_result = None
    if stderr and (stderr.find(b'error:') >= 0):
        # mmi6kor 25102018
        stderr = stderr.decode(encoding="utf-8", errors="ignore")
        if dbg is not None:
            dbg.out(1, '\n' + gcc_exec + ' > ' + c_filename + ': \n' + stderr)
    else:
        stderr = None
    return stdout, stdout_cleaned, command, search_result, stderr, ifile_totaltime, clean_totaltime



