# internal config
# Requirement 
# Interpolation requirements are defined in this header Files------------------------------
# mmi6kor 02112018 
# -D_IPOADAPTER_H_ -D_SRVX_ADAPTER_H -D_SRVF_ADAPTER_H
# ------------------------------------------------------------------------------------------
search_me=[]
srv_list_path=''
CONFIG_STD = [
    {"DESCRIPTION": "SRV DOWNSCALING",
     "BUILD_ENV": ["CLEARCASE_DS SWB", "NESTOR_GS_MAKE"],
     "PRECOMPILER_FLAGS": '-D_IPOADAPTER_H_ -D_SRVX_ADAPTER_H -D_SRVF_ADAPTER_H -DRBA_SWTRACE_SHAREDBUILD_GLIWAON -DSYSTEM_H="\\"system.h\\"" -DDFPMDEF_H="\\"dsm.h\\"" -DEEPROM_H="\\"eep.h\\"" -DDSMDEF_H="\\"dsm.h\\"" -DPROJECT_H=SYSTEM_H',
     "CLEAN_I_CONTENT": True,
     "SEARCH_RETURN": "->_?(\w+)",
     "WHOLE_WORD": True,
     "CASE_SENS": False,
     "SEARCH_LIST": [
         "SrvX_IpoMap_S16S16_S32",
         "SrvX_IpoMap_S16S16_S8",
         "SrvX_IpoMap_S16S16_U16",
         "SrvX_IpoMap_S16S16_U8",
         "SrvX_IpoMap_S16S8_S16",
         "SrvX_IpoMap_S16S8_S8",
         "SrvX_IpoMap_S16S8_U16",
         "SrvX_IpoMap_S16S8_U8",
         "SrvX_IpoMap_S16U8_S16",
         "SrvX_IpoMap_S16U8_S8",
         "SrvX_IpoMap_S16U8_U16",
         "SrvX_IpoMap_S16U8_U8",
         "SrvX_IpoMap_S8S8_S16",
         "SrvX_IpoMap_S8S8_U16",
         "SrvX_IpoMap_S8S8_U8",
         "SrvX_IpoMap_U16S16_S16",
         "SrvX_IpoMap_U16S16_S8",
         "SrvX_IpoMap_U16S16_U16",
         "SrvX_IpoMap_U16S16_U8",
         "SrvX_IpoMap_U16S8_S16",
         "SrvX_IpoMap_U16S8_S8",
         "SrvX_IpoMap_U16S8_U16",
         "SrvX_IpoMap_U16S8_U8",
         "SrvX_IpoMap_U16U16_S16",
         "SrvX_IpoMap_U16U16_S8",
         "SrvX_IpoMap_U16U16_U8",
         "SrvX_IpoMap_U16U8_S16",
         "SrvX_IpoMap_U16U8_S8",
         "SrvX_IpoMap_U16U8_U16",
         "SrvX_IpoMap_U16U8_U8",
         "SrvX_IpoMap_U8S8_S16",
         "SrvX_IpoMap_U8S8_S8",
         "SrvX_IpoMap_U8S8_U16",
         "SrvX_IpoMap_U8S8_U8",
         "SrvX_IpoMap_U8U8_S16",
         "SrvX_IpoMap_U8U8_S8",
         "SrvX_IpoMap_U8U8_U16",
         "SrvF_IpoMap_R32R32_S8",
         "SrvF_IpoMap_R32R32_U8",
         "SrvF_IpoMap_R32R32_U16",
         "SrvF_IpoMap_U8U8_R32",
         "SrvF_IpoMap_U8S8_R32",
         "SrvF_IpoMap_S8S8_R32",
         "SrvF_IpoMap_U16U16_R32",
         "SrvF_IpoMap_U16S16_R32",
         "SrvF_IpoMap_U16U8_R32",
         "SrvF_IpoMap_U16S8_R32",
         "SrvF_IpoMap_S16U8_R32",
         "SrvF_IpoMap_S16S8_R32",
         "SrvF_IpoMap_R32U8_R32",
         "SrvF_IpoMap_R32S8_R32",
         "SrvF_IpoMap_R32U16_R32",
         "SrvF_IpoMap_S16S16_R32",
         "SrvF_IpoMap_R32R32_S16",
         "SrvF_IpoMap_R32S16_R32",
         "SrvF_IpoMap_R32S16_S16",
         "SrvF_IpoMap_R32S16_U8",
         "SrvF_IpoMap_R32U8_U8",
         "SrvF_IpoMap_R32S8_U8",
         "SrvF_IpoMap_R32U16_U8",
         "SrvF_IpoMap_R32U8_S8",
         "SrvF_IpoMap_R32S8_S8",
         "SrvF_IpoMap_R32U16_S8",
         "SrvF_IpoMap_R32S16_S8",
         "SrvF_IpoMap_R32U8_U16",
         "SrvF_IpoMap_R32S8_U16",
         "SrvF_IpoMap_R32U16_U16",
         "SrvF_IpoMap_R32S16_U16",
         "SrvF_IpoMap_R32U8_S16",
         "SrvF_IpoMap_R32S8_S16",
         "SrvF_IpoMap_R32U16_S16",
         "SrvF_IpoMap_R32R32_R32",
         "Ifx_IntIpoMap_s16s16_s8",
         "Ifx_IntIpoMap_s16s16_u16",
         "Ifx_IntIpoMap_s16s16_u8",
         "Ifx_IntIpoMap_s16s8_s16",
         "Ifx_IntIpoMap_s16s8_s8",
         "Ifx_IntIpoMap_s16s8_u16",
         "Ifx_IntIpoMap_s16s8_u8",
         "Ifx_IntIpoMap_s16u8_s16",
         "Ifx_IntIpoMap_s16u8_s8",
         "Ifx_IntIpoMap_s16u8_u16",
         "Ifx_IntIpoMap_s16u8_u8",
         "Ifx_IntIpoMap_s8s8_s16",
         "Ifx_IntIpoMap_s8s8_u16",
         "Ifx_IntIpoMap_s8s8_u8",
         "Ifx_IntIpoMap_u16s16_s16",
         "Ifx_IntIpoMap_u16s16_s8",
         "Ifx_IntIpoMap_u16s16_u16",
         "Ifx_IntIpoMap_u16s16_u8",
         "Ifx_IntIpoMap_u16s8_s16",
         "Ifx_IntIpoMap_u16s8_s8",
         "Ifx_IntIpoMap_u16s8_u16",
         "Ifx_IntIpoMap_u16s8_u8",
         "Ifx_IntIpoMap_u16u16_s16",
         "Ifx_IntIpoMap_u16u16_s8",
         "Ifx_IntIpoMap_u16u16_u8",
         "Ifx_IntIpoMap_u16u8_s16",
         "Ifx_IntIpoMap_u16u8_s8",
         "Ifx_IntIpoMap_u16u8_u16",
         "Ifx_IntIpoMap_u16u8_u8",
         "Ifx_IntIpoMap_u8s8_s16",
         "Ifx_IntIpoMap_u8s8_s8",
         "Ifx_IntIpoMap_u8s8_u16",
         "Ifx_IntIpoMap_u8s8_u8",
         "Ifx_IntIpoMap_u8u8_s16",
         "Ifx_IntIpoMap_u8u8_s8",
         "Ifx_IntIpoMap_u8u8_u16",
         "Ifl_IntIpoMap_f32f32_f32",
         "kf_ipol_S16U16U16",
         "kf_ipol_S16U8S16",
         "kf_ipol_S8U16U8",
         "kf_ipol_S8U8S16",
         "kf_ipol_S8U8U8",
         "kf_ipol_U16S8S8",
         "kf_ipol_U16U8U8",
         "kf_ipol_U8U8S8",
         "kf_ipol_U8U16U16",
         "kf_ipol_U8U16U8",
         "SrvX_IpoMapS16U8",
         "SrvX_IpoMapU8S16",
     ],
     "ULF_LABEL_FOUND_DESC": {
         "DESC": 'Direct call {FUNC} done in {PATH} of source file {FILE} (line: {LINE}), to access {LABEL}.',
         "SHORTNAME": 'SRVCHK_001',
     },
     "ULF_LABEL_FOUND_REDUCED_DESC": {
         "DESC": 'Direct call {FUNC} done in {PATH} of source file {FILE} (line: {LINE}), to access {LABEL}. And the {LABEL} is reduced. This is prohibited.',
         "SHORTNAME": 'SRVCHK_002',
     },
     "WIKI": 'https://connect.bosch.com/blogs/Service_Library_PS-EC/entry/Right_Usage_of_Curves_and_Maps?lang=en_us ',
     },

    {"DESCRIPTION": "SRV DOWNSCALING",
     "BUILD_ENV": ["MIC_MDGB", "MIC_PMB", "LWS_MDGB", "LWS_PMB"],
     "PRECOMPILER_FLAGS": '-D_IPOADAPTER_H_ -D_SRVX_ADAPTER_H -D_SRVF_ADAPTER_H -DRBA_SWTRACE_SHAREDBUILD_GLIWAON -DSYSTEM_H="\\"system.h\\"" -DDFPMDEF_H="\\"dsm.h\\"" -DEEPROM_H="\\"eep.h\\"" -DDSMDEF_H="\\"dsm.h\\"" -DPROJECT_H=SYSTEM_H',
     "CLEAN_I_CONTENT": True,
     "SEARCH_RETURN": "->_?(\w+)",
     "WHOLE_WORD": True,
     "CASE_SENS": False,
     "SEARCH_LIST": [
         "SrvX_IpoMap_S16S16_S32",
         "SrvX_IpoMap_S16S16_S8",
         "SrvX_IpoMap_S16S16_U16",
         "SrvX_IpoMap_S16S16_U8",
         "SrvX_IpoMap_S16S8_S16",
         "SrvX_IpoMap_S16S8_S8",
         "SrvX_IpoMap_S16S8_U16",
         "SrvX_IpoMap_S16S8_U8",
         "SrvX_IpoMap_S16U8_S16",
         "SrvX_IpoMap_S16U8_S8",
         "SrvX_IpoMap_S16U8_U16",
         "SrvX_IpoMap_S16U8_U8",
         "SrvX_IpoMap_S8S8_S16",
         "SrvX_IpoMap_S8S8_U16",
         "SrvX_IpoMap_S8S8_U8",
         "SrvX_IpoMap_U16S16_S16",
         "SrvX_IpoMap_U16S16_S8",
         "SrvX_IpoMap_U16S16_U16",
         "SrvX_IpoMap_U16S16_U8",
         "SrvX_IpoMap_U16S8_S16",
         "SrvX_IpoMap_U16S8_S8",
         "SrvX_IpoMap_U16S8_U16",
         "SrvX_IpoMap_U16S8_U8",
         "SrvX_IpoMap_U16U16_S16",
         "SrvX_IpoMap_U16U16_S8",
         "SrvX_IpoMap_U16U16_U8",
         "SrvX_IpoMap_U16U8_S16",
         "SrvX_IpoMap_U16U8_S8",
         "SrvX_IpoMap_U16U8_U16",
         "SrvX_IpoMap_U16U8_U8",
         "SrvX_IpoMap_U8S8_S16",
         "SrvX_IpoMap_U8S8_S8",
         "SrvX_IpoMap_U8S8_U16",
         "SrvX_IpoMap_U8S8_U8",
         "SrvX_IpoMap_U8U8_S16",
         "SrvX_IpoMap_U8U8_S8",
         "SrvX_IpoMap_U8U8_U16",
         "SrvF_IpoMap_R32R32_S8",
         "SrvF_IpoMap_R32R32_U8",
         "SrvF_IpoMap_R32R32_U16",
         "SrvF_IpoMap_U8U8_R32",
         "SrvF_IpoMap_U8S8_R32",
         "SrvF_IpoMap_S8S8_R32",
         "SrvF_IpoMap_U16U16_R32",
         "SrvF_IpoMap_U16S16_R32",
         "SrvF_IpoMap_U16U8_R32",
         "SrvF_IpoMap_U16S8_R32",
         "SrvF_IpoMap_S16U8_R32",
         "SrvF_IpoMap_S16S8_R32",
         "SrvF_IpoMap_R32U8_R32",
         "SrvF_IpoMap_R32S8_R32",
         "SrvF_IpoMap_R32U16_R32",
         "SrvF_IpoMap_S16S16_R32",
         "SrvF_IpoMap_R32R32_S16",
         "SrvF_IpoMap_R32S16_R32",
         "SrvF_IpoMap_R32S16_S16",
         "SrvF_IpoMap_R32S16_U8",
         "SrvF_IpoMap_R32U8_U8",
         "SrvF_IpoMap_R32S8_U8",
         "SrvF_IpoMap_R32U16_U8",
         "SrvF_IpoMap_R32U8_S8",
         "SrvF_IpoMap_R32S8_S8",
         "SrvF_IpoMap_R32U16_S8",
         "SrvF_IpoMap_R32S16_S8",
         "SrvF_IpoMap_R32U8_U16",
         "SrvF_IpoMap_R32S8_U16",
         "SrvF_IpoMap_R32U16_U16",
         "SrvF_IpoMap_R32S16_U16",
         "SrvF_IpoMap_R32U8_S16",
         "SrvF_IpoMap_R32S8_S16",
         "SrvF_IpoMap_R32U16_S16",
         "SrvF_IpoMap_R32U16_S16",
         "SrvF_IpoMap_R32R32_R32",
         "Ifx_IntIpoMap_s16s16_s8",
         "Ifx_IntIpoMap_s16s16_u16",
         "Ifx_IntIpoMap_s16s16_u8",
         "Ifx_IntIpoMap_s16s8_s16",
         "Ifx_IntIpoMap_s16s8_s8",
         "Ifx_IntIpoMap_s16s8_u16",
         "Ifx_IntIpoMap_s16s8_u8",
         "Ifx_IntIpoMap_s16u8_s16",
         "Ifx_IntIpoMap_s16u8_s8",
         "Ifx_IntIpoMap_s16u8_u16",
         "Ifx_IntIpoMap_s16u8_u8",
         "Ifx_IntIpoMap_s8s8_s16",
         "Ifx_IntIpoMap_s8s8_u16",
         "Ifx_IntIpoMap_s8s8_u8",
         "Ifx_IntIpoMap_u16s16_s16",
         "Ifx_IntIpoMap_u16s16_s8",
         "Ifx_IntIpoMap_u16s16_u16",
         "Ifx_IntIpoMap_u16s16_u8",
         "Ifx_IntIpoMap_u16s8_s16",
         "Ifx_IntIpoMap_u16s8_s8",
         "Ifx_IntIpoMap_u16s8_u16",
         "Ifx_IntIpoMap_u16s8_u8",
         "Ifx_IntIpoMap_u16u16_s16",
         "Ifx_IntIpoMap_u16u16_s8",
         "Ifx_IntIpoMap_u16u16_u8",
         "Ifx_IntIpoMap_u16u8_s16",
         "Ifx_IntIpoMap_u16u8_s8",
         "Ifx_IntIpoMap_u16u8_u16",
         "Ifx_IntIpoMap_u16u8_u8",
         "Ifx_IntIpoMap_u8s8_s16",
         "Ifx_IntIpoMap_u8s8_s8",
         "Ifx_IntIpoMap_u8s8_u16",
         "Ifx_IntIpoMap_u8s8_u8",
         "Ifx_IntIpoMap_u8u8_s16",
         "Ifx_IntIpoMap_u8u8_s8",
         "Ifx_IntIpoMap_u8u8_u16",
         "Ifl_IntIpoMap_f32f32_f32",
         ("kf_ipol_S16U16U16", [("BC:SrvPT", "=1.<11"), ]),
         ("kf_ipol_S16U8S16", [("BC:SrvPT", "=1.<11"), ]),
         ("kf_ipol_S8U16U8", [("BC:SrvPT", "=1.<11"), ]),
         ("kf_ipol_S8U8S16", [("BC:SrvPT", "=1.<11"), ]),
         ("kf_ipol_S8U8U8", [("BC:SrvPT", "=1.<11"), ]),
         ("kf_ipol_U16S8S8", [("BC:SrvPT", "=1.<11"), ]),
         ("kf_ipol_U16U8U8", [("BC:SrvPT", "=1.<11"), ]),
         ("kf_ipol_U8U8S8", [("BC:SrvPT", "=1.<11"), ]),
         ("kf_ipol_U8U16U16", [("BC:SrvPT", "=1.<11"), ]),
         ("kf_ipol_U8U16U8", [("BC:SrvPT", "=1.<11"), ]),
         ("SrvX_IpoMapS16U8", [("BC:SrvPT", "=1.<11"), ]),
         ("SrvX_IpoMapU8S16", [("BC:SrvPT", "=1.<11"), ]),
     ],
     "ULF_LABEL_FOUND_DESC": {
         "DESC": 'Direct call {FUNC} done in {PATH} of source file {FILE} (line: {LINE}), to access {LABEL}.',
         "SHORTNAME": 'SRVCHK_001',
     },
     "ULF_LABEL_FOUND_REDUCED_DESC": {
         "DESC": 'Direct call {FUNC} done in {PATH} of source file {FILE} (line: {LINE}), to access {LABEL}. And the {LABEL} is reduced. This is prohibited.',
         "SHORTNAME": 'SRVCHK_002',
     },
     "WIKI": 'https://connect.bosch.com/blogs/Service_Library_PS-EC/entry/Right_Usage_of_Curves_and_Maps?lang=en_us ',
     },
    {"DESCRIPTION": "SRV DOWNSCALING",
     "BUILD_ENV": ["LWS_DGSB", "LWS_SWB", "MIC_DGSB", "LWS_GS_MAKE"],
     "PRECOMPILER_FLAGS": '-D_IPOADAPTER_H_ -D_SRVX_ADAPTER_H -D_SRVF_ADAPTER_H -DRBA_SWTRACE_SHAREDBUILD_GLIWAON  -DSYSTEM_H="\\"system.h\\"" -DDFPMDEF_H="\\"dsm.h\\"" -DEEPROM_H="\\"eep.h\\"" -DDSMDEF_H="\\"dsm.h\\"" -DPROJECT_H=SYSTEM_H',
     "CLEAN_I_CONTENT": True,
     "SEARCH_RETURN": "->_?(\w+)",
     "WHOLE_WORD": True,
     "CASE_SENS": False,
     "SEARCH_LIST": [
         "SrvX_IpoMap_S16S16_S32",
         "SrvX_IpoMap_S16S16_S8",
         "SrvX_IpoMap_S16S16_U16",
         "SrvX_IpoMap_S16S16_U8",
         "SrvX_IpoMap_S16S8_S16",
         "SrvX_IpoMap_S16S8_S8",
         "SrvX_IpoMap_S16S8_U16",
         "SrvX_IpoMap_S16S8_U8",
         "SrvX_IpoMap_S16U8_S16",
         "SrvX_IpoMap_S16U8_S8",
         "SrvX_IpoMap_S16U8_U16",
         "SrvX_IpoMap_S16U8_U8",
         "SrvX_IpoMap_S8S8_S16",
         "SrvX_IpoMap_S8S8_U16",
         "SrvX_IpoMap_S8S8_U8",
         "SrvX_IpoMap_U16S16_S16",
         "SrvX_IpoMap_U16S16_S8",
         "SrvX_IpoMap_U16S16_U16",
         "SrvX_IpoMap_U16S16_U8",
         "SrvX_IpoMap_U16S8_S16",
         "SrvX_IpoMap_U16S8_S8",
         "SrvX_IpoMap_U16S8_U16",
         "SrvX_IpoMap_U16S8_U8",
         "SrvX_IpoMap_U16U16_S16",
         "SrvX_IpoMap_U16U16_S8",
         "SrvX_IpoMap_U16U16_U8",
         "SrvX_IpoMap_U16U8_S16",
         "SrvX_IpoMap_U16U8_S8",
         "SrvX_IpoMap_U16U8_U16",
         "SrvX_IpoMap_U16U8_U8",
         "SrvX_IpoMap_U8S8_S16",
         "SrvX_IpoMap_U8S8_S8",
         "SrvX_IpoMap_U8S8_U16",
         "SrvX_IpoMap_U8S8_U8",
         "SrvX_IpoMap_U8U8_S16",
         "SrvX_IpoMap_U8U8_S8",
         "SrvX_IpoMap_U8U8_U16",
         "SrvF_IpoMap_R32R32_S8",
         "SrvF_IpoMap_R32R32_U8",
         "SrvF_IpoMap_R32R32_U16",
         "SrvF_IpoMap_U8U8_R32",
         "SrvF_IpoMap_U8S8_R32",
         "SrvF_IpoMap_S8S8_R32",
         "SrvF_IpoMap_U16U16_R32",
         "SrvF_IpoMap_U16S16_R32",
         "SrvF_IpoMap_U16U8_R32",
         "SrvF_IpoMap_U16S8_R32",
         "SrvF_IpoMap_S16U8_R32",
         "SrvF_IpoMap_S16S8_R32",
         "SrvF_IpoMap_R32U8_R32",
         "SrvF_IpoMap_R32S8_R32",
         "SrvF_IpoMap_R32U16_R32",
         "SrvF_IpoMap_S16S16_R32",
         "SrvF_IpoMap_R32R32_S16",
         "SrvF_IpoMap_R32S16_R32",
         "SrvF_IpoMap_R32S16_S16",
         "SrvF_IpoMap_R32S16_U8",
         "SrvF_IpoMap_R32U8_U8",
         "SrvF_IpoMap_R32S8_U8",
         "SrvF_IpoMap_R32U16_U8",
         "SrvF_IpoMap_R32U8_S8",
         "SrvF_IpoMap_R32S8_S8",
         "SrvF_IpoMap_R32U16_S8",
         "SrvF_IpoMap_R32S16_S8",
         "SrvF_IpoMap_R32U8_U16",
         "SrvF_IpoMap_R32S8_U16",
         "SrvF_IpoMap_R32U16_U16",
         "SrvF_IpoMap_R32S16_U16",
         "SrvF_IpoMap_R32U8_S16",
         "SrvF_IpoMap_R32S8_S16",
         "SrvF_IpoMap_R32U16_S16",
         "SrvF_IpoMap_R32U16_S16",
         "SrvF_IpoMap_R32R32_R32",
         "Ifx_IntIpoMap_s16s16_s8",
         "Ifx_IntIpoMap_s16s16_u16",
         "Ifx_IntIpoMap_s16s16_u8",
         "Ifx_IntIpoMap_s16s8_s16",
         "Ifx_IntIpoMap_s16s8_s8",
         "Ifx_IntIpoMap_s16s8_u16",
         "Ifx_IntIpoMap_s16s8_u8",
         "Ifx_IntIpoMap_s16u8_s16",
         "Ifx_IntIpoMap_s16u8_s8",
         "Ifx_IntIpoMap_s16u8_u16",
         "Ifx_IntIpoMap_s16u8_u8",
         "Ifx_IntIpoMap_s8s8_s16",
         "Ifx_IntIpoMap_s8s8_u16",
         "Ifx_IntIpoMap_s8s8_u8",
         "Ifx_IntIpoMap_u16s16_s16",
         "Ifx_IntIpoMap_u16s16_s8",
         "Ifx_IntIpoMap_u16s16_u16",
         "Ifx_IntIpoMap_u16s16_u8",
         "Ifx_IntIpoMap_u16s8_s16",
         "Ifx_IntIpoMap_u16s8_s8",
         "Ifx_IntIpoMap_u16s8_u16",
         "Ifx_IntIpoMap_u16s8_u8",
         "Ifx_IntIpoMap_u16u16_s16",
         "Ifx_IntIpoMap_u16u16_s8",
         "Ifx_IntIpoMap_u16u16_u8",
         "Ifx_IntIpoMap_u16u8_s16",
         "Ifx_IntIpoMap_u16u8_s8",
         "Ifx_IntIpoMap_u16u8_u16",
         "Ifx_IntIpoMap_u16u8_u8",
         "Ifx_IntIpoMap_u8s8_s16",
         "Ifx_IntIpoMap_u8s8_s8",
         "Ifx_IntIpoMap_u8s8_u16",
         "Ifx_IntIpoMap_u8s8_u8",
         "Ifx_IntIpoMap_u8u8_s16",
         "Ifx_IntIpoMap_u8u8_s8",
         "Ifx_IntIpoMap_u8u8_u16",
         "Ifl_IntIpoMap_f32f32_f32",
         "SrvX_IpoCurve_S16_S32",
         "SrvX_IpoCurve_S16_S8",
         "SrvX_IpoCurve_S16_U16",
         "SrvX_IpoCurve_S16_U8",
         "SrvX_IpoCurve_S8_S16",
         "SrvX_IpoCurve_S8_U16",
         "SrvX_IpoCurve_S8_U8",
         "SrvX_IpoCurve_U16_S16",
         "SrvX_IpoCurve_U16_S8",
         "SrvX_IpoCurve_U16_U8",
         "SrvX_IpoCurve_U8_S16",
         "SrvX_IpoCurve_U8_S8",
         "SrvX_IpoCurve_U8_U16",
         "SrvF_IpoCurve_R32_U16",
         "SrvF_IpoCurve_U16_R32",
         "SrvF_IpoCurve_S16_R32",
         "SrvF_IpoCurve_R32_S16",
         "SrvF_IpoCurve_R32_S8",
         "SrvF_IpoCurve_S8_R32",
         "SrvF_IpoCurve_R32_U8",
         "SrvF_IpoCurve_U8_R32",
         "Ifx_IntIpoCur_s16_s8",
         "Ifx_IntIpoCur_s16_u16",
         "Ifx_IntIpoCur_s16_u8",
         "Ifx_IntIpoCur_s8_s16",
         "Ifx_IntIpoCur_s8_u16",
         "Ifx_IntIpoCur_s8_u8",
         "Ifx_IntIpoCur_u16_s16",
         "Ifx_IntIpoCur_u16_s8",
         "Ifx_IntIpoCur_u16_u8",
         "Ifx_IntIpoCur_u8_s16",
         "Ifx_IntIpoCur_u8_s8",
         "Ifx_IntIpoCur_u8_u16",
         "Ifl_IntIpoCur_f32_f32",
         ("kf_ipol_S16U16U16", [("BC:Srv", "=1.<26"), ("BC:Srv", "10.<7"), ]),
         ("kf_ipol_S16U8S16", [("BC:Srv", "=1.<26"), ("BC:Srv", "10.<7"), ]),
         ("kf_ipol_S8U16U8", [("BC:Srv", "=1.<26"), ("BC:Srv", "10.<7"), ]),
         ("kf_ipol_S8U8S16", [("BC:Srv", "=1.<26"), ("BC:Srv", "10.<7"), ]),
         ("kf_ipol_S8U8U8", [("BC:Srv", "=1.<26"), ("BC:Srv", "10.<7"), ]),
         ("kf_ipol_U16S8S8", [("BC:Srv", "=1.<26"), ("BC:Srv", "10.<7"), ]),
         ("kf_ipol_U16U8U8", [("BC:Srv", "=1.<26"), ("BC:Srv", "10.<7"), ]),
         ("kf_ipol_U8U8S8", [("BC:Srv", "=1.<26"), ("BC:Srv", "10.<7"), ]),
         ("kf_ipol_U8U16U16", [("BC:Srv", "=1.<26"), ("BC:Srv", "10.<7"), ]),
         ("kf_ipol_U8U16U8", [("BC:Srv", "=1.<26"), ("BC:Srv", "10.<7"), ]),
         ("SrvX_IpoMapS16U8", [("BC:Srv", "=1.<26"), ("BC:Srv", "10.<7"), ]),
         ("SrvX_IpoMapU8S16", [("BC:Srv", "=1.<26"), ("BC:Srv", "10.<7"), ]),
     ],
     "ULF_LABEL_FOUND_DESC": {
         "DESC": 'Direct call {FUNC} done in {PATH} of source file {FILE} (line: {LINE}), to access {LABEL}.',
         "SHORTNAME": 'SRVCHK_001',
     },
     "ULF_LABEL_FOUND_REDUCED_DESC": {
         "DESC": 'Direct call {FUNC} done in {PATH} of source file {FILE} (line: {LINE}), to access {LABEL}. And the {LABEL} is reduced. This is prohibited.',
         "SHORTNAME": 'SRVCHK_002',
     },
     "WIKI": 'https://connect.bosch.com/blogs/Service_Library_PS-EC/entry/Right_Usage_of_Curves_and_Maps?lang=en_us ',
     },
    # last config has mandatory data, if no source (pver) is passed
    {
        "ULF_LABEL_FOUND_REDUCED_DESC": {
           "DESC": 'Label {LABEL} has reduced axispoints and wrongly accessed in source.',
           "SHORTNAME": 'SRVCHK_100',
        },
        "WIKI": 'https://connect.bosch.com/blogs/Service_Library_PS-EC/entry/Right_Usage_of_Curves_and_Maps?lang=en_us',
    }
]


