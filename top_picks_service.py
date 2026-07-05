def get_top_picks(ranking, limit=5):
    top_items = ranking[:limit]

    results = []

    for index, item in enumerate(top_items, start=1):
        results.append({
            "rank": index,
            "stock": item.get("stock"),
            "score": item.get("combined_score", item.get("score", 0)),
            "rating": item.get("rating", ""),
        })

    return results