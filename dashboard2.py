import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="ECB | Churn Segmentation Analytics", page_icon="🏛️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background: #f0f4f8; }
.section-header {
    font-size: 1.25rem; font-weight: 700; color: #1B4F72;
    border-bottom: 2px solid #AED6F1; padding-bottom: 8px; margin-bottom: 18px; margin-top: 6px;
}
.insight-box { background:#EBF5FB; border:1px solid #AED6F1; border-radius:8px; padding:14px 18px; font-size:0.9rem; color:#1B4F72; margin-bottom:12px; }
.insight-box.danger { background:#FDEDEC; border-color:#F1948A; color:#78281F; }
.insight-box.warning { background:#FEF9E7; border-color:#F9E79F; color:#7D6608; }
.insight-box.success { background:#EAFAF1; border-color:#A9DFBF; color:#1E8449; }
div[data-testid="stMetric"] { background:white; border-radius:10px; padding:16px; box-shadow:0 1px 6px rgba(0,0,0,0.08); }
div[data-testid="stMetric"] label { color:#4A5568 !important; font-weight:600 !important; }
div[data-testid="stMetricValue"] { color:#1A202C !important; font-weight:700 !important; font-size:1.8rem !important; }
div[data-testid="stMetricValue"] > div { color:#1A202C !important; }
div[data-testid="stMetricDelta"] { color:#4A5568 !important; }
.stPlotlyChart { background:white; border-radius:12px; padding:8px; }
.js-plotly-plot .plotly .gtitle { fill:#1A202C !important; }
.js-plotly-plot .plotly .xtitle { fill:#1A202C !important; }
.js-plotly-plot .plotly .ytitle { fill:#1A202C !important; }
.js-plotly-plot .plotly .xtick text { fill:#1A202C !important; }
.js-plotly-plot .plotly .ytick text { fill:#1A202C !important; }
.js-plotly-plot .plotly .legendtext { fill:#1A202C !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    import os
    url = "https://raw.githubusercontent.com/harish220900/european-bank-retention-analytics/main/European_Bank.csv"
    paths = ['European_Bank.csv', os.path.join(os.getcwd(), 'European_Bank.csv')]
    df = None
    for p in paths:
        try:
            if os.path.exists(p):
                df = pd.read_csv(p)
                break
        except: continue
    if df is None:
        try: df = pd.read_csv(url)
        except: pass
    if df is None: raise FileNotFoundError("Dataset not found")

    df['AgeGroup'] = pd.cut(df.Age, bins=[0,30,45,60,100], labels=['<30','30–45','46–60','60+'])
    df['CreditBand'] = pd.cut(df.CreditScore, bins=[0,550,700,850], labels=['Low (≤550)','Medium (551–700)','High (>700)'])
    df['TenureGroup'] = pd.cut(df.Tenure, bins=[-1,2,6,10], labels=['New (0–2yr)','Mid (3–6yr)','Long (7–10yr)'])
    df['BalanceSeg'] = 'Zero Balance'
    df.loc[df.Balance.between(1,50000), 'BalanceSeg'] = 'Low (€1–50K)'
    df.loc[df.Balance.between(50001,125000), 'BalanceSeg'] = 'Medium (€50K–125K)'
    df.loc[df.Balance > 125000, 'BalanceSeg'] = 'High (>€125K)'
    df['SalaryQ'] = pd.qcut(df.EstimatedSalary, q=4, labels=['Q1 Low','Q2','Q3','Q4 High'])
    df['HighValue'] = (df.Balance > 100000).astype(int)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## 🏛️ European Central Bank")
    st.markdown("**Churn Segmentation Analytics**")
    st.markdown("---")
    st.markdown("### 🔍 Filters")
    geo = st.multiselect("Geography", df.Geography.unique().tolist(), default=df.Geography.unique().tolist())
    gender = st.multiselect("Gender", df.Gender.unique().tolist(), default=df.Gender.unique().tolist())
    age_groups = st.multiselect("Age Group", ['<30','30–45','46–60','60+'], default=['<30','30–45','46–60','60+'])
    credit_bands = st.multiselect("Credit Band", ['Low (≤550)','Medium (551–700)','High (>700)'], default=['Low (≤550)','Medium (551–700)','High (>700)'])
    active_filter = st.selectbox("Member Status", ["All","Active Only","Inactive Only"])
    st.markdown("---")
    st.markdown("**N = 10,000 customers**")
    st.markdown("**Year: 2025**")
    st.markdown("**Source: European Central Bank**")

# ── FILTER ──
dff = df[
    df.Geography.isin(geo) &
    df.Gender.isin(gender) &
    df.AgeGroup.isin(age_groups).fillna(False) &
    df.CreditBand.isin(credit_bands).fillna(False)
].copy()
if active_filter == "Active Only": dff = dff[dff.IsActiveMember==1]
elif active_filter == "Inactive Only": dff = dff[dff.IsActiveMember==0]

def chart_layout(fig, title, h=360):
    fig.update_layout(
        title=title,
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', color='#1A202C'),
        title_font=dict(size=14, color='#1A202C'),
        legend=dict(font=dict(color='#1A202C')),
        height=h
    )
    fig.update_xaxes(gridcolor='#EDF2F7', tickfont=dict(color='#1A202C'), title_font=dict(color='#1A202C'))
    fig.update_yaxes(gridcolor='#EDF2F7', tickfont=dict(color='#1A202C'), title_font=dict(color='#1A202C'))
    return fig

# ── HEADER ──
st.markdown(f"""
<div style='background:linear-gradient(135deg,#1B4F72 0%,#2471A3 100%);border-radius:16px;padding:28px 36px;margin-bottom:24px;color:white;'>
    <h1 style='margin:0;font-size:1.9rem;font-weight:700;'>🏛️ Customer Segmentation & Churn Pattern Analytics</h1>
    <p style='margin:8px 0 0 0;opacity:0.85;font-size:1rem;'>European Central Bank · Retail Banking Analytics · 2025 · N = {len(dff):,} customers (filtered)</p>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──
k1,k2,k3,k4,k5 = st.columns(5)
overall = dff.Exited.mean()*100 if len(dff) > 0 else 0
churned = dff.Exited.sum()
hv_churn = dff[dff.Balance>100000].Exited.mean()*100 if len(dff[dff.Balance>100000])>0 else 0
bal_risk = dff[dff.Exited==1].Balance.sum()
ger_churn = dff[dff.Geography=='Germany'].Exited.mean()*100 if len(dff[dff.Geography=='Germany'])>0 else 0

k1.metric("Overall Churn Rate", f"{overall:.1f}%", delta=f"{overall-20.4:.1f}pp vs baseline")
k2.metric("Total Churned", f"{int(churned):,}", delta="customers exited")
k3.metric("High-Value Churn", f"{hv_churn:.1f}%", delta="Balance >€100K")
k4.metric("Balance at Risk", f"€{bal_risk/1e6:.1f}M", delta="from churned customers")
k5.metric("Germany Churn", f"{ger_churn:.1f}%", delta="vs 16.2% France")

st.markdown("---")

# ── TABS ──
tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    "🌍 Geographic Segmentation",
    "👥 Age & Tenure Analysis",
    "💳 Credit & Balance Profiles",
    "💰 High-Value Customer Analysis",
    "📊 Demographic Comparison",
    "🎯 Segment Risk Matrix"
])

# ════════════════════════════════════════════
# TAB 1 — GEOGRAPHIC
# ════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Geographic Churn Segmentation</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        geo_d = dff.groupby('Geography')['Exited'].agg(['mean','count','sum']).reset_index()
        geo_d['ChurnRate'] = geo_d['mean']*100
        fig = go.Figure(go.Bar(
            x=geo_d['Geography'], y=geo_d['ChurnRate'],
            marker_color=['#1E8449' if v<20 else '#E74C3C' for v in geo_d['ChurnRate']],
            text=[f"{v:.1f}%<br>(n={c:,})" for v,c in zip(geo_d['ChurnRate'],geo_d['count'])],
            textposition='outside'
        ))
        fig.add_hline(y=20.4, line_dash="dash", line_color="#7F8C8D", annotation_text="Portfolio Avg 20.4%")
        chart_layout(fig, "Churn Rate by Geography")
        fig.update_yaxes(range=[0,45])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        geo_d['Contribution'] = geo_d['sum']/geo_d['sum'].sum()*100
        fig2 = go.Figure(go.Bar(
            x=geo_d['Geography'], y=geo_d['Contribution'],
            marker_color=['#2471A3','#E74C3C','#1E8449'],
            text=[f"{v:.1f}%" for v in geo_d['Contribution']],
            textposition='outside'
        ))
        chart_layout(fig2, "Churn Contribution by Geography (% of Total Churned)")
        fig2.update_yaxes(range=[0,55])
        st.plotly_chart(fig2, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        geo_age = dff.groupby(['Geography','AgeGroup'], observed=True)['Exited'].mean().reset_index()
        geo_age['ChurnRate'] = geo_age['Exited']*100
        try:
            pivot = geo_age.pivot(index='Geography', columns='AgeGroup', values='ChurnRate').fillna(0)
            fig3 = px.imshow(pivot, text_auto='.1f', color_continuous_scale='RdYlGn_r',
                            title="Churn Heatmap: Geography × Age Group", aspect='auto')
            fig3.update_layout(font=dict(family='Inter', color='#1A202C'),
                               title_font=dict(size=14, color='#1A202C'), height=320)
            st.plotly_chart(fig3, use_container_width=True)
        except: st.info("Not enough data for heatmap with current filters.")

    with c4:
        geo_active = dff.groupby(['Geography','IsActiveMember'])['Exited'].mean().reset_index()
        geo_active['ChurnRate'] = geo_active['Exited']*100
        geo_active['Status'] = geo_active['IsActiveMember'].map({0:'Inactive',1:'Active'})
        fig4 = px.bar(geo_active, x='Geography', y='ChurnRate', color='Status', barmode='group',
                      color_discrete_map={'Active':'#1E8449','Inactive':'#E74C3C'},
                      title="Churn by Geography × Activity Status",
                      labels={'ChurnRate':'Churn Rate (%)'})
        chart_layout(fig4, "Churn by Geography × Activity Status", h=320)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="insight-box danger">🔴 <strong>Critical:</strong> Germany churns at 32.4% — double France and Spain — and contributes 40% of all exits. Germany × Age 46–60 reaches 67.3% churn. Immediate regional intervention required.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 2 — AGE & TENURE
# ════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Age & Tenure Churn Segmentation</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        age_d = dff.groupby('AgeGroup', observed=True)['Exited'].agg(['mean','count','sum']).reset_index()
        age_d['ChurnRate'] = age_d['mean']*100
        bar_colors = ['#1E8449' if v<20 else ('#F39C12' if v<35 else '#E74C3C') for v in age_d['ChurnRate']]
        fig = go.Figure(go.Bar(
            x=age_d['AgeGroup'].astype(str), y=age_d['ChurnRate'],
            marker_color=bar_colors,
            text=[f"{v:.1f}%<br>(n={c:,})" for v,c in zip(age_d['ChurnRate'],age_d['count'])],
            textposition='outside'
        ))
        fig.add_hline(y=20.4, line_dash="dash", line_color="#7F8C8D", annotation_text="Avg 20.4%")
        chart_layout(fig, "Churn Rate by Age Group")
        fig.update_yaxes(range=[0,70])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        age_d['Contribution'] = age_d['sum']/age_d['sum'].sum()*100
        fig2 = px.pie(age_d, values='Contribution', names='AgeGroup',
                      title="Churn Contribution by Age Group",
                      color_discrete_sequence=['#1E8449','#2471A3','#E74C3C','#884EA0'],
                      hole=0.4)
        fig2.update_layout(font=dict(family='Inter', color='#1A202C'),
                           title_font=dict(size=14, color='#1A202C'), height=360,
                           legend=dict(font=dict(color='#1A202C')))
        st.plotly_chart(fig2, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        ten_d = dff.groupby('TenureGroup', observed=True)['Exited'].agg(['mean','count']).reset_index()
        ten_d['ChurnRate'] = ten_d['mean']*100
        fig3 = go.Figure(go.Bar(
            x=ten_d['TenureGroup'].astype(str), y=ten_d['ChurnRate'],
            marker_color=['#E74C3C','#F39C12','#1E8449'],
            text=[f"{v:.1f}%<br>(n={c:,})" for v,c in zip(ten_d['ChurnRate'],ten_d['count'])],
            textposition='outside'
        ))
        fig3.add_hline(y=20.4, line_dash="dash", line_color="#7F8C8D")
        chart_layout(fig3, "Churn Rate by Tenure Group")
        fig3.update_yaxes(range=[0,32])
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        age_ten = dff.groupby(['AgeGroup','TenureGroup'], observed=True)['Exited'].mean().reset_index()
        age_ten['ChurnRate'] = age_ten['Exited']*100
        fig4 = px.bar(age_ten, x='AgeGroup', y='ChurnRate', color='TenureGroup', barmode='group',
                      title="Churn Rate: Age Group × Tenure",
                      labels={'ChurnRate':'Churn Rate (%)','AgeGroup':'Age Group'},
                      color_discrete_sequence=['#E74C3C','#F39C12','#1E8449'])
        chart_layout(fig4, "Churn Rate: Age Group × Tenure", h=340)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="insight-box danger">🔴 <strong>Critical:</strong> Age 46–60 churns at 51.1% — contributing 41.3% of total exits. This cohort is at a financial lifecycle inflection point and requires dedicated pre-retirement retention programs.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 3 — CREDIT & BALANCE
# ════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Credit Score & Balance Segmentation</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        cr_d = dff.groupby('CreditBand', observed=True)['Exited'].agg(['mean','count']).reset_index()
        cr_d['ChurnRate'] = cr_d['mean']*100
        fig = go.Figure(go.Bar(
            x=cr_d['CreditBand'].astype(str), y=cr_d['ChurnRate'],
            marker_color=['#E74C3C','#F39C12','#1E8449'],
            text=[f"{v:.1f}%<br>(n={c:,})" for v,c in zip(cr_d['ChurnRate'],cr_d['count'])],
            textposition='outside'
        ))
        fig.add_hline(y=20.4, line_dash="dash", line_color="#7F8C8D", annotation_text="Avg 20.4%")
        chart_layout(fig, "Churn Rate by Credit Score Band")
        fig.update_yaxes(range=[0,30])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        bal_order = ['Zero Balance','Low (€1–50K)','Medium (€50K–125K)','High (>€125K)']
        bal_d = dff.groupby('BalanceSeg')['Exited'].agg(['mean','count']).reset_index()
        bal_d['ChurnRate'] = bal_d['mean']*100
        bal_d['BalanceSeg'] = pd.Categorical(bal_d['BalanceSeg'], categories=bal_order, ordered=True)
        bal_d = bal_d.sort_values('BalanceSeg')
        fig2 = go.Figure(go.Bar(
            x=bal_d['BalanceSeg'].astype(str), y=bal_d['ChurnRate'],
            marker_color=['#7F8C8D','#E74C3C','#F39C12','#884EA0'],
            text=[f"{v:.1f}%<br>(n={c:,})" for v,c in zip(bal_d['ChurnRate'],bal_d['count'])],
            textposition='outside'
        ))
        fig2.add_hline(y=20.4, line_dash="dash", line_color="#7F8C8D")
        chart_layout(fig2, "Churn Rate by Balance Segment")
        fig2.update_yaxes(range=[0,48])
        st.plotly_chart(fig2, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        try:
            cr_bal = dff.groupby(['CreditBand','BalanceSeg'], observed=True)['Exited'].mean().reset_index()
            cr_bal['ChurnRate'] = (cr_bal['Exited']*100).round(1)
            pivot_cb = cr_bal.pivot(index='CreditBand', columns='BalanceSeg', values='ChurnRate').fillna(0)
            fig3 = px.imshow(pivot_cb, text_auto='.1f', color_continuous_scale='RdYlGn_r',
                            title="Churn Heatmap: Credit Band × Balance Segment", aspect='auto')
            fig3.update_layout(font=dict(family='Inter', color='#1A202C'),
                               title_font=dict(size=14, color='#1A202C'), height=340)
            st.plotly_chart(fig3, use_container_width=True)
        except: st.info("Not enough data with current filters.")

    with c4:
        prod_d = dff.groupby('NumOfProducts')['Exited'].agg(['mean','count']).reset_index()
        prod_d['ChurnRate'] = prod_d['mean']*100
        fig4 = go.Figure(go.Bar(
            x=[f"{p} Product{'s' if p>1 else ''}" for p in prod_d['NumOfProducts']],
            y=prod_d['ChurnRate'],
            marker_color=['#F39C12','#1E8449','#E74C3C','#78281F'],
            text=[f"{v:.1f}%<br>(n={c:,})" for v,c in zip(prod_d['ChurnRate'],prod_d['count'])],
            textposition='outside'
        ))
        chart_layout(fig4, "Churn Rate by Number of Products", h=340)
        fig4.update_yaxes(range=[0,120])
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="insight-box warning">⚠️ <strong>Key Insight:</strong> Low credit score customers churn at 22.7% — elevated financial stress. Low balance segment (€1–50K) shows 34.7% churn — possibly customers testing the bank before deciding to stay.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 4 — HIGH VALUE CUSTOMER ANALYSIS
# ════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">High-Value Customer Churn Explorer</div>', unsafe_allow_html=True)

    bal_threshold = st.slider("Define 'High-Value' — Minimum Balance (€)", 0, 200000, 100000, step=10000, format="€%d")

    hv = dff[dff.Balance >= bal_threshold]
    lv = dff[dff.Balance < bal_threshold]

    h1c, h2c, h3c, h4c = st.columns(4)
    h1c.metric("High-Value Customers", f"{len(hv):,}", delta=f"{len(hv)/max(len(dff),1)*100:.1f}% of base")
    h2c.metric("High-Value Churn Rate", f"{hv.Exited.mean()*100:.1f}%" if len(hv)>0 else "N/A", delta=f"vs {lv.Exited.mean()*100:.1f}% lower-value")
    h3c.metric("Balance at Risk", f"€{hv[hv.Exited==1].Balance.sum()/1e6:.1f}M", delta="from HV churned")
    h4c.metric("Avg Churned Balance", f"€{hv[hv.Exited==1].Balance.mean():,.0f}" if hv[hv.Exited==1].shape[0]>0 else "N/A")

    c1,c2 = st.columns(2)
    with c1:
        if len(hv) > 0:
            hv_geo = hv.groupby('Geography')['Exited'].agg(['mean','count']).reset_index()
            hv_geo['ChurnRate'] = hv_geo['mean']*100
            fig = go.Figure(go.Bar(
                x=hv_geo['Geography'], y=hv_geo['ChurnRate'],
                marker_color=['#1E8449' if v<20 else '#E74C3C' for v in hv_geo['ChurnRate']],
                text=[f"{v:.1f}%<br>(n={c:,})" for v,c in zip(hv_geo['ChurnRate'],hv_geo['count'])],
                textposition='outside'
            ))
            chart_layout(fig, f"High-Value Customer Churn by Geography (Balance ≥ €{bal_threshold:,})")
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if len(hv) > 0:
            hv_age = hv.groupby('AgeGroup', observed=True)['Exited'].agg(['mean','count']).reset_index()
            hv_age['ChurnRate'] = hv_age['mean']*100
            fig2 = go.Figure(go.Bar(
                x=hv_age['AgeGroup'].astype(str), y=hv_age['ChurnRate'],
                marker_color=['#1E8449' if v<20 else ('#F39C12' if v<35 else '#E74C3C') for v in hv_age['ChurnRate']],
                text=[f"{v:.1f}%<br>(n={c:,})" for v,c in zip(hv_age['ChurnRate'],hv_age['count'])],
                textposition='outside'
            ))
            chart_layout(fig2, "High-Value Customer Churn by Age Group")
            st.plotly_chart(fig2, use_container_width=True)

    # Scatter plot
    st.markdown("#### Balance vs Salary — Churned vs Retained")
    sample = dff.sample(min(2000, len(dff)), random_state=42)
    fig3 = px.scatter(sample, x='EstimatedSalary', y='Balance',
                      color='Exited', color_discrete_map={0:'#2471A3',1:'#E74C3C'},
                      opacity=0.5, labels={'EstimatedSalary':'Estimated Salary (€)','Balance':'Balance (€)','Exited':'Churned'},
                      hover_data=['Geography','Age','NumOfProducts'])
    chart_layout(fig3, "Salary vs Balance — Churned (Red) vs Retained (Blue)", h=420)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="insight-box danger">🔴 <strong>Revenue Alert:</strong> High-value customers churn at 25.2% — above portfolio average. Total balance at risk from churned customers exceeds €185.6M. These customers have the financial means to consolidate at wealth management competitors.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 5 — DEMOGRAPHIC COMPARISON
# ════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">Comparative Demographic Analysis</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        gen_d = dff.groupby('Gender')['Exited'].agg(['mean','count']).reset_index()
        gen_d['ChurnRate'] = gen_d['mean']*100
        fig = go.Figure(go.Bar(
            x=gen_d['Gender'], y=gen_d['ChurnRate'],
            marker_color=['#E91E8C','#2471A3'],
            text=[f"{v:.1f}%<br>(n={c:,})" for v,c in zip(gen_d['ChurnRate'],gen_d['count'])],
            textposition='outside', width=0.4
        ))
        chart_layout(fig, "Churn Rate by Gender")
        fig.update_yaxes(range=[0,35])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        act_d = dff.groupby('IsActiveMember')['Exited'].agg(['mean','count']).reset_index()
        act_d['Label'] = act_d['IsActiveMember'].map({0:'Inactive',1:'Active'})
        act_d['ChurnRate'] = act_d['mean']*100
        fig2 = go.Figure(go.Bar(
            x=act_d['Label'], y=act_d['ChurnRate'],
            marker_color=['#E74C3C','#1E8449'],
            text=[f"{v:.1f}%<br>(n={c:,})" for v,c in zip(act_d['ChurnRate'],act_d['count'])],
            textposition='outside', width=0.4
        ))
        chart_layout(fig2, "Churn Rate: Active vs Inactive Members")
        fig2.update_yaxes(range=[0,38])
        st.plotly_chart(fig2, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        gen_geo = dff.groupby(['Geography','Gender'])['Exited'].mean().reset_index()
        gen_geo['ChurnRate'] = gen_geo['Exited']*100
        fig3 = px.bar(gen_geo, x='Geography', y='ChurnRate', color='Gender', barmode='group',
                      color_discrete_map={'Female':'#E91E8C','Male':'#2471A3'},
                      title="Churn by Geography × Gender",
                      labels={'ChurnRate':'Churn Rate (%)'})
        chart_layout(fig3, "Churn by Geography × Gender", h=340)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        sal_d = dff.groupby('SalaryQ', observed=True)['Exited'].agg(['mean','count']).reset_index()
        sal_d['ChurnRate'] = sal_d['mean']*100
        fig4 = go.Figure(go.Bar(
            x=sal_d['SalaryQ'].astype(str), y=sal_d['ChurnRate'],
            marker_color=['#2471A3','#2471A3','#2471A3','#2471A3'],
            text=[f"{v:.1f}%" for v in sal_d['ChurnRate']],
            textposition='outside'
        ))
        fig4.add_hline(y=20.4, line_dash="dash", line_color="#7F8C8D")
        chart_layout(fig4, "Churn Rate by Salary Quartile", h=340)
        fig4.update_yaxes(range=[0,28])
        st.plotly_chart(fig4, use_container_width=True)

    # Churned vs Retained Profile
    st.markdown('<div class="section-header">Churned vs Retained Customer Profile Comparison</div>', unsafe_allow_html=True)
    if len(dff) > 0:
        profile = dff.groupby('Exited')[['CreditScore','Age','Tenure','Balance','NumOfProducts','EstimatedSalary']].mean().reset_index()
        profile['Status'] = profile['Exited'].map({0:'Retained',1:'Churned'})
        metrics = ['CreditScore','Age','Tenure','Balance','NumOfProducts','EstimatedSalary']
        cols = st.columns(len(metrics))
        for i, m in enumerate(metrics):
            if len(profile) >= 2:
                churned_val = profile[profile.Exited==1][m].values
                retained_val = profile[profile.Exited==0][m].values
                if len(churned_val)>0 and len(retained_val)>0:
                    diff = churned_val[0] - retained_val[0]
                    prefix = "€" if m in ['Balance','EstimatedSalary'] else ""
                    fmt = f"{prefix}{churned_val[0]:,.0f}" if m in ['Balance','EstimatedSalary'] else f"{churned_val[0]:.1f}"
                    cols[i].metric(f"Churned Avg {m}", fmt, delta=f"{diff:+.1f} vs retained")

    st.markdown('<div class="insight-box warning">⚠️ <strong>Profile Insight:</strong> Churned customers are on average 7.4 years older, carry 25% higher balances, and earn slightly more — they are financially independent customers with more options and higher switching capability.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 6 — SEGMENT RISK MATRIX
# ════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-header">Segment Risk Matrix — All Dimensions</div>', unsafe_allow_html=True)

    all_segments = []
    # Geography
    for grp, label in [(dff[dff.Geography=='France'],'France'), (dff[dff.Geography=='Germany'],'Germany'), (dff[dff.Geography=='Spain'],'Spain')]:
        if len(grp)>0: all_segments.append({'Dimension':'Geography','Segment':label,'Customers':len(grp),'ChurnRate':grp.Exited.mean()*100,'Churned':grp.Exited.sum()})
    # Age
    for ag in ['<30','30–45','46–60','60+']:
        grp = dff[dff.AgeGroup==ag]
        if len(grp)>0: all_segments.append({'Dimension':'Age','Segment':ag,'Customers':len(grp),'ChurnRate':grp.Exited.mean()*100,'Churned':grp.Exited.sum()})
    # Credit
    for cb in ['Low (≤550)','Medium (551–700)','High (>700)']:
        grp = dff[dff.CreditBand==cb]
        if len(grp)>0: all_segments.append({'Dimension':'Credit Score','Segment':cb,'Customers':len(grp),'ChurnRate':grp.Exited.mean()*100,'Churned':grp.Exited.sum()})
    # Tenure
    for tg in ['New (0–2yr)','Mid (3–6yr)','Long (7–10yr)']:
        grp = dff[dff.TenureGroup==tg]
        if len(grp)>0: all_segments.append({'Dimension':'Tenure','Segment':tg,'Customers':len(grp),'ChurnRate':grp.Exited.mean()*100,'Churned':grp.Exited.sum()})
    # Balance
    for bs in ['Zero Balance','Low (€1–50K)','Medium (€50K–125K)','High (>€125K)']:
        grp = dff[dff.BalanceSeg==bs]
        if len(grp)>0: all_segments.append({'Dimension':'Balance','Segment':bs,'Customers':len(grp),'ChurnRate':grp.Exited.mean()*100,'Churned':grp.Exited.sum()})
    # Gender
    for g in ['Female','Male']:
        grp = dff[dff.Gender==g]
        if len(grp)>0: all_segments.append({'Dimension':'Gender','Segment':g,'Customers':len(grp),'ChurnRate':grp.Exited.mean()*100,'Churned':grp.Exited.sum()})

    risk_df = pd.DataFrame(all_segments)
    risk_df['RiskLevel'] = risk_df['ChurnRate'].apply(lambda x: '🔴 Critical' if x>=35 else ('🟠 High' if x>=25 else ('🟡 Medium' if x>=18 else '🟢 Low')))
    risk_df['ChurnRate'] = risk_df['ChurnRate'].round(1)
    risk_df['Contribution%'] = (risk_df['Churned']/risk_df['Churned'].sum()*100).round(1)
    risk_df = risk_df.sort_values('ChurnRate', ascending=False)

    c1,c2 = st.columns(2)
    with c1:
        fig = px.bar(risk_df.head(12), x='ChurnRate', y='Segment', orientation='h',
                     color='ChurnRate', color_continuous_scale='RdYlGn_r',
                     title="Top 12 Highest-Risk Segments",
                     labels={'ChurnRate':'Churn Rate (%)','Segment':''},
                     text=[f"{v:.1f}%" for v in risk_df.head(12)['ChurnRate']])
        fig.update_traces(textposition='outside')
        chart_layout(fig, "Top 12 Highest-Risk Segments", h=480)
        fig.update_xaxes(range=[0, risk_df['ChurnRate'].max()*1.25])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.scatter(risk_df, x='Customers', y='ChurnRate', color='Dimension',
                          size='Churned', hover_name='Segment',
                          title="Segment Size vs Churn Rate (bubble = churned count)",
                          labels={'Customers':'Segment Size','ChurnRate':'Churn Rate (%)'},
                          color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.add_hline(y=20.4, line_dash="dash", line_color="#7F8C8D", annotation_text="Portfolio Avg")
        chart_layout(fig2, "Segment Size vs Churn Rate", h=480)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### 📋 Complete Segment Risk Table")
    display_df = risk_df[['Dimension','Segment','Customers','ChurnRate','Churned','Contribution%','RiskLevel']].copy()
    display_df.columns = ['Dimension','Segment','Customers','Churn Rate (%)','Churned','Contribution (%)','Risk Level']
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="insight-box success">✅ <strong>Action Priority:</strong> Focus immediately on Germany (32.4%), Age 46–60 (51.1%), Low Balance segment (34.7%), and Inactive Members (26.9%). These 4 segments collectively drive the majority of churn exits.</div>', unsafe_allow_html=True)
