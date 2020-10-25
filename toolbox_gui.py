import sys
from tkinter import Tk, Button, filedialog, messagebox
from audacity import get_label_tracks, save_label_track, get_tracks, init_pipe
from pathlib import Path

root = Tk()
root.title("Audacity Toolbox")
if sys.platform == 'win32':
    root.attributes('-toolwindow', True)
root.minsize(150, 32)
# root.overrideredirect(1)
# root.resizable(0,0)
root.attributes('-topmost', True)

def btn_save_labels():
    folder = filedialog.askdirectory()
    if not folder:
        return
    track_info = get_tracks()
    for i, l in enumerate(get_label_tracks()):
        trackname = track_info[l['index']]['name']
        if trackname[:2].isdigit() and trackname[2] == '_':
            trackname = trackname[3:]  # trim 01_ at the beginning
        filename = "%02d_%s.txt" % (i + 1, trackname)
        save_label_track(Path(folder) / filename, l['labels'])

B = Button(root, text="Save labels...", command=btn_save_labels)
B.pack()

try:
    init_pipe()
except EnvironmentError:
    messagebox.showinfo(message="Ensure Audacity is running and mod-script-pipe is active.")
    exit(0)

root.mainloop()
