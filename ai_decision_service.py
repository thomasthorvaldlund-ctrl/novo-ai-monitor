def get_ai_decision(score):
    """
    Central AI Decision Engine.
    Alle BUY/HOLD/WATCH-signaler kommer herfra.
    """

    if score >= 80:
        return {
            "signal": "BUY",
            "stars": "⭐⭐⭐⭐⭐",
            "trend": "📈",
            "confidence": 95,
            "risk": "Low",
            "comment": "Meget stærkt samlet signal."
        }

    elif score >= 70:
        return {
            "signal": "BUY",
            "stars": "⭐⭐⭐⭐",
            "trend": "📈",
            "confidence": 85,
            "risk": "Low",
            "comment": "Stærk positiv udvikling."
        }

    elif score >= 60:
        return {
            "signal": "HOLD",
            "stars": "⭐⭐⭐",
            "trend": "➡️",
            "confidence": 70,
            "risk": "Medium",
            "comment": "Neutral til positiv udvikling."
        }

    elif score >= 50:
        return {
            "signal": "WATCH",
            "stars": "⭐⭐",
            "trend": "➡️",
            "confidence": 60,
            "risk": "Medium",
            "comment": "Bør overvåges tæt."
        }

    else:
        return {
            "signal": "REDUCE",
            "stars": "⭐",
            "trend": "📉",
            "confidence": 90,
            "risk": "High",
            "comment": "Svagt samlet signal."
        }