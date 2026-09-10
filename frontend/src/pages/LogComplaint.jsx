import {useRef,useState} from 'react';
import {useDispatch,useSelector} from 'react-redux';
import {runIntake,saveComplaint,reset,loadComplaints,loadDashboard} from '../store';
import {api} from '../services/api';
import {FlaskConical,Paperclip,Send,Check,CheckCircle2,ShieldCheck,FileText,UserRound,Sparkles,RotateCcw,Lightbulb,ListChecks,FileCheck2} from 'lucide-react';

const WELCOME='Ready to process new complaints. Paste the customer email, describe the issue, or upload a complaint report. I\u2019ll extract the facts and run an initial risk assessment.';

// All fields that must be filled before saving
const REQUIRED_FIELDS=[
  ['source','Complaint Source'],
  ['customer_name','Customer Name'],
  ['product_name','Product Name'],
  ['product_strength','Product Strength / Grade'],
  ['batch_number','Batch / Lot Number'],
  ['affected_quantity','Affected Quantity'],
  ['manufacturing_date','Manufacturing Date'],
  ['expiry_date','Expiry Date'],
  ['complaint_type','Complaint Category'],
  ['description','Complaint Description'],
];

const groups=[
  ['1. Origin & Customer Details',[['source','Complaint Source'],['customer_name','Customer Name']]],
  ['2. Product & Batch Identification',[['product_name','Product Name'],['product_strength','Product Strength / Grade'],['batch_number','Batch / Lot Number'],['affected_quantity','Affected Quantity'],['manufacturing_date','Manufacturing Date'],['expiry_date','Expiry Date']]],
  ['3. Facility & Material Impact',[['originating_site','Originating Site Block'],['impacted_materials','Impacted Non-Product Materials (NPM)']]],
  ['4. Defect Analysis',[['complaint_type','Complaint Category','wide'],['description','Complaint Description','wide area']]],
];
const label=name=>name.replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
const welcomeMsg=()=>({role:'assistant',kind:'welcome',text:WELCOME});

