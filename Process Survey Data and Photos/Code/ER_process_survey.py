import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import sys

codes = "BB,BED,BEN,BG,BIN,BL,BOL,BSHE,BSIG,BUS,BUSB,BUSH,CC,CE,CLID,CMK,COL,COMB,CR,DD,DK,DLID,DP,DR,DU,EARR,EARS," \
        "EB,EC,ED,EF,EG,ELID,EM,EMK,EP,ES,ET,EV,EW,EXTA,EXTM,F,FEAT,FFL,FH,FL,G,GA,GC,GL,GLID,GM,GMK,GS,GUY,GV,ILID," \
        "INV,IP,JT,KB,KC,KO,KT,LID,LIDC,LIDD,LIDE,LIDG,LIDI,LIDL,LIDS,LIDT,LIDW,LINE,LP,LW,LWD,LY,LYD,MBX,MH,MHL,MON," \
        "NOTE,OHC,PBX,PHBX,POLE,POST,POT,POTSH,PP,PSM,PY,RAMP,RW,RWP,SEP,SH,SIGN,SLID,SM,SN,SOF,SPRK,ST,STOB,SV,TANK," \
        "TAP,TB,TBX,TDL,TLID,TMK,TP,TPIL,TRAF,TREE,TS,TWL,UMK,UV,VB,VCOA,VCOB,VCOC,VCOD,VCOZ,VEAA,VEAB,VEAC,VEAD," \
        "VEAZ,VEEA,VEEB,VEEC,VEED,VEEZ,VELA,VELB,VELC,VELD,VELZ,VENT,VFSA,VFSB,VFSC,VFSD,VFSZ,VGAA,VGAB,VGAC,VGAD," \
        "VGAZ,VHVA,VHVB,VHVC,VHVD,VHVZ,VOFA,VOFB,VOFC,VOFD,VOFZ,VOIA,VOIB,VOIC,VOID,VOIZ,VOPA,VOPB,VOPC,VOPD,VOPZ," \
        "VOTA,VOTB,VOTC,VOTD,VOTZ,VRWA,VRWB,VRWC,VRWD,VRWZ,VSEA,VSEB,VSEC,VSED,VSEZ,VSSA,VSSB,VSSC,VSSD,VSSZ,VSTA," \
        "VSTB,VSTC,VSTD,VSTZ,VTEA,VTEB,VTEC,VTED,VTEZ,VTSA,VTSB,VTSC,VTSD,VTSZ,VTTA,VTTB,VTTC,VTTD,VTTZ,VUNA,VUNB," \
        "VUNC,VUND,VUNZ,VWAA,VWAB,VWAC,VWAD,VWAZ,WALL,WB,WH,WL,WLID,WLV,WM,WMK,WT,WV,B,CONTINUE,E,C,H,V,SO," \
        "CIR".split(",")

survey_codes = ["CHK", "RES", "STN", "TEMP", "Free"]

raw_data = []
potsh = {}
pot = []
photo_root_path = ""
photo_output_path = ""

# unique numberings for points, overflow notes and survey point numbers
point_num = 1
note_num = 90000
survey_num = 100000

app_window = tk.Tk()
app_window.withdraw()
ftypes = [('CSV', '.csv')]

# get input files from user
file_open = filedialog.askopenfilenames(filetypes=ftypes, title='Please select files for automatic processing')

# if no files selected, warn user and abort script
if not file_open:
    messagebox.showerror('No file selected', 'No input file was detected. \nPlease check the file is valid. '
                                             '\nScript aborting')
    sys.exit()

# sort input files into order to ensure lowest to highest processing order
sorted(file_open)

# check if any photos to be renamed
if messagebox.askyesno("Pothole Photos", "Are there any pothole photos to be renamed?"):
    photo_root_path = filedialog.askdirectory(initialdir=os.path.abspath(file_open[0]),
                                              title="Select root folder for photo filepaths")
    photo_output_path = filedialog.askdirectory(initialdir=os.path.abspath(file_open[0]),
                                                title="Select folder for renamed photos")

