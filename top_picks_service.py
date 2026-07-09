from signal_history_service import save_signal
from ai_decision_service import get_ai_decision

def get_top_picks(ranking, limit=5):
    picks = []

    for stock in ranking[:limit]:
        score = stock["combined_score"]

        decision = get_ai_decision(score)
        
        save_signal(
            stock["stock"],
            score,
            decision["signal"],
            decision["confidence"],
            decision["risk"],
        )

        picks.append({
            "stock": stock["stock"],
            "score": score,
            **decision,
        })

    return picks