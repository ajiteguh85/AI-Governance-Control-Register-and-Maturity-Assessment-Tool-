import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analyticsAPI, candidatesAPI, jobsAPI } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#6366f1', '#14b8a6'];

const STAGE_LABELS = {
  new: 'New', screening: 'Screening', interview: 'Interview',
  assessment: 'Assessment', offer: 'Offer', hired: 'Hired', rejected: 'Rejected',
};

function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [recentCandidates, setRecentCandidates] = useState([]);
  const [recentJobs, setRecentJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsAPI.dashboard().catch(() => ({ data: null })),
      candidatesAPI.list({ page_size: 5 }).catch(() => ({ data: { results: [] } })),
      jobsAPI.list({ page_size: 5, status: 'open' }).catch(() => ({ data: { results: [] } })),
    ]).then(([statsRes, candidatesRes, jobsRes]) => {
      setStats(statsRes.data);
      setRecentCandidates(candidatesRes.data?.results || []);
      setRecentJobs(jobsRes.data?.results || []);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  const pipelineData = stats?.pipeline?.map((p) => ({
    name: STAGE_LABELS[p.stage] || p.stage,
    value: p.count,
  })) || [];

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Overview of your recruitment pipeline</p>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard label="Total Candidates" value={stats?.total_candidates || 0} color="#3b82f6" />
        <StatCard label="Open Jobs" value={stats?.open_jobs || 0} color="#10b981" />
        <StatCard label="Active Applications" value={stats?.active_applications || 0} color="#f59e0b" />
        <StatCard label="Interviews Scheduled" value={stats?.interviews_scheduled || 0} color="#8b5cf6" />
      </div>

      <div className="content-grid">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Candidate Pipeline</h3>
          </div>
          {pipelineData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={pipelineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis dataKey="name" fontSize={12} />
                <YAxis fontSize={12} />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state"><p>No pipeline data yet</p></div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Candidate Sources</h3>
          </div>
          {pipelineData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={pipelineData} cx="50%" cy="50%" outerRadius={100} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                  {pipelineData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state"><p>No source data yet</p></div>
          )}
        </div>
      </div>

      <div className="content-grid" style={{ marginTop: 24 }}>
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Recent Candidates</h3>
            <Link to="/candidates" className="btn btn-secondary btn-sm">View All</Link>
          </div>
          {recentCandidates.length > 0 ? (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Title</th>
                    <th>Stage</th>
                  </tr>
                </thead>
                <tbody>
                  {recentCandidates.map((c) => (
                    <tr key={c.id}>
                      <td><Link to={`/candidates/${c.id}`}>{c.first_name} {c.last_name}</Link></td>
                      <td>{c.current_title || '-'}</td>
                      <td><span className={`badge badge-${getStageBadge(c.stage)}`}>{STAGE_LABELS[c.stage] || c.stage}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state"><p>No candidates yet</p></div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Open Jobs</h3>
            <Link to="/jobs" className="btn btn-secondary btn-sm">View All</Link>
          </div>
          {recentJobs.length > 0 ? (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Department</th>
                    <th>Applications</th>
                  </tr>
                </thead>
                <tbody>
                  {recentJobs.map((j) => (
                    <tr key={j.id}>
                      <td><Link to={`/jobs/${j.id}`}>{j.title}</Link></td>
                      <td>{j.department || '-'}</td>
                      <td>{j.application_count || 0}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state"><p>No open jobs yet</p></div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }) {
  return (
    <div className="stat-card">
      <div className="stat-card-header">
        <span className="stat-label">{label}</span>
        <div className="stat-icon" style={{ background: `${color}15` }}>
          <div style={{ width: 12, height: 12, borderRadius: '50%', background: color }} />
        </div>
      </div>
      <div className="stat-value">{value}</div>
    </div>
  );
}

function getStageBadge(stage) {
  const map = {
    new: 'info', screening: 'info', interview: 'warning',
    assessment: 'warning', offer: 'success', hired: 'success', rejected: 'danger',
  };
  return map[stage] || 'gray';
}

export default DashboardPage;
