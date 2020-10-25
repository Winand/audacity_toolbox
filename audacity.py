"""
Audacity communication module. Call init_pipe() beforehand.
Based on https://github.com/audacity/audacity/blob/master/scripts/piped-work/pipe_test.py
"""

import os
import sys
import json
import csv

STATUS_LABEL = "BatchCommand finished:"
TOFILE, FROMFILE = None, None

if sys.platform == 'win32':
    # print("pipe-test.py, running on windows")
    TONAME = '\\\\.\\pipe\\ToSrvPipe'
    FROMNAME = '\\\\.\\pipe\\FromSrvPipe'
    EOL = '\r\n\0'
else:
    # print("pipe-test.py, running on linux or mac")
    TONAME = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
    FROMNAME = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
    EOL = '\n'

def init_pipe():
    "Opens read/write pipes. Call before using other functions"
    try:
        global TOFILE, FROMFILE
        if not TOFILE:
            # TOFILE.close()
            # FROMFILE.close()
            TOFILE = open(TONAME, 'w', encoding='utf-8')
            FROMFILE = open(FROMNAME, 'rt')
    except FileNotFoundError:
        raise EnvironmentError("Failed to open pipe. Ensure Audacity is running with mod-script-pipe.")


def send_command(command):
    """Send a single command."""
    TOFILE.write(command + EOL)
    TOFILE.flush()

def get_response():
    """Return the command response."""
    result = ''
    line = ''
    while True:
        result += line
        line = FROMFILE.readline()
        if line == '\n' and len(result) > 0:
            break
    return result

def do_command(command):
    """Send one command, and return the response."""
    send_command(command)
    response = get_response()
    status_pos = response.index(STATUS_LABEL)
    status = response[status_pos + len(STATUS_LABEL):].strip()
    response = response[:status_pos].strip()
    if status == "OK":
        status = True
    elif status == "Failed!":
        status = False
    else:
        raise ValueError("Unknown response status:", status)
    return response, status

def get_info(info_type, fmt="JSON"):
    """
    info_type - Commands|Menus|Preferences|Tracks|Clips|Envelopes|Labels|Boxes
    fmt - JSON(default)|LISP|Brief
    """
    command = "GetInfo: Type=%s Format=%s" % (info_type, fmt)
    resp, status = do_command(command)
    if not status:
        raise Exception("Command failed", command)
    # resp = resp.replace("\\", "\\\\")
    return json.loads(resp) if fmt == "JSON" else resp

def get_tracks():
    """
    Get tracks info as a list of dicts
    [{'name': 'track_name, 'focused': 1,  'selected': 0, 'kind': 'wave',
      'start': 0, 'end': end_time, 'pan': 0, 'gain': 1, 'channels': 1,
      'solo': 0, 'mute': 0, 'VZoomMin': -1, 'VZoomMax': 1}, ...]
    """
    return get_info("Tracks")

def get_track_count():
    "Returns number of tracks"
    return len(get_info("Tracks", "Brief").splitlines())

def get_label_tracks():
    """
    Get list of label tracks data
    [{'index': track_index, 'labels': labels_list}, ...]
    """
    ret = []
    for num, lbs in get_info("Labels"):
        ret.append({
            'index': num,
            'labels': lbs,
        })
    return ret

def save_label_track(path, labels):
    """
    Export label track to text file
    `path` - output file path
    `labels` - list of labels: [[start(s), stop(s), label], ...]
    """
    with open(path, 'w', encoding='utf-8') as f:
        for line in labels:
            f.write("\t".join(str(i) for i in line) + "\n")

def get_boxes():
    """
    Get coordinates and names of all the windows and subwindows
    """
    return get_info("Boxes")

def get_preferences():
    """
    Get coordinates and names of all the windows and subwindows
    """
    return get_info("Preferences")

def get_clips():
    """

    """
    return get_info("Clips")

def get_envelopes():
    """

    """
    return get_info("Envelopes")

def get_commands():
    """

    """
    return get_info("Commands")

def get_menus():
    """

    """
    return get_info("Menus")

def create_track(track_type) -> int:
    """
    Creates new track: Mono|Stereo|Label|Time
    Return track index
    """
    command = "New%sTrack:" % track_type
    resp, status = do_command(command)
    if not status:
        raise Exception("Command failed", command)
    return get_track_count() - 1

def create_label_track() -> int:
    "Creates new label track, returns track index"
    return create_track("Label")

def get_labels_count(track_index) -> int:
    "Gets label count of the specified track `track_index`"
    for index, labels in get_info("Labels"):
        if index == track_index:
            return len(labels)

def get_label_range(track_index):
    "Gets 1st label index and count of the specified `track_index`"
    count = 0
    for index, labels in get_info("Labels"):
        if index == track_index:
            return count, len(labels)
        count += len(labels)
    # return 0, 0

def add_label(track_index, start, end, text):
    add_labels(track_index, [(start, end, text)])

def add_labels(track_index, labels_list):
    first, count = get_label_range(track_index)
    do_command("SelectTracks: Track=%d Mode=Set" % track_index)
    do_command("SelectTime: Start=0 Stop=0")
    for start, end, text in labels_list:
        do_command("AddLabel:")
        do_command('SetLabel: Label=%d Text="%s" Start=%f End=%f' % 
                (first, text, start, end))

if __name__ == '__main__':
# tracks = get_tracks()
# labels = get_label_tracks()
# path = r"F:\_BACKUP\_work\Учёба\Музыка\Гитара\Сплин - Мороз по коже\\"
# for l in labels:
#     idx = l['index']
#     save_label_track(path + "labels-%s-%d.txt" % (tracks[idx]['name'], idx),
#                       l["labels"])

    # print(create_label_track())
    # add_label(0)
    # print(get_tracks())
    # print(get_label_tracks())

    def read_labels_file(path):
        "Read labels from file"
        with open(path, 'r', encoding='utf-8') as f:
            for row in csv.reader(f, delimiter='\t'):
                yield float(row[0]), float(row[1]), row[2]

    filepath = r"F:\_BACKUP\_work\Учёба\Музыка\Гитара\Сплин - Мороз по коже\labels-Label Track-1.txt"
    lbls = read_labels_file(filepath)
    add_labels(1, lbls)
