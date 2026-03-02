from flask import Flask, jsonify, request
from flask_cors import CORS
from providers.provider_factory import get_provider

app = Flask(__name__)
CORS(app)

@app.route("/api/health")
def health():
    return jsonify({"status": "ThriftCloud Backend Running"})

@app.route("/api/analyze", methods=["POST"])
def analyze():
    # 1. Extract provider from request
    provider_name = request.json.get("provider")
    provider = get_provider(provider_name)

    # 2. Process data through the provider logic
    # Note: Passing 'None' assumes the provider handles data fetching internally
    data = provider.parse_billing(None)
    waste = provider.detect_waste(data)
    
    # 3. Use modified logic: recommendations based on waste, score based on both
    recommendations = provider.generate_recommendations(waste)
    score = provider.calculate_efficiency_score(data, waste)
    total_savings = provider.calculate_total_savings(waste)

    # 4. Return the enriched response
    return jsonify({
        "billing_data": data,
        "optimization_insights": waste,
        "recommendations": recommendations,
        "efficiency_score": score,
        "estimated_monthly_savings": total_savings,
        "projected_6_month_savings": total_savings * 6
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)