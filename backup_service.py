from datetime import datetime
from pathlib import Path
from aureum_paths import PROJECT_DIR
import json
import os
import platform
import re
import shutil
import subprocess
import tarfile


BACKUP_DIR = PROJECT_DIR / "backups"
RECOVERY_DIR = PROJECT_DIR / "recovery"

SYSTEMD_SERVICE = Path("/etc/systemd/system/aureum-ai.service")
CADDY_FILE = Path("/etc/caddy/Caddyfile")

PLATFORM_VERSION = "2.1"


EXCLUDE = {
    "venv",
    "venv-old-path-backup",
    "__pycache__",
    ".git",
    "backups",
}


def run_command(command):
    """
    Kører en systemkommando og returnerer tekstoutput.
    """

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return "unavailable"


def get_git_commit():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return "unknown"


def redact_service_secrets(service_text):
    """
    Bevarer miljøvariablernes navne, men fjerner deres værdier.
    """

    pattern = r'Environment="([^="]+)=.*?"'

    return re.sub(
        pattern,
        lambda match: f'Environment="{match.group(1)}=REDACTED"',
        service_text,
    )


def export_recovery_files():
    """
    Eksporterer den aktuelle serverkonfiguration til recovery-mappen.
    Følsomme værdier i systemd-servicefilen bliver maskeret.
    """

    RECOVERY_DIR.mkdir(exist_ok=True)

    if SYSTEMD_SERVICE.exists():
        service_text = SYSTEMD_SERVICE.read_text(encoding="utf-8")
        safe_service_text = redact_service_secrets(service_text)

        (RECOVERY_DIR / "aureum-ai.service").write_text(
            safe_service_text,
            encoding="utf-8",
        )

    crontab_text = run_command(["crontab", "-l"])

    (RECOVERY_DIR / "root-crontab.txt").write_text(
        crontab_text + "\n",
        encoding="utf-8",
    )

    if CADDY_FILE.exists():
        shutil.copy2(
            CADDY_FILE,
            RECOVERY_DIR / "Caddyfile",
        )

    server_info = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "hostname": run_command(["hostname"]),
        "hostnamectl": run_command(["hostnamectl"]),
        "os_release": run_command(["cat", "/etc/os-release"]),
        "python_version": platform.python_version(),
        "git_commit": get_git_commit(),
        "service_enabled": run_command(
            ["systemctl", "is-enabled", "aureum-ai.service"]
        ),
        "service_active": run_command(
            ["systemctl", "is-active", "aureum-ai.service"]
        ),
    }

    server_info_file = RECOVERY_DIR / "server-info.json"
    temp_server_info_file = server_info_file.with_suffix(
        server_info_file.suffix + ".tmp"
    )

    with open(
        temp_server_info_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            server_info,
            f,
            indent=2,
            ensure_ascii=False,
        )

        f.flush()
        os.fsync(f.fileno())

    temp_server_info_file.replace(
        server_info_file
    )

    return {
        "success": True,
        "directory": str(RECOVERY_DIR),
        "files": sorted(
            path.name
            for path in RECOVERY_DIR.iterdir()
            if path.is_file()
        ),
    }


def create_platform_backup():
    """
    Opretter en komprimeret backup af Aureum AI Platform,
    inklusive maskeret recovery-konfiguration.
    """

    BACKUP_DIR.mkdir(exist_ok=True)

    recovery_result = export_recovery_files()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"aureum_backup_{timestamp}"

    backup_file = BACKUP_DIR / f"{backup_name}.tar.gz"
    metadata_file = BACKUP_DIR / f"{backup_name}.json"

    file_count = 0

    with tarfile.open(backup_file, "w:gz") as tar:
        for root, dirs, files in os.walk(PROJECT_DIR):
            dirs[:] = [
                directory
                for directory in dirs
                if directory not in EXCLUDE
            ]

            for filename in files:
                path = Path(root) / filename
                relative_path = path.relative_to(PROJECT_DIR)

                tar.add(path, arcname=relative_path)
                file_count += 1

    size_bytes = backup_file.stat().st_size
    size_mb = round(size_bytes / 1024 / 1024, 2)

    metadata = {
        "success": True,
        "platform": "Aureum AI Platform",
        "version": PLATFORM_VERSION,
        "file": backup_file.name,
        "path": str(backup_file),
        "metadata_file": metadata_file.name,
        "size_bytes": size_bytes,
        "size_mb": size_mb,
        "file_count": file_count,
        "created": timestamp,
        "git_commit": get_git_commit(),
        "python_version": platform.python_version(),
        "recovery_included": recovery_result["success"],
        "recovery_files": recovery_result["files"],
    }

    temp_metadata_file = metadata_file.with_suffix(
        metadata_file.suffix + ".tmp"
    )

    with open(
        temp_metadata_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            metadata,
            f,
            indent=2,
            ensure_ascii=False,
        )

        f.flush()
        os.fsync(f.fileno())

    temp_metadata_file.replace(
        metadata_file
    )

    return metadata




