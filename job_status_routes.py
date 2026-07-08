from flask import Blueprint, render_template

from job_status_service import get_job_statuses

job_status_bp = Blueprint("job_status", __name__)


@job_status_bp.route("/job-status")
def job_status():
    jobs = get_job_statuses()

    return render_template(
        "job_status.html",
        jobs=jobs,
    )