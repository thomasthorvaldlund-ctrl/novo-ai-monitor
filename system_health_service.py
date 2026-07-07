import shutil
import subprocess


def get_system_health():
    disk = shutil.disk_usage("/")

    disk_pct = round((disk.used / disk.total) * 100)

    mem = subprocess.check_output(["free", "-m"]).decode().splitlines()[1].split()

    mem_used = int(mem[2])
    mem_total = int(mem[1])

    mem_pct = round((mem_used / mem_total) * 100)

    disk_status = "OK"
    if disk_pct >= 90:
        disk_status = "Critical"
    elif disk_pct >= 80:
        disk_status = "Warning"

    memory_status = "OK"
    if mem_pct >= 90:
        memory_status = "Critical"
    elif mem_pct >= 80:
        memory_status = "Warning"

    return {
        "server": "Online",
        "disk_pct": disk_pct,
        "disk_status": disk_status,
        "mem_used": mem_used,
        "mem_total": mem_total,
        "mem_pct": mem_pct,
        "memory_status": memory_status,
        "ai": "OK",
    }