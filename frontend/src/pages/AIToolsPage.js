import React, { useState } from 'react';
import { aiAPI } from '../api/client';
import toast from 'react-hot-toast';

function AIToolsPage() {
  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Tools</h1>
          <p className="page-subtitle">AI-powered recruitment automation</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 24 }}>
        <ResumeParserTool />
        <JobDescriptionGenerator />
        <InterviewQuestionGenerator />
        <CandidateScoringTool />
      </div>
    </div>
  );
}

function ResumeParserTool() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('resume', file);
    try {
      const { data } = await aiAPI.parseResume(formData);
      setResult(data);
      toast.success('Resume parsed!');
    } catch {
      toast.error('Failed to parse resume');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3 className="card-title" style={{ marginBottom: 8 }}>Resume Parser</h3>
      <p style={{ fontSize: 13, color: '#6b7280', marginBottom: 16 }}>
        Upload a resume to extract skills, experience, and contact information using AI.
      </p>
      <label className="btn btn-primary" style={{ cursor: 'pointer', display: 'inline-flex' }}>
        {loading ? 'Parsing...' : 'Upload Resume'}
        <input type="file" accept=".pdf,.doc,.docx,.txt" onChange={handleUpload} style={{ display: 'none' }} disabled={loading} />
      </label>
      {result && (
        <div style={{ marginTop: 16, padding: 12, background: '#f9fafb', borderRadius: 8, fontSize: 13 }}>
          {result.email && <p><strong>Email:</strong> {result.email}</p>}
          {result.phone && <p><strong>Phone:</strong> {result.phone}</p>}
          {result.years_experience > 0 && <p><strong>Experience:</strong> {result.years_experience} years</p>}
          {result.skills?.technical?.length > 0 && (
            <div style={{ marginTop: 8 }}>
              <strong>Technical Skills:</strong>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 4 }}>
                {result.skills.technical.map((s, i) => <span key={i} className="badge badge-info">{s}</span>)}
              </div>
            </div>
          )}
          {result.ai_summary && (
            <div style={{ marginTop: 8 }}>
              <strong>AI Summary:</strong>
              <p style={{ marginTop: 4, color: '#374151' }}>{result.ai_summary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function JobDescriptionGenerator() {
  const [title, setTitle] = useState('');
  const [department, setDepartment] = useState('');
  const [skills, setSkills] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!title) { toast.error('Enter a job title'); return; }
    setLoading(true);
    try {
      const { data } = await aiAPI.generateJobDescription({
        title,
        department,
        requirements: skills.split(',').map((s) => s.trim()).filter(Boolean),
      });
      setDescription(data.description);
      toast.success('Description generated!');
    } catch {
      toast.error('Generation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3 className="card-title" style={{ marginBottom: 8 }}>Job Description Generator</h3>
      <p style={{ fontSize: 13, color: '#6b7280', marginBottom: 16 }}>
        Generate professional job descriptions with AI.
      </p>
      <div className="form-group">
        <input className="form-input" placeholder="Job Title" value={title} onChange={(e) => setTitle(e.target.value)} />
      </div>
      <div className="form-group">
        <input className="form-input" placeholder="Department" value={department} onChange={(e) => setDepartment(e.target.value)} />
      </div>
      <div className="form-group">
        <input className="form-input" placeholder="Key skills (comma-separated)" value={skills} onChange={(e) => setSkills(e.target.value)} />
      </div>
      <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate'}
      </button>
      {description && (
        <div style={{ marginTop: 16, padding: 12, background: '#f9fafb', borderRadius: 8, fontSize: 13, whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto' }}>
          {description}
        </div>
      )}
    </div>
  );
}

function InterviewQuestionGenerator() {
  const [jobId, setJobId] = useState('');
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!jobId) { toast.error('Enter a Job ID'); return; }
    setLoading(true);
    try {
      const { data } = await aiAPI.generateInterviewQuestions({ job_id: jobId });
      setQuestions(data.questions);
      toast.success('Questions generated!');
    } catch {
      toast.error('Generation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3 className="card-title" style={{ marginBottom: 8 }}>Interview Questions</h3>
      <p style={{ fontSize: 13, color: '#6b7280', marginBottom: 16 }}>
        Generate tailored interview questions for a job.
      </p>
      <div className="form-group">
        <input className="form-input" placeholder="Job ID (UUID)" value={jobId} onChange={(e) => setJobId(e.target.value)} />
      </div>
      <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Questions'}
      </button>
      {questions.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <ol style={{ paddingLeft: 20, fontSize: 13, lineHeight: 1.8 }}>
            {questions.map((q, i) => <li key={i} style={{ marginBottom: 4 }}>{q}</li>)}
          </ol>
        </div>
      )}
    </div>
  );
}

function CandidateScoringTool() {
  const [candidateId, setCandidateId] = useState('');
  const [jobId, setJobId] = useState('');
  const [scores, setScores] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleScore = async () => {
    if (!candidateId || !jobId) { toast.error('Enter both IDs'); return; }
    setLoading(true);
    try {
      const { data } = await aiAPI.scoreCandidate({ candidate_id: candidateId, job_id: jobId });
      setScores(data);
      toast.success('Scoring complete!');
    } catch {
      toast.error('Scoring failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3 className="card-title" style={{ marginBottom: 8 }}>Candidate Scoring</h3>
      <p style={{ fontSize: 13, color: '#6b7280', marginBottom: 16 }}>
        Score a candidate's fit for a specific job.
      </p>
      <div className="form-group">
        <input className="form-input" placeholder="Candidate ID (UUID)" value={candidateId} onChange={(e) => setCandidateId(e.target.value)} />
      </div>
      <div className="form-group">
        <input className="form-input" placeholder="Job ID (UUID)" value={jobId} onChange={(e) => setJobId(e.target.value)} />
      </div>
      <button className="btn btn-primary" onClick={handleScore} disabled={loading}>
        {loading ? 'Scoring...' : 'Score Candidate'}
      </button>
      {scores && (
        <div style={{ marginTop: 16, padding: 12, background: '#f9fafb', borderRadius: 8, fontSize: 13 }}>
          <ScoreRow label="Overall" value={scores.overall_score} />
          <ScoreRow label="Skills" value={scores.skill_match} />
          <ScoreRow label="Experience" value={scores.experience_score} />
          <ScoreRow label="Location" value={scores.location_score} />
          {scores.explanation && (
            <p style={{ marginTop: 8, color: '#374151', fontStyle: 'italic' }}>{scores.explanation}</p>
          )}
        </div>
      )}
    </div>
  );
}

function ScoreRow({ label, value }) {
  const color = value >= 70 ? '#10b981' : value >= 40 ? '#f59e0b' : '#ef4444';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
      <span style={{ width: 80, fontSize: 12, color: '#6b7280' }}>{label}</span>
      <div className="score-bar" style={{ flex: 1 }}>
        <div className="score-bar-fill" style={{ width: `${value}%`, background: color }} />
      </div>
      <span style={{ fontWeight: 600, fontSize: 12, width: 40, textAlign: 'right' }}>{value}%</span>
    </div>
  );
}

export default AIToolsPage;
