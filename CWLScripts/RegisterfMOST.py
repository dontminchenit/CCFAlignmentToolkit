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
from CCFAlignmentToolkit.RegisterfMOSTtoCCF import RegisterfMOSTtoCCF
import sys
import logging

iDir = os.getenv("INPUT_DIR")
oDir = os.getenv("OUTPUT_DIR")

fMOSTFile = os.path.join(iDir, sys.argv[1])
fMOSTtoCCFAtlasDir = os.path.join(iDir, sys.argv[2])

print(fMOSTFile)
#Register Images 
RegisterfMOSTtoCCF(fMOSTFile,fMOSTtoCCFAtlasDir,oDir,sys.argv[3])
    
    



