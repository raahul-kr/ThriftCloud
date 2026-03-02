from .aws_provider import AWSProvider
from .azure_provider import AzureProvider


def get_provider(provider_name):
    if provider_name == "aws":
        return AWSProvider()
    elif provider_name == "azure":
        return AzureProvider()
    else:
        raise ValueError("Unsupported provider")