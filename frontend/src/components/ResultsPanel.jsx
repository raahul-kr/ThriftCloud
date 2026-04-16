import React from 'react';
import { ResponsiveContainer, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Bar } from 'recharts';
import { DollarSign, Percent, TrendingDown, AlertCircle, CheckCircle } from 'lucide-react';

export default function ResultsPanel({ data, provider }) {
  if (!data) return null;

  const chartData = data.breakdown.map(item => ({
    service: item.name,
    cost: item.cost,
  }));

  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--success)';
    if (score >= 50) return 'var(--warning)';
    return 'var(--danger)';
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Value Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
        <MetricCard 
          title="Total Monthly Cost" 
          value={`$${data.total_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          icon={<DollarSign color="var(--accent-primary)" size={24} />}
        />
        <MetricCard 
          title="Potential Savings" 
          value={`$${data.savings_potential.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          valueColor="var(--success)"
          icon={<TrendingDown color="var(--success)" size={24} />}
        />
        <MetricCard 
          title="Efficiency Score" 
          value={`${data.efficiency_score}/100`}
          valueColor={getScoreColor(data.efficiency_score)}
          icon={<Percent color={getScoreColor(data.efficiency_score)} size={24} />}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Chart */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '24px', color: 'var(--text-primary)' }}>Cost Breakdown</h3>
          <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer>
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                <XAxis dataKey="service" stroke="var(--text-muted)" fontSize={12} tickLine={false} />
                <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} tickFormatter={val => `$${val}`} />
                <Tooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                  contentStyle={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px' }}
                />
                <Bar 
                  dataKey="cost" 
                  fill={provider === 'aws' ? 'var(--accent-aws)' : 'var(--accent-azure)'} 
                  radius={[4, 4, 0, 0]} 
                  barSize={40}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recommendations */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '24px', color: 'var(--text-primary)' }}>Top Recommendations</h3>
          {data.recommendations.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {data.recommendations.map((rec, i) => (
                <div key={i} style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                  <div style={{ marginTop: '2px' }}><AlertCircle size={18} color="var(--warning)" /></div>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{rec}</p>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '80%', gap: '12px', color: 'var(--text-muted)' }}>
              <CheckCircle size={48} color="var(--success)" />
              <p>Your environment is highly optimized!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon, valueColor = 'var(--text-primary)' }) {
  return (
    <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontWeight: 500, marginBottom: '8px' }}>{title}</p>
        <h2 style={{ color: valueColor, fontSize: '2rem', fontWeight: 700 }}>{value}</h2>
      </div>
      <div style={{ background: 'rgba(255,255,255,0.05)', width: '48px', height: '48px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {icon}
      </div>
    </div>
  );
}