# loop through each input file
for f in file_open:

    data = []
    survey = []
    extra_notes = []

    e_pot_dup = []  # error duplicate pothole ID's (PHID, PointID)
    e_potsh_dup = []  # error of duplicate potsh ID's (PHID, PointID)
    e_pot_nosh = []  # potholes with no corresponding POTSH (PHID, PointID)
    e_invalid_note = []  # points with notes that shouldn't have notes (PointID, Code, Note)
    e_invalid_code = []  # points with invalid survey code (PointID, Code)
    e_photo_missing = []  # missing pothole photo files (PHID, PointID, Photo A/B, File name)

    # output data file for input data file, numbered one higher than input file
    out_file_num = int(f[-6:-4]) + 1
    out_file_num = "0" + str(out_file_num) if out_file_num < 10 else str(out_file_num)
    out_file = open(f[:-6] + out_file_num + ".csv", 'w')

    with open(f) as in_data:

        # loop through each line of input data
        for line in in_data:

            # if row of data is duplicate
            if line in raw_data:
                continue
            else:
                raw_data.append(line)

            # strip off the trailing newline and separate the csv data
            d = line.replace('\n', '').split(',')

            # if row of data has less than 5 cells (ie, only PENZ or less) then ignore the info
            if len(d) < 5:
                continue

            # extract the code field
            c = d[4]

            # separate out the survey data
            if c.startswith("SM") or c.startswith("PSM") or (c in survey_codes):
                survey.append(d)

            # otherwise if its normal data, separate out the pothole SH info (potsh)
            # and append row data to normal dataset
            else:
                if c == "POTSH":
                    if d[6] in potsh:
                        e_potsh_dup.append([d[6], d[0]])
                    else:
                        potsh[d[6]] = d[3]

                data.append(d)

        # loop through input data rows, test for errors and output
        for i in data:

            if len(i) > 5 and i[5].startswith("Modified"):
                i = i[:5]

            # if point ID has text in it (ie, is not a number), skip row of data
            if not i[0].isdigit():
                continue

            # setup point number. if the original point number (i[0]) is lower than the current available number,
            # change current point to new number but keep record of old / original number
            pnum = i[0]
            if int(i[0]) < point_num:
                pnum = str(point_num)
                point_num += 1
            else:
                point_num = int(i[0]) + 1

            # check for valid point codes
            invalid_code = False
            for j in i[4].split():
                if j.strip("0123456789") not in codes:
                    invalid_code = True
            if invalid_code:
                e_invalid_code.append([i[0], i[4]])

            # check for codes assigned notes that shouldnt have notes
            if len(i) > 5 and len(i[5]) > 0 and not ((i[4].startswith(("LID", "V", "CC"))) or (i[4] in ["POT", "POTSH", "NOTE"])):
                e_invalid_note.append([i[0], i[4], i[5]])
                extra_notes.append([str(note_num), i[1], i[2], i[3], "NOTE", i[5], i[0]])
                note_num += 1

            # write non-pothole points to file
            out_data = ""
            if not (i[4] in ["POT", "POTSH"]):
                temp_note = i[5] if len(i) > 5 else ""

                out_data = [pnum, i[1], i[2], i[3], i[4], temp_note, i[0]]

            # write pothole surface points to file
            elif i[4] == "POTSH":
                out_data = [pnum, i[1], i[2], i[3], i[4], i[6], i[0]]

            # write pothole data points to file
            elif i[4] == "POT":
                # check if pothole ID is unique
                if i[6] in pot:
                    e_pot_dup.append([i[6], i[0]])
                else:
                    pot.append(i[6])

                # capture POTSH for POT
                elev_surface = float(i[3]) + float(i[18])
                elev_qla = float(i[3])

                if i[6] not in potsh:
                    e_pot_nosh.append([i[6], i[0]])
                else:
                    elev_surface = float(potsh[i[6]])

                # Check for "unknown" sui type (trims the 'Unknown/other (add note etc)"
                if i[12].startswith("Unknown"):
                    i[12] = "Unknown"

                # setup QA values for POT
                depth_taped = round(float(i[18]), 2)
                depth_survey = round(elev_surface, 2) - float(i[3])
                depth_diff = abs(depth_survey - depth_taped)
                depth_check = "OK" if depth_diff <= 0.05 else "CHECK"

                out_data = [pnum, i[1], i[2], i[3], i[4], i[6], i[0], str(elev_surface), i[8], i[12], i[14], i[16],
                            i[22], i[24], i[26], str(depth_taped), str(depth_survey), str(depth_diff), depth_check,
                            i[20]]

                # re-naming photos if confirmed at start of script
                # setup full path for both photos by combining hte photo root path and the image path from file
                # check if file exists
                # if so, copy and rename to output location, replacing dots with dashes in pothole ID
                # if not, add to error list as missing the photo file
                if len(photo_root_path) > 0:
                    photos = [["A", i[24]], ["B", i[26]]]

                    for p in photos:
                        if os.path.isfile(photo_root_path + "/" + p[1]):
                            shutil.copyfile(photo_root_path + "/" + p[1], photo_output_path +
                                            f'\QLA_PH{i[6].replace(".","-")}{p[0]}.jpg')
                        else:
                            e_photo_missing.append([i[6], i[0], p[0], p[1]])

            out_file.write(",".join(out_data) + "\n")

        # write extra notes to file:
        for i in extra_notes:
            out_file.write(",".join(i) + "\n")

        # write survey data to file:
        for i in survey:
            if i[4].startswith("SM") or i[4].startswith("PSM"):
                out_data = [str(survey_num), i[1], i[2], i[3], i[4], i[0]]
                out_file.write(",".join(out_data) + "\n")
                survey_num += 1

        out_file.close()

    # if any errors, write error messages to separate file
    if len(e_pot_nosh + e_potsh_dup + e_pot_dup + e_invalid_note + e_invalid_code + e_photo_missing) > 0:
        error_file = open(f[:-6] + out_file_num + "_errors.csv", 'w')

        # write duplicate pothole ID's
        if len(e_pot_dup) > 0:
            error_file.write("The following potholes have duplicate ID's\n")
            error_file.write("Pothole ID, Point Number\n")
            for i in e_pot_dup:
                error_file.write(",".join(i) + "\n")
            error_file.write("\n")

        # write duplicate potsh ID's
        if len(e_potsh_dup) > 0:
            error_file.write("The following potsh have duplicate ID's\n")
            error_file.write("Pothole ID, Point Number\n")
            for i in e_potsh_dup:
                error_file.write(",".join(i) + "\n")
            error_file.write("\n")

        # write potholes missing potsh
        if len(e_pot_nosh) > 0:
            error_file.write("The following potholes are missing potsh\n")
            error_file.write("Pothole ID, Point Number\n")
            for i in e_pot_nosh:
                error_file.write(",".join(i) + "\n")
            error_file.write("\n")

        # write invalid notes
        if len(e_invalid_note) > 0:
            error_file.write("The following points have a note but the Code does not bring the note into CAD\n")
            error_file.write("Point Number, Code, Note\n")
            for i in e_invalid_note:
                error_file.write(",".join(i) + "\n")
            error_file.write("\n")

        # write invalid codes
        if len(e_invalid_code) > 0:
            error_file.write("The following points have an invalid Code\n")
            error_file.write("Point Number, Code\n")
            for i in e_invalid_code:
                error_file.write(",".join(i) + "\n")
            error_file.write("\n")

        # write missing photos
        if len(e_photo_missing) > 0:
            error_file.write("The following potholes have missing photo files\n")
            error_file.write("Pothole ID, Point Number, Photo A\B, Missing file path\n")
            for i in e_pot_dup:
                error_file.write(",".join(i) + "\n")
            error_file.write("\n")

        error_file.close()
