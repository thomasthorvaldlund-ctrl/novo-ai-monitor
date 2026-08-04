def normalize_confidence_label(value):
    """
    Konverterer AI confidence labels til dansk standardformat.
    """

    mapping = {
        "High": "Høj",
        "Medium": "Middel",
        "Low": "Lav",

        "HIGH": "Høj",
        "MEDIUM": "Middel",
        "LOW": "Lav",

        "high": "Høj",
        "medium": "Middel",
        "low": "Lav",
    }

    if value in mapping:
        return mapping[value]

    return value