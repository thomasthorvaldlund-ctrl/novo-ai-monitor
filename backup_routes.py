from pathlib import Path

from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    send_from_directory,
    url_for,
)

from backup_service import create_backup, create_full_backup, list_backups


backup_bp = Blueprint(
    "backup_manager",
    __name__,
)


@backup_bp.route("/backup-manager")
def backup_manager():
    backups = list_backups()
    latest = backups[0] if backups else None

    return render_template(
        "backup_manager.html",
        latest_backup=latest,
        backups=backups,
    )


@backup_bp.route("/backup-manager/create", methods=["POST"])
def create_backup_route():
    create_backup()

    return redirect(
        url_for("backup_manager.backup_manager")
    )


@backup_bp.route("/backup-manager/create-full", methods=["POST"])
def create_full_backup_route():
    create_full_backup()

    return redirect(
        url_for("backup_manager.backup_manager")
    )

@backup_bp.route("/backup-manager/download/<filename>")
def download_backup(filename):
    backup_dir = Path(__file__).parent / "backups"
    file_path = backup_dir / filename

    if not file_path.exists() or not file_path.is_file():
        abort(404)

    return send_from_directory(
        backup_dir,
        filename,
        as_attachment=True,
    )

