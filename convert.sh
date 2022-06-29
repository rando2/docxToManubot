#!/bin/bash

# INPUTS (USER MUST DEFINE)

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

# Sections to skip, other than front and back matter
# Change to simply check if this file exists, add to readme
toSkip=sectionsToSkip.txt

#********************************************
# OPTIONAL VARIABLES (leave as is or change if you prefer)
new_branch=docx_$(date +"%s")
tmp=tmp

#********************************************
# Workflow Assumptions:
# 1. The paper's body starts with an Abstract
# 2. Rootstock front matter text describing permalink has been kept (see "# RETRIEVE MARKDOWN FROM UPSTREAM")
# 3. Currently, set up for manuscripts built from single markdown files
# 4. If sections besides front matter and back matter should be skipped, specify names in sectionsToSkip.txt
#********************************************
# SET UP WORKSPACE
mkdir -p $tmp

# CREATE MARKDOWN FROM WORD
#pandoc -s $docx -t markdown --wrap=none --reference-links --track-changes=all --markdown-headings=atx -o $tmp/docxAll.md
#pandoc -s $docx -t markdown --wrap=none --reference-links --track-changes=reject --markdown-headings=atx -o $tmp/docxNone.md

# Diff and identify differences
#wdiff $tmp/docxNone.md $tmp/docxAll.md > $tmp/diff.txt
#python 01.cropDiff.py $toSkip $tmp/diff.txt $tmp/textblocks.txt
#python 02.IDChanges.py $tmp/textblocks.txt $tmp/textIndices.txt

# RETRIEVE MARKDOWN FROM UPSTREAM
# Uses commit info in docx to retrieve appropriate head
#python 03.retrieveMD.py $origMD $tmp/docxNone.md $tmp/upstream.md

# APPLY CHANGES TO HEAD
python recompare.py $tmp/upstream.md $tmp/textblocks.txt $tmp/textIndices.txt $tmp/matchedText.txt
#python 03.compareText.py $tempUpstreamMD
#python 04.writeMarkdown.py $tempUpstreamMD $tempDocxMD
exit
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
