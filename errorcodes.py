#!/usr/bin/env python
# -*- coding: utf-8 -*-

dbgmsg = {
    'OK': (3, '000', 'Tool executed successfully.',),
    'TOOL_FAILURE': (1, '<error_code_placeholder>', 'srvChecker aborted with error.'),
    'UC2_NOA2L': (0, 'SRVCHK_T001', 'A2L file %s not found.',),
    'UC2_NOHEX': (0, 'SRVCHK_T002', 'Calibrated HEX file %s not found.',),
    'UC2_NOA2LHEX': (1, 'SRVCHK_T003', 'A2L or calibrated HEX filepath not passed; use --a2l and --hex.',),
    'UC2_INPUT': (0, 'SRVCHK_T004', 'Input lst file %s not found.'),
    'UC2_A2L_OK': (3, 'SRVCHK_T005', 'A2L file read.'),
    'UC2_HEX_OK': (3, 'SRVCHK_T006', 'HEX file %s read.'),
    'UC2_SCAN_NEEDED': (2, 'SRVCHK_T007',
                        'Scanning disabled since no input *.lst file given or option --no-scan used.'),
    'UC2_NOSCAN': (3, 'SRVCHK_T008', 'No reduced axispoints found in hex file(s) and it is not impacted.  '
                                     'Use force-scan option to check the PVER for possible risk in future.'),
    'UC2_SCAN': (3, 'SRVCHK_T009', 'No reduced axispoints found in hex file(s).'
                                   'PVER scanning will start as --force-scan is provided.'),
    'UC2_REDUCED': (2, 'SRVCHK_T010', '%d reduced axispoints found in hex files. Hex file might be impacted. '
                                      'Validate srvchecker_scan.lst and %ssrvchecker_impact.lst further.'),
    'UC2_INPUTLSTW': (2, 'SRVCHK_T011', 'Format of input file %s may not be correct.'),
    'UC2_INPUTLST': (3, 'SRVCHK_T012', 'Input file %s read successfully.'),
    'UC2_AFFECTED': (2, 'SRVCHK_T013', '%d labels with invalid reduction in axispoints found in hex file. '
                                       'Validate the contents of "%s" and perform risk analysis.'),
    'UC2_NOTAFFECTED': (3, 'SRVCHK_T014',
                        'No labels with invalid reduction in axispoints found in %s file. Hence, the Hex file '
                        'is not affected.'),
    # 'UC1_PVER_SWB': (2,'SRVCHK_T015', '"SWB" build system detected. paths for header including may not be complete.'),
    'UC2_ENDIAN': (4, 'SRVCHK_T016', '%s endian used.'),
    'UC1_INCPATH': (4, 'SRVCHK_T017', 'Used paths for header including: %s'),
    'WRITEFILE': (3, 'SRVCHK_T018', '"%s" written to "%s"'),
    'WRITEFILEONE': (3, 'SRVCHK_T019', 'reduced axispoints details of hex file %s and A2L file written to %s'),
    'UC1_UNCPATH_FAIL': (0, 'SRVCHK_T020', 'Failed fetching project from UNC path!'),
    'UC1_UNCPATH_WARN': (2, 'SRVCHK_T021', 'Given project path is a network path. Hence, it will take more time for '
                                           'processing. For faster processing, copy PVER with results to local drive.'),
    'UC1_NOPVER': (0, 'SRVCHK_T022', 'Successfully built PVER in a local path is required for scanning!'),
    'UC2_NOHEXLIST': (0, 'SRVCHK_T023', 'List of calibrated HEX files %s not found.',),
    'UC1_NODIRECTCALL': (3, 'SRVCHK_T024', 'No labels with direct call found. '
                                           'Hence, the hex file will not be impacted.'),
    'UC1_DIRECTCALL_WITH_SRV': (2, 'SRVCHK_T025', '%d labels are accessed wrongly with srv function. Validate the contents of srvchecker_scan.lst.'),
    'UC1_REGEX_INFO': (4, 'SRVCHK_T026', 'regex pattern used: "%s"'),
    'UC1_INPUTSEARCH': (0, 'SRVCHK_T027', 'Input search file list %s not found.'),
    'UC1_INPUTEMPTY': (0, 'SRVCHK_T028', 'Input search file %s seems to be empty.'),
    'UC1_INPUTUSE': (2, 'SRVCHK_T029', 'Input search file %s replaces internal search list.'),
    'TOOLERROR': (1, 'SRVCHK_T030', 'Tool internal error.'),
    'UNKNWONPRIO': (1, 'SRVCHK_T031', 'Unknown prio passed: use idle, low, normal or parent.'),
    'INPUTSRCERR': (0, 'SRVCHK_T032', 'Input source file list %s not found.'),
    'SRCNOPRJABS': (1, 'SRVCHK_T033', 'Could not detect a valid project with given input source file list.'),
    'SRCNOPRJREL': (1, 'SRVCHK_T034', 'Input source file list with relative filepaths are given, '
                                      'but project not found in given root folder.'),
    # 'SRCNOTFOUND': (0, 'SRVCHK_T035', 'Some of the listed source files not found.'),
    'SRCNOFILES': (1, 'SRVCHK_T036', 'No source files listed.'),
    'INPUTSRCREAD': (3, 'SRVCHK_T037', 'Input source file %s read.'),
    'UNKNWONENDIAN': (1, 'SRVCHK_T038', 'Unknown endian mode.'),
    'PVERLSTCONFIGURE': (2, 'SRVCHK_T039', 'Please configure successfully built PVER path or maps/curves with invalid '
                                           'access list from previous PVER scan result.'),
    'OPTIONS': (4, 'SRVCHK_T040', 'options passed ...'),
    'CONFCREATED': (3, 'SRVCHK_T041', 'Config file %s created.'),
    'CONF_FAILED': (1, 'SRVCHK_T042', 'Could not open configuration file %s'),
    'FORCESCAN': (1, 'SRVCHK_T043', '--forcescan is provided, so PVER path needs to be provided.'),
    'GCC_VERSION': (3, 'SRVCHK_T044', 'Using gcc version %s'),
    'CREATING_I': (3, 'SRVCHK_T045', 'Scanning %d relevant source files ...'),
    'CREATED_I': (3, 'SRVCHK_T046', '%.1fMB done in %3.1f seconds (%.1fMB/s).'),
    'UNC_DELFAIL': (2, 'SRVCHK_T047', 'Could not remove path %s'),
    'UNC_DELDONE': (3, 'SRVCHK_T048', '%s folder %s deleted.'),
    'UNC_START': (3, 'SRVCHK_T049', 'Start analyzing source UNC path.'),
    'UNC_PATH_DONE': (3, 'SRVCHK_T050', '%d paths built up in %.1f secs.'),
    'UNC_STARTCOPY': (3, 'SRVCHK_T051', 'Fetching %s source files.'),
    'UNC_COPY_DONE': (3, 'SRVCHK_T052', '%d files copied in %.1f sec.'),
    'GCC_COMPERR': (2, 'SRVCHK_T053', 'Error during pre-compiling: %s. '
                                      'Please check if the PVER is built successfully.'),
    'GCC_COMPERR_I': (2, 'SRVCHK_T054', 'In %d files precompiler error detected. '
                                        'For the precompiler error information, refer srvchecker_scan.ulf '
                                        'in the output path. Please check if the PVER is built successfully or some of '
                                        'the artifacts expected are missing.'),
    'USERBREAK': (1, 'SRVCHK_T055', 'interrupted by user.'),
    'NOOUTPUTPATH': (0, 'SRVCHK_T056', 'Please provide the output path. Output path is mandatory.'),
    'UC3_NOSRVIPOLIST': (1, 'SRVCHK_T057', 'serviceCheckLibraryList.lst file not found in %s'),
    'UC3_SRVIPOLIST_OK': (3, 'SRVCHK_T058', 'Using serviceCheckLibraryList.lst found in %s for search.'),
    'UC3_NOPOSSIBILYAFFECTEDLIST': (0, 'SRVCHK_T059',
                                    '%s not found. If relative path, check existence within PVER.'),
    'UC3_AFFECTEDLIST_DGSB': (2, 'SRVCHK_T060', 'Ignoring the option --affected-list(-a) as it is applicable only'
                                                'for a MDGB PVER.'),
    'UC3_AFFECTEDLIST_NOPVER': (2, 'SRVCHK_T061', 'Ignoring the option --affected-list(-a) as --input-lst is provided '
                                                  'and PVER is ignored. Continuing to write srvchecker_impact.lst.'),
    'UC3_WRONGLISTENTRY': (1, 'SRVCHK_T062', 'Line "%s" is an invalid entry in %s.'),  # DOUBT
    'UC3_WRONGLISTFORMAT': (1, 'SRVCHK_T063', '%s format is wrong: "%s"'),
    'UC3_AFFECTEDNUM': (3, 'SRVCHK_T064', 'MDGB usecase: %d labels are accessed wrongly, '
                                          'validate the content of affected_items.lst.'),
    'UC3_AFFECTEDITEMSCREATED': (3, 'SRVCHK_T065', 'Successfully created "affected_items.lst" in %s'),
    'UC3_AFFECTEDLISTTIME': (3, 'SRVCHK_T066', 'Time taken to generate "affected_items.lst": %3.5f seconds.'),
    'IFILE_TIME': (4, 'SRVCHK_T067', '%3.1f seconds for generating i files.'),
    'IFILECLEAN_TIME': (4, 'SRVCHK_T068', '%3.1f seconds taken to clean i files.'),
    'UC2_WRONGHEXINPUT': (0, 'SRVCHK_T069', '%s is an invalid hex input type. A valid calibrated hex file with ".hex" '
                                            'extension or a list of calibrated hex files in a "lst" file is expected.'),
    'UC1_NOROOT_NOINPUTLST': (0, 'SRVCHK_T070', 'Either successfully built PVER Path or srvchecker_scan.lst '
                                                'needs to be provided (not both).'),
    'UC2_WRONGHEXFILESPATH': (2, 'SRVCHK_T071', '%d wrong hex file(s) path present in the hex input list: %s. '
                                                'Files written to %s'),
    'UC2_ALLHEXPATHWRONG': (1, 'SRVCHK_T072', 'All the hex file paths provided in the hex input list "%s" is wrong.'),
    'UC2_HEXFILELISTEMPTY': (1, 'SRVCHK_T073', 'Hex file lst "%s" is empty.'),
    'NOOPTIONS': (0, 'SRVCHK_T074', 'Successfully built PVER Path or srvchecker_scan.lst or A2L & Hex File'
                                    ' seems to be empty.'),
    'WRONGROOT': (0, 'SRVCHK_T075', 'PVER should only be a folder. It cannot be a file or a zip.'),
    'ROOTMANDATORY': (0, 'SRVCHK_T076', 'PVER path is mandatory with --input-src-lst.'),
    'ROOTRELATIVE': (0, 'SRVCHK_T077', 'PVER path must be an absolute path.'),
    'RELATIVEPATH': (0, 'SRVCHK_T078', '%s path is relative. Provide PVER path or an absolute path as input.'),
    'RELATIVEHEXPATH': (0, 'SRVCHK_T079', 'Hex files within %s is relative: %s. '
                                          'Provide PVER path or an absolute path as input. '),
    'ALM_WARNING': (2, 'SRVCHK_T080', 'ALM projects usecase is tested with limited PVERs. '
                                      'Hence can be used for piloting. '
                                      'Request you to contact “Tool-Hotline ICEDCGMCOP RBEI/ETB (CAP-SST/ESS1) ICEDCGMCOP.Tool-Hotline@de.bosch.com” for any related queries.'),
    # 'MISMATCH_ROOT': (1, 'SRVCHK_T081', 'PVER path is not same as PVER root path '
    #                                    'within --input-src-lst: %s'),
    'INPUTSRCLSTNOTPRESENT': (0, 'SRVCHK_T082', '--input-src-lst file not found: %s'),
    'NO_PERMISSION': (1, 'SRVCHK_T083', 'No access for creating file. Please check your permissions in folder %s'),
    'BACKING_UP': (3, 'SRVCHK_T084', 'Taking backup of old srvchecker files in %s'),
    'BACKUP_COMPLETED': (3, 'SRVCHK_T085', 'Taking backup in %s completed.'),
    'UC1_INVALIDPVER': (1, 'SRVCHK_T086', 'Configured PVER is invalid or not supported by srvchecker. '
                                          'Please configure a valid MDG1 or MEDC17 project.(MIC projects with UNC path is not supported)'),
    'INPUTWHITELSTNOTPRESENT': (2, 'SRVCHK_T087', 'whitelist file not found: %s'),
    'WHITELST_DISCARDED': (2, 'SRVCHK_T088', 'Invalid template header, hence whitelist discarded: %s'),
    'INVALID_ENTRY': (2, 'SRVCHK_T089', 'Invalid entry, hence ignoring line %d: %s'),
    'IFILE_START': (4, 'SRVCHK_T090', 'i files creation started.'),
    'IFILE_END': (4, 'SRVCHK_T091', 'i files creation ended.'),
    'TIME_TAKEN_DEBUG': (4, 'SRVCHK_T092', 'Total time taken for %s: %.2f seconds.'),
    'ARTIFACTS_VALIDATION_START': (4, 'SRVCHK_T093', 'Validation of the provided artifacts started.'),
    'ARTIFACTS_VALIDATION_END': (4, 'SRVCHK_T094', 'Validation of the provided artifacts ended.'),
    'TIME_TAKEN_INFO': (3, 'SRVCHK_T095', 'Total time taken for %s: %.2f seconds.'),
    'NO_INCLUDE_FILES': (1, 'SRVCHK_T096', 'No source files to scan in the PVER.'),
    'COPYING_REQUIRED_FILES_FOR_PRJ_MEDC17': (3, 'SRVCHK_T097', 'Copying the required files from UNC to local path for pver validation.'),
    'PVER_VALIDATION': (3, 'SRVCHK_T098', 'Validating the PVER. . .'),
    'PVER_SUCCESS': (3, 'SRVCHK_T099', 'PVER validation successful: %s PVER of %s nature.'),
    'PVER_NOT_FOUND': (0, 'SRVCHK_T100', 'PVER path not found: %s.'),
    'COPY_FAILURE':(1,  'SRVCHK_T101', 'Issue with copying the required files. %d files are left out from copying.'),
    'BUGGY_INPUTLIST_FILE': (1, 'SRVCHK_T102', 'Previous run of SrvChecker was with a buggy version "%s". Please re-run SrvChecker by providing PVER path. Refer "%s" for versions info'),
    'FILE_NOT_FOUND': (1, 'SRVCHK_T103', '"%s" file was not found either at "%s" or at "%s"'),
    'UC1_DIRECTCALL_WITH_UNKOWN': (2, 'SRVCHK_T104', '%d labels are accessed directly. Validate the contents of srvchecker_scan.lst.'),
}

