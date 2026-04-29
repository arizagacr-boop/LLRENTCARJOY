import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
BG = "#05051a"
CI = "#1a56ff"
CE = "#ff3333"
CN = "#00cc88"
CA = "#aa44ff"
TC = "#a0b4ff"
CAT_COLORS = ["#1a56ff","#ff3333","#00cc88","#ffaa00","#aa44ff","#ff6699","#00ccff","#ff9933","#66ff99","#cc44ff"]

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG,
    "axes.edgecolor": "#1a1aff33", "axes.labelcolor": TC,
    "xtick.color": TC, "ytick.color": TC,
    "text.color": TC, "grid.color": "#1a1aff18",
    "grid.linestyle": "--", "grid.linewidth": 0.5,
})

# ── PARSE PLANILLA ÚNICA ───────────────────────────────────────────────────────
def parse_planilla(f):
    try:
        name = f.name.lower()
        if name.endswith(".csv"):
            raw = pd.read_csv(f, header=None, encoding="utf-8-sig")
        else:
            raw = pd.read_excel(f, header=None)

        # Encontrar fila de encabezados buscando "Fecha" o "fecha"
        header_row = 0
        for i, row in raw.iterrows():
            vals = [str(v).strip().lower() for v in row.values]
            if "fecha" in vals:
                header_row = i
                break

        df = raw.iloc[header_row:].copy()
        df.columns = [str(v).strip() for v in df.iloc[0].values]
        df = df.iloc[1:].reset_index(drop=True)

        # Detectar columnas de EGRESOS (izquierda): Fecha, Concepto, Monto
        cols = list(df.columns)
        egr_fecha_col = next((c for c in cols if str(c).lower() == "fecha"), None)
        egr_monto_col = next((c for c in cols if str(c).lower() == "monto"), None)
        egr_concepto_col = next((c for c in cols if str(c).lower() in ["concepto","categoria","category","descripcion"]), None)

        # Detectar columnas de INGRESOS (derecha): buscar segunda ocurrencia de Fecha/Monto
        fecha_cols = [c for c in cols if str(c).lower() == "fecha"]
        monto_cols = [c for c in cols if str(c).lower() == "monto"]

        ing_fecha_col = fecha_cols[1] if len(fecha_cols) > 1 else None
        ing_monto_col = monto_cols[1] if len(monto_cols) > 1 else None

        # Si hay columnas duplicadas con sufijos automáticos de pandas
        if ing_fecha_col is None:
            ing_fecha_col = next((c for c in cols if "fecha" in str(c).lower() and c != egr_fecha_col), None)
        if ing_monto_col is None:
            ing_monto_col = next((c for c in cols if "monto" in str(c).lower() and c != egr_monto_col), None)

        # Armar DF egresos
        egr_df = pd.DataFrame()
        if egr_fecha_col and egr_monto_col:
            egr_df = df[[egr_fecha_col, egr_monto_col] + ([egr_concepto_col] if egr_concepto_col else [])].copy()
            egr_df.columns = ["fecha","monto"] + (["concepto"] if egr_concepto_col else [])
            egr_df["fecha"] = pd.to_datetime(egr_df["fecha"], errors="coerce", dayfirst=True)
            egr_df["monto"] = pd.to_numeric(egr_df["monto"].astype(str).str.replace(r"[.$]","",regex=True).str.replace(",",".",regex=False), errors="coerce")
            egr_df = egr_df.dropna(subset=["fecha","monto"])
            if "concepto" not in egr_df.columns:
                egr_df["concepto"] = "Sin categoría"
            else:
                egr_df["concepto"] = egr_df["concepto"].fillna("Sin categoría").astype(str).str.strip()
                egr_df = egr_df[~egr_df["concepto"].str.lower().isin(["agregar peajes","agregar seguro","mas gastos ?","nan",""])]

        # Armar DF ingresos
        ing_df = pd.DataFrame()
        if ing_fecha_col and ing_monto_col:
            ing_df = df[[ing_fecha_col, ing_monto_col]].copy()
            ing_df.columns = ["fecha","monto"]
            ing_df["fecha"] = pd.to_datetime(ing_df["fecha"], errors="coerce", dayfirst=True)
            ing_df["monto"] = pd.to_numeric(ing_df["monto"].astype(str).str.replace(r"[.$]","",regex=True).str.replace(",",".",regex=False), errors="coerce")
            ing_df = ing_df.dropna(subset=["fecha","monto"])

        return ing_df, egr_df

    except Exception as e:
        st.error(f"Error leyendo planilla: {e}")
        return pd.DataFrame(), pd.DataFrame()

