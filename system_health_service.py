import shutil
import subprocess


def get_system_health():
    disk = shutil.disk_usage("/")

    disk_pct = round((disk.used / disk.total) * 100)

    mem = subprocess.check_output(["free", "-m"]).decode().splitlines()[1].split()

    mem_used = int(mem[2])
    mem_total = int(mem[1])

    return {
        "server": "Online",
        "disk_pct": disk_pct,
        "mem_used": mem_used,
        "mem_total": mem_total,
        "ai": "OK",
    }