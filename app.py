import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from datetime import datetime

st.set_page_config(
    page_title="LL Rent a Car Joy",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    section[data-testid="stSidebar"] .stSelectbox > div { background-color: #0a0a2e !important; border: 1px solid #1a1aff55 !important; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 500 !important; }
    p, span, label, div { color: #c8d4ff; }
    div[data-testid="metric-container"] { background: linear-gradient(135deg, #0d0d35 0%, #0a0a2e 100%); border: 1px solid #1a1aff33; border-radius: 14px; padding: 1.2rem 1.4rem; position: relative; overflow: hidden; }
    div[data-testid="metric-container"] label { color: #7a94ff !important; font-size: 13px !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; }
    .stFileUploader { border: 1px dashed #1a1aff55 !important; border-radius: 12px !important; background-color: #0a0a2e !important; padding: 1rem !important; }
    .stDownloadButton button { background: linear-gradient(135deg, #1a1aff 0%, #3333ff 100%) !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
    .stButton button { background: linear-gradient(135deg, #1a1aff 0%, #3333ff 100%) !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
    .stAlert { border-radius: 10px !important; background-color: #0a0a2e !important; border-left: 3px solid #1a1aff !important; }
    .stSelectbox > div > div { background-color: #0a0a2e !important; border: 1px solid #1a1aff33 !important; border-radius: 8px !important; }
    .stMultiSelect > div { background-color: #0a0a2e !important; border: 1px solid #1a1aff33 !important; border-radius: 8px !important; }
    .stDataFrame { border: 1px solid #1a1aff33 !important; border-radius: 12px !important; }
    .streamlit-expanderHeader { color: #7a94ff !important; background-color: #0a0a2e !important; border: 1px solid #1a1aff33 !important; border-radius: 10px !important; }
    .streamlit-expanderContent { background-color: #0a0a2e !important; border: 1px solid #1a1aff22 !important; }
    hr { border-color: #1a1aff22 !important; }
    .kpi-card { background: linear-gradient(135deg, #0d0d35 0%, #0a0a2e 100%); border: 1px solid #1a1aff33; border-radius: 14px; padding: 1.2rem 1.4rem; position: relative; overflow: hidden; margin-bottom: 0.5rem; }
    .kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
    .kpi-card.blue::before { background: linear-gradient(90deg, #1a1aff, #4499ff); }
    .kpi-card.green::before { background: linear-gradient(90deg, #00cc88, #00ff99); }
    .kpi-card.red::before { background: linear-gradient(90deg, #ff3333, #ff6666); }
    .kpi-card.amber::before { background: linear-gradient(90deg, #ffaa00, #ffcc44); }
    .kpi-label { font-size: 12px; color: #7a94ff; margin: 0 0 6px; letter-spacing: 0.5px; text-transform: uppercase; }
    .kpi-value { font-size: 1.8rem; font-weight: 600; color: #ffffff; font-family: 'DM Mono', monospace; margin: 0; line-height: 1.1; }
    .kpi-delta { font-size: 12px; margin: 6px 0 0; }
    .kpi-delta.pos { color: #00cc88; }
    .kpi-delta.neg { color: #ff4444; }
    .kpi-delta.neu { color: #7a94ff; }
    .section-title { font-size: 13px; font-weight: 500; color: #7a94ff; letter-spacing: 1px; text-transform: uppercase; margin: 0 0 1rem; padding-bottom: 8px; border-bottom: 1px solid #1a1aff22; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTES ─────────────────────────────────────────────────────────────────
MONTHS_ES = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
             7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
PLOT_BG = "#05051a"
GRID_COLOR = "#1a1aff18"
TEXT_COLOR = "#a0b4ff"
COLOR_ING = "#1a56ff"
COLOR_EGR = "#ff3333"
COLOR_NET = "#00cc88"
COLOR_ACUM = "#aa44ff"

# ── DEMO DATA ──────────────────────────────────────────────────────────────────
def get_demo_data():
    ing = {1:380000,2:420000,3:390000,4:510000,5:475000,6:560000,
           7:640000,8:620000,9:490000,10:530000,11:480000,12:610000}
    egr = {1:180000,2:195000,3:210000,4:230000,5:220000,6:260000,
           7:290000,8:275000,9:235000,10:250000,11:240000,12:280000}
    rows_i, rows_e = [], []
    import random; random.seed(42)
    for m, tot in ing.items():
        n = random.randint(8, 14)
        for i in range(n):
            rows_i.append({"fecha": pd.Timestamp(f"2024-{m:02d}-{min(i*2+1,28):02d}"), "monto": round(tot/n)})
    for m, tot in egr.items():
        n = random.randint(4, 7)
        for i in range(n):
            rows_e.append({"fecha": pd.Timestamp(f"2024-{m:02d}-{min(i*3+1,28):02d}"), "monto": round(tot/n)})
    return pd.DataFrame(rows_i), pd.DataFrame(rows_e)

# ── PARSE ──────────────────────────────────────────────────────────────────────
def parse_file(f):
    try:
        name = f.name.lower()
        df = pd.read_csv(f, encoding="utf-8-sig") if name.endswith(".csv") else pd.read_excel(f)
        df.columns = [str(c).strip().lower() for c in df.columns]
        fc = next((c for c in df.columns if "fecha" in c or "date" in c), None)
        mc = next((c for c in df.columns if any(k in c for k in ["monto","amount","importe","valor","total"])), None)
        if not fc or not mc:
            st.error(f"Columnas no encontradas. Disponibles: {list(df.columns)}")
            return pd.DataFrame()
        df = df[[fc, mc]].copy(); df.columns = ["fecha","monto"]
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", dayfirst=True)
        df["monto"] = pd.to_numeric(df["monto"].astype(str).str.replace(r"[$\.](?=\d{3})", "", regex=True).str.replace(",",".",regex=False), errors="coerce")
        return df.dropna()
    except Exception as e:
        st.error(f"Error: {e}"); return pd.DataFrame()

def agg_monthly(df):
    if df.empty: return {}
    df = df.copy(); df["mes"] = df["fecha"].dt.month
    return df.groupby("mes")["monto"].sum().to_dict()

def base_layout(**kw):
    return dict(plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
                font=dict(color=TEXT_COLOR, family="DM Sans"),
                margin=dict(l=10, r=10, t=30, b=10), **kw)

def style_ax(fig):
    fig.update_xaxes(gridcolor=GRID_COLOR, linecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    return fig

def fmt(n): return f"${n:,.0f}".replace(",",".")

# ── CHARTS ─────────────────────────────────────────────────────────────────────
def chart_main(months, ing, egr, net):
    lbls = [MONTHS_ES[m] for m in months]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Ingresos", x=lbls, y=ing, marker_color=COLOR_ING, marker_line_width=0, opacity=0.9))
    fig.add_trace(go.Bar(name="Egresos", x=lbls, y=egr, marker_color=COLOR_EGR, marker_line_width=0, opacity=0.9))
    fig.add_trace(go.Scatter(name="Ganancia neta", x=lbls, y=net, mode="lines+markers",
                             line=dict(color=COLOR_NET, width=2.5), marker=dict(size=7, color=COLOR_NET)))
    fig.update_layout(**base_layout(
        barmode="group", height=320,
        legend=dict(orientation="h", y=1.12, x=0, bgcolor="rgba(0,0,0,0)", font_size=12),
        yaxis=dict(tickprefix="$", tickformat=",.0f", gridcolor=GRID_COLOR),
    ))
    return style_ax(fig)

def chart_acum(months, net):
    lbls = [MONTHS_ES[m] for m in months]
    acum = list(np.cumsum(net))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=lbls, y=acum, mode="lines+markers", fill="tozeroy",
                             fillcolor="rgba(170,68,255,0.08)", line=dict(color=COLOR_ACUM, width=2.5),
                             marker=dict(size=7, color=COLOR_ACUM)))
    fig.update_layout(**base_layout(showlegend=False, height=240,
                                    yaxis=dict(tickprefix="$", tickformat=",.0f", gridcolor=GRID_COLOR)))
    return style_ax(fig)

def chart_margen(months, ing, net):
    lbls = [MONTHS_ES[m] for m in months]
    mgn = [round(n/i*100,1) if i else 0 for n,i in zip(net,ing)]
    colors = [COLOR_NET if m>=30 else "#ffaa00" if m>0 else COLOR_EGR for m in mgn]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=lbls, y=mgn, marker_color=colors, marker_line_width=0,
                         text=[f"{m}%" for m in mgn], textposition="outside",
                         textfont=dict(color=TEXT_COLOR, size=11)))
    fig.add_hline(y=0, line_color=GRID_COLOR, line_width=1)
    fig.update_layout(**base_layout(showlegend=False, height=240,
                                    yaxis=dict(ticksuffix="%", gridcolor=GRID_COLOR)))
    return style_ax(fig)

def chart_donut(total_ing, total_egr):
    fig = go.Figure(go.Pie(
        labels=["Ingresos","Egresos"], values=[total_ing, total_egr], hole=0.65,
        marker=dict(colors=[COLOR_ING, COLOR_EGR], line=dict(color=PLOT_BG, width=3)),
        textinfo="percent", textfont=dict(color="#ffffff", size=12),
    ))
    pct_egr = round(total_egr/total_ing*100) if total_ing else 0
    fig.update_layout(**base_layout(showlegend=False, height=220,
        annotations=[dict(text=f"{pct_egr}%<br>costo", x=0.5, y=0.5,
                         font_size=16, showarrow=False, font_color="#ffffff")]))
    return fig

# ── EXCEL EXPORT ───────────────────────────────────────────────────────────────
def build_excel(months, ing, egr, net, year):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    wb = Workbook(); ws = wb.active; ws.title = "Dashboard"
    thin = Side(style="thin", color="1a1aff")
    brd = Border(left=thin, right=thin, top=thin, bottom=thin)
    hdrs = ["Mes","Ingresos ($)","Egresos ($)","Ganancia Neta ($)","Margen (%)"]
    for i,h in enumerate(hdrs,1):
        c = ws.cell(row=1,column=i,value=h)
        c.font=Font(bold=True,color="FFFFFF",name="Calibri")
        c.fill=PatternFill("solid",start_color="1a1aff")
        c.alignment=Alignment(horizontal="center"); c.border=brd
    for i,m in enumerate(months):
        r=i+2; i_=ing[i]; e_=egr[i]; n_=net[i]
        mgn=round(n_/i_*100,1) if i_ else 0
        for j,v in enumerate([MONTHS_ES[m],i_,e_,n_,mgn],1):
            c=ws.cell(row=r,column=j,value=v)
            c.font=Font(name="Calibri"); c.border=brd
            if j==1: c.alignment=Alignment(horizontal="center")
            elif j in [2,3,4]: c.number_format="#,##0"; c.alignment=Alignment(horizontal="right")
            elif j==5: c.number_format='0.0"%"'; c.alignment=Alignment(horizontal="center")
            if j==4: c.font=Font(name="Calibri",color="1A6B1A" if n_>=0 else "A32D2D")
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = max(len(str(c.value or "")) for c in col)+4
    buf=BytesIO(); wb.save(buf); buf.seek(0); return buf

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#0a0a2e 0%,#07071f 100%);
     padding:1.8rem 2.5rem;border-radius:16px;margin-bottom:2rem;
     display:flex;align-items:center;gap:2rem;
     border:1px solid #1a1aff33;position:relative;overflow:hidden;">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
       background:linear-gradient(90deg,#1a1aff,#4499ff,#00cc88);"></div>
  <div style="width:60px;height:60px;border-radius:14px;
       background:linear-gradient(135deg,#1a1aff,#3333ff);
       display:flex;align-items:center;justify-content:center;font-size:28px;flex-shrink:0;">🚗</div>
  <div>
    <div style="font-size:1.7rem;font-weight:600;color:#ffffff;letter-spacing:-0.5px;line-height:1.1;">
      LL Rent a Car Joy
    </div>
    <div style="font-size:13px;color:#7a94ff;margin-top:4px;letter-spacing:0.5px;">
      Dashboard Financiero · Ingresos & Egresos
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.markdown("---")
    st.markdown("**📂 Tus archivos**")
    ing_file = st.file_uploader("Ingresos (CSV / Excel)", type=["csv","xlsx","xls"], key="ing")
    egr_file = st.file_uploader("Egresos (CSV / Excel)", type=["csv","xlsx","xls"], key="egr")
    st.markdown("---")
    st.markdown("**📅 Período**")
    year_sel = st.selectbox("Año", [2024, 2025, 2026], index=0)
    months_sel = st.multiselect("Meses", list(range(1,13)), default=list(range(1,13)),
                                format_func=lambda m: MONTHS_ES[m])
    st.markdown("---")
    with st.expander("📌 ¿Cómo preparar mis datos?"):
        st.markdown("""
Tu archivo necesita **dos columnas**:

| fecha | monto |
|-------|-------|
| 01/01/2024 | 45000 |
| 15/01/2024 | 32000 |

Formatos: **CSV** o **Excel (.xlsx)**

La columna fecha puede llamarse `fecha` o `date`.
La de monto: `monto`, `amount`, `importe`, `valor` o `total`.
        """)
    st.markdown("---")
    st.caption("LL Rent a Car Joy · v1.0")

# ── DATOS ──────────────────────────────────────────────────────────────────────
using_demo = not ing_file and not egr_file
if using_demo:
    ing_df, egr_df = get_demo_data()
else:
    ing_df = parse_file(ing_file) if ing_file else pd.DataFrame(columns=["fecha","monto"])
    egr_df = parse_file(egr_file) if egr_file else pd.DataFrame(columns=["fecha","monto"])
    if ing_df.empty and egr_df.empty: st.stop()
    ing_df = ing_df[ing_df["fecha"].dt.year == year_sel] if not ing_df.empty else ing_df
    egr_df = egr_df[egr_df["fecha"].dt.year == year_sel] if not egr_df.empty else egr_df

if using_demo:
    st.info("📊 Mostrando **datos de ejemplo**. Cargá tus archivos en el panel lateral para ver tus números reales.")

ing_by_m = agg_monthly(ing_df)
egr_by_m = agg_monthly(egr_df)
all_months = sorted(set(list(ing_by_m.keys()) + list(egr_by_m.keys())))
if months_sel: all_months = [m for m in all_months if m in months_sel]
if not all_months: st.warning("No hay datos para el período seleccionado."); st.stop()

ing_v = [ing_by_m.get(m,0) for m in all_months]
egr_v = [egr_by_m.get(m,0) for m in all_months]
net_v = [i-e for i,e in zip(ing_v,egr_v)]
total_ing = sum(ing_v); total_egr = sum(egr_v); total_net = total_ing - total_egr
margen = round(total_net/total_ing*100,1) if total_ing else 0
mejor = all_months[net_v.index(max(net_v))] if net_v else 1
peor  = all_months[net_v.index(min(net_v))] if net_v else 1

# ── KPIs ───────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">Resumen del período</p>', unsafe_allow_html=True)
k1,k2,k3,k4 = st.columns(4)

with k1:
    st.markdown(f'<div class="kpi-card blue"><p class="kpi-label">Ingresos totales</p><p class="kpi-value">{fmt(total_ing)}</p><p class="kpi-delta neu">{len(all_months)} meses analizados</p></div>', unsafe_allow_html=True)
with k2:
    pct_e = round(total_egr/total_ing*100) if total_ing else 0
    st.markdown(f'<div class="kpi-card red"><p class="kpi-label">Egresos totales</p><p class="kpi-value">{fmt(total_egr)}</p><p class="kpi-delta neu">{pct_e}% de los ingresos</p></div>', unsafe_allow_html=True)
with k3:
    col_net = "green" if total_net>=0 else "red"
    icon = "▲ Rentable" if total_net>=0 else "▼ En pérdida"
    dcls = "pos" if total_net>=0 else "neg"
    st.markdown(f'<div class="kpi-card {col_net}"><p class="kpi-label">Ganancia neta</p><p class="kpi-value">{fmt(total_net)}</p><p class="kpi-delta {dcls}">{icon}</p></div>', unsafe_allow_html=True)
with k4:
    mc = "green" if margen>=30 else "amber" if margen>0 else "red"
    st.markdown(f'<div class="kpi-card {mc}"><p class="kpi-label">Margen neto</p><p class="kpi-value">{margen}%</p><p class="kpi-delta neu">Mejor: {MONTHS_ES[mejor]} · Peor: {MONTHS_ES[peor]}</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CHART PRINCIPAL ────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">Ingresos vs Egresos</p>', unsafe_allow_html=True)
st.plotly_chart(chart_main(all_months, ing_v, egr_v, net_v), use_container_width=True, config={"displayModeBar":False})

# ── CHARTS SECUNDARIOS ─────────────────────────────────────────────────────────
st.markdown('<p class="section-title">Análisis detallado</p>', unsafe_allow_html=True)
c1,c2,c3 = st.columns([2,2,1])
with c1:
    st.markdown("**Tendencia acumulada**")
    st.plotly_chart(chart_acum(all_months, net_v), use_container_width=True, config={"displayModeBar":False})
with c2:
    st.markdown("**Margen mensual (%)**")
    st.plotly_chart(chart_margen(all_months, ing_v, net_v), use_container_width=True, config={"displayModeBar":False})
with c3:
    st.markdown("**Distribución**")
    if total_ing > 0:
        st.plotly_chart(chart_donut(total_ing, total_egr), use_container_width=True, config={"displayModeBar":False})

# ── TABLA ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-title">Detalle mensual</p>', unsafe_allow_html=True)
rows = []
for i,m in enumerate(all_months):
    i_=ing_v[i]; e_=egr_v[i]; n_=net_v[i]
    mgn_m=round(n_/i_*100,1) if i_ else 0
    est = "✅ Excelente" if n_>0 and mgn_m>=30 else "🟡 Positivo" if n_>0 else "🔴 Negativo"
    rows.append({"Mes":MONTHS_ES[m],"Ingresos":fmt(i_),"Egresos":fmt(e_),"Ganancia neta":fmt(n_),"Margen":f"{mgn_m}%","Estado":est})
rows.append({"Mes":"TOTAL","Ingresos":fmt(total_ing),"Egresos":fmt(total_egr),"Ganancia neta":fmt(total_net),"Margen":f"{margen}%","Estado":"—"})
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── EXPORT ─────────────────────────────────────────────────────────────────────
st.markdown("---")
col_dl, col_info = st.columns([1,3])
with col_dl:
    st.download_button(
        label="⬇️ Descargar Excel",
        data=build_excel(all_months, ing_v, egr_v, net_v, year_sel),
        file_name=f"ll_rent_a_car_joy_{year_sel}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
with col_info:
    st.caption(f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} · LL Rent a Car Joy")
