let historyChart = null;

function loadHistory(stock) {

    fetch(`/history-data?stock=${stock}`)
        .then(response => response.json())
        .then(data => {

            const labels = data.map(row => row.date);
            const prices = data.map(row => row.price);

            if (historyChart) {
                historyChart.destroy();
            }

            const canvas = document.getElementById("novoHistoryChart");

            historyChart = new Chart(canvas, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [{
                        label: stock + " kurs",
                        data: prices,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true
                }
            });
        });
}

document.addEventListener("DOMContentLoaded", function () {

    const canvas = document.getElementById("novoHistoryChart");

    if (!canvas) {
        return;
    }

    loadHistory("NOVO");

    const selector = document.getElementById("stockSelector");

    if (selector) {

        selector.addEventListener("change", function () {
            loadHistory(this.value);
        });

    }

});