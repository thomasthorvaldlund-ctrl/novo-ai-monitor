"""
Brugerflade og API til personlige Deep AI-aktievalg.
"""

from urllib.parse import urlsplit

from flask import (
    Blueprint,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from deep_ai_entitlement_service import (
    get_user_deep_ai_usage,
)

from deep_ai_storage_status_service import (
    get_deep_ai_storage_status,
)

from user_identity_service import (
    require_current_user_id,
)

from deep_ai_selection_service import (
    add_user_deep_ai_selection,
    get_user_selected_deep_ai_stocks,
    remove_user_deep_ai_selection,
)

from stock_universe_service import (
    get_active_stocks,
    get_deep_ai_stocks,
    get_stock_metadata,
)


deep_ai_settings_bp = Blueprint(
    "deep_ai_settings",
    __name__,
)


def _current_user_id():
    return require_current_user_id()


def _is_same_origin_post():
    source_url = (
        request.headers.get("Origin")
        or request.headers.get("Referer")
        or ""
    ).strip()

    if not source_url:
        return False

    parsed = urlsplit(
        source_url
    )

    return (
        parsed.scheme in {
            "http",
            "https",
        }
        and parsed.netloc.lower()
        == request.host.lower()
    )


def _stock_item(
    symbol,
    ticker,
    *,
    selected=False,
    core=False,
):
    metadata = (
        get_stock_metadata(symbol)
        or {}
    )

    return {
        "symbol": symbol,
        "name": (
            metadata.get("name")
            or symbol
        ),
        "ticker": ticker,
        "country": (
            metadata.get("country")
            or ""
        ),
        "market": (
            metadata.get("market")
            or ""
        ),
        "currency": (
            metadata.get("currency")
            or ""
        ),
        "sector": (
            metadata.get("sector")
            or ""
        ),
        "selected": selected,
        "core": core,
    }


def _settings_context(
    user_id,
    *,
    error_message=None,
):
    core_stocks = get_deep_ai_stocks()

    selected_stocks = (
        get_user_selected_deep_ai_stocks(
            user_id
        )
    )

    usage = get_user_deep_ai_usage(
        user_id,
        len(selected_stocks),
    )

    core_items = sorted(
        (
            _stock_item(
                symbol,
                ticker,
                core=True,
            )
            for symbol, ticker
            in core_stocks.items()
        ),
        key=lambda item: (
            item["name"].casefold(),
            item["ticker"],
        ),
    )

    selected_items = sorted(
        (
            _stock_item(
                symbol,
                ticker,
                selected=True,
            )
            for symbol, ticker
            in selected_stocks.items()
        ),
        key=lambda item: (
            item["name"].casefold(),
            item["ticker"],
        ),
    )

    plan_labels = {
        "free": "Grundpakke",
        "owner": "Ejer",
        "plus": "Plus",
        "pro": "Pro",
    }

    status_code = request.args.get(
        "status",
        "",
    )

    status_messages = {
        "added": (
            "Aktien er tilføjet til dine "
            "personlige Deep AI-analyser."
        ),
        "removed": (
            "Aktien er fjernet fra dine "
            "personlige Deep AI-analyser."
        ),
    }

    return {
        "user_id": user_id,
        "plan_label": plan_labels.get(
            usage["plan_code"],
            usage["plan_code"]
            .replace("_", " ")
            .title(),
        ),
        "usage": usage,
        "core_stocks": core_items,
        "selected_stocks": selected_items,
        "storage_status": (
            get_deep_ai_storage_status()
        ),
        "status_message": (
            status_messages.get(
                status_code
            )
        ),
        "error_message": error_message,
    }


@deep_ai_settings_bp.route(
    "/deep-ai-settings",
    methods=[
        "GET",
        "POST",
    ],
)
def deep_ai_settings_page():
    user_id = _current_user_id()

    if request.method == "POST":
        if not _is_same_origin_post():
            abort(400)

        action = request.form.get(
            "action",
            "",
        ).strip().lower()

        symbol = request.form.get(
            "symbol",
            "",
        ).strip().upper()

        try:
            if action == "add":
                add_user_deep_ai_selection(
                    user_id,
                    symbol,
                )

                status = "added"

            elif action == "remove":
                remove_user_deep_ai_selection(
                    user_id,
                    symbol,
                )

                status = "removed"

            else:
                raise ValueError(
                    "Ukendt Deep AI-handling."
                )

        except ValueError as error:
            return (
                render_template(
                    "deep_ai_settings.html",
                    **_settings_context(
                        user_id,
                        error_message=str(error),
                    ),
                ),
                400,
            )

        except RuntimeError:
            return (
                render_template(
                    "deep_ai_settings.html",
                    **_settings_context(
                        user_id,
                        error_message=(
                            "Indstillingerne kunne ikke "
                            "gemmes lige nu."
                        ),
                    ),
                ),
                500,
            )

        return redirect(
            url_for(
                "deep_ai_settings."
                "deep_ai_settings_page",
                status=status,
            )
        )

    return render_template(
        "deep_ai_settings.html",
        **_settings_context(
            user_id
        ),
    )


@deep_ai_settings_bp.route(
    "/api/deep-ai-stocks"
)
def deep_ai_stock_search():
    user_id = _current_user_id()

    query = request.args.get(
        "q",
        "",
    ).strip()[:80]

    if len(query) < 2:
        return jsonify({
            "stocks": [],
        })

    normalized_query = query.casefold()

    active_stocks = get_active_stocks()
    core_symbols = set(
        get_deep_ai_stocks()
    )

    selected_symbols = set(
        get_user_selected_deep_ai_stocks(
            user_id
        )
    )

    matches = []

    for symbol, ticker in active_stocks.items():
        if symbol in core_symbols:
            continue

        item = _stock_item(
            symbol,
            ticker,
            selected=(
                symbol in selected_symbols
            ),
        )

        searchable = " ".join([
            item["symbol"],
            item["name"],
            item["ticker"],
            item["country"],
            item["market"],
            item["sector"],
        ]).casefold()

        if normalized_query not in searchable:
            continue

        matches.append(
            item
        )

    matches.sort(
        key=lambda item: (
            not item["selected"],
            item["name"].casefold(),
            item["ticker"],
        )
    )

    return jsonify({
        "stocks": matches[:30],
    })
