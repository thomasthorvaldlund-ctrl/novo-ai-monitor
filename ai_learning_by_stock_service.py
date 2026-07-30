from collections import defaultdict

from ai_portfolio_performance_service import get_portfolio_performance


SUCCESS = {
    "God beslutning",
    "God risikostyring",
    "Stabil vurdering",
    "Positiv udvikling",
}


def get_learning_by_stock():
    performance = get_portfolio_performance()

    stocks = defaultdict(
        lambda: {
            "total": 0,
            "correct": 0,
            "average_score": 0,
            "score_sum": 0,
        }
    )

    for row in performance:
        stock = row.get("stock", "Ukendt")
        stats = stocks[stock]

        stats["total"] += 1
        stats["score_sum"] += row.get("score", 0)

        if row.get("ai_result") in SUCCESS:
            stats["correct"] += 1

    result = []

    for stock, stats in sorted(stocks.items()):
        total = stats["total"]

        accuracy = round(stats["correct"] / total * 100, 1) if total else 0.0
        average_score = round(stats["score_sum"] / total, 1) if total else 0.0

        result.append(
            {
                "stock": stock,
                "total": total,
                "correct": stats["correct"],
                "accuracy": accuracy,
                "average_score": average_score,
            }
        )

    return result
