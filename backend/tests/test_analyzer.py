"""
Tests for the ThriftCloud analyzer module.
"""

from app.analyzer import (
    analyze,
    calculate_efficiency_score,
    calculate_savings_potential,
    generate_breakdown,
    generate_recommendations,
    get_categories,
    get_sample_data,
)


def test_get_sample_data_aws():
    data = get_sample_data("aws")
    assert "Amazon EC2" in data
    assert "Amazon S3" in data
    assert data["Amazon EC2"] == 1320.00


def test_get_sample_data_azure():
    data = get_sample_data("azure")
    assert "Virtual Machines" in data
    assert "Blob Storage" in data


def test_get_sample_data_invalid():
    try:
        get_sample_data("gcp")
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_analyze_aws_sample():
    result = analyze("aws")
    assert "total_cost" in result
    assert "savings_potential" in result
    assert "efficiency_score" in result
    assert "recommendations" in result
    assert "breakdown" in result
    assert result["total_cost"] > 0
    assert 0 <= result["efficiency_score"] <= 100
    assert result["input_source"] == "sample_data"


def test_analyze_azure_sample():
    result = analyze("azure")
    assert result["total_cost"] > 0
    assert len(result["breakdown"]) > 0


def test_analyze_custom_data():
    custom = {"Amazon EC2": 2000, "Amazon S3": 100}
    result = analyze("aws", custom)
    assert result["total_cost"] == 2100.0
    assert result["input_source"] == "request_payload"


def test_analyze_invalid_provider():
    try:
        analyze("gcp")
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_efficiency_score_range():
    categories = get_categories("aws")
    data = get_sample_data("aws")
    score = calculate_efficiency_score(data, categories)
    assert 0 <= score <= 100


def test_savings_potential_positive():
    categories = get_categories("aws")
    data = {"Amazon EC2": 1500}
    savings = calculate_savings_potential(data, categories)
    assert savings > 0


def test_recommendations_generated():
    categories = get_categories("aws")
    from app.analyzer import get_recommendations_map
    rec_map = get_recommendations_map("aws")
    data = {"Amazon EC2": 1500, "Amazon S3": 500}
    recs = generate_recommendations(data, categories, rec_map)
    assert len(recs) > 0


def test_breakdown_structure():
    categories = get_categories("aws")
    from app.analyzer import get_recommendations_map
    rec_map = get_recommendations_map("aws")
    data = {"Amazon EC2": 1320}
    breakdown = generate_breakdown(data, categories, rec_map)
    assert len(breakdown) == 1
    assert breakdown[0]["name"] == "Amazon EC2"
    assert breakdown[0]["category"] == "Compute"
    assert "recommendation" in breakdown[0]
