document.addEventListener("DOMContentLoaded", async () => {
    const canvas = document.getElementById("marketScoreHistoryChart");

    if (!canvas) {
        return;
    }

    try {
        const response = await fetch("/market-score-history");

        if (!response.ok) {
            throw new Error(
                `Market Score History kunne ikke hentes: ${response.status}`
            );
        }

        const data = await response.json();
        const history = data.history || [];

        new Chart(canvas, {
            type: "line",
            data: {
                labels: history.map(row => row.date),
                datasets: [
                    {
                        label: "Market Score",
                        data: history.map(row => row.score),
                        tension: 0.25,
                        fill: false,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        ticks: {
                            stepSize: 10,
                        },
                    },
                },
                plugins: {
                    legend: {
                        display: true,
                    },
                },
            },
        });
    } catch (error) {
        console.error("Market Score History-fejl:", error);
    }
});