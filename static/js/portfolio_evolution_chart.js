document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("portfolioEvolutionChart");

    if (!canvas) {
        return;
    }

    const labels = JSON.parse(canvas.dataset.labels || "[]");
    const health = JSON.parse(canvas.dataset.health || "[]");
    const risk = JSON.parse(canvas.dataset.risk || "[]");
    const diversification = JSON.parse(
        canvas.dataset.diversification || "[]"
    );
    const momentum = JSON.parse(canvas.dataset.momentum || "[]");
    const confidence = JSON.parse(
        canvas.dataset.confidence || "[]"
    );

    new Chart(canvas, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Health Score",
                    data: health,
                    tension: 0.25,
                    borderWidth: 3,
                    pointRadius: 4,
                },
                {
                    label: "Risiko",
                    data: risk,
                    tension: 0.25,
                    borderWidth: 2,
                    pointRadius: 3,
                },
                {
                    label: "Diversifikation",
                    data: diversification,
                    tension: 0.25,
                    borderWidth: 2,
                    pointRadius: 3,
                },
                {
                    label: "Momentum",
                    data: momentum,
                    tension: 0.25,
                    borderWidth: 2,
                    pointRadius: 3,
                },
                {
                    label: "AI-confidence",
                    data: confidence,
                    tension: 0.25,
                    borderWidth: 2,
                    pointRadius: 3,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false,
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                    },
                },
            },
            plugins: {
                legend: {
                    position: "top",
                },
            },
        },
    });
});
