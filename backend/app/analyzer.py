"""
Cost analysis engine for ThriftCloud.

Provides billing analysis, waste detection, efficiency scoring,
and actionable recommendations for AWS and Azure.
"""

# ---------------------------------------------------------------------------
# Sample billing data
# ---------------------------------------------------------------------------

AWS_SAMPLE_DATA: dict[str, float] = {
    "Amazon EC2": 1320.00,
    "Amazon S3": 410.00,
    "RDS": 350.00,
    "Lambda": 80.00,
    "CloudFront": 60.00,
}

AZURE_SAMPLE_DATA: dict[str, float] = {
    "Virtual Machines": 1100.00,
    "Blob Storage": 380.00,
    "Azure SQL": 420.00,
    "Functions": 90.00,
}

# ---------------------------------------------------------------------------
# Service category mappings
# ---------------------------------------------------------------------------

AWS_CATEGORIES: dict[str, str] = {
    "Amazon EC2": "Compute",
    "Amazon S3": "Storage",
    "RDS": "Database",
    "Lambda": "Serverless",
    "CloudFront": "CDN",
}

AZURE_CATEGORIES: dict[str, str] = {
    "Virtual Machines": "Compute",
    "Blob Storage": "Storage",
    "Azure SQL": "Database",
    "Functions": "Serverless",
}

# ---------------------------------------------------------------------------
# Category average thresholds (used for savings calculation)
# ---------------------------------------------------------------------------

CATEGORY_AVERAGES: dict[str, float] = {
    "Compute": 800.00,
    "Storage": 300.00,
    "Database": 250.00,
    "Serverless": 100.00,
    "CDN": 80.00,
}

# ---------------------------------------------------------------------------
# Recommendation templates
# ---------------------------------------------------------------------------

AWS_RECOMMENDATIONS: dict[str, str] = {
    "Amazon EC2": "Consider Reserved Instances or Savings Plans for EC2 to reduce compute costs by up to 40%.",
    "Amazon S3": "Move infrequently accessed objects to S3 Glacier or Intelligent-Tiering to cut storage costs.",
    "RDS": "Right-size RDS instances and enable auto-scaling. Consider Aurora Serverless for variable workloads.",
    "Lambda": "Optimize Lambda memory allocation and reduce cold starts with provisioned concurrency.",
    "CloudFront": "Increase cache TTLs and enable compression to reduce origin fetches and bandwidth costs.",
}

AZURE_RECOMMENDATIONS: dict[str, str] = {
    "Virtual Machines": "Use Azure Reserved VM Instances or Spot VMs for non-critical workloads to save up to 72%.",
    "Blob Storage": "Apply lifecycle management policies to move cold data to Cool or Archive tiers automatically.",
    "Azure SQL": "Scale down vCores during off-peak hours. Use elastic pools for multi-database workloads.",
    "Functions": "Optimize function execution time and memory. Use Durable Functions for orchestration patterns.",
}


def get_sample_data(provider: str) -> dict[str, float]:
    """Return built-in sample billing data for the given provider."""
    if provider == "aws":
        return dict(AWS_SAMPLE_DATA)
    elif provider == "azure":
        return dict(AZURE_SAMPLE_DATA)
    raise ValueError(f"Unsupported provider: {provider}")


def get_categories(provider: str) -> dict[str, str]:
    """Return service-to-category mapping for the given provider."""
    if provider == "aws":
        return dict(AWS_CATEGORIES)
    return dict(AZURE_CATEGORIES)


def get_recommendations_map(provider: str) -> dict[str, str]:
    """Return service-to-recommendation mapping for the given provider."""
    if provider == "aws":
        return dict(AWS_RECOMMENDATIONS)
    return dict(AZURE_RECOMMENDATIONS)


def calculate_savings_potential(billing_data: dict[str, float], categories: dict[str, str]) -> float:
    """
    Calculate savings potential.
    For each service above its category average, savings = (cost - avg) * 0.3
    """
    total_savings = 0.0
    for service, cost in billing_data.items():
        category = categories.get(service, "Other")
        avg = CATEGORY_AVERAGES.get(category, 200.0)
        if cost > avg:
            total_savings += (cost - avg) * 0.3
    return round(total_savings, 2)


def calculate_efficiency_score(billing_data: dict[str, float], categories: dict[str, str]) -> int:
    """
    Calculate efficiency score from 0-100.
    100 = perfectly optimized, lower = more waste.
    Penalizes services exceeding category averages.
    """
    if not billing_data:
        return 100

    total_cost = sum(billing_data.values())
    if total_cost == 0:
        return 100

    total_excess = 0.0
    for service, cost in billing_data.items():
        category = categories.get(service, "Other")
        avg = CATEGORY_AVERAGES.get(category, 200.0)
        if cost > avg:
            total_excess += cost - avg

    waste_ratio = total_excess / total_cost
    score = int(100 - (waste_ratio * 100))
    return max(0, min(100, score))


def generate_recommendations(
    billing_data: dict[str, float],
    categories: dict[str, str],
    rec_map: dict[str, str],
) -> list[str]:
    """Generate actionable recommendation strings for services above threshold."""
    recs: list[str] = []
    for service, cost in billing_data.items():
        category = categories.get(service, "Other")
        avg = CATEGORY_AVERAGES.get(category, 200.0)
        if cost > avg and service in rec_map:
            recs.append(rec_map[service])
    return recs


def generate_breakdown(
    billing_data: dict[str, float],
    categories: dict[str, str],
    rec_map: dict[str, str],
) -> list[dict]:
    """Generate per-service breakdown with category and recommendation."""
    breakdown = []
    for service, cost in billing_data.items():
        category = categories.get(service, "Other")
        avg = CATEGORY_AVERAGES.get(category, 200.0)
        rec = rec_map.get(service, "No specific recommendation.")
        if cost <= avg:
            rec = f"{service} spending is within optimal range. Keep monitoring."
        breakdown.append({
            "name": service,
            "cost": cost,
            "category": category,
            "recommendation": rec,
        })
    return breakdown


def analyze(provider: str, billing_data: dict[str, float] | None = None) -> dict:
    """
    Run full cost analysis for the given provider and billing data.
    If billing_data is None, uses built-in sample data.
    """
    provider = provider.strip().lower()
    if provider not in ("aws", "azure"):
        raise ValueError(f"Unsupported provider: '{provider}'. Use 'aws' or 'azure'.")

    if billing_data is None:
        data = get_sample_data(provider)
        source = "sample_data"
    else:
        data = {k: float(v) for k, v in billing_data.items() if float(v) > 0}
        if not data:
            data = get_sample_data(provider)
            source = "sample_data"
        else:
            source = "request_payload"

    categories = get_categories(provider)
    rec_map = get_recommendations_map(provider)

    total_cost = round(sum(data.values()), 2)
    savings = calculate_savings_potential(data, categories)
    score = calculate_efficiency_score(data, categories)
    recs = generate_recommendations(data, categories, rec_map)
    breakdown = generate_breakdown(data, categories, rec_map)

    return {
        "total_cost": total_cost,
        "savings_potential": savings,
        "efficiency_score": score,
        "recommendations": recs,
        "breakdown": breakdown,
        "input_source": source,
    }
