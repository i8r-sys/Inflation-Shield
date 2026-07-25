import json
import plotly.graph_objects as go
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Inflation Shield", layout="wide"
)

# Translations dictionary
I18N = {
    "en": {
        "title": "Inflation Shield",
        "subtitle": "Personal Inflation Calculator",
        "desc": "Calculate your personal inflation rate based on your actual daily expenses.",
        "settings": "Settings",
        "select_country": "Select Country:",
        "select_lang": "Select Language:",
        "expenses_header": "Your Monthly Expenses",
        "curr_expenses": "Current Monthly Expenses",
        "official_cpi": "Official Inflation (CPI)",
        "personal_cpi": "Personal Inflation",
        "vs_official": "vs Official",
        "chart_title": "Expense Growth Forecast",
        "your_rate": "With Personal Inflation",
        "off_rate": "With Official Inflation",
        "time_horizon": "Time Horizon",
        "monthly_expenses": "Monthly Expenses",
        "table_title": "Expense Breakdown",
        "col_category": "Category",
        "col_amount": "Amount",
        "col_share": "Share",
        "col_rate": "Category Inflation",
        "now": "Now",
        "year": "year",
        "years": "years",
        "inflation": "Inflation",
    },
    "de": {
        "title": "Inflation Shield",
        "subtitle": "Persönlicher Inflationsrechner",
        "desc": "Berechnen Sie Ihre persönliche Inflationsrate basierend auf Ihren tatsächlichen Ausgaben.",
        "settings": "Einstellungen",
        "select_country": "Land auswählen:",
        "select_lang": "Sprache auswählen:",
        "expenses_header": "Ihre monatlichen Ausgaben",
        "curr_expenses": "Aktuelle monatliche Ausgaben",
        "official_cpi": "Offizielle Inflation (VPI)",
        "personal_cpi": "Persönliche Inflation",
        "vs_official": "ggü. offizieller Rate",
        "chart_title": "Prognose der Ausgabenentwicklung",
        "your_rate": "Mit persönlicher Inflation",
        "off_rate": "Mit offizieller Inflation",
        "time_horizon": "Zeithorizont",
        "monthly_expenses": "Monatliche Ausgaben",
        "table_title": "Ausgabenstruktur",
        "col_category": "Kategorie",
        "col_amount": "Betrag",
        "col_share": "Anteil",
        "col_rate": "Kategorie-Inflation",
        "now": "Jetzt",
        "year": "Jahr",
        "years": "Jahre",
        "inflation": "Inflation",
    },
    "ja": {
        "title": "インフレ・シールド",
        "subtitle": "個人インフレ率計算ツール",
        "desc": "実際の日常の支出に基づいて、あなた個人のインフレ率を計算します。",
        "settings": "設定",
        "select_country": "国を選択:",
        "select_lang": "言語を選択:",
        "expenses_header": "毎月の支出",
        "curr_expenses": "現在の月間支出",
        "official_cpi": "公式インフレ率 (CPI)",
        "personal_cpi": "個人インフレ率",
        "vs_official": "公式比",
        "chart_title": "支出増加予測",
        "your_rate": "個人インフレ率を適用",
        "off_rate": "公式インフレ率を適用",
        "time_horizon": "タイムホライズン",
        "monthly_expenses": "月間支出",
        "table_title": "支出の内訳",
        "col_category": "カテゴリー",
        "col_amount": "金額",
        "col_share": "割合",
        "col_rate": "カテゴリー別インフレ率",
        "now": "現在",
        "year": "年後",
        "years": "年後",
        "inflation": "インフレ率",
    },
}


def load_data():
    with open("categories.json", "r", encoding="utf-8") as f:
        return json.load(f)


data = load_data()
countries = data.get("countries", {})

# Sidebar Settings
st.sidebar.header("Settings")

# Language Selection
lang_options = {"en": "English", "de": "Deutsch", "ja": "日本語"}
selected_lang = st.sidebar.selectbox(
    "Language / Sprache / 言語:",
    options=list(lang_options.keys()),
    format_func=lambda x: lang_options[x],
)

t = I18N[selected_lang]

# Main Title & Subtitle
st.title(t["title"])
st.subheader(t["subtitle"])
st.write(t["desc"])

