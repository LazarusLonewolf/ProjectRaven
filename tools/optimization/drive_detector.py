import os

def detect_external_drives():
    possible_drives = []
    for drive_letter in range(65, 91):  # ASCII A-Z
        drive = f"{chr(drive_letter)}:/"
        if os.path.exists(drive):
            try:
                if os.path.ismount(drive):
                    possible_drives.append(drive)
            except PermissionError:
                continue
    return possible_drives
