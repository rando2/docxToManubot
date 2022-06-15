#!/bin/bash

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

# Where is the docx with the track changes saved?
docx=./diagnostics-manuscript\(1\).docx

# Who is the author of the docx edits?
# Please put this in the format of git --author, i.e. 'Name <email>
docxEditAuthor='Halie Rando <halie.rando@cuanschutz.edu>'

#********************************************
# OPTIONAL VARIABLES (leave as is or change if you prefer)
tempUpstreamMD=originalMD.md
tempDocxMD=docxMD.md
docxMetadataDir=file-content
editedMarkdown=./$origMD
new_branch=docx_$(date +"%s")

# RETRIEVE MARKDOWN FROM UPSTREAM
# Convert docx to md & retrieve markdown file from upstream based on the commit info in docx
# If you have edited the front matter from rootstock, you should confirm that the
# syntax used to detect the permalink (which contains the commit info used to generate the docx)
# is the same in your manuscript
echo pandoc -s $docx -t markdown --wrap=none -o $tempDocxMD
python retrieveMD.py $repository $origMD $tempDocxMD $tempUpstreamMD

# COMPARE DOCX TO UPSTREAM
# Extract XML from docx into working directory
# Compare docx to upstream, store edited markdown, and remove extracted metadata
unzip $docx -d ./$docxMetadataDir
python xmlparser.py $origMD $docxMetadataDir $tempDocxMD

# COMMIT CHANGES FROM DOCX
# go to the local manubot project directory, make a new branch, add changes there
wd=$(pwd)
cd $localProjectDir
git checkout -b $new_branch
mv $wd/$editedMarkdown ./content/$origMD

# Commit changes and instruct user to push
git add $localProjectDir/content/$origMD
git commit --author="$docxEditAuthor" -m "suggestions from docx, generated automatically from track changes with docx-to-manubot"
echo To push: git push upstream $new_branch

# CLEAN UP TEMP
rm -rf $docxMetadataDir
rm $tempUpstreamMD $tempDocxMD

# Future functions: edit other markdown/HTML syntax and transfer comments from docx to PR (in-line
# is probably easiest)

# Clean original md
#echo pandoc -s $origMD -t markdown --wrap=preserve -o origmdMD.md
