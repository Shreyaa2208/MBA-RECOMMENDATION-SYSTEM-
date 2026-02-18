def recommend_products(rules, user_input_products, min_confidence=0.1, top_n=5):
    """
    Recommend products based on user-selected basket items.
    Always returns recommendations if possible.
    """
    recommendations = []

    # Normalize user input
    user_input_set = set([p.strip().upper() for p in user_input_products])

    # Filter rules by confidence
    filtered_rules = rules[rules["confidence"] >= min_confidence].copy()
    filtered_rules["antecedents_norm"] = filtered_rules["antecedents"].apply(lambda s: set([x.strip().upper() for x in s]))
    filtered_rules["consequents_norm"] = filtered_rules["consequents"].apply(lambda s: set([x.strip().upper() for x in s]))

    # Match rules
    for _, row in filtered_rules.iterrows():
        if row["antecedents_norm"] & user_input_set:
            for item in row["consequents_norm"]:
                if item not in user_input_set:
                    recommendations.append((item, row["confidence"], row["lift"]))

    # Fallback: top rules if nothing matched
    if not recommendations:
        fallback_rules = rules.copy()
        fallback_rules["consequents_norm"] = fallback_rules["consequents"].apply(lambda s: set([x.strip().upper() for x in s]))
        for _, row in fallback_rules.sort_values(by=["lift", "confidence"], ascending=False).head(top_n*2).iterrows():
            for item in row["consequents_norm"]:
                if item not in user_input_set:
                    recommendations.append((item, row["confidence"], row["lift"]))

    # Remove duplicates and sort
    seen = set()
    unique_recommendations = []
    for item in recommendations:
        if item[0] not in seen:
            unique_recommendations.append(item)
            seen.add(item[0])

    unique_recommendations.sort(key=lambda x: (x[2], x[1]), reverse=True)

    return unique_recommendations[:top_n]