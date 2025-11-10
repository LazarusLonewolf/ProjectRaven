# system_scan.py

import psutil
import platform
import shutil

def get_resource_heavy_processes(threshold=20.0):
    heavy_procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            if proc.info['cpu_percent'] > threshold or proc.info['memory_percent'] > threshold:
                heavy_procs.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return heavy_procs

def get_disk_space(path="/"):
    usage = shutil.disk_usage(path)
    return {
        "total_gb": usage.total // (2**30),
        "used_gb": usage.used // (2**30),
        "free_gb": usage.free // (2**30),
        "percent_used": round(usage.used / usage.total * 100, 2)
    }

def get_startup_programs():
    system = platform.system()
    startup_items = []
    if system == "Windows":
        import winreg
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                for i in range(0, winreg.QueryInfoKey(key)[1]):
                    name, value, _ = winreg.EnumValue(key, i)
                    startup_items.append({"name": name, "path": value})
        except Exception:
            pass
    return startup_items
