import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { jobsAPI, applicationsAPI, aiAPI } from '../api/client';
import toast from 'react-hot-toast';

const STATUS_LABELS = { draft: 'Draft', open: 'Open', paused: 'Paused', closed: 'Closed', filled: 'Filled' };
const APP_STATUS_LABELS = {
  applied: 'Applied', reviewing: 'Reviewing', shortlisted: 'Shortlisted',
  interviewing: 'Interviewing', offered: 'Offered', accepted: 'Accepted',
  rejected: 'Rejected', withdrawn: 'Withdrawn',
};
const APP_BADGE = {
  applied: 'gray', reviewing: 'info', shortlisted: 'info', interviewing: 'warning',
  offered: 'success', accepted: 'success', rejected: 'danger', withdrawn: 'danger',
};

function JobDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [applications, setApplications] = useState([]);
  const [rankings, setRankings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rankingLoading, setRankingLoading] = useState(false);

  useEffect(() => {
    Promise.all([
      jobsAPI.get(id),
      applicationsAPI.list({ job: id }),
    ]).then(([jobRes, appRes]) => {
      setJob(jobRes.data);
      setApplications(appRes.data?.results || appRes.data || []);
      setLoading(false);
    }).catch(() => {
      toast.error('Job not found');
      navigate('/jobs');
    });
  }, [id, navigate]);

  const handlePublish = async () => {
    try {
      const { data } = await jobsAPI.publish(id);
      setJob(data);
      toast.success('Job published!');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to publish');
    }
  };

  const handleClose = async () => {
    try {
      const { data } = await jobsAPI.close(id);
      setJob(data);
      toast.success('Job closed');
    } catch {
      toast.error('Failed to close job');
    }
  };

  const handleRankCandidates = async () => {
    setRankingLoading(true);
    try {
      const { data } = await aiAPI.rankCandidates(id);
      setRankings(data.rankings);
      toast.success(`Ranked ${data.rankings.length} candidates`);
    } catch {
      toast.error('Failed to rank candidates');
    } finally {
      setRankingLoading(false);
    }
  };

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;
  if (!job) return null;

  return (
    <div>
      <div className="page-header">
        <div>
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/jobs')} style={{ marginBottom: 8 }}>
            &larr; Back to Jobs
          </button>
          <h1 className="page-title">{job.title}</h1>
          <p className="page-subtitle">
            {job.department} &middot; {job.location} &middot; {job.remote_policy} &middot;
            <span className={`badge badge-${job.status === 'open' ? 'success' : 'gray'}`} style={{ marginLeft: 8 }}>
              {STATUS_LABELS[job.status]}
            </span>
          </p>
        </div>
        <div className="page-actions">
          <button className="btn btn-secondary" onClick={handleRankCandidates} disabled={rankingLoading}>
            {rankingLoading ? 'Ranking...' : 'AI Rank Candidates'}
          </button>
          {job.status === 'draft' && <button className="btn btn-primary" onClick={handlePublish}>Publish</button>}
          {job.status === 'open' && <button className="btn btn-danger" onClick={handleClose}>Close</button>}
        </div>
      </div>

      <div className="content-grid">
        <div className="card">
          <h3 className="card-title" style={{ marginBottom: 16 }}>Job Details</h3>
          <InfoRow label="Type" value={(job.job_type || '').replace('_', ' ')} />
          <InfoRow label="Experience" value={job.experience_level} />
          <InfoRow label="Remote Policy" value={job.remote_policy} />
          {job.salary_min && <InfoRow label="Salary Range" value={`${job.salary_currency} ${Number(job.salary_min).toLocaleString()} - ${Number(job.salary_max).toLocaleString()}`} />}
          <InfoRow label="Applications" value={applications.length} />
          <InfoRow label="Created" value={new Date(job.created_at).toLocaleDateString()} />
          {job.required_skills?.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <span style={{ fontSize: 13, color: '#6b7280' }}>Required Skills</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>
                {job.required_skills.map((s, i) => <span key={i} className="badge badge-info">{s}</span>)}
              </div>
            </div>
          )}
        </div>

        <div className="card">
          <h3 className="card-title" style={{ marginBottom: 16 }}>Description</h3>
          <div style={{ fontSize: 14, lineHeight: 1.7, color: '#374151', whiteSpace: 'pre-wrap' }}>
            {job.description || 'No description provided.'}
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 24 }}>
        <div className="card-header">
          <h3 className="card-title">Applications ({applications.length})</h3>
        </div>
        {applications.length === 0 ? (
          <div className="empty-state"><p>No applications yet</p></div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Status</th>
                  <th>AI Match</th>
                  <th>Applied</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => (
                  <tr key={app.id}>
                    <td style={{ fontWeight: 500 }}>{app.candidate_name || 'Unknown'}</td>
                    <td><span className={`badge badge-${APP_BADGE[app.status]}`}>{APP_STATUS_LABELS[app.status]}</span></td>
                    <td>
                      {app.ai_match_score != null ? (
                        <span style={{ fontWeight: 500, color: app.ai_match_score >= 70 ? '#10b981' : '#f59e0b' }}>
                          {app.ai_match_score}%
                        </span>
                      ) : '-'}
                    </td>
                    <td style={{ color: '#6b7280', fontSize: 13 }}>{new Date(app.applied_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {rankings && (
        <div className="card" style={{ marginTop: 24 }}>
          <div className="card-header">
            <h3 className="card-title">AI Candidate Rankings</h3>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Candidate</th>
                  <th>Title</th>
                  <th>Overall</th>
                  <th>Skills</th>
                  <th>Experience</th>
                  <th>Matched Skills</th>
                </tr>
              </thead>
              <tbody>
                {rankings.map((r, i) => (
                  <tr key={r.candidate_id}>
                    <td style={{ fontWeight: 600, color: '#6b7280' }}>{i + 1}</td>
                    <td style={{ fontWeight: 500 }}>{r.name}</td>
                    <td style={{ color: '#6b7280' }}>{r.current_title || '-'}</td>
                    <td>
                      <span style={{ fontWeight: 600, color: r.scores.overall_score >= 70 ? '#10b981' : r.scores.overall_score >= 40 ? '#f59e0b' : '#ef4444' }}>
                        {r.scores.overall_score}%
                      </span>
                    </td>
                    <td>{r.scores.skill_match}%</td>
                    <td>{r.scores.experience_score}%</td>
                    <td>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                        {r.scores.matched_skills?.slice(0, 3).map((s, j) => (
                          <span key={j} className="badge badge-success" style={{ fontSize: 11 }}>{s}</span>
                        ))}
                        {(r.scores.matched_skills?.length || 0) > 3 && (
                          <span className="badge badge-gray" style={{ fontSize: 11 }}>+{r.scores.matched_skills.length - 3}</span>
                        )}
                      </div>
                    </td>
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

function InfoRow({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f9fafb' }}>
      <span style={{ fontSize: 13, color: '#6b7280' }}>{label}</span>
      <span style={{ fontSize: 14, fontWeight: 500 }}>{value}</span>
    </div>
  );
}

export default JobDetailPage;