def to_conf_file(path, filename='srvchecker.json'):
    from windows_tools import write_file
    import json
    write_file(json.dumps(CONFIG_STD, indent=2), path=path, filename=filename, date_time_stamp=False, retry=True)
    return filename


def from_conf_file(filepath='srvchecker.json'):
    import json

    import os.path
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r') as F:
        dumps = F.read()
    return json.loads(dumps)


def get_default_config(conf_key, configs=None):
    if configs is None:
        # use internal configuration
        configs = CONFIG_STD
    return configs[-1][conf_key]


def create_regex_list(configs=None, build_env=None, search_replace=None):
    isfile_config = True
    if configs is None:
        # use internal configuration
        configs = CONFIG_STD
        isfile_config = False

    build_env_split = build_env.upper().split('_VA')
    build_env=build_env_split[0]

    # get correct regex search configuration by checking build_env matching
    for config in configs:
        if ('BUILD_ENV' in config) and (build_env is not None) and (build_env in config['BUILD_ENV']):
            break
        if 'BUILD_ENV' not in config:
            # if no build env is configured, take the first one
            break
    else:
        # no (matched) configuration found
        return None

    boundary, search_return, add_flags, description, ulf_conf, search_list, dep_search_list, case_sense, \
        clean_content, wiki = br'', None, '', '', None, [], None, False, True, ''
    ulf_label_found_desc, ulf_label_found_reduced_desc = None, None
    if ('WHOLE_WORD' in config) and (config['WHOLE_WORD']):
        boundary = br'\b'
    if 'SEARCH_RETURN' in config:
        search_return = config['SEARCH_RETURN']
    if 'PRECOMPILER_FLAGS' in config:
        add_flags = config['PRECOMPILER_FLAGS']
    if 'DESCRIPTION' in config:
        description = config['DESCRIPTION']
    if 'ULF_LABEL_FOUND_DESC' in config:
        ulf_label_found_desc = config['ULF_LABEL_FOUND_DESC']
    if 'ULF_LABEL_FOUND_REDUCED_DESC' in config:
        ulf_label_found_reduced_desc = config['ULF_LABEL_FOUND_REDUCED_DESC']
    if 'CASE_SENS' in config:
        case_sense = config['CASE_SENS']
    if 'CLEAN_I_CONTENT' in config:
        clean_content = config['CLEAN_I_CONTENT']
    if 'WIKI' in config:
        wiki = config['WIKI']


    if search_me is not None:
        if type(search_me) is not tuple:
            search_list = [boundary + x.strip().encode() + boundary for x in search_me if
                           (type(x) is not tuple) and (type(x) is not list)]
            dep_search_list = [(boundary + x[0].encode() + boundary, x[1]) for x in search_me if
                               (type(x) is tuple) or (type(x) is list)]

        else:
            search_list, dep_search_list = get_searchlst_ice(search_me, boundary)

    return search_list, dep_search_list, search_return, add_flags, description, ulf_label_found_desc, \
        ulf_label_found_reduced_desc, case_sense, clean_content, wiki


