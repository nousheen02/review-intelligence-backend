def get_insights(df):
    insights = []
    if df[df["sentiment"] == "Negative"]["review"].str.contains("delivery", case=False).sum() > 5:
        insights.append("🚚 Many customers are unhappy with delivery")
    if df[df["sentiment"] == "Positive"]["review"].str.contains("quality", case=False).sum() > 10:
        insights.append("⭐ Product quality is praised")
    return insights
