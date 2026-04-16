"""
Tests for the ThriftCloud parser module.
"""

from app.parser import parse_file, ParseError


def test_parse_csv():
    csv_content = b"service,cost\nEC2,1300\nS3,400\n"
    result = parse_file(csv_content, "billing.csv")
    assert result["EC2"] == 1300.0
    assert result["S3"] == 400.0


def test_parse_txt():
    txt_content = b"service,cost\nLambda,80\nRDS,350\n"
    result = parse_file(txt_content, "billing.txt")
    assert result["Lambda"] == 80.0


def test_parse_json_object():
    json_content = b'{"billing_data": {"EC2": 1300, "S3": 400}}'
    result = parse_file(json_content, "billing.json")
    assert result["EC2"] == 1300.0


def test_parse_json_array():
    json_content = b'[{"service": "EC2", "cost": 1300}, {"service": "S3", "cost": 400}]'
    result = parse_file(json_content, "billing.json")
    assert result["EC2"] == 1300.0
    assert result["S3"] == 400.0


def test_parse_empty_file():
    try:
        parse_file(b"", "empty.csv")
        assert False, "Should raise ParseError"
    except ParseError:
        pass


def test_parse_unsupported_extension():
    try:
        parse_file(b"data", "billing.xlsx")
        assert False, "Should raise ParseError"
    except ParseError:
        pass


def test_parse_invalid_json():
    try:
        parse_file(b"{invalid json", "billing.json")
        assert False, "Should raise ParseError"
    except ParseError:
        pass


def test_parse_csv_with_currency():
    csv_content = b"service,cost\nEC2,$1300\nS3,$400\n"
    result = parse_file(csv_content, "billing.csv")
    assert result["EC2"] == 1300.0
