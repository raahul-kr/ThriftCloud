from .base_provider import BaseProvider


class AzureProvider(BaseProvider):

    def parse_billing(self, file):
        return {
            "VM": 900,
            "BlobStorage": 500
        }

    def detect_waste(self, data):
        waste = []

        if data["BlobStorage"] > 400:
            waste.append({
                "resource": "BlobStorage",
                "issue": "Excess unused storage",
                "severity": "High",
                "estimated_monthly_savings": 200
            })

        return waste

    def generate_recommendations(self, waste):
        recommendations = []

        for item in waste:
            if item["resource"] == "BlobStorage":
                recommendations.append("Enable lifecycle management and delete cold data")

        return recommendations

    def calculate_efficiency_score(self, data, waste):
        base_score = 100
        total_penalty = 0

        for item in waste:
            if item["severity"] == "High":
                total_penalty += 20

        return max(base_score - total_penalty, 0)

    def calculate_total_savings(self, waste):
        return sum(item["estimated_monthly_savings"] for item in waste)