# ── DEMO DATA ──────────────────────────────────────────────────────────────────
def get_demo():
    categorias = ["Nafta","Mecánico","Seguro","Peajes","GPS","Lavado","Patente"]
    ing_rows, egr_rows = [], []
    import random; random.seed(42)
    ing_totals = {1:380000,2:420000,3:390000,4:510000,5:475000,6:560000,7:640000,8:620000,9:490000,10:530000,11:480000,12:610000}
    egr_totals = {1:180000,2:195000,3:210000,4:230000,5:220000,6:260000,7:290000,8:275000,9:235000,10:250000,11:240000,12:280000}
    for m,t in ing_totals.items():
        n=random.randint(6,12)
        for i in range(n): ing_rows.append({"fecha":pd.Timestamp(f"2024-{m:02d}-{min(i*2+1,28):02d}"),"monto":round(t/n)})
    for m,t in egr_totals.items():
        n=random.randint(4,8)
        for i in range(n):
            egr_rows.append({"fecha":pd.Timestamp(f"2024-{m:02d}-{min(i*3+1,28):02d}"),
                             "monto":round(t/n),"concepto":random.choice(categorias)})
    return pd.DataFrame(ing_rows), pd.DataFrame(egr_rows)

def agg_monthly(df):
    if df.empty: return {}
    d = df.copy(); d["mes"] = d["fecha"].dt.month
    return d.groupby("mes")["monto"].sum().to_dict()

def fmt(n): return f"${n:,.0f}".replace(",",".")

def fig_to_img(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor=BG)
    buf.seek(0); plt.close(fig); return buf

# ── CHARTS ─────────────────────────────────────────────────────────────────────
def chart_main(months, ing, egr, net):
    lbls = [MONTHS_ES[m] for m in months]
    x = np.arange(len(lbls)); w = 0.35
    fig, ax = plt.subplots(figsize=(10,4))
    ax.bar(x-w/2, ing, w, color=CI, alpha=0.9, label="Ingresos")
    ax.bar(x+w/2, egr, w, color=CE, alpha=0.9, label="Egresos")
    ax2 = ax.twinx()
    ax2.plot(x, net, color=CN, linewidth=2.5, marker="o", markersize=6, label="Ganancia neta")
    ax2.set_ylabel("Ganancia neta", color=CN, fontsize=10)
    ax2.tick_params(colors=CN)
    for spine in ax2.spines.values(): spine.set_edgecolor("#1a1aff22")
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"${v/1000:.0f}k"))
    ax.set_xticks(x); ax.set_xticklabels(lbls, fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"${v/1000:.0f}k"))
    ax.grid(axis="y"); ax.set_axisbelow(True)
    for spine in ax.spines.values(): spine.set_edgecolor("#1a1aff22")
    h1 = [mpatches.Patch(color=CI,label="Ingresos"), mpatches.Patch(color=CE,label="Egresos")]
    h2 = [plt.Line2D([0],[0],color=CN,linewidth=2,marker="o",markersize=5,label="Ganancia neta")]
    ax.legend(handles=h1+h2, loc="upper left", framealpha=0.1, labelcolor=TC, fontsize=10)
    fig.tight_layout(); return fig_to_img(fig)

def chart_acum(months, net):
    lbls = [MONTHS_ES[m] for m in months]
    acum = list(np.cumsum(net))
    fig, ax = plt.subplots(figsize=(6,3.5))
    ax.fill_between(range(len(lbls)), acum, alpha=0.15, color=CA)
    ax.plot(range(len(lbls)), acum, color=CA, linewidth=2.5, marker="o", markersize=6)
    ax.set_xticks(range(len(lbls))); ax.set_xticklabels(lbls, fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"${v/1000:.0f}k"))
    ax.grid(axis="y"); ax.set_axisbelow(True)
    for spine in ax.spines.values(): spine.set_edgecolor("#1a1aff22")
    fig.tight_layout(); return fig_to_img(fig)

def chart_margen(months, ing, net):
    lbls = [MONTHS_ES[m] for m in months]
    mgn = [round(n/i*100,1) if i else 0 for n,i in zip(net,ing)]
    colors = [CN if m>=30 else "#ffaa00" if m>0 else CE for m in mgn]
    fig, ax = plt.subplots(figsize=(6,3.5))
    bars = ax.bar(range(len(lbls)), mgn, color=colors, alpha=0.9)
    for bar,val in zip(bars,mgn):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5, f"{val}%",
                ha="center", va="bottom", fontsize=9, color=TC)
    ax.axhline(0, color="#1a1aff33", linewidth=1)
    ax.set_xticks(range(len(lbls))); ax.set_xticklabels(lbls, fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"{v:.0f}%"))
    ax.grid(axis="y"); ax.set_axisbelow(True)
    for spine in ax.spines.values(): spine.set_edgecolor("#1a1aff22")
    fig.tight_layout(); return fig_to_img(fig)

