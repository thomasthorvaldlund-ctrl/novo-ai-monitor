document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("performanceChart");

    if (!canvas) return;

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: ["BUY", "HOLD", "WATCH", "SELL"],
            datasets: [{
                label: "AI Signals",
                data: [
                    Number(canvas.dataset.buy),
                    Number(canvas.dataset.hold),
                    Number(canvas.dataset.watch),
                    Number(canvas.dataset.sell)
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
});