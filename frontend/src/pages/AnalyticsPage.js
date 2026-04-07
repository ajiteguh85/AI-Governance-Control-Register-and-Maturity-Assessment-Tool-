import React, { useState, useEffect } from 'react';
import { analyticsAPI } from '../api/client';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#6366f1'];

function AnalyticsPage() {
  const [funnel, setFunnel] = useState([]);
  const [sources, setSources] = useState([]);
  const [trends, setTrends] = useState({ candidates: [], applications: [] });
  const [jobPerf, setJobPerf] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsAPI.funnel().catch(() => ({ data: { funnel: [] } })),
      analyticsAPI.sources().catch(() => ({ data: { sources: [] } })),
      analyticsAPI.trends().catch(() => ({ data: { candidates: [], applications: [] } })),
      analyticsAPI.jobPerformance().catch(() => ({ data: { jobs: [] } })),
    ]).then(([funnelRes, sourcesRes, trendsRes, jobPerfRes]) => {
      setFunnel(funnelRes.data.funnel);
      setSources(sourcesRes.data.sources);
      setTrends(trendsRes.data);
      setJobPerf(jobPerfRes.data.jobs);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  const sourceData = sources.map((s) => ({
    name: (s.source || 'unknown').replace('_', ' '),
    value: s.count,
  }));

  const trendData = trends.candidates.map((c, i) => ({
    month: new Date(c.month).toLocaleDateString('en', { month: 'short' }),
    candidates: c.count,
    applications: trends.applications[i]?.count || 0,
  }));

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Analytics</h1>
          <p className="page-subtitle">Recruitment performance insights</p>
        </div>
      </div>

      <div className="content-grid">
        <div className="card">
          <h3 className="card-title" style={{ marginBottom: 16 }}>Hiring Funnel</h3>
          {funnel.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={funnel} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis type="number" fontSize={12} />
                <YAxis dataKey="stage" type="category" fontSize={12} width={100} />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state"><p>No funnel data yet</p></div>
          )}
        </div>

        <div className="card">
          <h3 className="card-title" style={{ marginBottom: 16 }}>Candidate Sources</h3>
          {sourceData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={sourceData} cx="50%" cy="50%" outerRadius={100} dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                  {sourceData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state"><p>No source data yet</p></div>
          )}
        </div>
      </div>

      <div className="card" style={{ marginTop: 24 }}>
        <h3 className="card-title" style={{ marginBottom: 16 }}>Hiring Trends (6 Months)</h3>
        {trendData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis dataKey="month" fontSize={12} />
              <YAxis fontSize={12} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="candidates" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="applications" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="empty-state"><p>No trend data yet</p></div>
        )}
      </div>

      {jobPerf.length > 0 && (
        <div className="card" style={{ marginTop: 24 }}>
          <h3 className="card-title" style={{ marginBottom: 16 }}>Job Performance</h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Department</th>
                  <th>Applications</th>
                  <th>Avg Match Score</th>
                  <th>Days Open</th>
                </tr>
              </thead>
              <tbody>
                {jobPerf.map((j) => (
                  <tr key={j.id}>
                    <td style={{ fontWeight: 500 }}>{j.title}</td>
                    <td>{j.department || '-'}</td>
                    <td>{j.applications}</td>
                    <td>{j.avg_match_score != null ? `${j.avg_match_score}%` : '-'}</td>
                    <td>{j.days_open}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalyticsPage;
