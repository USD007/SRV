# About Dialog Box

# Importing of necessary function
from __future__ import print_function
from general import TOOLNAME
from version import VERSION
import win_console

TITLE_TEXT = TOOLNAME + 'v' + VERSION
ABOUT_PIC = ""
ABOUT_TEXT = """
Source scanner for service routines, checking usage of axispoints reduction by parsing A2L and HEX

LICENSE INFORMATION:
--------------------
srvchecker BOSCH license

For any questions please contact : 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tool-Hotline ICEDCGMCOP RBEI/ETB (CAP-SST/ESS1) 
ICEDCGMCOP.Tool-Hotline@de.bosch.com


This software is property of Robert Bosch Engineering and Business Solutions Private Limited. All rights reserved.
This software must be made accessible only within BOSCH or subsidiaries of BOSCH. 
The disclosure of open source software components shall not be effected by the foregoing provision.
The software may not be distributed to third parties and no sub-license or other grant of rights to use the software shall be made without RBEI's consent.
Any use of the software by third parties will require a separate agreement between RBEI and the third party.
The use of the software does not replace appropriate verification of the results.
The use of srvchecker will be on your own risk! 

*Following open source software components used to create this product:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pip 9.0.1 (https://pip.pypa.io/, MIT)
  Copyright (c) 2008-2016 The pip developers

*This product contains the following open source software components:
intelhex 2.2.1 (https://pypi.org/project/IntelHex/, BSD 3c)
  Copyright (C) Alexander Belchenko, 2005-2018
  Path to license: intelhex-2.2.1\LICENSE.txt

lxml 3.7.3 (https://pypi.python.org/pypi/lxml/3.7.3, BSD 3c, ZPL 2.0, elementtree)
  lxml/ElemenTree - Copyright (c) 1999-2003 by Secret Labs AB
  lxml/ElemenTree - Copyright (c) 1999-2003 by Fredrik Lundh
  lxml - Copyright (c) 2004 Infrae. All rights reserved.
  lxml.cssselect and lxml.html copyright by Ian Bicking
  Path to license: lxml-3.7.3\LICENSES.txt

psutil 5.4.7 (https://pypi.python.org/pypi?:action=display&name=psutil#downloads, BSD 3c)
  Copyright (c) 2009, Jay Loden, Dave Daeschler, Giampaolo Rodola
  Path to license: psutil-5.4.7\LICENSE

pycrypto 2.6.1 (https://pypi.python.org/pypi/pycrypto/, Public Domain LibTom, PSF 2.2)
  Path to license: pycrypto-2.6.1/COPYRIGHT

pyinstaller 3.3.0 (https://pypi.python.org/pypi/PyInstaller/3.3, PyInstaller_Bootloader)
  Copyright (c) 2010-2017, PyInstaller Development Team
  Copyright (c) 2005-2009, Giovanni Bajo
  Based on previous work under copyright (c) 2002 McMillan Enterprises, Inc.
  Path to license: PyInstaller-3.3\COPYING.txt

Python 3.6.1 (https://www.python.org/downloads/, PSF 2.3)

scandir 1.5 (https://github.com/benhoyt/scandir, BSD 3c)
  Copyright (c) 2012, Ben Hoyt
  Path to license: scandir-1.5\LICENSE.txt

"""


# ------------------------------------------------------------------------------
# Read a File
# ------------------------------------------------------------------------------
def print_about():
    """
    Usage   : Open the About Window Dialog Box

    Syntax  : print_about()

    Example : print_about()

    """
    try:
        title = TITLE_TEXT
        win_console.print_console_text(title)
        win_console.print_console_text(ABOUT_TEXT, start_cnt=len(ABOUT_PIC.splitlines()) + len(title.splitlines()))
    except:
        print(ABOUT_TEXT)
# ------------------------------------------------------------------------------
