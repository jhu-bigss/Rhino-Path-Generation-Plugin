# GRBL controller dialog

from __future__ import absolute_import
from __future__ import print_function

__version__ = "0.1.10-dev"
__date__    = "1 Aug 2019"
__author__  = "Joshua Liu"
__email__   = "liushuya7@gmail.com"

import rhinoscriptsyntax as rs
import Rhino.UI
import Eto.Drawing as drawing
import Eto.Forms as forms

import os
import sys
import getopt

try:
	import serial
except:
	serial = None

PRGPATH=os.path.abspath(os.path.dirname(__file__))
sys.path.append(PRGPATH)
sys.path.append(os.path.join(PRGPATH, 'lib'))
sys.path.append(os.path.join(PRGPATH, 'controller'))

import gettext
_ = gettext.gettext

from Sender import Sender, NOT_CONNECTED, STATECOLOR, STATECOLORDEF

_openserial = True	# override ini parameters
_device     = None
_baud       = None

MONITOR_AFTER =  200	# ms
DRAW_AFTER    =  300	# ms

RX_BUFFER_SIZE = 128

MAX_HISTORY  = 500

#ZERO = ["G28", "G30", "G92"]

FILETYPES = [	(_("All accepted"), ("*.ngc","*.cnc","*.nc", "*.tap", "*.gcode", "*.dxf", "*.probe", "*.orient", "*.stl", "*.svg")),
		(_("G-Code"),("*.ngc","*.cnc","*.nc", "*.tap", "*.gcode")),
		(_("G-Code clean"),("*.txt")),
		("DXF",       "*.dxf"),
		("SVG",       "*.svg"),
		(_("Probe"),  ("*.probe", "*.xyz")),
		(_("Orient"), "*.orient"),
		("STL",       "*.stl"),
		(_("All"),    "*")]

geometry = None

#==============================================================================
# Main Application Dialog
#==============================================================================
class GrblDialog(forms.Dialog[bool],Sender):

    def __init__(self):
        Sender.__init__(self)
        
        self.Title = "GRBL GUI"
        self.Resizable = False
        self.Padding = drawing.Padding(5)
        
        
        
        
        
        
        

def main():
    
    
    # Parse arguments
    try:
        optlist, args = getopt.getopt(sys.argv[1:],
            '?b:dDfhi:g:rlpPSs:',
            ['help', 'ini=', 'fullscreen', 'recent', 'list','pendant=','serial=','baud=','run'])
    except getopt.GetoptError:
        usage(1)

    dialog = GrblDialog()
    dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)

if __name__ == "__main__":
    main()