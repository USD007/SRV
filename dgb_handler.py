#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function
from future import standard_library
from builtins import str
from builtins import range
from builtins import object
import sys

standard_library.install_aliases()


class DbgHandler(object):

    # handling pipes
    dbg_main_pipe = {0: None}
    debug_queue_receiver = None
    debug_queue_sender = None
    dbg_break = [False]

    DBG_OUT = ['', 'ERROR', 'WARN', 'INFO', 'DEBUG']
    DBG_NO = 0
    DBG_ERROR = 1
    DBG_WARNING = 2
    DBG_INFO = 3
    DBG_MOREINFO = 4
    DBG_FILE = [sys.stdout, sys.stdout, sys.stdout, sys.stdout, sys.stdout]
    
    DBG_MAX_LEVEL = 4

    DBG_REC_CHAR = '-'

    DBG_FORMAT = '%s: %s'

    styles = ['straight', 'recursive']

    S_STRAIGHT = 0
    S_RECURSIVE = 1

    recursive_out_max_backwards = 30

    def __init__(self, name, debug_level, style='straight', debug_queue_sender=None, dbg_thread_out=None):

        if debug_queue_sender is not None:
            self.debug_queue_sender = debug_queue_sender
        else:
            self.debug_queue_sender = None
            if dbg_thread_out is not None:
                self.main_pipe_create(thread_function=dbg_thread_out)

        if style not in self.styles:
            return
        self.style = self.styles.index(style)
        self.dbg_container = []
        self.name = name
        self.debug_level = debug_level
        self.recording = False
        self.record_hide_output = False
        self.verbose = False
        self.ignore_now = None
        return

    def break_tasks(self):
        return self.dbg_break[0]

    def break_set_request(self):
        self.dbg_break[0] = True
        return

    def break_clear(self):
        self.dbg_break[0] = False

    def dbg_thread_out(self):
        import time
        while not self.main_pipe_closed():
            if self.main_pipe_closed():
                break
            for data, err_class in self.main_pipe_recv():
                if data is None:
                    break
                print(data)
            time.sleep(0.1)

    def main_pipe_create(self, thread_function=None):

        if self.main_pipe_closed():
            # from multiprocessing import Pipe
            from threading import Thread
            from collections import deque

            self.dbg_main_pipe[0] = deque()
            # signals closing Pipe on receiver side if True
            self.dbg_main_pipe[1] = False
            # start thread
            if thread_function is None:
                self.dbg_main_pipe[3] = self.dbg_thread_out
            else:
                self.dbg_main_pipe[3] = thread_function
            self.dbg_main_pipe[2] = Thread(target=self.dbg_main_pipe[3])
            self.dbg_main_pipe[2].start()

    def close(self, this_is_receiver=False, t_sleep=0.1, timeout=2.0):
        import time
        if this_is_receiver:
            if self.dbg_main_pipe[0] is not None:
                self.dbg_main_pipe[0].clear()
                self.dbg_main_pipe[0] = None
                self.dbg_main_pipe[1] = False
                self.dbg_main_pipe[3] = None
        else:
            self.dbg_main_pipe[1] = True
            while timeout > 0.0:
                if self.main_pipe_closed():
                    break
                time.sleep(t_sleep)
                timeout -= t_sleep
            self.dbg_main_pipe[2].join()

    def main_pipe_closed(self):
        if self.dbg_main_pipe[0] is None:
            return True
        return False

    def main_pipe_recv(self):
        if self.dbg_main_pipe[0] is not None:
            data = []
            while len(self.dbg_main_pipe[0]) > 0:
                data.append(self.dbg_main_pipe[0].popleft())
            if len(data) > 0:
                return data
            if self.dbg_main_pipe[1]:
                # close main pipe
                self.close(this_is_receiver=True)

        return [(None, None)]

    def queue_set_receiver(self, debug_queue):
        self.debug_queue_receiver = debug_queue

    def queue_close_receiver(self):
        self.debug_queue_receiver = None

    def queue_get_receiver(self):
        if self.debug_queue_receiver is not None:
            if not self.debug_queue_receiver.empty():
                while not self.debug_queue_receiver.empty():
                    self.send(*self.debug_queue_receiver.get())

    def send(self, data, err_class, end='\n', dbglvl=0):
        if self.debug_queue_sender is not None:
            self.debug_queue_sender.put((data, err_class))
        elif self.dbg_main_pipe[0] is not None:
            self.dbg_main_pipe[0].append((data, err_class))
        elif data is not None:
            print(data, end=end, file=self.DBG_FILE[dbglvl])

    @staticmethod
    def get_exception(traceback, sys, e):
        import io
        output = io.StringIO()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, file=output)
        return '\n'.join((str(e), output.getvalue()))
        
    def send_exception(self, traceback, sys, e, filename=None, no_break=False):
        import io
        output = io.StringIO()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, file=output)
        if no_break:
            err_class = {
                'FATAL': None,
                'NOBREAK': True,
            }
        else:
            err_class = {'FATAL': None, }

        tmp = output.getvalue()
        if filename is None:
            self.send('\n'.join((tmp, str(e))), err_class, dbglvl=1)
        else:
            self.send('\n'.join(('in file: %s' % filename, tmp, str(e))), err_class, dbglvl=1)
        return '\n'.join((tmp, str(e)))

    def record_start(self, level, hide_output=True):
        self.record = []
        self.recording = True
        self.record_hide_output = hide_output
        self.record_level = level

    def record_pop(self):
        result = self.record
        self.record = []
        return result

    def record_stop(self):
        if self.recording:
            self.recording = False
            self.record_hide_output = False
            return self.record

    def out_history(self, dbg_container_index, return_str=False, return_list=False):

        level, msg, depth, err_class = self.dbg_container[dbg_container_index]
        self.ignore_now = None
        result, err = self.create(self.name, self.style, self.debug_level, level, msg, depth, end_id=dbg_container_index)
        if not return_str:
            self.send('\n'.join(result), err_class, dbglvl=err)
            if return_list:
                return result
        else:
            if return_list:
                return list
            return '\n'.join(result)
        return None

    def out(self, level, msg, depth=0, err_class=None, return_str=False, return_list=False, message_only=False):

        if (depth == 0) and (not self.recording):
            # init if depth is zero and recording is turned off
            self.dbg_container = [(level, msg, depth, err_class)]
        elif depth < 0:
            # use last depth
            depth = self.dbg_container[-1][2]
        else:
            self.dbg_container.append((level, msg, depth, err_class))

        if self.recording:
            # get index if level match
            if level <= self.record_level:
                self.record.append(len(self.dbg_container) - 1)

        if not return_str:
            if not (self.recording and self.record_hide_output):
                # print out
                if depth == 0:
                    self.ignore_now = None
                if level <= self.debug_level:
                    data_out, err = self.create(self.name, self.style, self.debug_level,
                                                level, msg, depth, message_only=message_only)
                    self.send('\n'.join(data_out), err_class, dbglvl=err)
                    if return_list:
                        return data_out
                if return_list:
                    # same level for creating must be set
                    data_out, err = self.create(self.name, self.style, level, level,
                                                msg, depth, message_only=message_only)
                    return data_out

            return
        else:
            if level <= self.debug_level:
                if return_list:
                    return self.create(self.name, self.style, self.debug_level, level, msg, depth)[0]
                else:
                    return '\n'.join(self.create(self.name, self.style, self.debug_level, level, msg, depth)[0])
            else:
                if return_list:
                    return []
                else:
                    return ''

    def create(self, this_name, this_style, this_level, level, msg, depth, end_id=None, message_only=False):
        log = []
        if level <= this_level:
            # trigger output
            if this_style == self.S_STRAIGHT:
                if message_only:
                    log.append(msg)
                else:
                    log.append(''.join((self.DBG_FORMAT, '%s')) % (self.DBG_OUT[level], this_name, msg))
            elif this_style == self.S_RECURSIVE:
                if depth == 0:
                    if message_only:
                        log.append(msg)
                    else:
                        log.append(''.join((self.DBG_FORMAT, '%s')) % (self.DBG_OUT[level], this_name, msg))
                elif this_level == self.DBG_MAX_LEVEL:
                    if message_only:
                        log.append('-%s %s' % (self.DBG_REC_CHAR * depth, msg))
                    else:
                        log.append(''.join((self.DBG_FORMAT, '-%s%s')) % (self.DBG_OUT[level],
                                                                          this_name, self.DBG_REC_CHAR * depth, msg))
                else:
                    if end_id is None:
                        end_id = len(self.dbg_container) - 1

                    if self.ignore_now is None:
                        start_id = end_id - self.recursive_out_max_backwards
                        if start_id < 0:
                            start_id = 0
                        self.ignore_now = end_id
                        char_first = '.'
                    else:
                        start_id = self.ignore_now + 1
                        self.ignore_now = end_id
                        char_first = '|'

                    for chk_id in range(end_id - start_id + 1):
                        # check depth is zero
                        if self.dbg_container[end_id - chk_id][2] == 0:
                            start_id = end_id - chk_id
                            char_first = '/'
                            break
                    else:
                        # get id with zero depth
                        while start_id >= 0:
                            start_id -= 1
                            if self.dbg_container[start_id][2] == 0:
                                char_first = '/'
                                break

                    depth_last = None
                    for xlevel, msg, depth, err_class in reversed(self.dbg_container[start_id + 1:end_id + 1]):
                        if depth_last is None:
                            depth_last = depth
                        else:
                            if depth >= depth_last:
                                continue
                            else:
                                depth_last = depth
                        if message_only:
                            log.append('%s%s %s' % ('|', self.DBG_REC_CHAR * depth, msg))
                        else:
                            log.append(''.join(
                                (self.DBG_FORMAT, '%s%s%s')) % (self.DBG_OUT[xlevel],
                                                                this_name, '|', self.DBG_REC_CHAR * depth, msg))
                    if char_first != '|':
                        xlevel, msg, depth, err_class = self.dbg_container[start_id]
                        if message_only:
                            log.append('%s%s %s' % (char_first, self.DBG_REC_CHAR * depth, msg))
                        else:
                            log.append(''.join(
                                (self.DBG_FORMAT, '%s%s%s')) % (self.DBG_OUT[xlevel],
                                                                this_name, char_first, self.DBG_REC_CHAR * depth, msg))

        return tuple(reversed(log)), level
