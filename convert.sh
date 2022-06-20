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
new_branch=docx_$(date +"%s")
end_of_body_signifier="Additional Items"

#********************************************
# Workflow Assumptions:
# 1. The paper's body starts with an Abstract
# 2. Rootstock front matter text describing permalink has been kept (see "# RETRIEVE MARKDOWN FROM UPSTREAM")
# 3. Rootstock is in English
# 4. The manuscript body ends when the references begin, which are named "References"
#********************************************
# CODE IS BELOW

tempUpstreamMD=originalMD.md
tempDocxMD=docx-to-manubot-tmp/docxMD.md
docxMetadataDir=file-content
editedMarkdown=$origMD

# SET UP WORKSPACE
mkdir -p docx-to-manubot-tmp

# RETRIEVE MARKDOWN FROM UPSTREAM
# Convert docx to md & retrieve markdown file from upstream based on the commit info in docx
# I was unable to extract the hyperlink info from the docx, which is why there is the extra
# step of converting to markdown. If you have edited the front matter from rootstock, you
# should confirm that the syntax used to detect the permalink (which contains the commit
# info used to generate the docx) is the same in your manuscript
#pandoc -s $docx -t markdown --wrap=none -o $tempDocxMD
#python retrieveMD.py $repository $origMD $tempDocxMD $tempUpstreamMD

# PREPARE DOCX FOR COMPARISON BY UNZIPPING DOCX TO XML, THEN PARSE XML
#unzip $docx -d ./docx-to-manubot-tmp/file-content
python 01.xmlparser.py ./docx-to-manubot-tmp/file-content "$end_of_body_signifier"
python 02.IDChanges.py
python compare.py $tempUpstreamMD $tempDocxMD

# COMPARE DOCX TO UPSTREAM
# Compare docx to upstream, store edited markdown, and remove extracted metadata
#python $tempUpstreamMD

exit
# CHECK THAT THE PRECEEDING STEP WORKED
if ! test $tempDocxMD
then
  echo Failed to convert docx file to markdown
  exit
fi

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
#rm $tempUpstreamMD $tempDocxMD

# Future functions: edit other markdown/HTML syntax and transfer comments from docx to PR (in-line
# is probably easiest)

# Clean original md
#echo pandoc -s $origMD -t markdown --wrap=preserve -o origmdMD.md
