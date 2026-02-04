import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- KONFIGURACE ---
st.set_page_config(page_title="Iron & Soul", page_icon="🏋️", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stExpander"] { border: 1px solid #222; border-radius: 12px; background-color: #0c0c0c; margin-bottom: 25px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #e60000; color: white; font-weight: bold; border: none; }
    img { border-radius: 10px; filter: contrast(110%) brightness(90%); margin-bottom: 15px; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    /* Styl pro taby */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #111; border-radius: 10px 10px 0 0; padding: 10px 20px; color: white; }
    .stTabs [aria-selected="true"] { background-color: #e60000 !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "workout_history.csv"

days_translation = {
    "Monday": "Pondělí", "Tuesday": "Úterý", "Wednesday": "Středa", 
    "Thursday": "Čtvrtek", "Friday": "Pátek", "Saturday": "Sobota", "Sunday": "Neděle"
}

workout_plan = {
    "Pondělí": [("Benchpress", 4, "Benchpress.jpg"), ("Military Press", 3, "Military Press.jpg"), ("Shyby", 4, "Shyby.jpg"), ("Dipy", 3, "Dips.jpg")],
    "Středa": [("Dřep", 4, "Dřep.jpg"), ("Rumunský mrtvý tah", 3, "Rumunský mrtvý tah.jpg"), ("Předkopávání", 3, "Předkopávání.jpg"), ("Lýtka", 4, "Lýtka.jpg")],
    "Pátek": [("Přítahy činky", 4, "Přítahy činky.jpg"), ("Incline DB Press", 3, "Incline DB press.jpg"), ("Facepulls", 3, "Facepulls.jpg"), ("Biceps", 4, "Biceps.jpg")],
    "Neděle": [("Mrtvý tah", 3, "Mrtvý tah.jpg"), ("Legpress", 4, "Legpress.jpg"), ("Výpady", 3, "Výpady.jpg"), ("Plank", 3, "Plank.jpg")]
}

if 'current_day' not in st.session_state:
    eng_day = datetime.now().strftime('%A')
    st.session_state.current_day = days_translation.get(eng_day, "Pondělí")
    if st.session_state.current_day not in workout_plan:
        st.session_state.current_day = "Pondělí"

def save_data(entry):
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
    else:
        df = pd.DataFrame(columns=["Datum", "Cvik", "Váha", "Opakování", "Série"])
    new_df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    new_df.to_csv(DB_FILE, index=False)

tab1, tab2 = st.tabs(["🏋️ TRÉNINK", "📈 PROGRES"])

with tab1:
    cols = st.columns(4)
    plan_days = list(workout_plan.keys())
    for i, day in enumerate(plan_days):
        if cols[i].button(day):
            st.session_state.current_day = day

    current_day = st.session_state.current_day
    st.subheader(f"Dnešní výzva: {current_day}")

    if current_day in workout_plan:
        for exercise, sets, img in workout_plan[current_day]:
            with st.expander(f"🔥 {exercise.upper()}", expanded=True):
                if os.path.exists(img):
                    st.image(img, use_container_width=True)
                
                for s in range(1, sets + 1):
                    c1, c2, c3, c4 = st.columns([1, 2, 2, 1.5])
                    c1.write(f"{s}.")
                    w = c2.number_input("kg", key=f"w_{current_day}_{exercise}_{s}", step=2.5, label_visibility="collapsed")
                    r = c3.number_input("reps", key=f"r_{current_day}_{exercise}_{s}", step=1, label_visibility="collapsed")
                    
                    if c4.button("Log", key=f"log_{current_day}_{exercise}_{s}"):
                        if w > 0 and r > 0:
                            save_data({"Datum": datetime.now().strftime("%Y-%m-%d"), "Cvik": exercise, "Váha": w, "Opakování": r, "Série": s})
                            st.toast(f"Uloženo: {w}kg", icon="✅")
                        else:
                            st.error("Zadej data!")
    else:
        st.info("Vyber si tréninkový den.")

with tab2:
    st.header("Tvoje cesta vzhůru")
    if os.path.exists(DB_FILE):
        history_df = pd.read_csv(DB_FILE)
        if not history_df.empty:
            # Výběr cviku pro graf
            seznam_cviku = sorted(history_df['Cvik'].unique())
            vybrany_cvik = st.selectbox("Vyber cvik pro zobrazení progresu:", seznam_cviku)
            
            # Filtrace dat pro graf (bereme maximální váhu v daný den)
            chart_data = history_df[history_df['Cvik'] == vybrany_cvik]
            chart_data = chart_data.groupby('Datum')['Váha'].max().reset_index()
            
            if len(chart_data) > 0:
                fig = px.line(chart_data, x='Datum', y='Váha', title=f"Progres: {vybrany_cvik}",
                             markers=True, template="plotly_dark")
                fig.update_traces(line_color='#e60000', marker=dict(size=10, color='white'))
                fig.update_layout(yaxis_title="Maximální váha (kg)", xaxis_title="Datum")
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabulka posledních výkonů
                st.write("Poslední záznamy:")
                st.dataframe(history_df[history_df['Cvik'] == vybrany_cvik].tail(10), use_container_width=True)
            else:
                st.info("Pro tento cvik zatím nemáš dostatek dat pro graf.")
        else:
            st.info("Historie je zatím prázdná. Odcvič první trénink!")
    else:
        st.info("Zatím jsi neuložil žádná data. Jakmile klikneš na 'Log', uvidíš zde svůj progres.")
