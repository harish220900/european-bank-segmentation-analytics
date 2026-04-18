# 🏛️ Customer Segmentation & Churn Pattern Analytics
## European Central Bank | Retail Banking Analytics | 2025

## Project Overview
Comprehensive segmentation-driven churn analysis of 10,000 European Bank 
customers across France, Germany, and Spain — identifying highest-risk 
customer groups and quantifying financial exposure.

## Key Findings
- Overall churn rate: **20.4%**
- Germany churns at **32.4%** — double France and Spain
- Age 46–60 churns at **51.1%** — majority leaving
- Germany × Age 46–60 = **67.3%** — most extreme segment
- **€185.6 Million** in deposits at risk from churned customers

## Segmentation Dimensions
- Geographic: France, Germany, Spain
- Age: <30, 30–45, 46–60, 60+
- Credit Score: Low, Medium, High
- Tenure: New, Mid-term, Long-term
- Balance: Zero, Low, Medium, High

## Files
| File | Description |
|------|-------------|
| `dashboard2.py` | Streamlit analytics dashboard — 6 tabs |
| `European_Bank.csv` | Dataset — 10,000 customer records |
| `requirements.txt` | Python dependencies |

## How to Run
pip install streamlit plotly pandas numpy
streamlit run dashboard2.py

## Dashboard Tabs
1. Geographic Segmentation
2. Age & Tenure Analysis
3. Credit & Balance Profiles
4. High-Value Customer Explorer
5. Demographic Comparison
6. Segment Risk Matrix

## Tech Stack
Python · Pandas · Plotly · Streamlit