def chart_categorias(egr_df):
    if egr_df.empty or "concepto" not in egr_df.columns: return None
    cat = egr_df.groupby("concepto")["monto"].sum().sort_values(ascending=False)
    if cat.empty: return None
    colors = CAT_COLORS[:len(cat)]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    # Barras horizontales
    bars = ax1.barh(cat.index[::-1], cat.values[::-1], color=colors[::-1], alpha=0.9)
    for bar, val in zip(bars, cat.values[::-1]):
        ax1.text(bar.get_width()+max(cat.values)*0.01, bar.get_y()+bar.get_height()/2,
                 fmt(val), va="center", fontsize=9, color=TC)
    ax1.set_xlabel("Monto ($)", color=TC, fontsize=10)
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"${v/1000:.0f}k"))
    ax1.grid(axis="x"); ax1.set_axisbelow(True)
    for spine in ax1.spines.values(): spine.set_edgecolor("#1a1aff22")
    # Donut
    wedges, texts, autotexts = ax2.pie(
        cat.values, labels=None, colors=colors,
        autopct=lambda p: f"{p:.1f}%" if p > 4 else "",
        pctdistance=0.75, startangle=90,
        wedgeprops=dict(width=0.55, edgecolor=BG, linewidth=2)
    )
    for at in autotexts: at.set_color("#ffffff"); at.set_fontsize(9)
    ax2.legend(cat.index, loc="center left", bbox_to_anchor=(1,0.5),
               framealpha=0.1, labelcolor=TC, fontsize=9)
    fig.tight_layout(); return fig_to_img(fig)

def build_excel(months, ing, egr, net, year):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    wb = Workbook(); ws = wb.active; ws.title = "Dashboard"
    thin = Side(style="thin", color="1a1aff")
    brd = Border(left=thin, right=thin, top=thin, bottom=thin)
    for i,h in enumerate(["Mes","Ingresos ($)","Egresos ($)","Ganancia Neta ($)","Margen (%)"],1):
        c = ws.cell(row=1,column=i,value=h)
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

# ── HEADER ─────────────────────────────────────────────────────────────────────
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

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.markdown("---")
    st.markdown("**📂 Tu planilla**")
    planilla_file = st.file_uploader("Subí tu planilla Excel o CSV", type=["xlsx","xls","csv"], key="planilla")
    st.markdown("---")
    st.markdown("**📅 Período**")
    year_sel = st.selectbox("Año", [2025,2026,2024], index=0)
    months_sel = st.multiselect("Meses", list(range(1,13)), default=list(range(1,13)), format_func=lambda m: MONTHS_ES[m])
    st.markdown("---")
    with st.expander("📌 Formato esperado"):
        st.markdown("""
Tu planilla debe tener esta estructura:

**Egresos** (columnas A, B, C):
- `Fecha` | `Concepto` | `Monto`

**Ingresos** (columnas H, I o a la derecha):
- `Fecha` | `Monto`

Ambas secciones en la **misma hoja**.
        """)
    st.caption("LL Rent a Car Joy · v2.0")

# ── DATOS ──────────────────────────────────────────────────────────────────────
using_demo = planilla_file is None
if using_demo:
    ing_df, egr_df = get_demo()
    st.info("📊 Mostrando **datos de ejemplo**. Cargá tu planilla en el panel lateral para ver tus números reales.")
else:
    ing_df, egr_df = parse_planilla(planilla_file)
    if ing_df.empty and egr_df.empty:
        st.warning("No se pudieron leer los datos. Revisá el formato de tu planilla."); st.stop()

# Filtrar por año
if not ing_df.empty: ing_df = ing_df[ing_df["fecha"].dt.year == year_sel]
if not egr_df.empty: egr_df = egr_df[egr_df["fecha"].dt.year == year_sel]

im = agg_monthly(ing_df); em = agg_monthly(egr_df)
all_months = sorted(set(list(im.keys()) + list(em.keys())))
if months_sel: all_months = [m for m in all_months if m in months_sel]
if not all_months: st.warning("No hay datos para el período seleccionado."); st.stop()

iv = [im.get(m,0) for m in all_months]
ev = [em.get(m,0) for m in all_months]
nv = [i-e for i,e in zip(iv,ev)]
ti = sum(iv); te = sum(ev); tn = ti-te
mg = round(tn/ti*100,1) if ti else 0
mejor = all_months[nv.index(max(nv))] if nv else 1
peor  = all_months[nv.index(min(nv))] if nv else 1

