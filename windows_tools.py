#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

def sleep():
    import time
    time.sleep(0.3)


def prepare_file(path, filename, content, date_time_stamp=True, check_access=True, dbg=None, retry=False):


    if (path is None) or (filename is None):
        return False, None

    logpath = path
    logfilepath = os.path.join(logpath, filename)

    if not os.path.exists(logpath):
        try:
            os.makedirs(logpath)
        except:
            sleep()
            if not os.path.exists(logpath):
                try:
                    os.makedirs(logpath)
                except:
                    pass
        if content is None:
            return True, None

    elif os.path.exists(logfilepath):
        if date_time_stamp:
            # rename old file
            td = time.localtime(os.path.getmtime(logfilepath))
            time_stamp = '%d%02d%02d_%02d%02d%02d' % (td.tm_year, td.tm_mon, td.tm_mday,
                                                      td.tm_hour, td.tm_min, td.tm_sec)
            filename_base, filename_ext = os.path.splitext(filename)
            filename_old = '%s_%s%s' % (filename_base, time_stamp, filename_ext)
            try:
                os.rename(logfilepath, os.path.join(logpath, filename_old))
            except:
                if retry:
                    dbg.out(2, 'File "%s" is locked.' % logfilepath)
                    return True, logfilepath
                else:
                    dbg.send('Cannot rename "%s"; file is locked by another process.' % logfilepath, {'FATAL': None})
                    return False, None

        if content is None:
            # delete file if content is None
            try:
                os.remove(logfilepath)
                return True, None
            except:
                return True, None
    elif content is None:
        # if file does not exists / content not given return
        return True, None

    return True, logfilepath

def write_file(content, path=None, filename=None, access_binary=False, header_line=None,
               date_time_stamp=True, check_access=True, correct_etree=False, dbg=None, retry=False, retry_max=3):

    err, logfilepath = prepare_file(path, filename, content, date_time_stamp=date_time_stamp,
                                    check_access=check_access, dbg=dbg, retry=retry)
    if not err:
        return False  # No file access or file cannot be renamed.
    if logfilepath is None:
        return True

    if correct_etree:
        import re
        content = re.sub(r'\n( *)<(.*?)/>', r'\n\1<\2>\n\1</\2>', content)

    if access_binary:
        acc = 'wb'
    else:
        acc = 'w'

    def write_now(log_file_path):
        try:
            with open(log_file_path, acc) as F:
                if header_line is not None:
                    F.write(header_line + '\n')
                F.write(content)
        except:
            sleep()
            try:
                with open(log_file_path, acc) as F:
                    if header_line is not None:
                        F.write(header_line + '\n')
                    F.write(content)
            except:
                return False
            return True
        return True

    retried, lfp_base, lfp_ext = 0, '', ''
    while not write_now(logfilepath):
        if retry and (retried < retry_max):
            import os.path
            if retried == 0:
                lfp_base, lfp_ext = os.path.splitext(log_file_path)
            log_file_path = lfp_base + '__retry_' + retried + lfp_ext
            retried += 1
        else:
            return False
    return True


# UNUSED
def get_kb_input():
    import msvcrt
    if msvcrt.kbhit():
        return msvcrt.getch()
    else:
        return None


# UNUSED
def flush_kb_input():
    import msvcrt
    while msvcrt.kbhit():
        msvcrt.getch()
    return


def multiprocess_workaround():
    """
    use this for pyinstaller
    """
    import sys
    import os
    # Module multiprocessing is organized differently in Python 3.4+
    try:
        # Python 3.4+
        if sys.platform.startswith('win'):
            import multiprocessing.popen_spawn_win32 as forking
        else:
            import multiprocessing.popen_fork as forking  # other OS, not supported
    except ImportError:
        import multiprocessing.forking as forking

    if sys.platform.startswith('win'):
        # First define a modified version of Popen.
        class _Popen(forking.Popen):

            def __init__(self, *args, **kw):
                if hasattr(sys, 'frozen'):
                    # We have to set original _MEIPASS2 value from sys._MEIPASS
                    # to get --onefile mode working.
                    os.putenv('_MEIPASS2', sys._MEIPASS)  # sys._MEIPASS is a temp folder for pyInstaller
                try:
                    super(_Popen, self).__init__(*args, **kw)
                finally:
                    if hasattr(sys, 'frozen'):
                        # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                        # available. In those cases we cannot delete the variable
                        # but only set it to the empty string. The bootloader
                        # can handle this case.
                        if hasattr(os, 'unsetenv'):
                            os.unsetenv('_MEIPASS2')
                        else:
                            os.putenv('_MEIPASS2', '')

        # Second override 'Popen' class with our modified version.
        forking.Popen = _Popen


# UNUSED
def prevent_sleep(bSet, keep_display_on=False):
    try:
        import ctypes
        setState = ctypes.windll.kernel32.SetThreadExecutionState

        ES_CONTINUOUS = 0x80000000
        ES_AWAYMODE_REQUIRED = 0x00000040
        ES_SYSTEM_REQUIRED = 0x00000001

        if bSet:

            if keep_display_on:
                ES_DISPLAY_REQUIRED = 0x00000002
            else:
                ES_DISPLAY_REQUIRED = 0

            if ((setState(
                    ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED | ES_DISPLAY_REQUIRED) != 0) or  # Win7/Vista
                    (setState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED) != 0)):  # WinXP
                return True
        else:
            if setState(ES_CONTINUOUS) != 0:
                return True
    except:
        pass

    return False


