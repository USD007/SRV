#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dbg_handler import DbgHandler
import os


class AxisPoints:
    import re
    ignore_record_layout = ['GROUP', 'MAPG', 'FIXCURVE', 'FIXMAP', 'CURG', 'VALA', 'GKF', 'GKL', 'FKFNOSH', '^_REC_']
    re_reclayout = re.compile(r'W([USR])(8|16|32)')
    re_reclayout_gs = re.compile(r'SST[XY]?([US])(B|W)')
    re_reclayout_last = re.compile(r'([USR])(8|16|32)')
    re_reclayout_ignore = re.compile('|'.join(ignore_record_layout))

    a2l_typesize = {"BYTE": 1, "UBYTE": 1, "SBYTE": 1, "PBYTE": 1, "WORD": 2, "UWORD": 2,
                    "SWORD": 2, "PWORD": 2, "LONG": 4, "ULONG": 4, "SLONG": 4, "PLONG": 4,
                    "FLOAT32_IEEE": 4, "FLOAT64_IEEE": 8, "A_INT64": 8, "A_UINT64": 8}

    big_endian = {2, 3}

    def __init__(self, use_endian=None, debug=0):
        self.little_endian = use_endian
        self.debug = debug
        self.dbg = DbgHandler(self.__class__.__name__, debug)
        self.cal_content = self.reclayout = self.vendor_id = None
        self.ih = None

    def load_a2l(self, filepath, filter_type=None):

        # dtype size mapping (got from a2linspector)

        with open(filepath, 'r', encoding='UTF8', errors='ignore') as F:
            a2l_raw = F.read()

        import re

        # get also vendor id if exists in a2l
        vendor_id = re.search(r'SYSTEM_CONSTANT\s+"MDG1CPUVENDOR_SC"\s+"(\d+)"', a2l_raw)
        if vendor_id is not None:
            vendor_id = int(vendor_id.group(1))
        # check if little endian or big endian shell be used, if not given
        if self.little_endian is None:
            if vendor_id in self.big_endian:
                self.little_endian = False
            else:
                self.little_endian = True

        re_reclayout = re.compile(r'/begin RECORD_LAYOUT[\t ]+(\w+)\s+(.*?)/end RECORD_LAYOUT', flags=re.DOTALL)
        re_calprm = re.compile(r'/begin CHARACTERISTIC\s+(.*?)/end CHARACTERISTIC', flags=re.DOTALL)
        re_axis = re.compile(r'/begin AXIS_DESCR\s+(.*?)/end AXIS_DESCR', flags=re.DOTALL)

        cal_address = {}
        for calprm_raw in re_calprm.finditer(a2l_raw):
            idx = 0
            name, desc, caltype, address, record_layout = None, None, None, None, None
            for val in calprm_raw.group(1).splitlines():
                val = val.strip()
                if not len(val):
                    continue
                if idx == 0:
                    name = val  # ex:AcChrgrIntkT_ADCSensTransf_f_CUR
                elif idx == 1:  # ""
                    desc = val
                elif idx == 2:
                    if filter_type is not None:
                        if val not in filter_type:
                            idx = None
                            break
                    caltype = val  ##CURVE
                elif idx == 3:
                    if val.upper().startswith('0x'):  # ex:0x80621ACC
                        val = val[2:]  ##ex:80621ACC
                    address = int(val, 16)  # ex:2153913036
                elif idx == 4:
                    record_layout = val
                else:
                    break
                idx += 1
            if idx is None:
                continue

            axis_len = []
            for axis_raw in re_axis.finditer(calprm_raw.group(1)):  # inside the calparm raw
                val_idx = 0
                for val in axis_raw.group(1).splitlines():
                    val = val.strip()
                    if not len(val):
                        continue
                    if val_idx >= 3:  # ex:25
                        axis_len.append(int(val))
                        break
                    val_idx += 1

            if caltype not in cal_address:
                cal_address[caltype] = {}
            cal_address[caltype][name] = (desc, address, record_layout, axis_len)

        reclayout = {}
        for reclayout_raw in re_reclayout.finditer(a2l_raw):
            name = reclayout_raw.group(1)  # ex:DefaultValueRecordLayout_uint32
            tmp_dict = {}
            attribs = set([])
            for val in reclayout_raw.group(2).splitlines():  # ex:FNC_VALUES        1 ULONG COLUMN_DIR DIRECT
                val = val.strip()
                if not len(val):
                    continue
                tmp = [x.strip() for x in val.replace('\t', ' ').split(' ') if
                       len(x.strip())]  # ex:['FNC_VALUES', '1', 'ULONG', 'COLUMN_DIR', 'DIRECT']
                if len(tmp) == 1:  # if one word
                    attribs.add(tmp[0])
                    continue
                sub_name = tmp[0]  # ex:FNC_VALUES
                sub_idx = int(tmp[1])  # ex: 1
                sub_dtype = tmp[2].upper()  # ex:ULONG
                if sub_dtype not in self.a2l_typesize:  # ex:ULONG in sub_dtype
                    tmp_dict = None
                    break
                if len(tmp) > 3:
                    sub_attr = set(tmp[3:])  # ex:'COLUMN_DIR','DIRECT'
                else:
                    sub_attr = set([])
                tmp_dict[sub_name] = (sub_idx, self.a2l_typesize[sub_dtype], sub_attr)
            if tmp_dict is None:
                continue
            reclayout[name] = (tmp_dict, attribs)
            self.cal_content, self.reclayout, self.vendor_id = cal_address, reclayout, vendor_id

    def load_hex(self, filepath):
        # read in intelhex
        from intelhex import IntelHex
        self.ih = IntelHex(filepath)
        return

    def get_value(self, address, length=1):
        """Calculating X & Y aixs"""
        if length == 1:
            return self.ih[address]
        value_array = self.ih.tobinarray(address, address + length)
        value = 0
        if self.little_endian:
            for idx in range(length):
                value += (value_array[idx] << (idx * 8))
        else:
            for idx in range(length):
                value += (value_array[length - 1 - idx] << (idx * 8))
        return value

    def get_poslen_axis(self, name):
        if name not in self.reclayout:
            return None
        rl_dict, rl_attribs = self.reclayout[name]
        x_idx = y_idx = None
        x_size = y_size = 0
        if 'NO_AXIS_PTS_X' in rl_dict:
            x_idx, x_size, x_attr = rl_dict['NO_AXIS_PTS_X']  # act9kor x_size is by a2l_typesize
            if x_idx > 2:
                return None
        if 'NO_AXIS_PTS_Y' in rl_dict:
            y_idx, y_size, y_attr = rl_dict['NO_AXIS_PTS_Y']
            if y_idx > 2:
                return None
        if x_idx == 1:
            if y_idx is not None:
                return [(0, x_size), (x_size, y_size)]
            return [(0, x_size)]
        elif y_idx == 1:  # act9kor todo wrong logic this steps does't exicute any time
            if y_idx is not None:
                return [(0, y_size), (y_size, x_size)]
            return [(0, y_size)]
        return None

    def get_axis_len(self, different_only=False):
        """
        returns {
                calprm_label : {
                                calprm_type : (Axis X Max, Axis Y Max, Axis X, Axis Y, Longname, Address, RecordLayout)
                                }
                }
        """
        result = {}
        for cal_type_ in self.cal_content:
            result[cal_type_] = {}
            for cal_label_ in self.cal_content[cal_type_]:
                desc, address, record_layout_name, axis_len = self.cal_content[cal_type_][cal_label_]
                axis_poslen = self.get_poslen_axis(record_layout_name)

                if axis_poslen is None:
                    # record layout indicates that current label is not using axispoints
                    continue

                axis_no = len(axis_len)
                if len(axis_poslen) != axis_no:
                    # unexpected count of axispoint descriptions
                    self.dbg.out(1,
                                 f'!!! expected axis for {cal_type_}:{axis_no}, in record layout found:{len(axis_poslen)}')
                    # (cal_type_, axis_no, len(axis_poslen)))
                    continue

                tmp = []
                for pos, dlen in axis_poslen:
                    tmp.append(self.get_value(address + pos, length=dlen))

                if different_only:
                    ignore_this = True
                    for a_idx, axiscount in enumerate(tmp):
                        if axis_len[a_idx] != axiscount:
                            ignore_this = False
                            break
                    if ignore_this:
                        continue
                # (Axis X Max, Axis Y Max, Axis X, Axis Y, Longname, Address, RecordLayout) } }
                if axis_no == 1:
                    # curves
                    result[cal_type_][cal_label_] = (str(axis_len[0]), '', str(tmp[0]), '', desc, '0x%08X' %
                                                     address, record_layout_name)
                elif axis_no == 2:
                    # maps
                    result[cal_type_][cal_label_] = (str(axis_len[0]), str(axis_len[1]), str(tmp[0]), str(tmp[1]),
                                                     desc, '0x%08X' % address, record_layout_name)

        return result

    def create_log_file(self, results, xl_writer, filename):

        xl_writer.add_worksheet(filename)
        for cal_type_ in sorted(results.keys()):
            for cal_label_ in sorted(results[cal_type_].keys()):
                xl_writer.add_tablecontents(filename, [cal_label_, cal_type_] + list(results[cal_type_][cal_label_]))


