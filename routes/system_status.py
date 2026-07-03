from flask import Blueprint
import os
from datetime import datetime

system_status_bp = Blueprint("system_status", __name__)


@system_status_bp.route("/system-status-page")
def system_status_page():
    files = {
        "AI cache": "/root/novo-ai-monitor/stock_news_ai_cache.json",
        "Historik log": "/root/novo-ai-monitor/history_save.log",
        "Combined report log": "/root/novo-ai-monitor/combined_report.log",
        "Smart alerts log": "/root/novo-ai-monitor/last_smart_alerts.log",
        "Portfolio alerts log": "/root/novo-ai-monitor/portfolio_alerts.log",
    }

    rows = ""

    for name, path in files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")
            status = "✅ OK"
        else:
            size = "-"
            modified = "-"
            status = "⚠️ Mangler"

        rows += f"""
        <tr>
            <td><b>{name}</b></td>
            <td>{status}</td>
            <td>{size}</td>
            <td>{modified}</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>Systemstatus</title>
        <style>
            body {{ font-family: Arial, sans-serif; background:#eef2f7; padding:40px; }}
            .container {{ max-width:1000px; margin:auto; }}
            .card {{ background:white; padding:24px; border-radius:14px; margin-bottom:20px; box-shadow:0 10px 30px rgba(0,0,0,0.08); }}
            table {{ width:100%; border-collapse:collapse; background:white; border-radius:14px; overflow:hidden; }}
            th {{ background:#111827; color:white; padding:14px; text-align:left; }}
            td {{ padding:14px; border-bottom:1px solid #e5e7eb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚙️ Systemstatus V3.2</h1>

            <div class="card">
                <p><b>Novo AI service:</b> ✅ Aktiv hvis denne side vises</p>
                <p><b>HTTPS/Caddy:</b> ✅ Aktiv hvis siden åbnes via monitor.ethinking.dk</p>
                <p><b>Senest opdateret:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>

            <table>
                <tr>
                    <th>Komponent</th>
                    <th>Status</th>
                    <th>Størrelse</th>
                    <th>Sidst ændret</th>
                </tr>
                {rows}
            </table>
        </div>
    </body>
    </html>
    """