# use keys from 'dbgmsg' in errcode, telling handler to exit on this message with mapped errlevel

errcode = {
    'UC2_NOA2L': 1,
    'UC2_NOHEX': 2,
    'UC2_NOA2LHEX': 3,
    'UC2_INPUT': 4,
    'UC2_WRONGHEXINPUT': 69,
    'CONF_FAILED': 42,
    'FORCESCAN': 43,
    'UNKNWONPRIO': 11,
    'UNKNWONENDIAN': 11,
    'INPUTSRCERR': 32,
    'SRCNOPRJABS': 33,
    'SRCNOPRJREL': 34,
    # 'SRCNOTFOUND': 35,
    'SRCNOFILES': 36,
    'UC1_UNCPATH_FAIL': 20,
    'UC1_NOPVER': 22,
    'UC2_NOHEXLIST': 23,
    'UC1_INPUTSEARCH': 27,
    'UC1_INPUTEMPTY': 28,
    'TOOLERROR': 30,
    'USERBREAK': 55,
    'NOOUTPUTPATH': 56,
    'UC3_NOSRVIPOLIST': 57,
    'UC3_NOPOSSIBILYAFFECTEDLIST': 59,
    'UC3_WRONGLISTENTRY': 62,
    'UC3_WRONGLISTFORMAT': 63,
    'UC1_NOROOT_NOINPUTLST': 70,
    'UC2_ALLHEXPATHWRONG': 72,
    'UC2_HEXFILELISTEMPTY': 73,
    'NOOPTIONS': 74,
    'WRONGROOT': 75,
    'ROOTMANDATORY': 76,
    'ROOTRELATIVE': 77,
    'RELATIVEPATH': 78,
    'RELATIVEHEXPATH': 79,
    # 'MISMATCH_ROOT': 81,
    'INPUTSRCLSTNOTPRESENT': 82,
    'NO_PERMISSION': 83,
    'UC1_INVALIDPVER': 86,
    'NO_INCLUDE_FILES': 96,
    'PVER_NOT_FOUND': 100,
    'COPY_FAILURE':101,
    'BUGGY_INPUTLIST_FILE':102,
    'FILE_NOT_FOUND':103,
}