def get_file(rootpath, subpath, filemask):
    from fnmatch import fnmatch

    path = os.path.join(rootpath, subpath)
    if os.path.exists(path):
        for filename in os.listdir(path):
            if fnmatch(filename, filemask):
                return os.path.join(path, filename)
    return None


if __name__ == '__main__':  # pragma: no cover
    from optparse import OptionParser
    import os.path
    import sys

    usage = "usage: %prog -r prj_root_path"
    parser = OptionParser(usage=usage)
    parser.add_option('-r', '--root', default='.', type='string', help='project root path')
    parser.add_option('--a2lpath', default='_bin/swb', type='string', help='path to a2l')
    parser.add_option('--hexpath', default='_bin/swb', type='string', help='path to hex file')
    parser.add_option('--a2lfile', default='*internal.a2l', type='string', help='a2l filemask')
    parser.add_option('--hexfile', default='*.hex', type='string', help='hex filemask')
    parser.add_option('--diff-only', action='store_true', default=False,
                      help='lists only calprms with different axispoint max<>used count')
    (options, args) = parser.parse_args()

    dbg = 3
    dbgh = DbgHandler('SrvChecker', dbg)

    a2l_filepath = get_file(options.root, options.a2lpath, options.a2lfile)
    hex_filepath = get_file(options.root, options.hexpath, options.hexfile)

    if a2l_filepath is None:
        dbgh.out(1, '%s not found' % options.a2lfile)
        sys.exit(1)
    if hex_filepath is None:
        dbgh.out(1, '%s not found' % options.hexfile)
        sys.exit(1)

    ap = AxisPoints()
    ap.load_a2l(a2l_filepath, filter_type={'CURVE', 'MAP'})
    ap.load_hex(hex_filepath)
    # get axispoints and get dictionary
    cal_axispoints = ap.get_axis_len(different_only=options.diff_only)

    # create output
    log = [','.join(['CalPrm Label', 'Type', 'Axis X Max', 'Axis Y Max', 'Axis X', 'Axis Y', 'Longname',
                     'Address', 'RecordLayout'])]
    for cal_type in sorted(cal_axispoints.keys()):
        for cal_label in sorted(cal_axispoints[cal_type].keys()):
            log.append(','.join([cal_label, cal_type] + list(cal_axispoints[cal_type][cal_label])))

    with open(os.path.join(options.root, 'calprm_results.xlsx'), 'w') as F:
        F.write('\n'.join(log) + '\n')
