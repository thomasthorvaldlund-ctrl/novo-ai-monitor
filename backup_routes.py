from flask import Blueprint, redirect, render_template, url_for

from backup_service import create_backup, list_backups


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