successcode = {
    'OK': 0,
    'CONFCREATED': 0
}


class ErrHandler:
    def __init__(self, timestamp=True, msg_category=None, ti=None, usedbg=None, debug=False):
        self.dbg = usedbg
        self.ulfs = {}
        self.msg_on_creation = []
        self.current_ulf_id = None
        self.timestamp = timestamp
        self.ti = ti
        self.msg_category = msg_category
        self.xl_writer = None
        self.debug = debug
        self.start_time = None
        self.srv_log = None
        self.tool_error = dbgmsg['TOOL_FAILURE']

    def create(self, ulf_id, filepath, toolname, version, wiki=None):
        if (ulf_id not in self.ulfs) or (self.ulfs[ulf_id] is None):
            from ulf import ULF
            self.ulfs[ulf_id] = ULF(filepath, toolname, version, wiki=wiki, ti=self.ti, msg_category=self.msg_category)
            for key_, ulf_msg_ in self.msg_on_creation:
                self.msg(ulf_id, key_, ulfmsg=ulf_msg_)
        self.current_ulf_id = ulf_id

    def get_current(self):
        return self.current_ulf_id

    def set_xl_writer(self, xl_obj):
        self.xl_writer = xl_obj

    def msg(self, ulf_id, msgkey, ulfmsg=None, ft=None, filename=None, stdout=True, print_val=True):
        sn = ''
        if msgkey in dbgmsg:
            errtype, sn, errmsg = dbgmsg[msgkey]
            if ulfmsg is not None:
                errmsg = ulfmsg
            elif ft is not None:
                errmsg = errmsg % ft
            if ulf_id is not None:
                if ulf_id == 'ALL':
                    for ulf_id in self.ulfs:
                        self.ulfs[ulf_id].add(errtype, sn, errmsg, filename)
                else:
                    self.ulfs[ulf_id].add(errtype, sn, errmsg, filename)
                if msgkey in errcode:
                    error_code_val = sn.replace('SRVCHK_T', '')
                    for ulf_id in self.ulfs:
                        self.ulfs[ulf_id].add(self.tool_error[0], error_code_val, self.tool_error[2], None)

            if stdout and (self.dbg is not None) and print_val:
                dlvl = errtype
                # FATAL logging changed to ERROR for users
                if not dlvl:
                    dlvl = 1
                if msgkey in errcode or msgkey in successcode:
                    from srvchecker import endtime_print
                    # close all ulf objects
                    for ulf_id in self.ulfs:
                        if self.ulfs[ulf_id] is not None:
                            self.ulfs[ulf_id].output(timestamp=self.timestamp)
                    if self.xl_writer is not None:
                        self.xl_writer.set_exec_status((None, 'SUCCESS') if msgkey in successcode else (errmsg, 'FAILURE'))
                        self.xl_writer.close_workbook()
                    if msgkey in successcode:
                        endtime_print(self, self.start_time, None, 'srvchecker completion')

                if sn == '000':
                    self.dbg.send('SUCCESS: %s, %s' % (sn, errmsg), {})
                else:
                    self.dbg.out(dlvl, '%s, %s' % (sn, errmsg))

                if dlvl != 4 or self.debug:
                    self.srv_log.logmessage(msgkey, ft)
        import sys
        if msgkey in successcode:
            sys.exit(successcode[msgkey])
        if msgkey in errcode:
            error_code_val = sn.replace('SRVCHK_T', '')
            dbgmsg['TOOL_FAILURE'] = (self.tool_error[0], error_code_val, self.tool_error[2])
            self.dbg.send('FAILURE: %s, %s' % (error_code_val, self.tool_error[2]), {})
            self.srv_log.logmessage('TOOL_FAILURE')
            sys.exit(errcode[msgkey])

    def add_on_creation(self, msgkey, ulfmsg=None):
        self.msg_on_creation.append((msgkey, ulfmsg))

    def update_logger(self, srv_log):
        self.srv_log = srv_log

    def update_start_time(self, starttime):
        self.start_time = starttime

    def __getitem__(self, key_):
        # direct access to ulf object
        return self.ulfs[key_]


if __name__ == "__main__":
    from ulf import ULF
    print('Do you want a sorted output based on the warning? If so enter "True", or enter "False"!!!')
    print_normal = True if input().upper() == 'TRUE' else False
    print('Possible tool errors:\n')
    print(f'{"ERR_CAT":10} {"SHORTNAME":14} {"MESSAGE":110} {"EXIT"}')

    def getkey(item):
        return item[0]

    msges = []

    for key in dbgmsg:
        ulf_errtype, ulf_sn, ulf_msg = dbgmsg[key]
        if ulf_sn == '000':
            err_text = 'SUCCESS'
        else:
            err_text = ULF.cat[ulf_errtype]
        if key in errcode:
            err = f'errorlevel {errcode[key]}'
        else:
            err = ''
        msges.append((err_text, ulf_sn, ulf_msg, err))

    if not print_normal:
        msges = sorted(msges, key=getkey)

    for msg in msges:
        print(f'{msg[0]:10} {msg[1]:14} {msg[2]:110} {msg[3]}')
