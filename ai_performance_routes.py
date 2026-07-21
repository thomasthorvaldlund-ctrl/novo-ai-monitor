
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

    chart_data = {
        "labels": ["1 dag", "3 dage", "5 dage"],
        "datasets": []
    }

    for signal, periods in statistics.items():

        chart_data["datasets"].append({
            "label": signal,
            "data": [
                periods["1d"]["average_return"],
                periods["3d"]["average_return"],
                periods["5d"]["average_return"]
            ]
        })

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

    <h2>🤖 Hvad måler AI Performance Dashboard?</h2>

    <p>
    Dette dashboard måler, hvor godt Stock AI Monitor's
    aktiesignaler har fungeret historisk.
    </p>

    <p>
    Når AI-systemet analyserer en aktie, gemmes signalet
    sammen med AI score, confidence, risiko og tidspunkt.
    Efterfølgende sammenlignes signalet med den faktiske
    kursudvikling efter 1, 3 og 5 dage.
    </p>

    <p>
    Formålet er ikke at forudsige fremtiden med sikkerhed,
    men at gøre AI-modellen målbar og løbende forbedre
    kvaliteten af dens beslutninger.
    </p>


    <h3>Sådan fungerer processen:</h3>

    <p>
    🧠 AI analyse
    → 📌 Signal gemmes
    → 📈 Kursudvikling måles
    → 📊 Performance beregnes
    → 🚀 AI kvalitet evalueres
    </p>

    </div>

    <div class="card">

    <h2>📊 Sådan læses performance-grafen</h2>

    <p>
    Grafen viser, hvordan de forskellige AI-signaler
    historisk har udviklet sig efter signalet blev oprettet.
    </p>

    <p>
    <b>Perioder:</b>
    </p>

    <ul>
        <li><b>1 dag:</b> Korttidseffekten efter AI-signalet.</li>
        <li><b>3 dage:</b> Om signalet fortsætter med at fungere på kort sigt.</li>
        <li><b>5 dage:</b> Den mere langsigtede udvikling efter signalet.</li>
    </ul>

    <p>
    <b>Signaler:</b>
    </p>

    <ul>
        <li>🟢 <b>BUY:</b> AI vurderer højere sandsynlighed for positiv udvikling.</li>
        <li>🟡 <b>HOLD:</b> Ingen tydeligt købssignal eller salgssignal.</li>
        <li>🟠 <b>WATCH:</b> Interessant udvikling, men med højere usikkerhed.</li>
    </ul>

    <p>
    Performance-data bruges til at evaluere og forbedre AI-modellen.
    Historiske resultater er ikke en garanti for fremtidige afkast.
    </p>


    <h2>Performance graf</h2>

    <canvas id="performanceChart"></canvas>

    </div>



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

    <h2>🧠 AI Performance Confidence</h2>

    <p>
    Analyserede signaler:
    <b>{{summary.tested_signals}}</b>
    </p>

    <p>
    Datakvalitet:
    {{summary.data_quality}}
    </p>

    <p>
    Status:
    ⚠️ Tidlig læring
    </p>

    <p>
    Anbefaling:
    Vent på 100+ signaler før stærke konklusioner.
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



<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>

const ctx = document.getElementById(
    'performanceChart'
);

new Chart(ctx, {

    type: 'bar',

    data: {
        labels: {{chart_data.labels | tojson}},
        datasets: {{chart_data.datasets | tojson}}
    },

    options: {

        responsive: true,

        plugins: {

            title: {
                display: true,
                text: '📊 Historisk AI signal-performance (%)'
            },

            legend: {
                position: 'top'
            },

            tooltip: {

                callbacks: {

                    label: function(context) {
                        return context.dataset.label +
                            ': ' +
                            context.raw.toFixed(2) +
                            '%';
                    }

                }

            }

        },

        scales: {

            y: {

                title: {

                    display: true,

                    text: 'Afkast (%)'

                }

            }

        }

    }

});

</script>


    </body>

    </html>
    """

    return render_template_string(
        html,
        summary=summary,
        statistics=statistics,
        chart_data=chart_data
    )
