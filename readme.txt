The following scripts have been written to aid in automating the processing and CAD workflow for Earth Radar / VAC Group. 
The scripts have been written in python and converted from .py to .exe using pyinstaller and are designed to run on Windows OS - setup so that the end user does not need python installed to run the script. 

CAD Sheet layout:
This script has been written to automate generation of CAD layouts, including renumbering the sheet name and setup of a grid in the viewport. 

DBYD Email sorter:
This script will ask for a DBYD (dial before you dig) request number and ask for an output folder, then search through the user's outlook email inbox. Any emails found from the relevant DBYD request will have the attachments copied to the specified folder and renamed to include the sender company ID.

PH Photo renamer:
The Trimble survey controllers can capture photos but the output is a generic incrementing file name (eg, img278.jpg, img279.jpg). When survey data is downloaded from the Trimble controller, this script will identify pothole numbers from the survey information and rename the images to a more useful filename that includes the pothole details. 

Process Survey data and Photos:
When survey data is downloaded from the Trimble survey controllers the raw data requires checking and processing before import into CAD. This script performs multiple checks on the data, including checking for:
- invalid survey codes
- survey codes with notes that will not have the note appear in CAD
- pothole surveyed depth (surface height - pothole depth height) is within tolerance of the tape measured depth of the pothole

