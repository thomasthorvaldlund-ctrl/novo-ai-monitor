from collections import defaultdict

from ai_portfolio_performance_service import get_portfolio_performance


SUCCESS = {
    "God beslutning",
    "God risikostyring",
    "Stabil vurdering",
    "Positiv udvikling",
}


def get_signal_accuracy():
    performance = get_portfolio_performance()

    signals = defaultdict(lambda: {"total": 0, "correct": 0})

    for row in performance:
        signal = row.get("action", "UNKNOWN")
        stats = signals[signal]

        stats["total"] += 1

        if row.get("ai_result") in SUCCESS:
            stats["correct"] += 1

    result = []

    for signal in sorted(signals):
        total = signals[signal]["total"]
        correct = signals[signal]["correct"]

        accuracy = round(correct / total * 100, 1) if total else 0.0

        result.append(
            {
                "signal": signal,
                "total": total,
                "correct": correct,
                "accuracy": accuracy,
            }
        )

    return result