def get_searchlst_ice(search_me, boundary):
    search_list_adap = search_list_non_adap = []
    search_list = []
    dep_search_list_non_adap = dep_search_list_adap = []

    if search_me[0] is not None:  # Non-Adapter
        search_list_non_adap = [boundary + x.encode() + boundary for x in search_me[0]
                                if (type(x) is not tuple) and (type(x) is not list)]

        dep_search_list_non_adap = [(boundary + x[0].encode() + boundary, x[1]) for x in search_me[0] if
                                    (type(x) is tuple) or (type(x) is list)]

    if search_me[1] is not None:  # Adapter
        search_list_adap = [boundary + x.encode() + boundary for x in search_me[1]
                            if(type(x) is not tuple) and (type(x) is not list)]

        dep_search_list_adap = [(boundary + x[0].encode() + boundary, x[1]) for x in search_me[1]
                                if (type(x) is tuple) or (type(x) is list)]

    if search_list_adap is not None or search_list_non_adap is not None:
        search_list = {"NON_ADAPTER": search_list_non_adap, "ADAPTER": search_list_adap}

    dep_search_list = dep_search_list_non_adap + dep_search_list_adap

    return search_list, dep_search_list

def serviceLibraryList():
    import os.path, sys
    global search_me
    prefix = ''
    if sys.executable.endswith("srvchecker.exe"):
        prefix = os.path.dirname(sys.executable)
    global srv_list_path
    srv_list_path = os.path.join(prefix, "config/serviceCheckLibraryList.lst")
    if os.path.exists(srv_list_path):
        with open(srv_list_path, 'r') as serviceListFile:
            search_me = serviceListFile.readlines()
        return True
    else:
        return False

		
