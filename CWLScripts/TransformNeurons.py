##################################################################
#
# In order to install ANTsPy, go to https://github.com/ANTsX/ANTsPy and
# we recommend building from scratch, i.e.,
#
#  $ git clone https://github.com/ANTsX/ANTsPy
#  $ cd ANTsPy
#  $ python3 setup.py install
#
#Alternatively you can try a pre-comipled binary available for MacOS/Linux:
#
#   #pip install antspyx
#

import ants
from glob import glob
from pathlib import Path
import os
from CCFAlignmentToolkit.ApplyTransformToSWC import ApplyTransformToSWC
import sys
import logging

iDir = os.getenv("INPUT_DIR")
oDir = os.getenv("OUTPUT_DIR")


SWCFile = os.path.join(iDir, sys.argv[1])
fMOSTFile = os.path.join(iDir, sys.argv[2])
OrientFile = os.path.join(iDir, sys.argv[3])
RegOutDir = os.path.join(iDir, sys.argv[4])
fMOSTtoCCFAtlasDir = os.path.join(iDir, sys.argv[5])
#TransformOutDir = os.path.join(oDir, sys.argv[6])
ApplyTransformToSWC(SWCFile, fMOSTFile,OrientImgFiles[0], RegOutDir, fMOSTtoCCFAtlasDir, oDir)



