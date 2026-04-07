import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { candidatesAPI, aiAPI } from '../api/client';
import toast from 'react-hot-toast';

const STAGE_LABELS = {
  new: 'New', screening: 'Screening', interview: 'Interview',
  assessment: 'Assessment', offer: 'Offer', hired: 'Hired', rejected: 'Rejected',
};

function CandidateDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    candidatesAPI.get(id)
      .then(({ data }) => { setCandidate(data); setLoading(false); })
      .catch(() => { toast.error('Candidate not found'); navigate('/candidates'); });
  }, [id, navigate]);

  const handleAdvanceStage = async () => {
    try {
      const { data } = await candidatesAPI.advanceStage(id, {});
      setCandidate(data);
      toast.success('Stage advanced');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to advance stage');
    }
  };

  const handleResumeUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('resume', file);
    try {
      const { data } = await candidatesAPI.uploadResume(id, formData);
      setCandidate(data);
      toast.success('Resume uploaded');
    } catch {
      toast.error('Failed to upload resume');
    }
  };

  const handleAIAnalysis = async () => {
    if (!candidate.resume_file) {
      toast.error('Upload a resume first');
      return;
    }
    setAiLoading(true);
    try {
      const formData = new FormData();
      const response = await fetch(candidate.resume_file);
      const blob = await response.blob();
      formData.append('resume', blob, 'resume.pdf');
      const { data } = await aiAPI.parseResume(formData);
      if (data.ai_summary) {
        await candidatesAPI.update(id, {
          ai_summary: data.ai_summary,
          ai_skills_extracted: data.skills?.all || [],
        });
        setCandidate((prev) => ({
          ...prev,
          ai_summary: data.ai_summary,
          ai_skills_extracted: data.skills?.all || [],
        }));
      }
      toast.success('AI analysis complete');
    } catch {
      toast.error('AI analysis failed');
    } finally {
      setAiLoading(false);
    }
  };

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;
  if (!candidate) return null;

  return (
    <div>
      <div className="page-header">
        <div>
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/candidates')} style={{ marginBottom: 8 }}>
            &larr; Back to Candidates
          </button>
          <h1 className="page-title">{candidate.first_name} {candidate.last_name}</h1>
          <p className="page-subtitle">{candidate.current_title} {candidate.current_company ? `at ${candidate.current_company}` : ''}</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-secondary" onClick={handleAIAnalysis} disabled={aiLoading}>
            {aiLoading ? 'Analyzing...' : 'AI Analysis'}
          </button>
          <button className="btn btn-primary" onClick={handleAdvanceStage}>Advance Stage</button>
        </div>
      </div>

      <div className="content-grid">
        <div className="card">
          <h3 className="card-title" style={{ marginBottom: 16 }}>Candidate Info</h3>
          <InfoRow label="Email" value={candidate.email} />
          <InfoRow label="Phone" value={candidate.phone || '-'} />
          <InfoRow label="Location" value={candidate.location || '-'} />
          <InfoRow label="Experience" value={candidate.years_experience ? `${candidate.years_experience} years` : '-'} />
          <InfoRow label="Source" value={(candidate.source || '').replace('_', ' ')} />
          <InfoRow label="Stage" value={<span className={`badge badge-info`}>{STAGE_LABELS[candidate.stage]}</span>} />
          {candidate.linkedin_url && <InfoRow label="LinkedIn" value={<a href={candidate.linkedin_url} target="_blank" rel="noopener noreferrer">View Profile</a>} />}
        </div>

        <div className="card">
          <h3 className="card-title" style={{ marginBottom: 16 }}>AI Assessment</h3>
          {candidate.ai_score != null && (
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span style={{ fontSize: 13, color: '#6b7280' }}>AI Score</span>
                <span style={{ fontWeight: 600 }}>{candidate.ai_score}%</span>
              </div>
              <div className="score-bar">
                <div className="score-bar-fill" style={{ width: `${candidate.ai_score}%`, background: candidate.ai_score >= 70 ? '#10b981' : candidate.ai_score >= 40 ? '#f59e0b' : '#ef4444' }} />
              </div>
            </div>
          )}
          {candidate.ai_summary ? (
            <div>
              <p style={{ fontSize: 14, color: '#374151', lineHeight: 1.6 }}>{candidate.ai_summary}</p>
            </div>
          ) : (
            <p style={{ color: '#9ca3af', fontSize: 14 }}>No AI analysis yet. Upload a resume and run AI Analysis.</p>
          )}
          {candidate.ai_skills_extracted?.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <h4 style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>Extracted Skills</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {candidate.ai_skills_extracted.map((skill, i) => (
                  <span key={i} className="badge badge-info">{skill}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="content-grid" style={{ marginTop: 24 }}>
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Skills</h3>
          </div>
          {candidate.skills?.length > 0 ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {candidate.skills.map((skill, i) => (
                <span key={i} className="badge badge-gray">{skill}</span>
              ))}
            </div>
          ) : (
            <p style={{ color: '#9ca3af', fontSize: 14 }}>No skills listed</p>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Resume</h3>
          </div>
          {candidate.resume_file ? (
            <div>
              <a href={candidate.resume_file} target="_blank" rel="noopener noreferrer" className="btn btn-secondary btn-sm">
                View Resume
              </a>
            </div>
          ) : (
            <div>
              <p style={{ color: '#9ca3af', fontSize: 14, marginBottom: 12 }}>No resume uploaded</p>
              <label className="btn btn-secondary btn-sm" style={{ cursor: 'pointer' }}>
                Upload Resume
                <input type="file" accept=".pdf,.doc,.docx,.txt" onChange={handleResumeUpload} style={{ display: 'none' }} />
              </label>
            </div>
          )}
        </div>
      </div>

      {candidate.candidate_notes?.length > 0 && (
        <div className="card" style={{ marginTop: 24 }}>
          <h3 className="card-title" style={{ marginBottom: 16 }}>Notes</h3>
          {candidate.candidate_notes.map((note) => (
            <div key={note.id} style={{ padding: '12px 0', borderBottom: '1px solid #f3f4f6' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span style={{ fontSize: 13, fontWeight: 500 }}>{note.author_name || 'System'}</span>
                <span style={{ fontSize: 12, color: '#9ca3af' }}>{new Date(note.created_at).toLocaleDateString()}</span>
              </div>
              <p style={{ fontSize: 14, color: '#374151' }}>{note.content}</p>
            </div>
          ))}
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

export default CandidateDetailPage;
