import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="LL Rent a Car Joy", page_icon="🚗", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background-color: #05051a; }
    .main { background-color: #05051a; }
    .block-container { padding: 1.5rem 2rem 3rem; }
    section[data-testid="stSidebar"] { background-color: #07071f; border-right: 1px solid #1a1aff33; }
    section[data-testid="stSidebar"] * { color: #a0b4ff !important; }
    section[data-testid="stSidebar"] input { background-color: #0a0a2e !important; border: 1px solid #1a1aff55 !important; color: #ffffff !important; border-radius: 8px !important; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 500 !important; }
    p, span, label, div { color: #c8d4ff; }
    div[data-testid="metric-container"] { background: #0d0d35; border: 1px solid #1a1aff33; border-radius: 14px; padding: 1.2rem 1.4rem; }
    div[data-testid="metric-container"] label { color: #7a94ff !important; font-size: 13px !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #ffffff !important; }
    .stFileUploader { border: 1px dashed #1a1aff55 !important; border-radius: 12px !important; background-color: #0a0a2e !important; }
    .stDownloadButton button { background: #1a1aff !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
    .stButton button { background: #1a1aff !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
    .stAlert { border-radius: 10px !important; background-color: #0a0a2e !important; border-left: 3px solid #1a1aff !important; }
    .stSelectbox > div > div { background-color: #0a0a2e !important; border: 1px solid #1a1aff33 !important; border-radius: 8px !important; }
    .stMultiSelect > div { background-color: #0a0a2e !important; border: 1px solid #1a1aff33 !important; border-radius: 8px !important; }
    .stDataFrame { border: 1px solid #1a1aff33 !important; border-radius: 12px !important; }
    .streamlit-expanderHeader { color: #7a94ff !important; background-color: #0a0a2e !important; border: 1px solid #1a1aff33 !important; border-radius: 10px !important; }
    hr { border-color: #1a1aff22 !important; }
    .kpi-card { background: #0d0d35; border: 1px solid #1a1aff33; border-top: 2px solid #1a1aff; border-radius: 14px; padding: 1.2rem 1.4rem; margin-bottom: 0.5rem; }
    .kpi-card.green { border-top-color: #00cc88; }
    .kpi-card.red { border-top-color: #ff3333; }
    .kpi-card.amber { border-top-color: #ffaa00; }
    .kpi-label { font-size: 12px; color: #7a94ff; margin: 0 0 6px; letter-spacing: 0.5px; text-transform: uppercase; }
    .kpi-value { font-size: 1.8rem; font-weight: 600; color: #ffffff; font-family: 'DM Mono', monospace; margin: 0; line-height: 1.1; }
    .kpi-delta { font-size: 12px; margin: 6px 0 0; }
    .kpi-delta.pos { color: #00cc88; }
    .kpi-delta.neg { color: #ff4444; }
    .kpi-delta.neu { color: #7a94ff; }
    .section-title { font-size: 13px; font-weight: 500; color: #7a94ff; letter-spacing: 1px; text-transform: uppercase; margin: 0 0 1rem; padding-bottom: 8px; border-bottom: 1px solid #1a1aff22; }
</style>
""", unsafe_allow_html=True)

MONTHS_ES = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
BG="#05051a"; GRID="#1a1aff18"; TC="#a0b4ff"; CI="#1a56ff"; CE="#ff3333"; CN="#00cc88"; CA="#aa44ff"

def get_demo():
    ing={1:380000,2:420000,3:390000,4:510000,5:475000,6:560000,7:640000,8:620000,9:490000,10:530000,11:480000,12:610000}
    egr={1:180000,2:195000,3:210000,4:230000,5:220000,6:260000,7:290000,8:275000,9:235000,10:250000,11:240000,12:280000}
    ri,re=[],[]
    import random; random.seed(42)
    for m,t in ing.items():
        n=random.randint(8,14)
        for i in range(n): ri.append({"fecha":pd.Timestamp(f"2024-{m:02d}-{min(i*2+1,28):02d}"),"monto":round(t/n)})
    for m,t in egr.items():
        n=random.randint(4,7)
        for i in range(n): re.append({"fecha":pd.Timestamp(f"2024-{m:02d}-{min(i*3+1,28):02d}"),"monto":round(t/n)})
    return pd.DataFrame(ri),pd.DataFrame(re)

def parse_file(f):
    try:
        name=f.name.lower()
        df=pd.read_csv(f,encoding="utf-8-sig") if name.endswith(".csv") else pd.read_excel(f)
        df.columns=[str(c).strip().lower() for c in df.columns]
        fc=next((c for c in df.columns if "fecha" in c or "date" in c),None)
        mc=next((c for c in df.columns if any(k in c for k in ["monto","amount","importe","valor","total"])),None)
        if not fc or not mc: st.error(f"Columnas no encontradas. Disponibles: {list(df.columns)}"); return pd.DataFrame()
        df=df[[fc,mc]].copy(); df.columns=["fecha","monto"]
        df["fecha"]=pd.to_datetime(df["fecha"],errors="coerce",dayfirst=True)
        df["monto"]=pd.to_numeric(df["monto"].astype(str).str.replace(r"[$\.](?=\d{3})","",regex=True).str.replace(",",".",regex=False),errors="coerce")
        return df.dropna()
    except Exception as e:
        st.error(f"Error: {e}"); return pd.DataFrame()

def agg(df):
    if df.empty: return {}
    d=df.copy(); d["mes"]=d["fecha"].dt.month
    return d.groupby("mes")["monto"].sum().to_dict()

def fmt(n): return f"${n:,.0f}".replace(",",".")

def chart_main(months,ing,egr,net):
    lbls=[MONTHS_ES[m] for m in months]
    fig=go.Figure()
    fig.add_trace(go.Bar(name="Ingresos",x=lbls,y=ing,marker_color=CI,marker_line_width=0,opacity=0.9))
    fig.add_trace(go.Bar(name="Egresos",x=lbls,y=egr,marker_color=CE,marker_line_width=0,opacity=0.9))
    fig.add_trace(go.Scatter(name="Ganancia neta",x=lbls,y=net,mode="lines+markers",
                             line=dict(color=CN,width=2.5),marker=dict(size=7,color=CN)))
    fig.update_layout(plot_bgcolor=BG,paper_bgcolor=BG,font=dict(color=TC,family="DM Sans"),
                      margin=dict(l=10,r=10,t=40,b=10),barmode="group",height=320,
                      showlegend=True,legend=dict(orientation="h",y=1.1,x=0,bgcolor="rgba(0,0,0,0)"),
                      xaxis=dict(gridcolor=GRID,linecolor=GRID),
                      yaxis=dict(tickprefix="$",tickformat=",.0f",gridcolor=GRID,linecolor=GRID))
    return fig

def chart_acum(months,net):
    lbls=[MONTHS_ES[m] for m in months]
    acum=list(np.cumsum(net))
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=lbls,y=acum,mode="lines+markers",fill="tozeroy",
                             fillcolor="rgba(170,68,255,0.08)",line=dict(color=CA,width=2.5),
                             marker=dict(size=7,color=CA)))
    fig.update_layout(plot_bgcolor=BG,paper_bgcolor=BG,font=dict(color=TC,family="DM Sans"),
                      margin=dict(l=10,r=10,t=30,b=10),showlegend=False,height=240,
                      xaxis=dict(gridcolor=GRID,linecolor=GRID),
                      yaxis=dict(tickprefix="$",tickformat=",.0f",gridcolor=GRID,linecolor=GRID))
    return fig

def chart_margen(months,ing,net):
    lbls=[MONTHS_ES[m] for m in months]
    mgn=[round(n/i*100,1) if i else 0 for n,i in zip(net,ing)]
    colors=[CN if m>=30 else "#ffaa00" if m>0 else CE for m in mgn]
    fig=go.Figure()
    fig.add_trace(go.Bar(x=lbls,y=mgn,marker_color=colors,marker_line_width=0,
                         text=[f"{m}%" for m in mgn],textposition="outside",
                         textfont=dict(color=TC,size=11)))
    fig.add_hline(y=0,line_color=GRID,line_width=1)
    fig.update_layout(plot_bgcolor=BG,paper_bgcolor=BG,font=dict(color=TC,family="DM Sans"),
                      margin=dict(l=10,r=10,t=30,b=10),showlegend=False,height=240,
                      xaxis=dict(gridcolor=GRID,linecolor=GRID),
                      yaxis=dict(ticksuffix="%",gridcolor=GRID,linecolor=GRID))
    return fig

def chart_donut(ti,te):
    pct=round(te/ti*100) if ti else 0
    fig=go.Figure(go.Pie(labels=["Ingresos","Egresos"],values=[ti,te],hole=0.65,
                         marker=dict(colors=[CI,CE],line=dict(color=BG,width=3)),
                         textinfo="percent",textfont=dict(color="#ffffff",size=12)))
    fig.update_layout(plot_bgcolor=BG,paper_bgcolor=BG,font=dict(color=TC,family="DM Sans"),
                      margin=dict(l=10,r=10,t=10,b=10),showlegend=False,height=220,
                      annotations=[dict(text=f"{pct}%<br>costo",x=0.5,y=0.5,
                                        font=dict(size=16,color="#ffffff"),showarrow=False)])
    return fig

def build_excel(months,ing,egr,net,year):
    from openpyxl import Workbook
    from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
    wb=Workbook(); ws=wb.active; ws.title="Dashboard"
    thin=Side(style="thin",color="1a1aff")
    brd=Border(left=thin,right=thin,top=thin,bottom=thin)
    for i,h in enumerate(["Mes","Ingresos ($)","Egresos ($)","Ganancia Neta ($)","Margen (%)"],1):
        c=ws.cell(row=1,column=i,value=h)
        c.font=Font(bold=True,color="FFFFFF",name="Calibri")
        c.fill=PatternFill("solid",start_color="1a1aff")
        c.alignment=Alignment(horizontal="center"); c.border=brd
    for i,m in enumerate(months):
        r=i+2; iv=ing[i]; ev=egr[i]; nv=net[i]; mg=round(nv/iv*100,1) if iv else 0
        for j,v in enumerate([MONTHS_ES[m],iv,ev,nv,mg],1):
            c=ws.cell(row=r,column=j,value=v); c.font=Font(name="Calibri"); c.border=brd
            if j==1: c.alignment=Alignment(horizontal="center")
            elif j in [2,3,4]: c.number_format="#,##0"; c.alignment=Alignment(horizontal="right")
            elif j==5: c.number_format='0.0"%"'; c.alignment=Alignment(horizontal="center")
            if j==4: c.font=Font(name="Calibri",color="1A6B1A" if nv>=0 else "A32D2D")
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width=max(len(str(c.value or "")) for c in col)+4
    buf=BytesIO(); wb.save(buf); buf.seek(0); return buf

st.markdown("""
<div style="background:#0a0a2e;padding:1.8rem 2.5rem;border-radius:16px;margin-bottom:2rem;
     display:flex;align-items:center;gap:2rem;border:1px solid #1a1aff33;border-top:2px solid #1a1aff;">
  <div style="width:60px;height:60px;border-radius:14px;background:#1a1aff;
       display:flex;align-items:center;justify-content:center;font-size:28px;flex-shrink:0;">🚗</div>
  <div>
    <div style="font-size:1.7rem;font-weight:600;color:#ffffff;letter-spacing:-0.5px;line-height:1.1;">LL Rent a Car Joy</div>
    <div style="font-size:13px;color:#7a94ff;margin-top:4px;letter-spacing:0.5px;">Dashboard Financiero · Ingresos & Egresos</div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.markdown("---")
    st.markdown("**📂 Tus archivos**")
    ing_file=st.file_uploader("Ingresos (CSV / Excel)",type=["csv","xlsx","xls"],key="ing")
    egr_file=st.file_uploader("Egresos (CSV / Excel)",type=["csv","xlsx","xls"],key="egr")
    st.markdown("---")
    st.markdown("**📅 Período**")
    year_sel=st.selectbox("Año",[2024,2025,2026],index=0)
    months_sel=st.multiselect("Meses",list(range(1,13)),default=list(range(1,13)),format_func=lambda m:MONTHS_ES[m])
    st.markdown("---")
    with st.expander("📌 ¿Cómo preparar mis datos?"):
        st.markdown("""
Tu archivo necesita **dos columnas**:

| fecha | monto |
|-------|-------|
| 01/01/2024 | 45000 |

Formatos: **CSV** o **Excel (.xlsx)**
        """)
    st.caption("LL Rent a Car Joy · v1.0")

using_demo=not ing_file and not egr_file
if using_demo:
    ing_df,egr_df=get_demo()
else:
    ing_df=parse_file(ing_file) if ing_file else pd.DataFrame(columns=["fecha","monto"])
    egr_df=parse_file(egr_file) if egr_file else pd.DataFrame(columns=["fecha","monto"])
    if ing_df.empty and egr_df.empty: st.stop()
    if not ing_df.empty: ing_df=ing_df[ing_df["fecha"].dt.year==year_sel]
    if not egr_df.empty: egr_df=egr_df[egr_df["fecha"].dt.year==year_sel]

if using_demo:
    st.info("📊 Mostrando **datos de ejemplo**. Cargá tus archivos en el panel lateral para ver tus números reales.")

im=agg(ing_df); em=agg(egr_df)
all_months=sorted(set(list(im.keys())+list(em.keys())))
if months_sel: all_months=[m for m in all_months if m in months_sel]
if not all_months: st.warning("No hay datos para el período seleccionado."); st.stop()

iv=[im.get(m,0) for m in all_months]
ev=[em.get(m,0) for m in all_months]
nv=[i-e for i,e in zip(iv,ev)]
ti=sum(iv); te=sum(ev); tn=ti-te
mg=round(tn/ti*100,1) if ti else 0
mejor=all_months[nv.index(max(nv))] if nv else 1
peor=all_months[nv.index(min(nv))] if nv else 1

st.markdown('<p class="section-title">Resumen del período</p>',unsafe_allow_html=True)
k1,k2,k3,k4=st.columns(4)
with k1: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Ingresos totales</p><p class="kpi-value">{fmt(ti)}</p><p class="kpi-delta neu">{len(all_months)} meses analizados</p></div>',unsafe_allow_html=True)
with k2:
    pe=round(te/ti*100) if ti else 0
    st.markdown(f'<div class="kpi-card red"><p class="kpi-label">Egresos totales</p><p class="kpi-value">{fmt(te)}</p><p class="kpi-delta neu">{pe}% de los ingresos</p></div>',unsafe_allow_html=True)
with k3:
    cc="green" if tn>=0 else "red"; ic="▲ Rentable" if tn>=0 else "▼ En pérdida"; dc="pos" if tn>=0 else "neg"
    st.markdown(f'<div class="kpi-card {cc}"><p class="kpi-label">Ganancia neta</p><p class="kpi-value">{fmt(tn)}</p><p class="kpi-delta {dc}">{ic}</p></div>',unsafe_allow_html=True)
with k4:
    mc="green" if mg>=30 else "amber" if mg>0 else "red"
    st.markdown(f'<div class="kpi-card {mc}"><p class="kpi-label">Margen neto</p><p class="kpi-value">{mg}%</p><p class="kpi-delta neu">Mejor: {MONTHS_ES[mejor]} · Peor: {MONTHS_ES[peor]}</p></div>',unsafe_allow_html=True)

st.markdown("<br>",unsafe_allow_html=True)
st.markdown('<p class="section-title">Ingresos vs Egresos</p>',unsafe_allow_html=True)
st.plotly_chart(chart_main(all_months,iv,ev,nv),use_container_width=True,config={"displayModeBar":False})

st.markdown('<p class="section-title">Análisis detallado</p>',unsafe_allow_html=True)
c1,c2,c3=st.columns([2,2,1])
with c1:
    st.markdown("**Tendencia acumulada**")
    st.plotly_chart(chart_acum(all_months,nv),use_container_width=True,config={"displayModeBar":False})
with c2:
    st.markdown("**Margen mensual (%)**")
    st.plotly_chart(chart_margen(all_months,iv,nv),use_container_width=True,config={"displayModeBar":False})
with c3:
    st.markdown("**Distribución**")
    if ti>0: st.plotly_chart(chart_donut(ti,te),use_container_width=True,config={"displayModeBar":False})

st.markdown("---")
st.markdown('<p class="section-title">Detalle mensual</p>',unsafe_allow_html=True)
rows=[]
for i,m in enumerate(all_months):
    i_=iv[i]; e_=ev[i]; n_=nv[i]; mg_=round(n_/i_*100,1) if i_ else 0
    est="✅ Excelente" if n_>0 and mg_>=30 else "🟡 Positivo" if n_>0 else "🔴 Negativo"
    rows.append({"Mes":MONTHS_ES[m],"Ingresos":fmt(i_),"Egresos":fmt(e_),"Ganancia neta":fmt(n_),"Margen":f"{mg_}%","Estado":est})
rows.append({"Mes":"TOTAL","Ingresos":fmt(ti),"Egresos":fmt(te),"Ganancia neta":fmt(tn),"Margen":f"{mg}%","Estado":"—"})
st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

st.markdown("---")
col_dl,col_info=st.columns([1,3])
with col_dl:
    st.download_button(label="⬇️ Descargar Excel",
                       data=build_excel(all_months,iv,ev,nv,year_sel),
                       file_name=f"ll_rent_a_car_joy_{year_sel}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
with col_info:
    st.caption(f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} · LL Rent a Car Joy")
