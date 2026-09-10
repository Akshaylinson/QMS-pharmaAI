import {useEffect,useState} from 'react';
import {useDispatch,useSelector} from 'react-redux';
import {Link} from 'react-router-dom';
import {LineChart,Line,XAxis,YAxis,CartesianGrid,Tooltip,Legend,ResponsiveContainer} from 'recharts';
import {loadDashboard} from '../store';
import {api} from '../services/api';

const STATUS_COLOR={'Pending Review':'#a06b00','Under Investigation':'#1264d6','Resolved':'#127753','Closed':'#607084','Escalated':'#b4232f'};
const PALETTE=['#0a3d8f','#1264d6','#2473d8','#3b82f6','#6aa3f0'];
const TICK={fontSize:11,fill:'#758399'};

export default function Dashboard(){
  const d=useDispatch(),data=useSelector(s=>s.dashboard.data),[trend,setTrend]=useState(null);
  useEffect(()=>{d(loadDashboard());api.analytics().then(setTrend).catch(()=>setTrend(false))},[d]);
  const cards=[['Total Complaints',data?.total],['Open Complaints',data?.open],['High Risk',data?.high_risk],['Critical',data?.critical],['Pending Review',data?.pending_review],['Resolved',data?.resolved]];
  const statusKeys=trend?.all_statuses||[];
  return <section className="page"><div className="title-row"><div><h1>Quality overview</h1><p>Complaint intake and review status at a glance.</p></div><Link className="primary" to="/log">Log Customer Complaint</Link></div><div className="metrics">{cards.map(([l,n])=><div className="card metric" key={l}><span>{l}</span><b>{n??'—'}</b></div>)}</div><div className="dashboard-grid"><section className="card"><h2>Complaints by severity</h2>{Object.entries(data?.by_severity||{}).map(([k,v])=><div className="bar" key={k}><span>{k}</span><i style={{width:`${Math.max(12,v*25)}%`}}></i><b>{v}</b></div>)}{!data&&<p>Loading dashboard…</p>}</section><section className="card"><h2>Recent complaints</h2><table><thead><tr><th>ID</th><th>Product</th><th>Risk</th><th>Status</th></tr></thead><tbody>{(data?.recent||[]).map(x=><tr key={x.id}><td>{x.complaint_number}</td><td>{x.product_name||'—'}</td><td>{x.risk_level||'—'}</td><td>{x.status}</td></tr>)}</tbody></table></section></div><section className="card dashboard-trend"><h2>Complaints over time — daily (by status)</h2>{trend&&<ResponsiveContainer width="100%" height={260}><LineChart data={trend.complaints_over_time} margin={{top:8,right:20,left:-10,bottom:0}}><CartesianGrid strokeDasharray="3 3" stroke="#e5eaf1"/><XAxis dataKey="date" tick={TICK} tickFormatter={date=>date.slice(5)} interval="preserveStartEnd"/><YAxis allowDecimals={false} tick={TICK}/><Tooltip/><Legend wrapperStyle={{fontSize:11,color:'#758399'}}/><Line type="monotone" dataKey="total" stroke="#1b2939" strokeWidth={2} dot={false} name="Total"/>{statusKeys.map((status,index)=><Line key={status} type="monotone" dataKey={status} stroke={STATUS_COLOR[status]||PALETTE[index%PALETTE.length]} strokeWidth={1.5} dot={false} name={status}/>)}</LineChart></ResponsiveContainer>}{trend===null&&<p className="dashboard-trend-state">Loading daily complaint activity…</p>}{trend===false&&<p className="dashboard-trend-state">Daily complaint activity is unavailable.</p>}</section></section>
}
