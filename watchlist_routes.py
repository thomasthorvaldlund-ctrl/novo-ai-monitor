from flask import Blueprint

watchlist_bp = Blueprint("watchlist", __name__)

@watchlist_bp.route("/watchlist-page")
def watchlist_page():
    return "OK"