ipo={'ifl':[],
'IpoMap':{'srvx_':[],
          'srvf_':[],
          'ifx_':[]},
        'ipol':[],
        'IpoCur':[],
    'IpoFixCurve':[],
    'IpoFixMap':[],
    'ipo_remain':[]
}
lkup={'SrvX_LkUp':[],
'Ifx_IntLkUp':[],
'Ifx_LkUp':[]
}
no_pat={'no_specific_pattren':[]}
counter=0
boundary = br'\b'
import os.path, sys
prefix = ''
if sys.executable.endswith("srvchecker.exe"):
    prefix = os.path.dirname(sys.executable)
srv_list_path = os.path.join(prefix, "C:\srv_checker\src\config\serviceCheckLibraryList.lst")
with open(srv_list_path,'r') as f:
    for each in f.readlines():
        each=each.lower().strip()
        each_byte=boundary+each.encode('utf-8')+boundary
        if 'ipo' in each:
            if 'ifl' in each:
                # regex of Ipo[ipol]
                ipo['ifl'].append(each_byte)
                counter+=1
            elif 'ipomap' in each:
                #regex of Ipo[IpoMap]
                if 'srvx_' in each:
                    ipo['IpoMap']['srvx_'].append(each_byte)
                    counter += 1
                elif 'srvf_' in each:
                    ipo['IpoMap']['srvf_'].append(each_byte)
                    counter += 1
                elif 'ifx_' in each:
                    ipo['IpoMap']['ifx_'].append(each_byte)
                    counter += 1
                else:
                    print(each)
            elif 'ipol' in each:
                # regex of Ipo[ipol]
                ipo['ipol'].append(each_byte)
                counter += 1

            elif 'ipocur' in each:
                # regex of Ipo[ipol]
                ipo['IpoCur'].append(each_byte)
                counter += 1

            elif 'ipofixcurve'in each:
                # regex of Ipo[ipol]
                ipo['IpoFixCurve'].append(each_byte)
                counter += 1

            elif 'ipofixmap' in each:
                # regex of Ipo['IpoFixMap']
                ipo['IpoFixMap'].append(each_byte)
                counter += 1

            else:
                # Ipo_remain
                ipo['ipo_remain'].append(each_byte)
                counter += 1
        elif 'lkup' in each:
            if 'srvx_lkup' in each:
                # regex_of LkUp[Ifx_IntLkUp]
                lkup['SrvX_LkUp'].append(each_byte)
                counter += 1

            elif 'ifx_intlkup'in each:
                # regex_of LkUp[Ifx_IntLkUp]
                lkup['Ifx_IntLkUp'].append(each_byte)
                counter += 1

            elif 'ifx_lkup' in each:
                # regex_of LkUp[Ifx_LkUp]
                lkup['Ifx_LkUp'].append(each_byte)
                counter += 1
        else:
            no_pat['no_specific_pattren'].append(each_byte)
            counter += 1

