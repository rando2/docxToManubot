#!/bin/bash

# Inputs
origMD="/Users/halierando/Dropbox/UPenn/COVID-19/covid19-review/content/10.diagnostics.md"
docx="./diagnostics-manuscript\(1\).docx"

# A specific fork of python-docx is needed. See https://github.com/python-openxml/python-docx/pull/734
pip install git+https://github.com/jfthuong/python-docx.git#egg=python-docx

# Checkout new branch

#git checkout master
#git checkout -b "docx-pr"

# Generate XML? May not need, unless implement comments
unzip $docx -d file-content

# Clean original md
#echo pandoc -s $origMD -t markdown --wrap=preserve -o origmdMD.md

# Convert docx to md
#echo pandoc -s $docx -t markdown --wrap=none -o docxMD.md

# Python script to reformat
# To Do: add comments inline

#python convertdocx.py

# Diff original and track changes
#diff -c  diagnostics-manuscript-track.md trackchanges.md


#rm origmdMD.md docxMD.md 
