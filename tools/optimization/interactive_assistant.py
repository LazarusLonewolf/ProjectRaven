# interactive_assistant.py

from system_scan import get_resource_heavy_processes, get_disk_space, get_startup_programs
from cleanup_engine import get_temp_files_summary, perform_temp_cleanup

def review_system_health():
    print("\n[System Review]")
    
    print("\nChecking disk usage...")
    disk = get_disk_space()
    print(f"Drive is {disk['percent_used']}% full. {disk['free_gb']} GB free of {disk['total_gb']} GB total.")

    print("\nIdentifying high-resource programs...")
    heavy = get_resource_heavy_processes()
    if heavy:
        for proc in heavy:
            print(f" - {proc['name']} (PID {proc['pid']}): CPU {proc['cpu_percent']}% | RAM {proc['memory_percent']}%")
    else:
        print(" - No high-resource processes found.")

    print("\nReviewing startup items...")
    startup = get_startup_programs()
    if startup:
        for item in startup:
            print(f" - {item['name']}: {item['path']}")
    else:
        print(" - No startup programs detected or access denied.")

def run_cleanup_preview():
    print("\n[Cleanup Preview]")
    summary = get_temp_files_summary()
    print(f"Found {summary['files']} temporary files using approximately {summary['approx_size_mb']} MB.")

def confirm_cleanup():
    print("\nPerforming cleanup...")
    perform_temp_cleanup()
    print("Temporary files cleared.")
