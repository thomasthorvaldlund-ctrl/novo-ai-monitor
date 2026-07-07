document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("novoHistoryChart");

    if (!canvas) {
        return;
    }

    fetch("/history-data?stock=NOVO")
        .then(response => response.json())
        .then(data => {
            const labels = data.map(row => row.date);
            const prices = data.map(row => row.price);

            new Chart(canvas, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "NOVO kurs",
                        data: prices,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true
                }
            });
        });
});