export default function LogComplaint(){
  const dispatch=useDispatch(),form=useSelector(s=>s.complaint.form),loading=useSelector(s=>s.complaint.loading),error=useSelector(s=>s.complaint.error),analysis=useSelector(s=>s.complaint.analysis);
  const [message,setMessage]=useState('');
  const [messages,setMessages]=useState([welcomeMsg()]);
  const [notice,setNotice]=useState('');
  const [dialog,setDialog]=useState(null);
  const [completenessDialog,setCompletenessDialog]=useState(null); // {missingFields, fillText}
  const [fillText,setFillText]=useState('');
  const [dragging,setDragging]=useState(false);
  const fileInput=useRef();
  const textareaRef=useRef();

  const missingRequired=REQUIRED_FIELDS.filter(([key])=>!form[key]);
  const allComplete=missingRequired.length===0;

  function autoResize(){
    const el=textareaRef.current;
    if(!el)return;
    el.style.height='auto';
    el.style.height=Math.min(el.scrollHeight,200)+'px';
  }

  async function process(text,type='text',fileName){
    const clean=text.trim();
    if(!clean||loading)return;
    setNotice('');
    setMessages(list=>[...list,{role:'user',text:fileName?'':clean,fileName}]);
    setMessage('');
    if(textareaRef.current){textareaRef.current.style.height='auto';}
    try{
      const result=await dispatch(runIntake({text:clean,type,currentComplaint:form})).unwrap();
      setMessages(list=>[...list,{role:'assistant',text:result.summary,updates:result.updated_fields}]);
    }catch(err){
      setMessages(list=>[...list,{role:'assistant',error:true,text:err.message||'I could not process that complaint. Please try again.'}]);
    }
  }

  async function handleFile(file){
    if(!file)return;
    setDragging(false);
    setNotice('Extracting document text\u2026');
    try{const extracted=await api.extract(file);setNotice('');await process(extracted.text,'document',file.name);}
    catch(err){setNotice(err.message||'The document could not be read.');}
  }

  function commitPayload(){
    const months={january:'01',february:'02',march:'03',april:'04',may:'05',june:'06',july:'07',august:'08',september:'09',october:'10',november:'11',december:'12'};
    const payload={...form};
    for(const field of ['manufacturing_date','expiry_date','complaint_date','received_date']){
      const value=payload[field];
      const match=typeof value==='string'&&value.trim().match(/^([a-zA-Z]+)\s+(\d{4})$/);
      if(match&&months[match[1].toLowerCase()])payload[field]=`${match[2]}-${months[match[1].toLowerCase()]}-01`;
    }
    ['manufacturing_date','expiry_date','complaint_date','received_date'].forEach(f=>{if(payload[f]==='')payload[f]=null;});
    return payload;
  }

  async function commit(){
    // Gate: show completeness checker if any required field is missing
    if(!allComplete){
      setFillText('');
      setCompletenessDialog(missingRequired);
      return;
    }
    try{
      const saved=await dispatch(saveComplaint(commitPayload())).unwrap();
      await Promise.all([dispatch(loadComplaints()),dispatch(loadDashboard())]);
      setDialog({type:'success',message:`Complaint ${saved.complaint_number} has been committed to the QMS ledger.`});
    }catch(err){
      setDialog({type:'error',message:err instanceof Error&&err.message?err.message:'Unable to commit the complaint. Please review the entered complaint details and try again.'});
    }
  }

  async function handleFillMissing(){
    if(!fillText.trim())return;
    const text=fillText.trim();
    setCompletenessDialog(null);
    setFillText('');
    await process(text);
  }

  function handleReset(){dispatch(reset());setMessages([welcomeMsg()]);setNotice('');}

  function dismissDialog(){
    const successful=dialog?.type==='success';
    setDialog(null);
    if(successful){dispatch(reset());setMessages([welcomeMsg()]);setNotice('');}
  }

  return (
    <section className="complaint-page">
      <div className="complaint-workspace">
        <div className="ledger">
          <div className="ledger-title">
            <div><h1>Log Customer Complaint</h1><p>API &amp; FDF Quality Assurance Module</p></div>
            <span className={allComplete?'commit-state ready':'commit-state'}><i/> {allComplete?'Ready to Commit':'Pending Triage'}</span>
          </div>
          {error&&<div className="alert">{error}</div>}
          {groups.map(([heading,fields])=>(
            <section className="ledger-group" key={heading}>
              <h2>{heading}</h2>
              <div className="ledger-fields">
                {fields.map(([name,title,kind=''])=>(
                  <label className={kind} key={name}>{title}
                    <div className={`read-value ${!form[name]?'empty-value':''}`}>{form[name]||'Awaiting AI extraction\u2026'}</div>
                  </label>
                ))}
              </div>
            </section>
          ))}
          <section className="risk-card">
            <div className="risk-heading"><ShieldCheck size={22}/><b>AI copilot risk assessment</b></div>
            <div className="risk-fields">
              <label>Severity (Suggested)<div className="read-value">{form.severity||'Awaiting assessment\u2026'}</div></label>
              <label>Suggested Next Action<div className="read-value">{form.suggested_next_action||'Awaiting assessment\u2026'}</div></label>
              <label className="wide">Initial Risk Assessment<div className="read-value risk-reason">{form.initial_risk_assessment||'The copilot will assess the reported facts after intake.'}</div></label>
            </div>
          </section>

          {/* AI Summary: Root Cause, CAPA, Complaint Summary */}
          {analysis&&(
            <section className="ai-summary-card">
              <div className="ai-summary-heading">
                <Sparkles size={19}/>
                <b>AI Analysis Summary</b>
                <span className="ai-summary-badge">Copilot Generated</span>
              </div>

              {analysis.root_causes?.length>0&&(
                <div className="ai-summary-block">
                  <div className="ai-summary-block-title"><Lightbulb size={15}/>Root Cause Recommendation</div>
                  <ul className="ai-summary-list">
                    {analysis.root_causes.map((c,i)=><li key={i}>{c}</li>)}
                  </ul>
                </div>
              )}

              {(analysis.capa?.corrective_actions?.length>0||analysis.capa?.preventive_actions?.length>0)&&(
                <div className="ai-summary-block">
                  <div className="ai-summary-block-title"><ListChecks size={15}/>CAPA Recommendations</div>
                  {analysis.capa.corrective_actions?.length>0&&(
                    <>
                      <p className="ai-summary-sub">Corrective Actions</p>
                      <ul className="ai-summary-list">
                        {analysis.capa.corrective_actions.map((a,i)=><li key={i}>{a}</li>)}
                      </ul>
                    </>
                  )}
                  {analysis.capa.preventive_actions?.length>0&&(
                    <>
                      <p className="ai-summary-sub">Preventive Actions</p>
                      <ul className="ai-summary-list">
                        {analysis.capa.preventive_actions.map((a,i)=><li key={i}>{a}</li>)}
                      </ul>
                    </>
                  )}
                </div>
              )}

              {analysis.summary&&(
                <div className="ai-summary-block ai-summary-block--last">
                  <div className="ai-summary-block-title"><FileCheck2 size={15}/>Complaint Summary</div>
                  <p className="ai-summary-text">{analysis.summary}</p>
                </div>
              )}
            </section>
          )}

          <div className="commit-buttons">
            <button className="reset-button" disabled={loading} onClick={handleReset}><RotateCcw size={19}/>Reset Form</button>
            <button className="commit-button" disabled={loading} onClick={commit}><Check size={19}/>{loading?'Processing\u2026':'Save Complaint'}</button>
          </div>
        </div>

        <aside className="copilot-panel">
          <div className="copilot-header">
            <FlaskConical size={25}/>
            <div><b>AIVOA Copilot</b><small>Drop complaint files or paste text below.</small></div>
            <span className="online"/>
          </div>
          <div className="conversation">
            {messages.map((item,index)=>item.role==='user'
              ? <div className={`user-message ${item.fileName?'attachment-message':''}`} key={index}>
                  {item.fileName
                    ? <span className="file-chip"><FileText size={19}/><span>{item.fileName}<small>Complaint document</small></span></span>
                    : item.text}
                  <UserRound size={18}/>
                </div>
              : <div className={`assistant-message ${item.error?'error-message':''}`} key={index}>
                  <span className="message-icon">{item.kind==='welcome'?<Sparkles size={19}/>:<Check size={18}/>}</span>
                  <p>{item.text}</p>
                  {item.updates?.length>0&&<small>Updated: {item.updates.map(label).join(', ')}</small>}
                </div>
            )}
          </div>

          <div className={`message-box ${dragging?'dragging':''}`}
            onDragOver={e=>{e.preventDefault();setDragging(true);}}
            onDragLeave={()=>setDragging(false)}
            onDrop={e=>{e.preventDefault();handleFile(e.dataTransfer.files[0]);}}>
            <div className="message-box-toolbar">
              <button className="attach" aria-label="Attach complaint file" onClick={()=>fileInput.current?.click()}>
                <Paperclip size={14}/>Attach file
              </button>
              <span className="attach-hint">PDF &middot; DOCX &middot; TXT &middot; Email</span>
            </div>
            <div className="message-box-input">
              <textarea
                ref={textareaRef}
                value={message}
                rows={2}
                onChange={e=>{setMessage(e.target.value);autoResize();}}
                onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();process(message);}}}
                placeholder="Type a message, paste a complaint or email…"
              />
              <button className="send-message" disabled={!message.trim()||loading} onClick={()=>process(message)}>
                <Send size={17}/>
              </button>
            </div>
            <input ref={fileInput} hidden type="file" accept=".pdf,.docx,.txt,.eml" onChange={e=>handleFile(e.target.files?.[0])}/>
            <div className="message-box-footer"><span>Powered by LangGraph</span></div>
          </div>
        </aside>
      </div>

      {/* Completeness checker dialog */}
      {completenessDialog&&(
        <div className="commit-dialog-backdrop" onClick={()=>setCompletenessDialog(null)}>
          <div className="commit-dialog completeness-dialog" role="dialog" aria-modal="true" aria-labelledby="completeness-title" onClick={e=>e.stopPropagation()}>
            <div className="completeness-dialog-header">
              <h2 id="completeness-title">Complaint Completeness Check</h2>
              <p>Some required fields are missing. Provide the details below and the Copilot will fill them in automatically.</p>
            </div>
            <div className="completeness-dialog-body">
              <p className="missing-fields-label">Missing fields</p>
              <ul className="missing-fields-list">
                {completenessDialog.map(([,title])=>(
                  <li key={title}><span className="missing-dot"/>{title}</li>
                ))}
              </ul>
              <p className="completeness-fill-label">Provide the missing details</p>
              <p className="completeness-fill-hint">Type naturally, e.g. &ldquo;Complaint source is Email, expiry date is March 2028, affected quantity is 3 vials&rdquo;</p>
              <textarea
                className="completeness-textarea"
                value={fillText}
                onChange={e=>setFillText(e.target.value)}
                placeholder="Enter the missing field values here…"
                rows={4}
                autoFocus
              />
              <div className="completeness-actions">
                <button className="outline" onClick={()=>setCompletenessDialog(null)}>Cancel</button>
                <button className="primary" disabled={!fillText.trim()||loading} onClick={handleFillMissing}>
                  <Check size={15}/>Add to Copilot
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Save / error dialog */}
      {dialog&&(
        <div className="commit-dialog-backdrop" onClick={dismissDialog}>
          <div className={`commit-dialog ${dialog.type}`} role="dialog" aria-modal="true" aria-labelledby="commit-dialog-title" onClick={e=>e.stopPropagation()}>
            <CheckCircle2 size={30}/>
            <h2 id="commit-dialog-title">{dialog.type==='success'?'Complaint committed':'Unable to commit complaint'}</h2>
            <p>{dialog.message}</p>
            <button className="primary" onClick={dismissDialog}>OK</button>
          </div>
        </div>
      )}
    </section>
  );
}
