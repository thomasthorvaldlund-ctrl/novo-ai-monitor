
from flask import Blueprint, render_template_string

from ai_performance_service import get_ai_performance_summary, get_time_based_statistics


ai_performance_bp = Blueprint(
    "ai_performance",
    __name__
)


@ai_performance_bp.route("/ai-performance")
def ai_performance_page():

    summary = get_ai_performance_summary()
    statistics = get_time_based_statistics()

    html = """
    <html>
    <head>
        <title>AI Performance</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                background: #f5f7fa;
            }

            .card {
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }

            table {
                width:100%;
                border-collapse: collapse;
            }

            th, td {
                padding:10px;
                border-bottom:1px solid #ddd;
                text-align:center;
            }

            .green {
                color:green;
                font-weight:bold;
            }

            .red {
                color:red;
                font-weight:bold;
            }

        </style>
    </head>

    <body>

    <h1>📈 AI Performance Dashboard</h1>


    <div class="card">

        <h2>Samlet status</h2>

        <p>
        Testede signaler:
        <b>{{summary.tested_signals}}</b>
        </p>

        <p>
        Bedste signal:
        <b>{{summary.best_signal}}</b>
        </p>

        <p>
        Bedste periode:
        <b>{{summary.best_period}}</b>
        </p>

        <p>
        Bedste gennemsnit:
        <b>{{summary.best_return}}%</b>
        </p>

        <p>
        Datakvalitet:
        {{summary.data_quality}}
        </p>

    </div>


    <div class="card">

    <h2>Signal Performance</h2>

    <table>

    <tr>
        <th>Signal</th>
        <th>1 dag</th>
        <th>3 dage</th>
        <th>5 dage</th>
    </tr>


    {% for signal, periods in statistics.items() %}

    <tr>

        <td><b>{{signal}}</b></td>

        {% for period in ["1d","3d","5d"] %}

        <td>
        {{periods[period].average_return}}%
        <br>
        Success:
        {{periods[period].success_rate}}%
        </td>

        {% endfor %}

    </tr>

    {% endfor %}


    </table>

    </div>


    </body>
    </html>
    """

    return render_template_string(
        html,
        summary=summary,
        statistics=statistics
    )
