import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { candidatesAPI } from '../api/client';
import toast from 'react-hot-toast';

const STAGES = ['', 'new', 'screening', 'interview', 'assessment', 'offer', 'hired', 'rejected'];
const STAGE_LABELS = {
  new: 'New', screening: 'Screening', interview: 'Interview',
  assessment: 'Assessment', offer: 'Offer', hired: 'Hired', rejected: 'Rejected',
};
const SOURCES = ['', 'direct', 'referral', 'linkedin', 'job_board', 'agency', 'ats_import', 'crm_import'];

function CandidatesPage() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [stageFilter, setStageFilter] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  const fetchCandidates = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (stageFilter) params.stage = stageFilter;
      if (sourceFilter) params.source = sourceFilter;
      const { data } = await candidatesAPI.list(params);
      setCandidates(data.results || data);
    } catch {
      toast.error('Failed to load candidates');
    } finally {
      setLoading(false);
    }
  }, [search, stageFilter, sourceFilter]);

  useEffect(() => {
    const timer = setTimeout(fetchCandidates, 300);
    return () => clearTimeout(timer);
  }, [fetchCandidates]);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Candidates</h1>
          <p className="page-subtitle">{candidates.length} candidates in your pipeline</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ Add Candidate</button>
      </div>

      <div className="filters-bar">
        <div className="search-input-wrapper">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
          </svg>
          <input className="search-input" placeholder="Search candidates..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <select className="filter-select" value={stageFilter} onChange={(e) => setStageFilter(e.target.value)}>
          <option value="">All Stages</option>
          {STAGES.filter(Boolean).map((s) => <option key={s} value={s}>{STAGE_LABELS[s]}</option>)}
        </select>
        <select className="filter-select" value={sourceFilter} onChange={(e) => setSourceFilter(e.target.value)}>
          <option value="">All Sources</option>
          {SOURCES.filter(Boolean).map((s) => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="loading-container"><div className="spinner" /></div>
      ) : candidates.length === 0 ? (
        <div className="card"><div className="empty-state"><h3>No candidates found</h3><p>Try adjusting your filters or add a new candidate</p></div></div>
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Current Title</th>
                  <th>Experience</th>
                  <th>Stage</th>
                  <th>AI Score</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map((c) => (
                  <tr key={c.id} onClick={() => navigate(`/candidates/${c.id}`)} style={{ cursor: 'pointer' }}>
                    <td style={{ fontWeight: 500 }}>{c.first_name} {c.last_name}</td>
                    <td style={{ color: '#6b7280' }}>{c.email}</td>
                    <td>{c.current_title || '-'}</td>
                    <td>{c.years_experience ? `${c.years_experience} yrs` : '-'}</td>
                    <td><span className={`badge badge-${getStageBadge(c.stage)}`}>{STAGE_LABELS[c.stage]}</span></td>
                    <td>
                      {c.ai_score != null ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div className="score-bar" style={{ width: 60 }}>
                            <div className="score-bar-fill" style={{ width: `${c.ai_score}%`, background: getScoreColor(c.ai_score) }} />
                          </div>
                          <span style={{ fontSize: 12, color: '#6b7280' }}>{c.ai_score}%</span>
                        </div>
                      ) : '-'}
                    </td>
                    <td><span className="badge badge-gray">{(c.source || '').replace('_', ' ')}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showModal && <AddCandidateModal onClose={() => setShowModal(false)} onSuccess={() => { setShowModal(false); fetchCandidates(); }} />}
    </div>
  );
}

function AddCandidateModal({ onClose, onSuccess }) {
  const [form, setForm] = useState({
    first_name: '', last_name: '', email: '', phone: '',
    current_title: '', current_company: '', location: '',
    years_experience: 0, source: 'direct',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await candidatesAPI.create(form);
      toast.success('Candidate added!');
      onSuccess();
    } catch (err) {
      const errors = err.response?.data;
      toast.error(errors ? Object.values(errors)[0] : 'Failed to add candidate');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">Add Candidate</h3>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="form-group">
              <label className="form-label">First Name *</label>
              <input className="form-input" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} required />
            </div>
            <div className="form-group">
              <label className="form-label">Last Name *</label>
              <input className="form-input" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} required />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Email *</label>
            <input type="email" className="form-input" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          </div>
          <div className="form-group">
            <label className="form-label">Phone</label>
            <input className="form-input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="form-group">
              <label className="form-label">Current Title</label>
              <input className="form-input" value={form.current_title} onChange={(e) => setForm({ ...form, current_title: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">Current Company</label>
              <input className="form-input" value={form.current_company} onChange={(e) => setForm({ ...form, current_company: e.target.value })} />
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="form-group">
              <label className="form-label">Location</label>
              <input className="form-input" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">Years Experience</label>
              <input type="number" className="form-input" value={form.years_experience} onChange={(e) => setForm({ ...form, years_experience: parseInt(e.target.value) || 0 })} />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Source</label>
            <select className="form-input form-select" value={form.source} onChange={(e) => setForm({ ...form, source: e.target.value })}>
              <option value="direct">Direct Application</option>
              <option value="referral">Referral</option>
              <option value="linkedin">LinkedIn</option>
              <option value="job_board">Job Board</option>
              <option value="agency">Agency</option>
            </select>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Adding...' : 'Add Candidate'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function getStageBadge(stage) {
  const map = { new: 'info', screening: 'info', interview: 'warning', assessment: 'warning', offer: 'success', hired: 'success', rejected: 'danger' };
  return map[stage] || 'gray';
}

function getScoreColor(score) {
  if (score >= 70) return '#10b981';
  if (score >= 40) return '#f59e0b';
  return '#ef4444';
}

export default CandidatesPage;