def create_full_backup():
    """
    Opretter en udvidet recovery-backup med platformdata,
    recovery-konfiguration og gendannelsesvejledning.
    """

    BACKUP_DIR.mkdir(exist_ok=True)

    recovery_result = export_recovery_files()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"aureum_full_backup_{timestamp}"

    backup_file = BACKUP_DIR / f"{backup_name}.tar.gz"
    metadata_file = BACKUP_DIR / f"{backup_name}.json"

    restore_guide = RECOVERY_DIR / "RESTORE_GUIDE.md"

    restore_guide.write_text(
        f"""# Aureum AI Platform – Restore Guide

1. Installér Ubuntu, Python 3 og Git.
2. Udpak backupen til `{PROJECT_DIR}`.
3. Opret et nyt virtuelt miljø:
   `python3 -m venv venv`
4. Installér pakker:
   `./venv/bin/python -m pip install -r requirements.lock.txt`
5. Genskab secrets manuelt i systemd-servicefilen.
6. Kopiér recovery-filer:
   - `aureum-ai.service`
   - `Caddyfile`
   - `root-crontab.txt`
7. Kør:
   `sudo systemctl daemon-reload`
8. Aktivér og start:
   `sudo systemctl enable --now aureum-ai.service`
9. Kontrollér:
   `curl -I http://127.0.0.1:3000/command-center`
""",
        encoding="utf-8",
    )

    file_count = 0

    with tarfile.open(backup_file, "w:gz") as tar:
        for root, dirs, files in os.walk(PROJECT_DIR):
            dirs[:] = [
                directory
                for directory in dirs
                if directory not in EXCLUDE
            ]

            for filename in files:
                path = Path(root) / filename
                relative_path = path.relative_to(PROJECT_DIR)

                tar.add(path, arcname=relative_path)
                file_count += 1

    size_bytes = backup_file.stat().st_size
    size_mb = round(size_bytes / 1024 / 1024, 2)

    metadata = {
        "success": True,
        "platform": "Aureum AI Platform",
        "backup_type": "full",
        "version": PLATFORM_VERSION,
        "file": backup_file.name,
        "path": str(backup_file),
        "metadata_file": metadata_file.name,
        "size_bytes": size_bytes,
        "size_mb": size_mb,
        "file_count": file_count,
        "created": timestamp,
        "git_commit": get_git_commit(),
        "python_version": platform.python_version(),
        "recovery_included": recovery_result["success"],
        "recovery_files": recovery_result["files"],
        "restore_guide": "recovery/RESTORE_GUIDE.md",
    }

    temp_metadata_file = metadata_file.with_suffix(
        metadata_file.suffix + ".tmp"
    )

    with open(
        temp_metadata_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            metadata,
            f,
            indent=2,
            ensure_ascii=False,
        )

        f.flush()
        os.fsync(f.fileno())

    temp_metadata_file.replace(
        metadata_file
    )

    return metadata

def create_backup():
    """
    Bagudkompatibel alias for Platform Backup.
    """
    return create_platform_backup()

def list_backups():
    """
    Returnerer alle backups sorteret med den nyeste først.
    """

    BACKUP_DIR.mkdir(exist_ok=True)

    backups = []

    metadata_files = list(BACKUP_DIR.glob("aureum_backup_*.json"))
    metadata_files += list(BACKUP_DIR.glob("aureum_full_backup_*.json"))

    for metadata_file in metadata_files:
        try:
            metadata = json.loads(
                metadata_file.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            continue

        backup_file = BACKUP_DIR / metadata.get("file", "")

        metadata["available"] = backup_file.exists()
        metadata["metadata_path"] = str(metadata_file)

        backups.append(metadata)

    backups.sort(
        key=lambda item: item.get("created", ""),
        reverse=True,
    )

    return backups
