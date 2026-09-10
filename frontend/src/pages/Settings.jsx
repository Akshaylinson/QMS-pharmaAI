import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { FlaskConical, Database, Bot, ShieldCheck, Info, CheckCircle2, AlertCircle } from 'lucide-react';

function Section({ icon: Icon, title, children }) {
  return (
    <section className="card st-section">
      <div className="st-section-head">
        <Icon size={18} />
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  );
}

function Row({ label, value, badge, mono }) {
  return (
    <div className="st-row">
      <span className="st-label">{label}</span>
      {badge
        ? <span className={`st-badge ${badge}`}>{value}</span>
        : <span className={`st-value${mono ? ' st-mono' : ''}`}>{value ?? '—'}</span>}
    </div>
  );
}

const WORKFLOW_DEFAULTS = [
  ['Default intake status',    'PENDING_REVIEW'],
  ['Required fields for commit', 'Customer name, Product name, Batch number, Description'],
  ['Duplicate match threshold', '≥ 0.55 similarity score'],
  ['Risk escalation trigger',  'CRITICAL or HIGH risk level'],
  ['Audit log',                'Every create / update / analysis action'],
];

const QMS_GUIDELINES = [
  'All AI risk assessments are recommendations only and require qualified human QA review before any regulatory or disposition decision.',
  'Complaint records are immutable once committed to the QMS ledger. Updates are tracked in the audit log.',
  'Duplicate detection is a QA-assistance tool, not a confirmed duplicate decision.',
  'Document extraction is text-based. Scanned image PDFs require OCR pre-processing outside this system.',
  'CAPA and root-cause suggestions are AI-generated starting points and must be validated by a qualified investigator.',
  'This system does not constitute a validated GxP system without a site-specific validation package.',
];

export default function Settings() {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.settingsInfo().then(d => { setInfo(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const activeProvider = info?.llm_provider?.toLowerCase();

  return (
    <section className="page st-page">
      <div className="title-row">
        <div><h1>Settings</h1><p>System configuration, AI provider status, and QMS operational guidelines.</p></div>
      </div>

      <div className="st-grid">

        {/* System info */}
        <Section icon={Info} title="System Information">
          <Row label="Application"   value={info?.app_name ?? 'AIVOA.AI — Pharmaceutical QMS'} />
          <Row label="Version"       value={info?.version ?? '1.0.0'} />
          <Row label="Frontend URL"  value={info?.frontend_origin} mono />
          <Row label="Database"      value={loading ? 'Loading…' : (info?.database_url ?? '—')} mono />
          <Row label="API status"    value="Online" badge="badge-ok" />
        </Section>

        {/* AI provider */}
        <Section icon={Bot} title="AI Provider">
          <Row label="Active provider"
            value={loading ? 'Loading…' : (info?.llm_provider?.toUpperCase() ?? '—')}
            badge={info ? 'badge-blue' : undefined} />
          <div className="st-provider-cards">
            <div className={`st-provider-card ${activeProvider === 'groq' ? 'active' : ''}`}>
              <div className="st-provider-head">
                <b>Groq</b>
                {info?.groq_configured
                  ? <span className="st-badge badge-ok"><CheckCircle2 size={11}/> Configured</span>
                  : <span className="st-badge badge-warn"><AlertCircle size={11}/> No API key</span>}
              </div>
              <Row label="Model" value={info?.groq_model ?? '—'} mono />
              {activeProvider === 'groq' && <div className="st-active-tag">● Active</div>}
            </div>
            <div className={`st-provider-card ${activeProvider === 'gemini' ? 'active' : ''}`}>
              <div className="st-provider-head">
                <b>Gemini</b>
                {info?.gemini_configured
                  ? <span className="st-badge badge-ok"><CheckCircle2 size={11}/> Configured</span>
                  : <span className="st-badge badge-warn"><AlertCircle size={11}/> No API key</span>}
              </div>
              <Row label="Model" value={info?.gemini_model ?? '—'} mono />
              {activeProvider === 'gemini' && <div className="st-active-tag">● Active</div>}
            </div>
          </div>
          <p className="st-note">API keys are configured via environment variables and are never exposed through this interface. To switch providers, update <code>LLM_PROVIDER</code> in your <code>.env</code> file and restart the service.</p>
        </Section>

        {/* Workflow defaults */}
        <Section icon={FlaskConical} title="Complaint Workflow Defaults">
          {WORKFLOW_DEFAULTS.map(([label, value]) => <Row key={label} label={label} value={value} />)}
          <p className="st-note">Workflow parameters are defined in the LangGraph pipeline and backend schema. Contact your system administrator to modify defaults.</p>
        </Section>

        {/* Database */}
        <Section icon={Database} title="Data & Storage">
          <Row label="Primary store"     value="PostgreSQL" />
          <Row label="UUID primary keys" value="Enabled" badge="badge-ok" />
          <Row label="Audit logging"     value="Enabled" badge="badge-ok" />
          <Row label="Analysis records"  value="Stored per complaint" />
          <Row label="Migrations"        value="Alembic (run alembic upgrade head)" mono />
          <p className="st-note">The application auto-creates tables on startup for clean Docker deployments. Use Alembic for production migration management.</p>
        </Section>

        {/* QMS guidelines — full width */}
        <Section icon={ShieldCheck} title="QMS Operational Guidelines">
          <ul className="st-guidelines">
            {QMS_GUIDELINES.map((g, i) => (
              <li key={i}>
                <CheckCircle2 size={14} className="st-check" />
                <span>{g}</span>
              </li>
            ))}
          </ul>
        </Section>

      </div>
    </section>
  );
}
