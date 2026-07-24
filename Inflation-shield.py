import json
import plotly.graph_objects as go
import streamlit as st

# Настройка страницы
st.set_page_config(
    page_title="Inflation Shield", page_icon="🛡️", layout="wide"
)

# Заголовок
st.title("🛡️ Inflation Shield")
st.subheader("Калькулятор персональной инфляции")
st.write(
    "Узнайте вашу личную инфляцию на основе ваших реальных ежедневных трат."
)


# Загрузка категорий из categories.json
@st.cache_data
def load_data():
    with open("categories.json", "r", encoding="utf-8") as f:
        return json.load(f)


data = load_data()
categories = data.get("categories", [])
official_cpi = data.get("official_cpi", 8.5)

st.sidebar.header("Ваши ежемесячные расходы (руб.)")

user_expenses = {}
total_current_monthly = 0.0
weighted_inflation_sum = 0.0

# Форма ввода трат в боковой панели
for cat in categories:
    cat_id = cat["id"]
    cat_name = cat["name"]
    default_val = float(cat["default_amount"])
    rate = float(cat["inflation_rate"])

    # Поле ввода для пользователя
    amount = st.sidebar.number_input(
        f"{cat_name} (Инфляция ~{rate}%)",
        min_value=0.0,
        value=default_val,
        step=500.0,
        key=cat_id,
    )

    user_expenses[cat_id] = {
        "amount": amount,
        "rate": rate,
        "name": cat_name,
    }

    total_current_monthly += amount
    weighted_inflation_sum += amount * (rate / 100.0)

# Расчет персональной инфляции
if total_current_monthly > 0:
    personal_inflation_rate = (
        weighted_inflation_sum / total_current_monthly
    ) * 100.0
else:
    personal_inflation_rate = 0.0

# Вывод метрик
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Текущие расходы в месяц",
        value=f"{total_current_monthly:,.0f} ₽".replace(",", " "),
    )

with col2:
    st.metric(
        label="Официальная инфляция (ИПЦ)", value=f"{official_cpi:.1f}%"
    )

with col3:
    diff = personal_inflation_rate - official_cpi
    st.metric(
        label="Ваша персональная инфляция",
        value=f"{personal_inflation_rate:.1f}%",
        delta=f"{diff:+.1f}% к официальной",
        delta_color="inverse",
    )

st.divider()

# Прогноз трат на 1, 3, 5 лет
years = [0, 1, 3, 5]
future_expenses_personal = []
future_expenses_official = []

for y in years:
    # По персональной инфляции
    p_val = total_current_monthly * ((1 + personal_inflation_rate / 100.0) ** y)
    future_expenses_personal.append(p_val)

    # По официальной инфляции
    o_val = total_current_monthly * ((1 + official_cpi / 100.0) ** y)
    future_expenses_official.append(o_val)

# Построение графика
st.subheader("📈 Прогноз роста ваших расходов")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=[f"{y} год" if y != 0 else "Сейчас" for y in years],
        y=future_expenses_personal,
        mode="lines+markers",
        name="С учетом Вашей инфляции",
        line=dict(color="#FF4B4B", width=3),
    )
)

fig.add_trace(
    go.Scatter(
        x=[f"{y} год" if y != 0 else "Сейчас" for y in years],
        y=future_expenses_official,
        mode="lines+markers",
        name="С учетом Официальной инфляции",
        line=dict(color="#0068C9", width=2, dash="dash"),
    )
)

fig.update_layout(
    xaxis_title="Временной горизонт",
    yaxis_title="Расходы в месяц (руб.)",
    hovermode="x unified",
    margin=dict(l=20, r=20, t=30, b=20),
)

st.plotly_chart(fig, use_container_width=True)

# Таблица развертки
st.subheader("📊 Структура ваших трат")
breakdown_data = []
for cat_id, info in user_expenses.items():
    if total_current_monthly > 0:
        share = (info["amount"] / total_current_monthly) * 100
    else:
        share = 0
    breakdown_data.append(
        {
            "Категория": info["name"],
            "Сумма (₽)": f"{info['amount']:,.0f}".replace(",", " "),
            "Доля в бюджете": f"{share:.1f}%",
            "Инфляция категории": f"{info['rate']}%",
        }
    )

st.table(breakdown_data)
