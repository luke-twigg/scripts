import tkinter as tk
import sys
from tkinter import filedialog, simpledialog, messagebox

app_window = tk.Tk()
app_window.withdraw()
ftypes = [('CSV', '.csv')]
file_open = filedialog.askopenfilename(filetypes = ftypes, title = 'Please select .csv file with bottom left X/Y coordinages for each autocad layout')

if not file_open:
    messagebox.showerror('No file selected', 'No input coordinate file was detected. \nScript aborting')
    sys.exit()

grid_size = simpledialog.askfloat("Grid size", "Specify grid size in metres\nTypically 10 for 1:100, 20 for 1:200")
if not grid_size:
    messagebox.showerror('No grid size specified', 'No Grid Size specified. \nScript aborting')
    sys.exit()
if grid_size <= 0:
    messagebox.showerror('Grid size error', 'Grid Size must be greater than zero. \nScript aborting')
    sys.exit()

start_num = simpledialog.askinteger("First layout drawing number", 'Specify the first layout drawing number\neg. 1, 16, etc (no leading zero)')
if not start_num:
    messagebox.showerror('No starting layout', 'No starting layout / drawing number specified. \nScript aborting')
    sys.exit()
if start_num <= 0:
    messagebox.showerror('Starting layout invalid', 'Starting layout / drawing number must be positive. \nScript aborting')
    sys.exit()

coords = []
layouts = []


with open(file_open) as f:
    for line in f:
        coords.append(line.rstrip('\n\r'))

l = len(coords)

for i in range(l):
    x = start_num + i
    if x < 10:
        x = "0"+str(x)
    else:
        x = str(x)
    layouts.append(x)


outfile = open(file_open[:-4]+'.scr', 'w')
for i in range(l-1):
    outfile.write(f'layout\nc\n{layouts[i]}\n{layouts[i+1]}\n')

for i in range(l):
    outfile.write(f'layout\ns\n{layouts[i]}\nmspace\nalignspace\n{coords[i]}\n\n368.268,164.060\n\n')
    outfile.write(f'pspace\nvpgrid\n368.268,164.060\n{grid_size}\n')
    outfile.write(f'-layer\nr\n_GRID_TEXT\n"_GRID_TEXT {layouts[i]}"\n\n')
    outfile.write(f'mspace\nvplayer\nV\n"_GRID_TEXT {layouts[i]}"\nF\nF\n"_GRID_TEXT {layouts[i]}"\nX\n\npspace\n')

outfile.close()

messagebox.showwarning("Check CAD file setup","CAD Script created at same location as input coordinate file. \n\nRemember to check the following in CAD before running:\n1. VPGRID v02.lsp file loaded (VPGRID command)\n2. all '_GRID_TEXT' layers removed\n3. Ensure the viewport in the first layout is on / visible")