import re
pt_ipo_ifl=re.compile(b'|'.join(ipo['ifl']))
# pt_ipo_imap=re.compile(b'|'.join(ipo['IpoMap']))
pt_ipo_m_sx=re.compile(b'|'.join(ipo['IpoMap']['srvx_']))
pt_ipo_m_sf=re.compile(b'|'.join(ipo['IpoMap']['srvf_']))
pt_ipo_m_ifx=re.compile(b'|'.join(ipo['IpoMap']['ifx_']))
pt_ipo_ipol=re.compile(b'|'.join(ipo['ipol']))
pt_ipo_ipcur=re.compile(b'|'.join(ipo['IpoCur']))
pt_ipo_ifixc=re.compile(b'|'.join(ipo['IpoFixCurve']))
pt_ipo_ifixm=re.compile(b'|'.join(ipo['IpoFixMap']))
pt_ipo_remain=re.compile(b'|'.join(ipo['ipo_remain']))
pt_lkup_srv=re.compile(b'|'.join(lkup['SrvX_LkUp']))
pt_lkup_ifx_int=re.compile(b'|'.join(lkup['Ifx_IntLkUp']))
pt_lkup_ifx=re.compile(b'|'.join(lkup['Ifx_LkUp']))
pt_no_pattren=re.compile(b'|'.join(no_pat['no_specific_pattren']))

