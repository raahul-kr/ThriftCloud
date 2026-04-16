"""
Service name normalization for uploaded billing data.

Maps common service name variations to canonical names
recognized by the analyzer for both AWS and Azure.
"""

AWS_SERVICE_ALIASES: dict[str, set[str]] = {
    "Amazon EC2": {"ec2", "amazon ec2", "elastic compute", "compute", "instances"},
    "Amazon S3": {"s3", "amazon s3", "simple storage", "storage", "object storage"},
    "RDS": {"rds", "amazon rds", "relational database", "database", "db"},
    "Lambda": {"lambda", "aws lambda", "serverless", "functions"},
    "CloudFront": {"cloudfront", "amazon cloudfront", "cdn", "content delivery"},
}

AZURE_SERVICE_ALIASES: dict[str, set[str]] = {
    "Virtual Machines": {"vm", "virtual machine", "virtual machines", "compute", "vms"},
    "Blob Storage": {"blob", "blob storage", "azure storage", "storage", "blobs"},
    "Azure SQL": {"sql", "azure sql", "sql database", "database", "sql db"},
    "Functions": {"functions", "azure functions", "serverless", "function app"},
}


def normalize_service_name(raw_name: str, provider: str) -> str:
    """
    Normalize an uploaded service name to its canonical form.

    Args:
        raw_name: The raw service name from the uploaded file.
        provider: 'aws' or 'azure'.

    Returns:
        Canonical service name, or the original name if no match found.
    """
    cleaned = raw_name.strip()
    lookup = cleaned.lower().replace("-", " ").replace("_", " ")

    aliases = AWS_SERVICE_ALIASES if provider == "aws" else AZURE_SERVICE_ALIASES

    for canonical, alias_set in aliases.items():
        if lookup == canonical.lower():
            return canonical
        if lookup in alias_set:
            return canonical

    return cleaned


def normalize_billing_data(billing_data: dict[str, float], provider: str) -> dict[str, float]:
    """
    Normalize all service names in billing data to canonical forms.
    Merges costs for services that resolve to the same canonical name.

    Args:
        billing_data: Raw {service: cost} from upload.
        provider: 'aws' or 'azure'.

    Returns:
        Normalized {canonical_service: total_cost} dictionary.
    """
    normalized: dict[str, float] = {}
    for raw_name, cost in billing_data.items():
        canonical = normalize_service_name(raw_name, provider)
        normalized[canonical] = round(normalized.get(canonical, 0.0) + cost, 2)
    return normalized
