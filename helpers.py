#!/usr/bin/env python
# -*- coding: utf-8 -*-


def version_check(ver_script, ver_input):
    """
    evaluates version by using given string, returns True/False
    input: unified version tuple, eval_string
    output: False/True
    
    syntax eval_string:
        [><=!]VERSION. [ [><=!]VARIANT. [ [><=!]BUGFIX; [ [><=!]REVISION ] ] ]
    examples:
        "11" or "=11" or "==11"
        > if version 11 return True
        "!11" or "!=11"
        > if version not 11 return True
        ">11" or ">=11" or "<=11" or "<11"
        > if version >, <, ... return True
        "11.<3"
        if version == 11 and variant < 3 return True
        "11.>=3.>=1" or "11.>=3.>=1;>=0"
        if version 11, variant >= 3, bugfix >= 1, (revsion >= 0) return True
    """

    # func_ids
    equal = 0
    greater = 1
    greater_eq = 2
    lesser = 3
    lesser_eq = 4
    _not = 5

    SCRIPT_VERSION, SCRIPT_VARIANT, SCRIPT_BUGFIX, SCRIPT_PROJECT, SCRIPT_REVISION = ver_script

    def get_func_ver(inp):
        funct = equal
        if inp.startswith('>='):
            funct = greater_eq
            num = int(inp[2:])
        elif inp.startswith('<='):
            funct = lesser_eq
            num = int(inp[2:])
        elif inp.startswith('=='):
            num = int(inp[2:])
        elif inp.startswith('='):
            num = int(inp[1:])
        elif inp.startswith('>'):
            funct = greater
            num = int(inp[1:])
        elif inp.startswith('<'):
            funct = lesser
            num = int(inp[1:])
        elif inp.startswith('!'):
            funct = _not
            num = int(inp[1:])
        elif inp.startswith('!='):
            funct = _not
            num = int(inp[2:])
        else:
            num = int(inp)
        return funct, num

    def check_func(funct, num, number_ref):
        if funct == equal:
            if number_ref == num:
                return True
        elif funct == greater:
            if number_ref > num:
                return True
        elif funct == greater_eq:
            if number_ref >= num:
                return True
        elif funct == lesser:
            if number_ref < num:
                return True
        elif funct == lesser_eq:
            if number_ref <= num:
                return True
        elif funct == _not:
            if number_ref != num:
                return True
        return False

    ver_input_splitted = ver_input.split('.')
    if len(ver_input_splitted) > 0:
        func, number = get_func_ver(ver_input_splitted[0])
        if not check_func(func, number, SCRIPT_VERSION):
            return False
    if len(ver_input_splitted) > 1:
        func, number = get_func_ver(ver_input_splitted[1])
        if not check_func(func, number, SCRIPT_VARIANT):
            return False
    if len(ver_input_splitted) > 2:
        bugfix_splitted = ver_input_splitted[2].split(';')
        if len(bugfix_splitted) == 1:
            func, number = get_func_ver(ver_input_splitted[2])
            if not check_func(func, number, SCRIPT_BUGFIX):
                return False
        elif len(bugfix_splitted) == 2:
            func, number = get_func_ver(bugfix_splitted[0])
            if not check_func(func, number, SCRIPT_BUGFIX):
                return False
            func, number = get_func_ver(bugfix_splitted[1])
            if not check_func(func, number, SCRIPT_REVISION):
                return False

    return True


def version_split(ver_raw, rev_raw):
    """
    splits verison input from sdom/lws_manager and stores to a unified verison tuple
    (version, variant, bugfix, project, revision)
    (int, int, int, str, int)
    """
    version = None
    variant = None
    bugfix = None
    project = None
    revision = None
    if ver_raw is not None:
        ver_raw = ver_raw.strip()
        if len(ver_raw):
            ver_splitted = ver_raw.split('.')
            if len(ver_splitted) > 0:
                version = int(ver_splitted[0])
            if len(ver_splitted) > 1:
                variant = int(ver_splitted[1])
            if len(ver_splitted) > 2:
                bugfix_splitted = ver_splitted[2].split('_')
                if len(bugfix_splitted) > 1:
                    bugfix = int(bugfix_splitted[0])
                    project = '_'.join(bugfix_splitted[1:])
                else:
                    bugfix = int(ver_splitted[2])
            if rev_raw is not None:
                revision = int(rev_raw)
    return version, variant, bugfix, project, revision
