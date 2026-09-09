"use client";
import { useEffect, useState } from "react";

type Breadth={date:string|null;eligible:number;above_20_sma:number|null;above_50_sma:number|null;above_200_sma:number|null;advances:number;declines:number;ad:number;new_highs:number;new_lows:number;movers_up_20_5d:number;movers_up_30_5d:number;up_4_volume:number;down_4_volume:number};
type Regime={regime:string;score:number;confidence:number;drivers:string[]};
type Global={symbol:string;price:number;change_pct:number|null;source:string;observed_at:string};
type Flow={date:string;fii_net:number;dii_net:number};
type Overview={breadth:Breadth;regime:Regime;global:Global[];flows:Flow[]};

const API=process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function Home(){
 const [data,setData]=useState<Overview|null>(null); const [error,setError]=useState("");
 useEffect(()=>{const load=()=>fetch(`${API}/market/overview`).then(r=>{if(!r.ok)throw new Error(`API returned ${r.status}`);return r.json()}).then(setData).catch(e=>setError(e.message)); load(); const id=setInterval(load,30000); return()=>clearInterval(id)},[]);
 if(error) return <main className="shell"><div className="top"><div><div className="brand">Market Monitor</div><div className="muted">Indian equity market intelligence</div></div></div><section className="card"><h2>Data unavailable</h2><p className="muted">{error}</p><p className="muted">The app intentionally shows no fabricated market values. Configure the backend and provider credentials.</p></section></main>;
 if(!data) return <main className="shell"><div className="card">Loading market data…</div></main>;
 const r=data.regime; const pill=r.regime==='RISK_ON'?'on':r.regime==='RISK_OFF'?'risk':'neutral';
 return <main className="shell">
  <div className="top"><div><div className="brand">Market Monitor</div><div className="muted">Live intelligence • auto-refresh 30s</div></div><span className={`pill ${pill}`}>{r.regime.replace("_"," ")}</span></div>
  <div className="grid">
   <section className="card span-4"><div className="muted">Market regime score</div><div className="kpi">{r.score}</div><div className="muted">Confidence {r.confidence}%</div><div className="rows">{r.drivers.map(d=><div className="row" key={d}>{d}</div>)}</div></section>
   <section className="card span-8"><h3>Market breadth</h3><div className="grid"><Metric label="Above 20 SMA" value={data.breadth.above_20_sma} suffix="%"/><Metric label="Above 50 SMA" value={data.breadth.above_50_sma} suffix="%"/><Metric label="Above 200 SMA" value={data.breadth.above_200_sma} suffix="%"/><Metric label="Advances" value={data.breadth.advances}/><Metric label="Declines" value={data.breadth.declines}/><Metric label="A/D" value={data.breadth.ad}/></div></section>
   <section className="card span-6"><h3>Global cues</h3><div className="rows">{data.global.map(x=><div className="row" key={x.symbol}><span>{x.symbol}</span><span className={x.change_pct!=null&&x.change_pct>=0?"positive": "negative"}>{Number.isFinite(x.price)?x.price.toLocaleString():"—"}{x.change_pct==null?"":` (${x.change_pct.toFixed(2)}%)`}</span></div>)}</div></section>
   <section className="card span-6"><h3>FII / DII (₹ Cr)</h3><div className="rows">{data.flows.map(x=><div className="row" key={x.date}><span>{x.date}</span><span>FII <b className={x.fii_net>=0?"positive":"negative"}>{x.fii_net.toFixed(0)}</b> · DII <b className={x.dii_net>=0?"positive":"negative"}>{x.dii_net.toFixed(0)}</b></span></div>)}</div></section>
   <section className="card span-6"><h3>Participation</h3><div className="rows"><div className="row"><span>20%+ / 5D</span><b>{data.breadth.movers_up_20_5d}</b></div><div className="row"><span>30%+ / 5D</span><b>{data.breadth.movers_up_30_5d}</b></div><div className="row"><span>4%+ + volume</span><b>{data.breadth.up_4_volume}</b></div><div className="row"><span>4%- + volume</span><b>{data.breadth.down_4_volume}</b></div></div></section>
   <section className="card span-6"><h3>Market extremes</h3><div className="rows"><div className="row"><span>52W new highs</span><b>{data.breadth.new_highs}</b></div><div className="row"><span>52W new lows</span><b>{data.breadth.new_lows}</b></div><div className="row"><span>Eligible universe</span><b>{data.breadth.eligible}</b></div><div className="row"><span>Last breadth date</span><b>{data.breadth.date??"—"}</b></div></div></section>
  </div>
 </main>
}
function Metric({label,value,suffix=""}:{label:string;value:number|null;suffix?:string}){return <div className="card" style={{gridColumn:"span 4"}}><div className="muted">{label}</div><div className="kpi" style={{fontSize:26}}>{value==null?"—":`${value.toFixed(2)}${suffix}`}</div></div>}