# ── KPIs ───────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">Resumen del período</p>', unsafe_allow_html=True)
k1,k2,k3,k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi-card"><p class="kpi-label">Ingresos totales</p><p class="kpi-value">{fmt(ti)}</p><p class="kpi-delta neu">{len(all_months)} meses analizados</p></div>', unsafe_allow_html=True)
with k2:
    pe = round(te/ti*100) if ti else 0
    st.markdown(f'<div class="kpi-card red"><p class="kpi-label">Egresos totales</p><p class="kpi-value">{fmt(te)}</p><p class="kpi-delta neu">{pe}% de los ingresos</p></div>', unsafe_allow_html=True)
with k3:
    cc="green" if tn>=0 else "red"; ic="▲ Rentable" if tn>=0 else "▼ En pérdida"; dc="pos" if tn>=0 else "neg"
    st.markdown(f'<div class="kpi-card {cc}"><p class="kpi-label">Ganancia neta</p><p class="kpi-value">{fmt(tn)}</p><p class="kpi-delta {dc}">{ic}</p></div>', unsafe_allow_html=True)
with k4:
    mc="green" if mg>=30 else "amber" if mg>0 else "red"
    st.markdown(f'<div class="kpi-card {mc}"><p class="kpi-label">Margen neto</p><p class="kpi-value">{mg}%</p><p class="kpi-delta neu">Mejor: {MONTHS_ES[mejor]} · Peor: {MONTHS_ES[peor]}</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CHART PRINCIPAL ────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">Ingresos vs Egresos</p>', unsafe_allow_html=True)
st.image(chart_main(all_months, iv, ev, nv), use_container_width=True)

# ── CHARTS SECUNDARIOS ─────────────────────────────────────────────────────────
st.markdown('<p class="section-title">Análisis detallado</p>', unsafe_allow_html=True)
c1,c2 = st.columns(2)
with c1:
    st.markdown("**Tendencia acumulada**")
    st.image(chart_acum(all_months, nv), use_container_width=True)
with c2:
    st.markdown("**Margen mensual (%)**")
    st.image(chart_margen(all_months, iv, nv), use_container_width=True)

# ── CATEGORÍAS EGRESOS ────────────────────────────────────────────────────────
if not egr_df.empty and "concepto" in egr_df.columns:
    st.markdown('<p class="section-title">Egresos por categoría</p>', unsafe_allow_html=True)
    cat_img = chart_categorias(egr_df)
    if cat_img:
        st.image(cat_img, use_container_width=True)

# ── TABLA ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-title">Detalle mensual</p>', unsafe_allow_html=True)
rows = []
for i,m in enumerate(all_months):
    i_=iv[i]; e_=ev[i]; n_=nv[i]; mg_=round(n_/i_*100,1) if i_ else 0
    est="✅ Excelente" if n_>0 and mg_>=30 else "🟡 Positivo" if n_>0 else "🔴 Negativo"
    rows.append({"Mes":MONTHS_ES[m],"Ingresos":fmt(i_),"Egresos":fmt(e_),"Ganancia neta":fmt(n_),"Margen":f"{mg_}%","Estado":est})
rows.append({"Mes":"TOTAL","Ingresos":fmt(ti),"Egresos":fmt(te),"Ganancia neta":fmt(tn),"Margen":f"{mg}%","Estado":"—"})
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── TABLA CATEGORÍAS ──────────────────────────────────────────────────────────
if not egr_df.empty and "concepto" in egr_df.columns:
    st.markdown('<p class="section-title">Detalle de egresos por categoría</p>', unsafe_allow_html=True)
    cat_rows = egr_df.groupby("concepto")["monto"].agg(["sum","count"]).reset_index()
    cat_rows.columns = ["Categoría","Total","Cantidad"]
    cat_rows = cat_rows.sort_values("Total", ascending=False)
    cat_rows["Total"] = cat_rows["Total"].apply(fmt)
    st.dataframe(cat_rows, use_container_width=True, hide_index=True)

# ── EXPORT ─────────────────────────────────────────────────────────────────────
st.markdown("---")
col_dl, col_info = st.columns([1,3])
with col_dl:
    st.download_button(
        label="⬇️ Descargar Excel",
        data=build_excel(all_months, iv, ev, nv, year_sel),
        file_name=f"ll_rent_a_car_joy_{year_sel}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
with col_info:
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.caption(f"Reporte generado el {now} · LL Rent a Car Joy")
