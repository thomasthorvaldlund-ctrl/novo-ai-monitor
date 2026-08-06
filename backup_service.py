from datetime import datetime
from pathlib import Path
import json
import os
import platform
import subprocess
import tarfile


PROJECT_DIR = Path("/root/aureum-ai-platform")
BACKUP_DIR = PROJECT_DIR / "backups"
PLATFORM_VERSION = "2.1"


EXCLUDE = {
    "venv",
    "venv-old-path-backup",
    "__pycache__",
    ".git",
    "backups",
}


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


def create_backup():
    """
    Opretter en komprimeret backup af Aureum AI Platform
    og gemmer metadata i en tilhørende JSON-fil.
    """

    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"aureum_backup_{timestamp}"

    backup_file = BACKUP_DIR / f"{backup_name}.tar.gz"
    metadata_file = BACKUP_DIR / f"{backup_name}.json"

    file_count = 0

    with tarfile.open(backup_file, "w:gz") as tar:
        for root, dirs, files in os.walk(PROJECT_DIR):
            dirs[:] = [directory for directory in dirs if directory not in EXCLUDE]

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
    }

    metadata_file.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return metadata

    return metadata


def list_backups():
    """
    Returnerer alle backups sorteret med den nyeste først.
    """

    BACKUP_DIR.mkdir(exist_ok=True)

    backups = []

    for metadata_file in BACKUP_DIR.glob("aureum_backup_*.json"):
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