def func_matcher(line):
    each=line.lower().strip()
    def srv_finder(pt_regx,each,counter):
        srv_func=[]
        for temp in pt_regx.finditer(each):
            srv_func.append((temp.group(0),temp.start(),temp.end()))
        if len(srv_func)>0:
            return srv_func

    if b'ipo' in each and  b'lkup' not in each:
        if b'ifl' in each:
             return srv_finder(pt_ipo_ifl,each,counter)
        elif b'ipomap' in each:
            if b'srvx_' in each:
                return srv_finder(pt_ipo_m_sx, each, counter)
            elif b'srvf_' in each:
                return srv_finder(pt_ipo_m_sf, each, counter)
            elif b'ifx_' in each:
                return srv_finder(pt_ipo_m_ifx, each, counter)
        elif b'ipol' in each:
            return srv_finder(pt_ipo_ipol, each, counter)
        elif b'ipocur' in each:
            return srv_finder(pt_ipo_ipcur, each, counter)
        elif b'ipofixcurve'in each:
            return srv_finder(pt_ipo_ifixc, each, counter)
        elif b'ipofixmap' in each:
            return srv_finder(pt_ipo_ifixm, each, counter)
        else:
            return srv_finder(pt_ipo_remain, each, counter)

    if b'lkup' in each:
        if b'srvx_lkup' in each:
            return srv_finder(pt_lkup_srv, each, counter)
        elif b'ifx_intlkup'in each:
            return srv_finder(pt_lkup_ifx_int, each, counter)
        elif b'ifx_lkup' in each:
            return srv_finder(pt_lkup_ifx, each, counter)
    if True:
        return srv_finder(pt_no_pattren, each, counter)

