import win32com.client
import datetime as dt
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os
import sys

app_window = tk.Tk()
app_window.withdraw()

senders_count = 1
senders = {}
if os.path.isfile("DBYD_asset_owners.csv"):
    with open("DBYD_asset_owners.csv") as f:
        for l in f:
            email_add, company = l.strip().split(",")
            senders[email_add] = company
else:
    messagebox.showerror("No Asset Owner List", "The .CSV file with the list of common DBYD asset owners could not be "
                                                "found.\n Please ensure the DBYD_asset_owners.csv file is in the same "
                                                "folder as this executable file.")


# ask for input DBYD search number
DBYD = simpledialog.askinteger("DBYD Request Number", "Please enter the DBYD Job No.", minvalue=0)
if not DBYD:
    messagebox.showerror('No DBYD Request number', 'No DBYD request number was entered.\nScript aborting')
    sys.exit()
DBYD = str(DBYD)

# ask for output folder
save_path = filedialog.askdirectory(title="Select folder to save DBYD files")

if not save_path:
    messagebox.showerror('No save location', 'No folder location was entered to store DBYD plans.\nScript aborting')
    sys.exit()


outlook = win32com.client.Dispatch("Outlook.Application").GetNameSpace("MAPI")

lastmonth = (dt.datetime.now() - dt.timedelta(days=28)).strftime('%d/%m/%Y %H:%M %p')
inbox = outlook.GetDefaultFolder(6)

messages = inbox.Items

messages = messages.Restrict(f"[ReceivedTime] >= '{lastmonth}'")
DBYD_msg = []

files_saved = False
asset_own_count = 1

# loop through each message, check if DBYD number in email title
j=0
for message in messages:
    j += 1
    if not ((DBYD in message.Subject) or (DBYD in message.Body)):
        continue

    attachs = message.Attachments
    sender = message.SenderEmailAddress.split("@")[1]

    asset_own = ""
    if sender in senders:
        asset_own = senders[sender]
    else:
        asset_own = "ASSET_OWNER_" + str(asset_own_count)
        asset_own_count += 1

    for i in attachs:
        files_saved = True
        i.SaveAsFile(save_path + "/" + asset_own + "_" + i.FileName)
    DBYD_msg.append(j)

DBYD_msg.sort(reverse=True)

if messagebox.askyesno("Delete emails", "Would you like the emails deleted from the inbox"):
    for k in DBYD_msg:
        messages.Item(k).Delete()

if not files_saved:
    messagebox.showerror('No DBYD Files Found', 'No DBYD Files found amongst the emails.\nScript Finished')
