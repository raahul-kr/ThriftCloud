class BaseProvider:
    def parse_billing(self, file):
        raise NotImplementedError

    def detect_waste(self, data):
        raise NotImplementedError

    def generate_recommendations(self, waste):
        raise NotImplementedError

    def calculate_efficiency_score(self, data, waste):
        raise NotImplementedError

    def calculate_total_savings(self, waste):
        raise NotImplementedError