class StockPicker {
    constructor(options) {
        this.stockInput = document.querySelector(options.stockInput);
        this.resultsBox = document.querySelector(options.resultsBox);
        this.tickerInput = document.querySelector(options.tickerInput);
        this.currencyInput = document.querySelector(options.currencyInput);
        this.apiUrl = options.apiUrl || "/api/stocks";
        this.selectedStock = null;

        if (
            !this.stockInput ||
            !this.resultsBox ||
            !this.tickerInput ||
            !this.currencyInput
        ) {
            console.error("StockPicker: Et eller flere nødvendige felter mangler.");
            return;
        }

        this.bindEvents();
    }

    bindEvents() {
        this.stockInput.addEventListener("input", () => {
            this.clearSelectedStock();
            this.search(this.stockInput.value);
        });

        this.stockInput.addEventListener("focus", () => {
            if (this.stockInput.value.trim()) {
                this.search(this.stockInput.value);
            }
        });

        document.addEventListener("click", (event) => {
            const clickedInside =
                this.stockInput.contains(event.target) ||
                this.resultsBox.contains(event.target);

            if (!clickedInside) {
                this.hideResults();
            }
        });
    }

    async search(query) {
        const normalizedQuery = query.trim();

        if (!normalizedQuery) {
            this.hideResults();
            return;
        }

        this.showMessage("Søger efter aktier...");

        try {
            const response = await fetch(
                `${this.apiUrl}?q=${encodeURIComponent(normalizedQuery)}`
            );

            if (!response.ok) {
                throw new Error(`API-fejl: ${response.status}`);
            }

            const data = await response.json();
            this.renderResults(data.stocks || []);
        } catch (error) {
            console.error("StockPicker søgefejl:", error);
            this.showMessage("Aktiesøgningen kunne ikke indlæses.");
        }
    }

    renderResults(stocks) {
        this.resultsBox.innerHTML = "";

        if (!stocks.length) {
            this.showMessage("Ingen aktier fundet.");
            return;
        }

        stocks.forEach((stock) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "stock-picker-result";

            const countryFlag = this.getCountryFlag(stock.country);

            button.innerHTML = `
                <span class="stock-picker-result-main">
                    <span class="stock-picker-flag">${countryFlag}</span>
                    <span>
                        <strong>${this.escapeHtml(stock.name)}</strong>
                        <small>
                            ${this.escapeHtml(stock.ticker)}
                            · ${this.escapeHtml(stock.sector || "")}
                        </small>
                    </span>
                </span>

                <span class="stock-picker-currency">
                    ${this.escapeHtml(stock.currency)}
                </span>
            `;

            button.addEventListener("click", () => {
                this.selectStock(stock);
            });

            this.resultsBox.appendChild(button);
        });

        this.resultsBox.hidden = false;
    }

    selectStock(stock) {
        this.selectedStock = stock;

        this.stockInput.value = stock.name;
        this.tickerInput.value = stock.ticker;
        this.currencyInput.value = stock.currency;

        this.stockInput.dataset.selectedTicker = stock.ticker;

        this.hideResults();

        this.stockInput.dispatchEvent(
            new CustomEvent("stock:selected", {
                bubbles: true,
                detail: stock,
            })
        );
    }

    clearSelectedStock() {
        if (!this.selectedStock) {
            return;
        }

        this.selectedStock = null;
        this.stockInput.dataset.selectedTicker = "";
        this.tickerInput.value = "";
    }

    showMessage(message) {
        this.resultsBox.innerHTML = "";

        const messageElement = document.createElement("div");
        messageElement.className = "stock-picker-message";
        messageElement.textContent = message;

        this.resultsBox.appendChild(messageElement);
        this.resultsBox.hidden = false;
    }

    hideResults() {
        this.resultsBox.hidden = true;
    }

    getCountryFlag(country) {
        const flags = {
            Denmark: "🇩🇰",
            USA: "🇺🇸",
            Netherlands: "🇳🇱",
            Sweden: "🇸🇪",
            Norway: "🇳🇴",
            Germany: "🇩🇪",
            France: "🇫🇷",
        };

        return flags[country] || "🌍";
    }

    escapeHtml(value) {
        const element = document.createElement("span");
        element.textContent = value || "";
        return element.innerHTML;
    }
}

window.stockPicker = new StockPicker({
    stockInput: "#stock",
    resultsBox: "#stock-results",
    tickerInput: "#ticker",
    currencyInput: "#currency",
    apiUrl: "/api/stocks",
});
