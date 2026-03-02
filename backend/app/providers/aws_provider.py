from .base_provider import BaseProvider


class AWSProvider(BaseProvider):

    def parse_billing(self, file):
        return {
            "EC2": 1200,
            "S3": 400,
            "RDS": 800
        }

    def detect_waste(self, data):
        waste = []

        if data["EC2"] > 1000:
            waste.append({
                "resource": "EC2",
                "issue": "Overprovisioned compute instances",
                "severity": "High",
                "estimated_monthly_savings": 300
            })

        if data["S3"] > 300:
            waste.append({
                "resource": "S3",
                "issue": "Unused storage objects",
                "severity": "Medium",
                "estimated_monthly_savings": 120
            })

        return waste

    def generate_recommendations(self, waste):
        recommendations = []

        for item in waste:
            if item["resource"] == "EC2":
                recommendations.append("Resize EC2 instances or move to reserved instances")
            if item["resource"] == "S3":
                recommendations.append("Enable lifecycle policy and delete unused objects")

        return recommendations

    def calculate_efficiency_score(self, data, waste):
        base_score = 100

        total_penalty = 0
        for item in waste:
            if item["severity"] == "High":
                total_penalty += 20
            elif item["severity"] == "Medium":
                total_penalty += 10

        return max(base_score - total_penalty, 0)

    def calculate_total_savings(self, waste):
        return sum(item["estimated_monthly_savings"] for item in waste)