def is_unc_path(path):
    # check if path is a (mapped) network path
    import os.path
    import win32wnet
    try:
        if os.path.splitunc(path)[0] or win32wnet.WNetGetUniversalName(path, 1):
            return True
    except:
        pass
    return False


# UNUSED
class XmlReDefs(object):
    import re
    re_entity_and = re.compile(br'\&\&')
    re_entity = re.compile(r"Entity '(.*?)' not defined")
    re_entity_uml = re.compile(br'\&(.)uml;')
    re_tag_spaces = re.compile(br'<(/?)\s*([\w\-]+)\s*>')
    re_char_not_allowed = re.compile(r'Char (0x\w\w?) out of allowed range')


# UNUSED
def parse_xml(inp, filename, parser, dbg, remove_blank_text=True, remove_comments=True):
    from lxml import etree
    done = set([])

    # parse and correct errors if exception occurs
    while True:
        try:
            tree = etree.XML(inp, parser)
            break
        except etree.XMLSyntaxError as e:
            logstr = 'XMLSyntaxError @(%d, %d)' % e.position
            if e.msg is None:
                # OTHER ERROR
                dbg.send('%s: unknown error' % filename, {'FATAL': None, })

            elif e.msg.startswith('xmlParseEntityRef'):
                # TESTCASE NEEDED > ENTITY REF FAIL
                if 'xmlParseEntityRef' not in done:
                    dbg.out(1, '%s: %s - wrong usage of EntityRef' % (filename, logstr))
                    inp = XmlReDefs.re_entity_and.sub(b'&amp;&amp;', inp)
                    done.add('xmlParseEntityRef')
                    continue
                else:
                    dbg.send('%s: %s' % (filename, e.msg), {'FATAL': None, })
            elif e.msg.startswith("Entity '"):
                # TESTCASE NEEDED > ENTITY UNKNOWN
                # check for entity
                match = XmlReDefs.re_entity.search(e.msg)
                if match is not None:
                    # not defined
                    dbg.out(1, '%s: %s - undefined Entity - ' % (filename, logstr))
                    if ('xmlParseEntityuml' not in done) and (match.group(1).endswith('uml')):
                        # correct uml entity
                        inp = XmlReDefs.re_entity_uml.sub(br'\1e', inp)
                        done.add('xmlParseEntityuml')
                        continue
                dbg.send('%s: %s' % (filename, e.msg), {'FATAL': None, })
            elif e.msg.startswith('Opening and ending tag mismatch'):
                # TESTCASE NEEDED > OPEN END TAG MISMATCH
                # Open End Tag mismatch > no autocorrect
                dbg.send('%s: %s' % (filename, e.msg), {'FATAL': None, })
                return None

            elif e.msg.find('invalid element name') > 0:
                # check for spaces in tags
                if 'xmlInvalidElementName' not in done:
                    # TESTCASE NEEDED > INVALID ELEMENT

                    # try correcting elements with spaces
                    inp = XmlReDefs.re_tag_spaces.sub(br'<\1\2>', inp)
                    done.add('xmlInvalidElementName')
                    dbg.out(1, '%s: %s - invalid element name - ' % (filename, logstr))
                    dbg.send('%s: %s' % (filename, e.msg), {'FATAL': None, })
                    continue
                dbg.send('%s: %s' % (filename, e.msg), {'FATAL': None, })

            elif e.msg.find('Input is not proper') >= 0:
                # utf-8 encoding configured, but other encoding used in file
                if 'xmlInvalidEncoding' not in done:
                    parser = etree.XMLParser(
                        remove_blank_text=remove_blank_text,
                        remove_comments=remove_comments)
                    #    encoding='iso-8859-1')
                    done.add('xmlInvalidEncoding')
                    continue
                dbg.send('%s: %s' % (filename, e.msg), {'FATAL': None, })

            elif (e.msg.find('Char') == 0) and (e.msg.find('out of allowed range') > 0):
                # not allowed char found
                char_match = XmlReDefs.re_char_not_allowed.search(e.msg)
                if char_match is not None:
                    char_str = char_match.group(1)
                    if ('notAllowedChar%s' % char_str) not in done:
                        done.add('notAllowedChar%s' % char_str)
                        inp = inp.replace(chr(int(char_str, 16)).encode(), b'')
                        continue
                dbg.send('%s: %s' % (filename, e.msg), {'FATAL': None, })

            else:
                # UNKNOWN ERROR
                dbg.send('%s: %s' % (filename, e.msg), {'FATAL': None, })
            return None

    if tree.tag.startswith('{'):
        # remove Namespaces from tag
        for el in tree.iter():
            try:
                el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
            except:
                pass

    return tree


# UNUSED
def get_xml_content(path, filename, raw_input, correct_utf_8, parser, dbg):
    import sys
    from codecs import open as codecs_open

    if raw_input is None:
        with codecs_open(u'\\'.join((path, filename)), "r", sys.getfilesystemencoding(), errors="ignore") as F:
            inp = F.read()
            inp = inp[inp.find('<'):]
            if correct_utf_8:
                return parse_xml(inp.encode('utf-8', 'ignore').decode().encode(), filename, parser, dbg)
            else:
                return parse_xml(inp.encode(), filename, parser, dbg)
    else:
        if correct_utf_8:
            if type(raw_input) is str:
                return parse_xml(raw_input.encode('utf-8', 'ignore').decode().encode(), filename, parser, dbg)
            else:
                return parse_xml(raw_input.decode().encode(), filename, parser, dbg)
        else:
            if type(raw_input) is str:
                return parse_xml(raw_input.encode(), filename, parser, dbg)
            else:
                return parse_xml(raw_input, filename, parser, dbg)
