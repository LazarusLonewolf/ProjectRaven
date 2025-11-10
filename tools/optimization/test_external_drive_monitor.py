# test_external_drive_monitor.py

import external_drive_monitor

def test_list_external_drives():
    print("Running test: test_list_external_drives")
    drives = external_drive_monitor.list_external_drives()
    if isinstance(drives, list):
        print(f"PASS: Function returned a list with {len(drives)} entries.")
        for drive in drives:
            assert 'device' in drive, "Missing 'device' key"
            assert 'mountpoint' in drive, "Missing 'mountpoint' key"
            assert 'fstype' in drive, "Missing 'fstype' key"
            assert 'total' in drive, "Missing 'total' key"
            assert 'free' in drive, "Missing 'free' key"
        if drives:
            print("Note: External drives detected. Ensure container has access to host volumes.")
    else:
        print("FAIL: Function did not return a list.")

if __name__ == "__main__":
    test_list_external_drives()
