# INPUTS (USER MUST DEFINE)

# Where is the repository for this manubot project located on github?
# Example: greenelab/covid19-review
repository=greenelab/covid19-review

# Where is your local git repo associated with the manubot project?
# Example: /Users/mycomputer/manubot/covid19-review
localProjectDir=/Users/halierando/Dropbox/UPenn/COVID-19/covid19-review

# What is the name of the file in Manubot's content directory that this docx was built from?
# Example: 10.diagnostics.md
origMD=10.diagnostics.md

############################################################
# docx-TC to markdown
#pandoc -s acceptAll.docx -t markdown -o docxMD.md
#python minimalproc.py docxMD.md

# docx-Orig to markdown
#pandoc -s base.docx -t markdown -o baseDocx.md
#python minimalproc.py baseDocx.md

wdiff baseDocx.md docxMD.md > diff.txt

#python retrieveMD.py $repository $origMD $tempDocxMD originalMD.md

#python diff.py originalMD.md diff.txt
