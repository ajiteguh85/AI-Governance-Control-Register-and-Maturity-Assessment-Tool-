import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { jobsAPI, aiAPI } from '../api/client';
import toast from 'react-hot-toast';

const STATUS_LABELS = { draft: 'Draft', open: 'Open', paused: 'Paused', closed: 'Closed', filled: 'Filled' };
const STATUS_BADGE = { draft: 'gray', open: 'success', paused: 'warning', closed: 'danger', filled: 'info' };

function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      const { data } = await jobsAPI.list(params);
      setJobs(data.results || data);
    } catch {
      toast.error('Failed to load jobs');
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter]);

  useEffect(() => {
    const timer = setTimeout(fetchJobs, 300);
    return () => clearTimeout(timer);
  }, [fetchJobs]);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Jobs</h1>
          <p className="page-subtitle">{jobs.length} job positions</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ Create Job</button>
      </div>

      <div className="filters-bar">
        <div className="search-input-wrapper">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
          </svg>
          <input className="search-input" placeholder="Search jobs..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <select className="filter-select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All Status</option>
          {Object.entries(STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="loading-container"><div className="spinner" /></div>
      ) : jobs.length === 0 ? (
        <div className="card"><div className="empty-state"><h3>No jobs found</h3><p>Create your first job posting</p></div></div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: 16 }}>
          {jobs.map((job) => (
            <div key={job.id} className="card" style={{ cursor: 'pointer' }} onClick={() => navigate(`/jobs/${job.id}`)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <div>
                  <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>{job.title}</h3>
                  <p style={{ fontSize: 13, color: '#6b7280' }}>{job.department || 'No department'} &middot; {job.location}</p>
                </div>
                <span className={`badge badge-${STATUS_BADGE[job.status]}`}>{STATUS_LABELS[job.status]}</span>
              </div>
              <div style={{ display: 'flex', gap: 16, fontSize: 13, color: '#6b7280' }}>
                <span>{job.job_type?.replace('_', ' ')}</span>
                <span>{job.remote_policy}</span>
                <span>{job.application_count || 0} applications</span>
              </div>
              {job.salary_min && job.salary_max && (
                <p style={{ fontSize: 13, color: '#374151', marginTop: 8, fontWeight: 500 }}>
                  {job.salary_currency} {Number(job.salary_min).toLocaleString()} - {Number(job.salary_max).toLocaleString()}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {showModal && <CreateJobModal onClose={() => setShowModal(false)} onSuccess={() => { setShowModal(false); fetchJobs(); }} />}
    </div>
  );
}

function CreateJobModal({ onClose, onSuccess }) {
  const [form, setForm] = useState({
    title: '', department: '', location: '', remote_policy: 'hybrid',
    job_type: 'full_time', experience_level: 'mid', description: '',
    required_skills: [], salary_min: '', salary_max: '', salary_currency: 'EUR',
  });
  const [skillInput, setSkillInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiGenerating, setAiGenerating] = useState(false);

  const handleAddSkill = () => {
    if (skillInput.trim() && !form.required_skills.includes(skillInput.trim())) {
      setForm({ ...form, required_skills: [...form.required_skills, skillInput.trim()] });
      setSkillInput('');
    }
  };

  const handleRemoveSkill = (skill) => {
    setForm({ ...form, required_skills: form.required_skills.filter((s) => s !== skill) });
  };

  const handleGenerateDescription = async () => {
    if (!form.title) { toast.error('Enter a title first'); return; }
    setAiGenerating(true);
    try {
      const { data } = await aiAPI.generateJobDescription({
        title: form.title, requirements: form.required_skills, department: form.department,
      });
      setForm({ ...form, description: data.description });
      toast.success('Description generated!');
    } catch {
      toast.error('Failed to generate description');
    } finally {
      setAiGenerating(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = { ...form };
      if (!payload.salary_min) delete payload.salary_min;
      if (!payload.salary_max) delete payload.salary_max;
      await jobsAPI.create(payload);
      toast.success('Job created!');
      onSuccess();
    } catch (err) {
      toast.error('Failed to create job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 700 }}>
        <div className="modal-header">
          <h3 className="modal-title">Create Job</h3>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Job Title *</label>
            <input className="form-input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="form-group">
              <label className="form-label">Department</label>
              <input className="form-input" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">Location *</label>
              <input className="form-input" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} required />
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
            <div className="form-group">
              <label className="form-label">Type</label>
              <select className="form-input form-select" value={form.job_type} onChange={(e) => setForm({ ...form, job_type: e.target.value })}>
                <option value="full_time">Full Time</option>
                <option value="part_time">Part Time</option>
                <option value="contract">Contract</option>
                <option value="freelance">Freelance</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Remote Policy</label>
              <select className="form-input form-select" value={form.remote_policy} onChange={(e) => setForm({ ...form, remote_policy: e.target.value })}>
                <option value="onsite">On-site</option>
                <option value="hybrid">Hybrid</option>
                <option value="remote">Remote</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Experience Level</label>
              <select className="form-input form-select" value={form.experience_level} onChange={(e) => setForm({ ...form, experience_level: e.target.value })}>
                <option value="entry">Entry</option>
                <option value="mid">Mid</option>
                <option value="senior">Senior</option>
                <option value="lead">Lead</option>
                <option value="executive">Executive</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Required Skills</label>
            <div style={{ display: 'flex', gap: 8 }}>
              <input className="form-input" value={skillInput} onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddSkill(); } }}
                placeholder="Type skill and press Enter" />
              <button type="button" className="btn btn-secondary" onClick={handleAddSkill}>Add</button>
            </div>
            {form.required_skills.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
                {form.required_skills.map((s) => (
                  <span key={s} className="badge badge-info" style={{ cursor: 'pointer' }} onClick={() => handleRemoveSkill(s)}>{s} &times;</span>
                ))}
              </div>
            )}
          </div>
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label className="form-label">Description</label>
              <button type="button" className="btn btn-secondary btn-sm" onClick={handleGenerateDescription} disabled={aiGenerating}>
                {aiGenerating ? 'Generating...' : 'AI Generate'}
              </button>
            </div>
            <textarea className="form-input form-textarea" value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={6} placeholder="Job description..." />
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default JobsPage;
