import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Improved, more distinct blue/cyan/purple palette
const COLORS = [
  '#2563eb', // strong blue
  '#60a5fa', // light blue
  '#0ea5e9', // cyan
  '#38bdf8', // sky blue
  '#818cf8', // light indigo
  '#6366f1', // indigo
  '#1e40af', // deep blue
  '#9333ea', // purple
  '#06b6d4', // teal/cyan
  '#f472b6'  // pink for max contrast
];

// Custom label function with inside/outside logic and ellipsis for long names
const renderCustomizedLabel = ({ name, weight, cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
  const RADIAN = Math.PI / 180;
  const radius = innerRadius + (outerRadius - innerRadius) * (percent > 0.08 ? 0.6 : 1.1);
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  // Truncate long names for label
  const displayName = name.length > 18 ? name.slice(0, 16) + '…' : name;
  return (
    <text
      x={x}
      y={y}
      fill={percent > 0.08 ? '#222' : '#2563eb'}
      textAnchor={x > cx ? 'start' : 'end'}
      dominantBaseline="central"
      fontSize={percent > 0.08 ? 17 : 13}
      fontWeight={percent > 0.08 ? 700 : 500}
      stroke={percent > 0.08 ? 'white' : 'none'}
      strokeWidth={percent > 0.08 ? 0.5 : 0}
    >
      {percent > 0.08 ? `${displayName}: ${(weight * 100).toFixed(1)}%` : `${(weight * 100).toFixed(1)}%`}
    </text>
  );
};

function PortfolioPieChart({ selectedStocks, onBack }) {
  const [allocations, setAllocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    setError('');
    fetch('http://localhost:5000/api/portfolio/optimize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stocks: selectedStocks, investment_amount: 10000 }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.allocations) {
          setAllocations(data.allocations);
        } else {
          setError(data.error || 'Failed to get portfolio allocations.');
        }
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to connect to backend.');
        setLoading(false);
      });
  }, [selectedStocks]);

  if (loading) return <div className="text-center text-xl text-white">Loading portfolio...</div>;
  if (error) return <div className="text-center text-red-500">{error}</div>;

  return (
    <section className="min-h-screen flex flex-col items-center justify-center font-mono bg-gradient-to-r from-cyan-500 via-indigo-500 to-sky-500">
      <div className="bg-white rounded-2xl shadow-2xl p-10 flex flex-col items-center" style={{ minWidth: 540, minHeight: 620 }}>
        <h1 className="text-3xl font-bold text-blue-700 mb-6">Your Optimized Portfolio</h1>
        <ResponsiveContainer width={520} height={520}>
          <PieChart margin={{ top: 24, right: 24, left: 24, bottom: 24 }}>
            <Pie
              data={allocations}
              dataKey="weight"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={80}
              outerRadius={180}
              label={renderCustomizedLabel}
              labelLine={true}
              minAngle={3}
              paddingAngle={2}
            >
              {allocations.map((entry, idx) => (
                <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${(value * 100).toFixed(2)}%`} contentStyle={{ fontSize: 16 }} />
            <Legend layout="horizontal" verticalAlign="bottom" align="center" wrapperStyle={{ marginTop: 96, fontSize: 16, maxWidth: 480, whiteSpace: 'normal', textAlign: 'center' }} iconSize={18} />
          </PieChart>
        </ResponsiveContainer>
        <button
          onClick={onBack}
          className="mt-8 px-6 py-2 rounded bg-blue-500 text-white font-semibold hover:bg-blue-700 transition text-lg"
        >
          Back
        </button>
      </div>
    </section>
  );
}

export default PortfolioPieChart; 