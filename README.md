<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=C5AA6D&height=180&section=header&text=EVELORA%20CO&fontSize=42&fontColor=F7E7CE&fontAlignY=38&desc=Where%20Elegance%20Meets%20Intelligence&descAlignY=58&descSize=16&descColor=E7C1B3" width="100%"/>

</div>

<div align="center">

```
✦  AI Adoption Index  ✦  Data Intelligence  ✦  2025
```

</div>

---

# The AI Adoption Index

**A full data investigation into which industries are genuinely using artificial intelligence — and which ones are simply saying they are.**

Built by [Parisha Sharma](https://linkedin.com/in/parisha-sharma15) · Evelora Co · May 2025

[![LinkedIn](https://img.shields.io/badge/Evelora%20Co-LinkedIn-C5AA6D?style=flat-square&logo=linkedin&logoColor=F7E7CE)](https://linkedin.com/company/evelora-co)
[![GitHub](https://img.shields.io/badge/github.com%2Feveloraco-111111?style=flat-square&logo=github&logoColor=C5AA6D)](https://github.com/eveloraco)
[![Streamlit](https://img.shields.io/badge/Live%20Dashboard-Streamlit-C5AA6D?style=flat-square&logo=streamlit&logoColor=F7E7CE)](https://eveloraco-ai-adoption.streamlit.app)

---

## What This Is

Every week, a new headline promises that AI is changing everything. Agriculture. Climate. Healthcare. Education. But what does the data actually say?

This project pulls real numbers from **McKinsey**, **IBM**, **Stanford HAI**, and **PwC** — spanning 2017 to 2025 — and builds a complete picture of where AI adoption actually stands, how fast it is moving, and where it is going next.

The findings are not what the headlines suggest.

---

## What We Found

| Finding | The Reality |
|---|---|
| Most-talked-about AI sectors | Agriculture (42%) and Environment (44%) rank dead last |
| Fastest-growing industry 2023-2025 | Legal Services — grew 30 percentage points |
| Who decides AI budgets | Strategy & Finance executives — 18% use AI themselves |
| US AI investment 2024 | $109 billion — but Singapore (2% of that) outperforms on adoption |
| Public AI optimism | China 83%, USA 39% — yet USA leads enterprise adoption |
| When Agriculture hits 80% | 2034. Nine years from now. |

---

## The Eight Chapters

```
01  Who Is Actually Using AI?        15 industries, one honest ranking
02  Who Moved the Fastest?           Growth speed 2023 to 2025
03  Where Inside Companies?          Which departments lead and which lag
04  The AI Readiness Score           A composite score built from 3 metrics
05  Predicting the Future            When each industry hits 80% adoption
06  Money vs. Reality                Investment vs. actual adoption by country
07  Does Trust Drive Adoption?       Public sentiment vs. enterprise usage
08  The 8-Year Journey               From 20% in 2017 to 88% in 2025
```

---

## Data Sources

| Source | What It Covers |
|---|---|
| McKinsey Global AI Survey (Annual) | Org-level adoption 2017 to 2025 |
| IBM Global AI Adoption Index 2024 | Business function breakdown |
| Stanford HAI AI Index 2025 | Investment, cost trends, country data |
| PwC AI Predictions | Industry-level adoption rates |
| Oxford Insights | Public sentiment by country |
| Ipsos Global AI Survey 2024 | Trust and optimism data |
| OpenAI / Reuters / TED 2025 | ChatGPT user growth milestones |

---

## Project Structure

```
evelora-ai-adoption-index/
│
├── app.py                          # Streamlit multi-page dashboard
├── notebooks/
│   └── 01_eda_ai_adoption.ipynb   # Full EDA — all 10 charts
├── assets/
│   └── evelora_theme.py           # Brand colors, palette, background
├── data/
│   └── raw/
│       ├── 1_McKinsey_Org_Adoption.csv
│       ├── 2_AI_By_Business_Function.csv
│       ├── 3_AI_Tool_Users_Global.csv
│       ├── 4_Investment_By_Country.csv
│       ├── 5_Adoption_By_Industry.csv
│       ├── 6_Public_Sentiment_By_Country.csv
│       ├── 7_Key_KPIs_Summary.csv
│       └── AI_Global_Trends_Dataset.xlsx
└── README.md
```

---

## Charts Built

| Chart | Type | What It Shows |
|---|---|---|
| Chart 1 | Horizontal bar | AI adoption by industry — 2025 |
| Chart 2 | Slope / overlay bar | Growth speed 2023 to 2025 |
| Chart 3 | Horizontal bar | AI by business function |
| Chart 4 | Bubble chart | AI Readiness Score — all industries |
| Chart 5 | Heatmap | Adoption all industries all years |
| Chart 6 | Scatter plot | Investment vs. adoption by country |
| Chart 7 | Lollipop | Public sentiment vs. enterprise adoption |
| Chart 8 | Area chart | McKinsey 8-year trend |
| Chart 9 | Step-line | ChatGPT user growth milestones |
| Chart 10 | KPI grid | 9 headline stats |

---

## The AI Readiness Score

A proprietary scoring model built for this project that combines three metrics into a single number out of 100.

```
Score = (Adoption 2025 × 0.50)
      + (Growth 2023–2025 × 0.30)
      + (Consistency × 0.20)
```

| Tier | Score | Industries |
|---|---|---|
| High — genuinely ready | 60+ | Professional Services, Technology, Financial Services |
| Developing | 40–60 | Healthcare, Media, Education, Manufacturing, Retail, Telecom, Transport |
| Lagging | Below 40 | Legal, Government, Environment, Agriculture, Real Estate |

---

## The Prediction Model

Using linear regression on 2022 to 2025 trend data, the model projects the year each industry crosses 80% adoption — the threshold for genuine, embedded transformation.

```
Technology            Already above 80%
Professional Services Already above 80%
Financial Services    Already above 80%
Healthcare            2028
Media & Entertainment 2028
Retail & Consumer     2029
Education             2030
Legal Services        2031
Government & Public   2032
Agriculture           2034
```

---

## How to Run

```bash
# Clone the repo
git clone https://github.com/eveloraco/evelora-ai-adoption-index.git
cd evelora-ai-adoption-index

# Install dependencies
pip install streamlit pandas plotly numpy

# Run the notebook first to generate chart outputs
# Open notebooks/01_eda_ai_adoption.ipynb and run all cells

# Launch the dashboard
streamlit run app.py
```

The app reads charts directly from the notebook's saved outputs. Update any chart in the notebook, save, press R in the browser — it updates automatically.

---

## The Methodology

All data is sourced from publicly available institutional research. No synthetic or AI-generated data is used anywhere in this project. Every chart includes its source citation.

The AI Readiness Score and prediction model are original constructs built specifically for this report using the methodology documented above.

---

## Brand

This project is built under **Evelora Co** — a luxury AI brand building AI-powered tools, automation systems, and data solutions for professionals and founders who demand precision over noise.

> *If it does not feel refined, it does not ship.*

**Founder:** Parisha Sharma  
**Email:** evelora.projects@gmail.com  
**LinkedIn:** [linkedin.com/company/evelora-co](https://linkedin.com/company/evelora-co)  
**GitHub:** [github.com/eveloraco](https://github.com/eveloraco)

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=C5AA6D&height=100&section=footer&fontColor=F7E7CE" width="100%"/>

*Evelora Co · Where Elegance Meets Intelligence · 2025*

</div>
