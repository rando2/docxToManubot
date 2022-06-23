tempUpstreamMD=originalMD.md
tempDocxMD=docx-to-manubot-tmp/docxMD.md
docx=./diagnostics-manuscript\(1\).docx
tempUpstreamMD=originalMD.md

# docx-TC to markdown
#pandoc -s acceptAll.docx -t markdown --wrap=none -o $tempDocxMD
#python minimalproc.py $tempDocxMD

# docx-Orig to markdown
#pandoc -s base.docx -t markdown --wrap=none -o baseDocx.md
#python minimalproc.py baseDocx.md

#diff -c baseDocx.md $tempDocxMD > docx-to-manubot-tmp/diff.txt

#python retrieveMD.py $repository $origMD $tempDocxMD $tempUpstreamMD

python diff.py $tempUpstreamMD docx-to-manubot-tmp/diff.txt
