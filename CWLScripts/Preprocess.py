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
from CCFAlignmentToolkit.PreProcessfMOST import PreProcessfMOST

import sys
import logging

iDir = os.getenv("INPUT_DIR")
oDir = os.getenv("OUTPUT_DIR")

fMOSTFile = os.path.join(iDir, sys.argv[1])

#Preprocess
fMOSTFile_Preprocessed=PreProcessfMOST(fMOSTFile,oDir)
    



