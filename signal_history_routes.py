from flask import Blueprint, render_template

from signal_history_service import load_signal_history

signal_history_bp = Blueprint("signal_history", __name__)


@signal_history_bp.route("/signal-history")
def signal_history():
    rows = load_signal_history()
    rows = list(reversed(rows))[:100]

    return render_template(
        "signal_history.html",
        signals=rows,
    )