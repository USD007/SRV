choices = ["map_static", "map_non_static", "curve_static", "curve_non_static"]
correct_calls = {"ADAPTER": [choices[1], choices[3]], "NON_ADAPTER": [choices[2]]}


# (srv_ipo_map, map_static, list of srv_searchstring)
def check_correct_calls(map_curves_key, aff_list_type, srv_search_list):

    if type(srv_search_list) is list:
        srv_search_list = {"NON_ADAPTER": srv_search_list}

    for srv_type in srv_search_list:
        for search_val in srv_search_list[srv_type]:
            if map_curves_key in search_val.decode("utf-8", 'ignore'):
                for choice in correct_calls[srv_type]:
                    if aff_list_type == choice:
                        return False
    return True


def print_impacted_file(affected_list, srv_searchlist, ulf, ulf_key, search_results,
                        ulf_label_found_desc, wiki, xl_writer):
    affected_items = set()
    for aff_listtype in affected_list:  # map_nonstatic, {indirectA, indirectB}
        for aff_lst in affected_list[aff_listtype]:  # indirectA
            for cpath, cfilename, result_re, label, line_number_start, line_number_end, ospstatus in search_results:
                if label in aff_lst:
                    if check_correct_calls(result_re, aff_listtype, srv_searchlist):
                        affected_items.add(aff_lst)
                        if ulf_label_found_desc is not None:
                            if line_number_start is not None:
                                if line_number_end is None:
                                    line_number = '%s..EOF' % line_number_start
                                else:
                                    line_number = '%s..%s' % (line_number_start, line_number_end)
                            else:
                                line_number = 'unknown'

                            descr = ulf_label_found_desc['DESC'].format(**{'PATH': cpath, 'FILE': cfilename,
                                                                           'FUNC': result_re, 'LABEL': label,
                                                                           'LINE': line_number, 'WIKI': wiki})
                            sn = ulf_label_found_desc['SHORTNAME']

                            xl_writer.add_tablecontents('affected_items', [sn, label, descr, wiki])
                            import os.path
                            ulf['AFFECTED'].add(1, sn, descr, os.path.join(cpath, cfilename),
                                                col_number='0', line_number=line_number_start, wiki=wiki)

    aff_data = list(affected_items)
    if len(aff_data):
        writetoaffectedlist = "\n".join(aff_data)
        ulf.msg(ulf_key, 'UC3_AFFECTEDNUM', ft=len(aff_data))
    else:
        writetoaffectedlist = ""
        ulf.msg(ulf_key, 'UC1_NODIRECTCALL')
    return writetoaffectedlist


def parse_affected_list(affected_list_path, ulf, affected_list, ulf_key):
    aff_lst = {}
    with open(affected_list_path, "r") as F:
        for line in F.read().splitlines():
            line_val = line.split(', ')
            if len(line_val) == 3:
                mc_val = line_val[1] + "_" + line_val[2]
                if mc_val in choices:
                    if mc_val in aff_lst:
                        aff_lst[mc_val] += [line_val[0]]
                    else:
                        aff_lst[mc_val] = [line_val[0]]
                else:
                    ulf.msg(ulf_key, 'UC3_WRONGLISTENTRY', ft=(str(line_val), affected_list))
            else:
                ulf.msg(ulf_key, 'UC3_WRONGLISTFORMAT', ft=(affected_list, str(line_val)))
        return aff_lst
