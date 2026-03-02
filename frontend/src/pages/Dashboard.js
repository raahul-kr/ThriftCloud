import React, { useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

function Dashboard() {
  const [provider, setProvider] = useState("aws");
  const [data, setData] = useState(null);

  const analyze = async () => {
    const response = await axios.post(
      "/api/analyze",
      { provider: provider }
    );
    setData(response.data);
  };

  const formatChartData = () => {
    if (!data) return [];
    return Object.entries(data.billing_data).map(([key, value]) => ({
      service: key,
      cost: value
    }));
  };

  return (
    <div style={{ padding: "40px" }}>
      <h1>ThriftCloud Dashboard</h1>

      <select
        value={provider}
        onChange={(e) => setProvider(e.target.value)}
      >
        <option value="aws">AWS</option>
        <option value="azure">Azure</option>
      </select>

      <button onClick={analyze} style={{ marginLeft: "10px" }}>
        Analyze
      </button>

      {data && (
        <div style={{ marginTop: "40px" }}>
          <h2>Efficiency Score: {data.efficiency_score}</h2>

          <h3>Estimated Monthly Savings: ₹{data.estimated_monthly_savings}</h3>
          <h3>
            Projected 6 Month Savings: ₹{data.projected_6_month_savings}
          </h3>

          <BarChart
            width={500}
            height={300}
            data={formatChartData()}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="service" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="cost" fill="#8884d8" />
          </BarChart>

          <h3>Optimization Insights:</h3>
          <ul>
            {data.optimization_insights.map((item, index) => (
              <li key={index}>
                <strong>{item.resource}</strong> — {item.issue}
                (Severity: {item.severity})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default Dashboard;