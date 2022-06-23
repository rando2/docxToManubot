# Move Track Changes from DOCX to Manubot Markdown

This is preliminary code to extract track changes from a docx file and overlay them on a markdown file as part of the Manubot workflow.
The workflow is run from the file `convert.sh`.
The main operations are carried out in the five python scripts in the home directory.

Code from an additional strategy that was attempted is located in the subfolder `diff-based-approach`, but this did not seem to bypass any of the most challenging elements of the original approach.
