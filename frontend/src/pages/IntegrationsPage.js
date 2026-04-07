import React, { useState, useEffect } from 'react';
import { integrationsAPI } from '../api/client';
import toast from 'react-hot-toast';

const PROVIDERS = [
  { value: 'greenhouse', label: 'Greenhouse ATS', icon: 'ATS' },
  { value: 'lever', label: 'Lever ATS', icon: 'ATS' },
  { value: 'workday', label: 'Workday', icon: 'HR' },
  { value: 'bamboohr', label: 'BambooHR', icon: 'HR' },
  { value: 'salesforce', label: 'Salesforce CRM', icon: 'CRM' },
  { value: 'hubspot', label: 'HubSpot CRM', icon: 'CRM' },
  { value: 'bullhorn', label: 'Bullhorn', icon: 'ATS' },
  { value: 'custom_webhook', label: 'Custom Webhook', icon: 'API' },
];

const STATUS_COLORS = { active: '#10b981', inactive: '#6b7280', error: '#ef4444', pending: '#f59e0b' };

function IntegrationsPage() {
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const fetchIntegrations = async () => {
    try {
      const { data } = await integrationsAPI.list();
      setIntegrations(data.results || data || []);
    } catch {
      toast.error('Failed to load integrations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchIntegrations(); }, []);

  const handleTestConnection = async (id) => {
    try {
      const { data } = await integrationsAPI.testConnection(id);
      toast[data.success ? 'success' : 'error'](data.message);
      fetchIntegrations();
    } catch {
      toast.error('Connection test failed');
    }
  };

  const handleSync = async (id) => {
    try {
      const { data } = await integrationsAPI.triggerSync(id, { direction: 'inbound' });
      toast.success(`Sync complete: ${data.records_created} created, ${data.records_updated} updated`);
    } catch {
      toast.error('Sync failed');
    }
  };

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Integrations</h1>
          <p className="page-subtitle">Connect your ATS, CRM, and HR systems</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ Add Integration</button>
      </div>

      {integrations.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <h3>No integrations configured</h3>
            <p>Connect your existing tools to sync candidates and jobs</p>
            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => setShowModal(true)}>
              Add Your First Integration
            </button>
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 16 }}>
          {integrations.map((integration) => (
            <div key={integration.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                <div>
                  <h3 style={{ fontSize: 16, fontWeight: 600 }}>{integration.name}</h3>
                  <p style={{ fontSize: 13, color: '#6b7280' }}>{integration.provider_display}</p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: STATUS_COLORS[integration.status] }} />
                  <span style={{ fontSize: 12, fontWeight: 500, color: STATUS_COLORS[integration.status] }}>
                    {integration.status_display}
                  </span>
                </div>
              </div>
              {integration.last_sync_at && (
                <p style={{ fontSize: 12, color: '#9ca3af', marginBottom: 12 }}>
                  Last synced: {new Date(integration.last_sync_at).toLocaleString()}
                </p>
              )}
              <div style={{ display: 'flex', gap: 8 }}>
                <button className="btn btn-secondary btn-sm" onClick={() => handleTestConnection(integration.id)}>
                  Test
                </button>
                <button className="btn btn-primary btn-sm" onClick={() => handleSync(integration.id)}>
                  Sync Now
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="card" style={{ marginTop: 32 }}>
        <h3 className="card-title" style={{ marginBottom: 16 }}>Available Integrations</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12 }}>
          {PROVIDERS.map((p) => (
            <div key={p.value} style={{
              border: '1px solid #e5e7eb', borderRadius: 8, padding: 16, textAlign: 'center',
              cursor: 'pointer', transition: 'all 0.15s',
            }}
              onMouseOver={(e) => e.currentTarget.style.borderColor = '#3b82f6'}
              onMouseOut={(e) => e.currentTarget.style.borderColor = '#e5e7eb'}
              onClick={() => setShowModal(true)}
            >
              <div style={{
                width: 40, height: 40, borderRadius: 8, background: '#eff6ff',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 8px', fontSize: 12, fontWeight: 700, color: '#2563eb',
              }}>{p.icon}</div>
              <p style={{ fontSize: 13, fontWeight: 500 }}>{p.label}</p>
            </div>
          ))}
        </div>
      </div>

      {showModal && <AddIntegrationModal onClose={() => setShowModal(false)} onSuccess={() => { setShowModal(false); fetchIntegrations(); }} />}
    </div>
  );
}

function AddIntegrationModal({ onClose, onSuccess }) {
  const [form, setForm] = useState({ name: '', provider: 'greenhouse', config: {} });
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await integrationsAPI.create({
        ...form,
        api_key_encrypted: apiKey,
        config: { ...form.config, use_mock: !apiKey },
      });
      toast.success('Integration added!');
      onSuccess();
    } catch {
      toast.error('Failed to add integration');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">Add Integration</h3>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Name *</label>
            <input className="form-input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required placeholder="My Greenhouse Integration" />
          </div>
          <div className="form-group">
            <label className="form-label">Provider *</label>
            <select className="form-input form-select" value={form.provider} onChange={(e) => setForm({ ...form, provider: e.target.value })}>
              {PROVIDERS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">API Key</label>
            <input type="password" className="form-input" value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder="Leave blank for demo mode" />
            <p style={{ fontSize: 12, color: '#9ca3af', marginTop: 4 }}>
              Leave blank to use mock data for testing
            </p>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Adding...' : 'Add Integration'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default IntegrationsPage;
