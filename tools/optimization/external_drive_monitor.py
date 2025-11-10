# external_drive_monitor.py

import psutil

def list_external_drives():
    external_drives = []
    partitions = psutil.disk_partitions(all=False)
    for partition in partitions:
        if 'removable' in partition.opts or partition.device.startswith('/dev/sd'):
            usage = psutil.disk_usage(partition.mountpoint)
            external_drives.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free
            })
    return external_drives

def notify_user(drives):
    if not drives:
        print("No external drives detected.")
        return
    print("External drive(s) detected:")
    for drive in drives:
        print(f"Device: {drive['device']}")
        print(f"Mountpoint: {drive['mountpoint']}")
        print(f"Filesystem Type: {drive['fstype']}")
        print(f"Total Space: {drive['total'] // (1024**3)} GB")
        print(f"Free Space: {drive['free'] // (1024**3)} GB\n")

if __name__ == "__main__":
    drives = list_external_drives()
    notify_user(drives)

