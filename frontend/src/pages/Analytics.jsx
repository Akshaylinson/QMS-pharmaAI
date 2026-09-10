import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { loadDashboard } from '../store';
import { api } from '../services/api';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const BLUE  = '#1264d6';
const TEAL  = '#1264d6';
const GRID  = '#e5eaf1';
const TICK  = { fontSize: 11, fill: '#758399' };

const SEV_COLOR    = { Critical: '#0a3d8f', Major: '#1264d6', Minor: '#6aa3f0' };
const STATUS_COLOR = {
  'Pending Review':     '#a06b00',
  'Under Investigation': BLUE,
  'Resolved':           '#127753',
  'Closed':             '#607084',
  'Escalated':          '#b4232f',
};
const PALETTE = ['#0a3d8f', '#1264d6', '#2473d8', '#3b82f6', '#6aa3f0', '#93bff5', '#bdd6fa', '#dceeff'];

function StatCard({ label, value }) {
  return (
    <div className="card metric">
      <span>{label}</span>
      <b>{value ?? '—'}</b>
    </div>
  );
}

function ChartCard({ title, children, full }) {
  return (
    <section className={`card an-card${full ? ' an-full' : ''}`}>
      <h2 className="an-title">{title}</h2>
      {children}
    </section>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#fff', border: '1px solid #e3e9f0', borderRadius: 7, padding: '10px 14px', fontSize: 12, color: '#374454' }}>
      {label && <div style={{ fontWeight: 600, marginBottom: 6, color: '#1b2939' }}>{label}</div>}
      {payload.map((p, i) => (
        <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 2 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: p.color, display: 'inline-block', flexShrink: 0 }} />
          <span style={{ color: '#758399' }}>{p.name}:</span>
          <span style={{ fontWeight: 600 }}>{p.value}</span>
        </div>
      ))}
    </div>
  );
};

export default function Analytics() {
  const dispatch = useDispatch();
  const stats = useSelector(s => s.dashboard.data);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    dispatch(loadDashboard());
    api.analytics()
      .then(d => { setData(d); setLoading(false); })
      .catch(() => { setError(true); setLoading(false); });
  }, [dispatch]);

  if (loading) return <section className="page an-page"><p style={{ color: '#758399', marginTop: 8 }}>Loading analytics…</p></section>;
  if (error || !data) return <section className="page an-page"><p style={{ color: '#b4232f', marginTop: 8 }}>Could not load analytics data. Ensure the backend is running.</p></section>;

  const sevKeys = [...new Set(data.severity_over_time.flatMap(d => Object.keys(d).filter(k => k !== 'month')))];
  // statuses come from backend — dynamic, never hard-coded
  const statusKeys = data.all_statuses || [];

  return (
    <section className="page an-page">
      <div className="title-row">
        <div><h1>Analytics</h1><p>Complaint trends, risk distribution, and quality insights.</p></div>
      </div>

      {/* KPI badges */}
      <div className="metrics" style={{ marginBottom: 24 }}>
        {[
          ['Total Complaints',  stats?.total],
          ['Open Complaints',   stats?.open],
          ['High Risk',         stats?.high_risk],
          ['Critical',          stats?.critical],
          ['Pending Review',    stats?.pending_review],
          ['Resolved',          stats?.resolved],
        ].map(([l, n]) => <StatCard key={l} label={l} value={n} />)}
      </div>

      {/* 1 — Multi-line: total + one line per status */}
      <ChartCard title="Complaints over time — daily (by status)" full>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={data.complaints_over_time} margin={{ top: 8, right: 20, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
            <XAxis dataKey="date" tick={TICK} tickFormatter={d => d.slice(5)} interval="preserveStartEnd" />
            <YAxis allowDecimals={false} tick={TICK} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 11, color: '#758399' }} />
            <Line type="monotone" dataKey="total" stroke="#1b2939" strokeWidth={2} dot={false} name="Total" />
            {statusKeys.map((s, i) => (
              <Line key={s} type="monotone" dataKey={s}
                stroke={STATUS_COLOR[s] || PALETTE[i % PALETTE.length]}
                strokeWidth={1.5} dot={false} name={s} strokeDasharray={i > 3 ? '4 2' : undefined} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* 2 — Monthly volume + severity trend */}
      <div className="an-grid">
        <ChartCard title="Monthly complaint volume">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.complaints_by_month} margin={{ top: 8, right: 16, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
              <XAxis dataKey="month" tick={TICK} />
              <YAxis allowDecimals={false} tick={TICK} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" fill={BLUE} name="Complaints" radius={[4, 4, 0, 0]} maxBarSize={40} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Severity trend by month">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.severity_over_time} margin={{ top: 8, right: 16, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
              <XAxis dataKey="month" tick={TICK} />
              <YAxis allowDecimals={false} tick={TICK} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: 11, color: '#758399' }} />
              {sevKeys.map(k => <Bar key={k} dataKey={k} stackId="a" fill={SEV_COLOR[k] || '#607084'} maxBarSize={40} />)}
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* 3 — Complaint types top 10 */}
      <ChartCard title="Top 10 complaint types" full>
        <ResponsiveContainer width="100%" height={Math.max(180, data.complaint_types.length * 36)}>
          <BarChart data={data.complaint_types} layout="vertical" margin={{ top: 4, right: 32, left: 4, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID} horizontal={false} />
            <XAxis type="number" allowDecimals={false} tick={TICK} />
            <YAxis type="category" dataKey="type" tick={{ fontSize: 11, fill: '#445368' }} width={200} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="count" fill={TEAL} name="Complaints" radius={[0, 4, 4, 0]} maxBarSize={22} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* 4 — Top customers + top products */}
      <div className="an-grid">
        <ChartCard title="Top 10 customers by complaint volume">
          <ResponsiveContainer width="100%" height={Math.max(180, data.top_customers.length * 32)}>
            <BarChart data={data.top_customers} layout="vertical" margin={{ top: 4, right: 32, left: 4, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={GRID} horizontal={false} />
              <XAxis type="number" allowDecimals={false} tick={TICK} />
              <YAxis type="category" dataKey="customer" tick={{ fontSize: 10, fill: '#445368' }} width={160} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" fill="#1264d6" name="Complaints" radius={[0, 4, 4, 0]} maxBarSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Top 10 products by complaint volume">
          <ResponsiveContainer width="100%" height={Math.max(180, data.top_products.length * 32)}>
            <BarChart data={data.top_products} layout="vertical" margin={{ top: 4, right: 32, left: 4, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={GRID} horizontal={false} />
              <XAxis type="number" allowDecimals={false} tick={TICK} />
              <YAxis type="category" dataKey="product" tick={{ fontSize: 10, fill: '#445368' }} width={160} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" fill="#3b82f6" name="Complaints" radius={[0, 4, 4, 0]} maxBarSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </section>
  );
}
