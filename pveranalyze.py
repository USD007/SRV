"""
mmi6kor
12 Nov 2018
Analyze the PVER and deduct the different PVER Type
"""
import os.path
import re
import subprocess
from glob import glob
from srvchecker import *


class PverAnalyze:

    def __init__(self, root,opath, is_unc_path=False, is_unc_valid=False):
        self.toolbaseexecpath = "C:/Program Files (x86)/Toolbase Client/texec.cmd"
        self.pverbuildnature = self.prjcfgname = self.pvernature = self.pverbuild = ''
        # self.root = root      # Changed from self.root = self.root.replace('\\', '/'). As prj_medc17 was not working with front slashes(//)
        self.miclws = re.compile(r'(LWS|MIC)_(DGSB|MDGB|PMB)', flags=re.IGNORECASE)
        self.srcfiles = re.compile(r'\.c\s*$', flags=re.IGNORECASE)
        self.pversuccess = False
        self.srvversion = ''
        self.db3file = ''
        self.bcname = ''
        self.hexfound = False
        self.a2lfound = False
        self.rebuild = False
        self.is_unc_path = is_unc_path
        self.is_unc_valid = is_unc_valid
        self.root=updateRootPath(root)
        self.output = opath

    # ------------------------------------------------------------------------------
    # Call the prj_medc17 tool
    # ------------------------------------------------------------------------------

    def checkpverproperties(self):

        try:
            # run toolbase prj_medc17 and wait till completion (prj_medc17/latest)
            calltxec = subprocess.Popen([self.toolbaseexecpath, 'prj_medc17/latest', '--srvchecker', '--projprops', self.root, '--output',self.output ],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = calltxec.communicate()
            p_status = calltxec.wait()

            # If executed successfully
            if calltxec.returncode == 0:
                pverproppath_1 = self.root + "/_log/Octane/proj_properties.txt"
                pverproppath_2 = self.output + "/_log/Octane/proj_properties.txt"
                if os.path.exists(pverproppath_1):
                    pverproppath = pverproppath_1
                elif os.path.exists(pverproppath_2):
                    pverproppath = pverproppath_2
                else:
                    return False
                with open(pverproppath, 'r') as F:
                    raw = F.read()
                self.pvernature = (re.findall('PRJ_NATURE=(\w+)', raw)[0]).upper()
                self.pverbuild = (re.findall('PRJ_BUILD_NAME=(\w.+)', raw)[0]).upper()

                # If Any Issue Octane will provide the output as UNKNOWN
                if self.pverbuild == 'UNKNOWN' or self.pvernature == 'UNKNOWN' or not self.pvernature or not self.pverbuild:
                    return False

                prjgname = re.findall('PRJ_CFG_NAME=(\w+)', raw)  # DOUBT - returns MEDC17 - Clearcase
                if prjgname:
                    self.prjcfgname = re.findall('PRJ_CFG_NAME=(\w+)', raw)[0]

                self.pverbuildnature = self.pvernature + "_" + self.pverbuild
                return True
            else:
                return False  # DOUBT - Delete 'pverproppath' is returning false.
        except Exception:
            return False
        finally:
            self.root = self.root.replace('\\', '/') # because paths having \t or \n will not work

    def get_pverbuildnature(self):
        return self.pverbuildnature

    def get_pvernature(self):
        return self.pvernature

    def get_pverbuild(self):
        return self.pverbuild

    def get_prjcfgname(self):
        return self.prjcfgname

    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # Get SRV/SRVPT Version
    # ------------------------------------------------------------------------------
    def getsrvversion(self, bcname):
        srvversion = revision = ''
        if self.pvernature != '' and self.pverbuild != '' and self.root != '':
            # MIC OR DB3
            if self.pvernature == 'LWS':
                # Read DB3 File
                srvversion, revision = self.readdb3file(bcname)

            elif self.pvernature == 'MIC':
                # Read MIC File
                srvversion, revision = self.readmicfile(bcname)
        return srvversion, revision
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # Get SRV/SRVPT Version from MIC File
    # ------------------------------------------------------------------------------
    def readmicfile(self, bcname):
        version = revision = ""
        micpath = self.root + "/" + bcname + "/_metadata/mic/temptypes.mic"
        if os.path.exists(micpath):
            with open(micpath, 'r') as F:
                raw = F.read()
            srv = re.findall("(\d+\.\d+\.\d+);(\d+)", raw)
            if srv:
                version, revision = srv[0]

        return version, revision

    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # Get version and revision value from the db3 file
    # ------------------------------------------------------------------------------
    def readdb3file(self, cont_name, class_name='BC'):
        version = revision = ""
        db3file = os.path.join(self.root, "workunit.lws.cc.db3").replace('\\', '/')
        if os.path.exists(db3file):
            import sqlite3

            # decoding function
            def sql_decode(text):
                try:
                    text = text.decode('UTF-8', 'ignore')
                except Exception as e:
                    raise e
                return text

            sqlite3.register_converter("TEXT", lambda v: v.decode('UTF-8').encode('UTF-8'))

            with sqlite3.connect(db3file) as conn:
                # use function instead of internal 'str' for decoding
                conn.text_factory = sql_decode
                for version, revision in conn.execute(
                        'SELECT Variant, Revision from Artifacts where Class=\"' + class_name + '\" and Name=\"' + cont_name + '\"').fetchall():
                    return version, revision

        return version, revision

    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # Check PVER Success
    # ------------------------------------------------------------------------------
    def successfulvalidation(self, options):

        try:
            if self.pverbuildnature != '' and self.root != '':
                if self.is_unc_path:
                    return self.is_unc_valid
                if options.affected_list and self.pverbuildnature == 'LWS_MDGB':
                    return True
                if self.miclws.search(self.pverbuildnature):
                    self.pversuccess = self.searchhexa2lfolder('/_bin/swb')
                elif self.pverbuildnature == 'LWS_SWB':
                    self.pversuccess = self.searchhexa2lfolder('/_bin/swb')
                elif self.pverbuildnature == 'LWS_GS_MAKE':
                    self.pversuccess = self.searchhexa2lfolder('/_bin/swb')
                elif self.pverbuildnature == 'CLEARCASE_DS SWB':
                    self.pversuccess = self.searchhexa2lfolder('/bin')
                elif self.pverbuildnature == 'NESTOR_GS_MAKE':
                    self.pversuccess = self.searchhexa2lfolder('/delivery')

            return self.pversuccess
        except:
            return False
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # Search Hex & A2L File
    # ------------------------------------------------------------------------------
    def searchhexa2lfolder(self, hexpath):

        self.hexfound = False
        self.a2lfound = False
        from general import hex_extensions
        for root, dirs, files in os.walk(self.root + hexpath):
            for file in files:
                if file.lower().endswith(hex_extensions):
                    self.hexfound = True
                if file.lower().endswith('.a2l'):
                    self.a2lfound = True

        if self.a2lfound and self.hexfound:
            return True
        else:
            return False
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # Get MSR A2L file path
    # ------------------------------------------------------------------------------
    def getA2LFilePath(self):
        a2lPath = None
        if self.miclws.search(
                self.pverbuildnature) or self.pverbuildnature == 'LWS_SWB' or self.pverbuildnature == 'LWS_GS_MAKE':
            for root, dirs, files in os.walk(self.root + '/_bin/swb'):
                for file in files:
                    if file.lower().endswith('_internal.a2l'):
                        a2lPath = os.path.join(self.root + '/_bin/swb', file)
                        return a2lPath
        elif self.pverbuildnature == 'CLEARCASE_DS SWB':
            for root, dirs, files in os.walk(self.root + '/bin'):
                for file in files:
                    if file.lower().endswith('_internal.a2l'):
                        a2lPath = os.path.join(self.root + '/bin', file)
                        return a2lPath
        elif self.pverbuildnature == 'NESTOR_GS_MAKE':
            for root, dirs, files in os.walk(self.root + '/delivery'):
                for file in files:
                    if file.lower().endswith('.a2l'):
                        a2lPath = os.path.join(self.root + '/delivery', file)
                        return a2lPath
        return a2lPath
    # ------------------------------------------------------------------------------
    # Get the list of C File names
    # ------------------------------------------------------------------------------
    def getsrclist(self,ulf):

        cfilelist = set()
        if self.pverbuildnature != '':
            if self.miclws.search(self.pverbuildnature):
                cfilelist = self.read_dgsbmdgbpmb('/_gen/swb/filegroup/compiler/src_lists')
            elif self.pverbuildnature == 'LWS_SWB':
                cfilelist = self.read_dssdom('/_gen/swb/build/filelist_all_c_files.c')
            elif self.pverbuildnature == 'CLEARCASE_DS SWB':
                cfilelist = self.read_dsclearcase('/tmp/build/filelist_all_c_files.c')
            elif self.pverbuildnature == 'NESTOR_GS_MAKE':
                cfilelist = self.read_gsnestor(ulf)
            elif self.pverbuildnature == 'LWS_GS_MAKE':
                cfilelist = self.read_gslws()

        return cfilelist
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # Read DS Nestor PVER
    # ------------------------------------------------------------------------------
    def read_gsnestor(self, ulf):

        cfilelistlws = set()

        # Added default file list
        cfilelistlws.add(self.root + '/makeout/damos/gen_files/pta_vect.c')
        cfilelistlws.add(self.root + '/makeout/damos/gen_files/epk.c')
        cfilelistlws.add(self.root + '/makeout/damos/gen_files/_merged_dat.c')
        cfilelistlws.add(self.root + '/makeout/mcop/mcop_copy.c')

        # Reading the filelist_gen
        with open(self.root + '/makeout/core/gen_filelists/filelist_gen.c', 'r') as F:
            raw = F.readlines()
        for filecont in raw:
            if self.srcfiles.search(filecont):
                filecont = re.sub('\s*$', '', filecont)
                linesplit = filecont.split('/makeout/')[-1]
                cfilelistlws.add(self.root + '/makeout/' + linesplit)

        # Reading the MAK File
        try:
            makFile_name='filelist.mak'
            makFile_location=self.root + '/makeout/temp/'+ makFile_name
            if not os.path.exists(makFile_location):
                makFile_location=self.root + '/' + makFile_name

            with open(makFile_location, 'r') as F:
                raw = F.readlines()
            for filecont in raw:
                filecont = re.sub(r'\s*(\$\(PST_PATH\)\\|\s+\\|\s*$|\w+\s*=\s*)', '', filecont)
                if self.srcfiles.search(filecont):
                    filecont = re.sub(r'\\', '/', filecont)
                    cfilelistlws.add(self.root + "/" + filecont)
            return cfilelistlws

        except Exception:
            ulf.msg('ALL','FILE_NOT_FOUND', ft=(makFile_name,(self.root + '/makeout/temp'), self.root ))

    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # Read GS SDOM
    # ------------------------------------------------------------------------------
    def read_gslws(self):

        cfilelistlws = set()

        # Reading the filelist_gen
        with open(self.root + '/_gen/swb/core/gen_filelists/filelist_gen.c', 'r') as F:
            raw = F.readlines()
        for filecont in raw:
            if self.srcfiles.search(filecont):
                filecont = re.sub('\s*$', '', filecont)
                linesplit = filecont.split('/_gen/')[-1]
                cfilelistlws.add(self.root + '/_gen/' + linesplit)

        # Reading the filelist_gen
        with open(self.root + '/_gen/swb/damos/gen_filelists/filelist_gen_c.lst', 'r') as F:
            raw = F.readlines()
        for filecont in raw:
            filecont = re.sub(r'\s*(\.\\|\s*$|\w+\s*=\s*)', '', filecont)
            if self.srcfiles.search(filecont):
                cfilelistlws.add(self.root + '/' + filecont)

        # Reading the MAK File
        with open(self.root + '/_gen/swb/temp/filelist.mak', 'r') as F:
            raw = F.readlines()
        for filecont in raw:
            filecont = re.sub(r'\s*(\.\\|\s+\\|\s*$|\w+\s*=\s*)', '', filecont)
            if self.srcfiles.search(filecont):
                filecont = re.sub(r'\\', '/', filecont)
                cfilelistlws.add(self.root + "/" + filecont)

        return cfilelistlws

    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # Read DS SWB SDOM
    # ------------------------------------------------------------------------------

    def read_dssdom(self, cfilepath):

        cfilelistlws = set()
        rootsplit = ''
        with open(self.root + '/' + cfilepath, 'r') as F:
            raw = F.readlines()

        # Search the Root Path during build, as this needs to be replaced with correct root
        for filecont in raw:
            if filecont.find('_gen/swb') > 0:
                rootsplit = filecont.split('_gen/swb')[0]
                break

        for filecont in raw:
            if self.srcfiles.search(filecont):
                filecont = re.sub('\s*$', '', filecont)
                cfilelistlws.add(filecont.replace(rootsplit, self.root+"/"))
        return cfilelistlws

    # ------------------------------------------------------------------------------
    # Read DS SWB Clearcase
    # ------------------------------------------------------------------------------
    def read_dsclearcase(self, cfilepath):

        cfilelistlws = set()
        with open(self.root + '/' + cfilepath, 'r') as F:
            raw = F.readlines()
        for filecont in raw:
            if self.srcfiles.search(filecont):
                filecont = re.sub('\s*$', '', filecont)
                linesplit = filecont.split('medc17')[-1]
                cfilelistlws.add(self.root + linesplit)
        return cfilelistlws

    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # Read MIC/SDOM for DGSB,MDGB, PMB
    # ------------------------------------------------------------------------------
    def read_dgsbmdgbpmb(self, path_list):

        cfilelistlws = set()
        for filename in glob(os.path.join(self.root + "/" + path_list, '*.lst')):
            with open(filename, 'r') as F:
                raw = F.readlines()
            for filecont in raw:
                if self.srcfiles.search(filecont):
                    filecont = re.sub('\s*$', '', filecont)
                    cfilelistlws.add(self.root + "/" + filecont)
        return cfilelistlws

    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # Read File List
    # ------------------------------------------------------------------------------
    def readfilelist(self, listoffiles):
        reqcfiles = []
        notavailablelist = []
        import ntpath
        for file in listoffiles:
            file = file.replace('\\', '/')
            if os.path.exists(file):
                filename = ntpath.basename(file)
                size = int(os.path.getsize(file))
                dirname = ntpath.dirname(file)
                bcfcname = dirname.replace(self.root + '/', "")
                reqcfiles.append([(bcfcname, filename), size])
            else:
                filename = ntpath.basename(file)
                dirname = ntpath.dirname(file)
                bcfcname = dirname.replace(self.root + '/', "")
                notavailablelist.append(bcfcname + "," + filename + ",NA,Missing")

        return reqcfiles, notavailablelist

    # exclude File List
    def exclude_files(self, src_file_list):
        excluded_file_list = ['_merged_dat.c', '_epk.c', 'mcop_copy.c', 'all_elements_h_c.c', 'all_elements_mcop.c', 'all_elements_d.c']
        import ntpath
        excluded_c_files_list = []
        for relist in excluded_file_list:
            for idx, s in enumerate(src_file_list):
                if s.endswith(relist):
                    filename = ntpath.basename(s)
                    dirname = ntpath.dirname(s)
                    bcfcname = dirname.replace(self.root + '/', "")
                    excluded_c_files_list.append(bcfcname + "," + filename + ",NA,Excluded")
                    del src_file_list[idx]
        return excluded_c_files_list

    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # For Compiler Flags
    # ------------------------------------------------------------------------------
    def parse_swb_config(self, root, config_name=''):
        # parse swb config xml
        # TODO version could be checked > 'CATALOG/ABLOCKS[1]/ABLOCK'.attrib > {"VAR" : "x.x.x"}
        # TODO Optimize to extract only compiler flags

        from dbg_handler import DbgHandler
        dbg = DbgHandler(self.__class__.__name__, 0)

        from lxml import etree
        import os.path

        # read raw data
        if config_name != 'swbuild_config.xml':
            return {}  # If the build doesn't contain configuration file

        import glob
        # Get all the paths containing configuration name - 'swbuild_config.xml'
        swb_config_filepath = glob.glob(os.path.join(root, '**', config_name), recursive=True)
        filesfound = len(swb_config_filepath)
        if filesfound:
            swb_config_filepath = swb_config_filepath[0].replace('\\', '/')
            swb_config_fn = swb_config_filepath.replace(root.replace('\\', '/'), '')
        else:
            # self.dbg.send('registered configuration file "%s" not found' % swb_config_fn, {'FATAL': None})
            dbg.out(1, 'registered configuration file "%s" not found' % config_name)
            return {}

        dbg.out(3, 'parsing swbuild config %s' % swb_config_fn)

        with open(swb_config_filepath, 'rb') as F:
            cfg_raw = F.read()

        # parse with etree
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        swb_config_tree = etree.XML(cfg_raw, parser)
        # collect all SD tags under the first parent sdg tag with attribute GID = 'SWBProjectConfiguration'
        swb_config_tags = swb_config_tree.xpath('//SDG[@GID="SWBProjectConfiguration"][1]//SD') + swb_config_tree.xpath(
            '//SDG[@GID="unified SWBProjectConfiguration"][1]//SD')
        swb_config = {}
        for cfg_tag in swb_config_tags:
            # copy each tag to swb_config dictionary
            if 'GID' in cfg_tag.attrib:
                if cfg_tag.text:
                    text = cfg_tag.text.strip()
                else:
                    text = ''
                swb_config[cfg_tag.attrib['GID'].upper().strip()] = text

        # if PRJ_NAME not defined use parent folder name instead ...
        if ('PRJ_NAME' in swb_config) and (not swb_config['PRJ_NAME']):
            swb_config['PRJ_NAME'] = os.path.abspath(root).replace('\\', '/').split('/')[-1]
            dbg.out(3, 'using parent folder as project name %s' % swb_config['PRJ_NAME'])

        return swb_config

    # ------------------------------------------------------------------------------

def updateRootPath(root):
    from win32com.client import Dispatch
    strComputer = "."
    drivename = dict()
    bjWMIService = Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = bjWMIService.ConnectServer(strComputer, "root\cimv2")
    colItems = objSWbemServices.ExecQuery("Select * from Win32_LogicalDisk")
    for objItem in colItems:
        drivename.update({objItem.Caption: [objItem.DriveType, objItem.ProviderName]})
    if root.startswith("\\"):
        return root
    else:
        if drivename.get(root[:2])[1]:
            return (root.replace(root[:2], drivename.get(root[:2])[1]))
        else:
            return root
# def copy_prjmedc_files_to_local(uncpath):
#     import os
#     from general import unc_to_local_path
#     # For LWS and CLEARCASE projects
#     ini_file_path = validate_copy_files(uncpath, unc_to_local_path, 'medc17_tools.ini', folders=['\\', '\\_conf\\'])
#
#     if ini_file_path is None:
#         # For NESTOR projects
#         ini_file_path = validate_copy_files(uncpath, unc_to_local_path, 'config.mak', folders=['\\'])
#
#     # TODO - Support for MIC PVERs
#
#     if ini_file_path is not None:
#         with open(ini_file_path, 'r') as file:
#             for entry in file.readlines():
#                 if '=' in entry:
#                     values = entry.strip().split('=')
#                     if values[0] == 'PRJ_CFG_NAME' and values[1] == 'swbuild_config.xml':
#                         if validate_copy_files(uncpath, unc_to_local_path, values[1], folders=['\\', '\\MAK\\MakeWare\\']) is None:
#                             return None, False
#                     elif values[0] == 'PRJ_CONTAINER':
#                         if validate_copy_files(uncpath, unc_to_local_path, values[1], folders=['\\', '\\_conf\\']) is None:
#                             return None, False
#         found_dir = False
#         hex_found = a2l_found = False
#         for directory in ['\\_bin\\swb', '\\bin', '\\delivery']:
#             if os.path.exists(uncpath + directory):
#                 src_files = os.listdir(uncpath + directory)
#                 for file in src_files:
#                     if file.endswith('.hex') and not hex_found:
#                         hex_found = True
#                     elif file.endswith('.a2l') and not a2l_found:
#                         a2l_found = True
#                 if not (a2l_found and hex_found):
#                     continue
#                 found_dir = True
#                 break
#         if not found_dir:
#             return unc_to_local_path, False
#         return unc_to_local_path, a2l_found and hex_found
#     return None, False


# def validate_copy_files(source_path, destination_path, file, folders):
#     import os
#     import shutil
#     from srvchecker import check_filepath_arg
#     for folder in folders:
#         filepath = source_path + folder + file
#         if os.path.exists(filepath):
#             destination_path = check_filepath_arg(destination_path + folder, file, "", create_file=True)
#             if destination_path is not None:
#                 shutil.copyfile(filepath, destination_path)
#                 return destination_path
#     return None