# Country Selection
country_options = {
    code: info["name"][selected_lang] for code, info in countries.items()
}
selected_country_code = st.sidebar.selectbox(
    t["select_country"],
    options=list(country_options.keys()),
    format_func=lambda x: country_options[x],
)

current_country = countries[selected_country_code]
currency_symbol = current_country.get("currency_symbol", "$")
official_cpi = float(current_country.get("official_cpi", 0.0))
categories = current_country.get("categories", [])

st.sidebar.markdown("---")
st.sidebar.header(f"{t['expenses_header']} ({currency_symbol})")

user_expenses = {}
total_current_monthly = 0.0
weighted_inflation_sum = 0.0

# Expense Inputs
for cat in categories:
    cat_id = cat["id"]
    cat_name = cat["name"][selected_lang]
    default_val = float(cat["default_amount"])
    rate = float(cat["inflation_rate"])

    step_val = 1.00

    amount = st.sidebar.number_input(
        f"{cat_name} ({t['inflation']} ~{rate}%)",
        min_value=0.0,
        value=default_val,
        step=step_val,
        key=f"{selected_lang}_{selected_country_code}_{cat_id}",
    )

    user_expenses[cat_id] = {
        "amount": amount,
        "rate": rate,
        "name": cat_name,
    }

    total_current_monthly += amount
    weighted_inflation_sum += amount * (rate / 100.0)

# Personal Inflation Calculation
if total_current_monthly > 0:
    personal_inflation_rate = (
        weighted_inflation_sum / total_current_monthly
    ) * 100.0
else:
    personal_inflation_rate = 0.0

# Display Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=t["curr_expenses"],
        value=f"{total_current_monthly:,.0f} {currency_symbol}".replace(
            ",", " "
        ),
    )

with col2:
    st.metric(label=t["official_cpi"], value=f"{official_cpi:.1f}%")

with col3:
    diff = personal_inflation_rate - official_cpi
    st.metric(
        label=t["personal_cpi"],
        value=f"{personal_inflation_rate:.1f}%",
        delta=f"{diff:+.1f}% {t['vs_official']}",
        delta_color="inverse",
    )

st.divider()

# Future Projections (1, 2, 3, 4, 5 years)
years = [0, 1, 2, 3, 4, 5]
future_expenses_personal = []
future_expenses_official = []

for y in years:
    p_val = total_current_monthly * (
        (1 + personal_inflation_rate / 100.0) ** y
    )
    future_expenses_personal.append(p_val)

    o_val = total_current_monthly * ((1 + official_cpi / 100.0) ** y)
    future_expenses_official.append(o_val)

# Chart labels
x_labels = []
for y in years:
    if y == 0:
        x_labels.append(t["now"])
    elif y == 1:
        x_labels.append(f"1 {t['year']}")
    else:
        x_labels.append(f"{y} {t['years']}")

# Render Plotly Chart
st.subheader(t["chart_title"])

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=x_labels,
        y=future_expenses_personal,
        mode="lines+markers",
        name=t["your_rate"],
        line=dict(color="#FF4B4B", width=3),
    )
)

fig.add_trace(
    go.Scatter(
        x=x_labels,
        y=future_expenses_official,
        mode="lines+markers",
        name=t["off_rate"],
        line=dict(color="#0068C9", width=3),
    )
)

fig.update_layout(
    xaxis_title=t["time_horizon"],
    yaxis_title=f"{t['monthly_expenses']} ({currency_symbol})",
    hovermode="x unified",
    margin=dict(l=20, r=20, t=30, b=20),
)

st.plotly_chart(fig, use_container_width=True)

# Breakdown Table
st.subheader(t["table_title"])
breakdown_data = []
for cat_id, info in user_expenses.items():
    if total_current_monthly > 0:
        share = (info["amount"] / total_current_monthly) * 100
    else:
        share = 0
    breakdown_data.append(
        {
            t["col_category"]: info["name"],
            f"{t['col_amount']} ({currency_symbol})": f"{info['amount']:,.0f}".replace(
                ",", " "
            ),
            t["col_share"]: f"{share:.1f}%",
            t["col_rate"]: f"{info['rate']}%",
        }
    )

st.table(breakdown_data)
