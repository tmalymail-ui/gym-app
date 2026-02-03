import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- KONFIGURACE A STYL ---
st.set_page_config(page_title="Iron & Soul - My Plan", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stExpander"] { 
        border: 1px solid #222; 
        border-radius: 12px; 
        background-color: #0c0c0c; 
        margin-bottom: 25px;
    }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        background-color: #e60000; 
        color: white; 
        font-weight: bold; 
        border: none;
    }
    img { 
        border-radius: 10px; 
        filter: grayscale(20%) contrast(110%); 
        margin-bottom: 15px;
    }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "workout_history.csv"

# --- TVŮJ PLÁN S TVÝMI OBRÁZKY ---
# Předpokládáme, že obrázky jsou ve stejném repozitáři na GitHubu
workout_plan = {
    "Pondělí": [
        ("Benchpress", 4, "benchpress.jpg"),
        ("Military Press", 3, "military_press.jpg"),
        ("Shyby", 4, "shyby.jpg"),
        ("Dipy", 3, "dipy.jpg")
    ],
    "Středa": [
        ("Dřep", 4, "drep.jpg"),
        ("Rumunský mrtvý tah", 3, "rumunsky_mrtvy_tah.jpg"),
        ("Předkopávání", 3, "predkopavani.jpg"),
        ("Lýtka", 4, "lytka.jpg")
    ],
    "Pátek": [
        ("Přítahy činky", 4, "pritahy_cinky.jpg"),
        ("Incline DB Press", 3, "incline_db_press.jpg"),
        ("Facepulls", 3, "facepulls.jpg"),
        ("Biceps", 3, "biceps.jpg")
    ],
    "Neděle": [
        ("Mrtvý tah", 3, "mrtvy_tah.jpg"),
        ("Legpress", 4, "legpress.jpg"),
        ("Výpady", 3, "vypady.jpg"),
        ("Plank", 3, "plank.jpg")
    ]
}

# --- LOGIKA NAČÍTÁNÍ ---
if os.path.exists(DB_FILE):
    df_history = pd.read_csv(DB_FILE)
else:
    df_history = pd.DataFrame(columns=["Datum", "Cvik", "Váha", "Opakování", "Série"])

tab1, tab2 = st.tabs(["🏋️ TRÉNINK", "📈 PROGRES"])

with tab1:
    cols_days = st.columns(4)
    if 'current_day' not in st.session_state: st.session_state.current_day = "Pondělí"
    for i, day_name in enumerate(workout_plan.keys()):
        if cols_days[i].button(day_name): st.session_state.current_day = day_name

    selected_day = st.session_state.current_day
    st.markdown(f"## {selected_day}")
    
    new_entries = []
    for exercise, sets, img_name in workout_plan[selected_day]:
        with st.expander(f"**{exercise.upper()}**", expanded=True):
            # Kontrola, zda obrázek existuje, jinak zobrazí info
            if os.path.exists(img_name):
                st.image(img_name, use_container_width=True)
            else:
                st.warning(f"Obrázek {img_name} nebyl nalezen na GitHubu.")
            
            h1, h2, h3 = st.columns([1, 2, 2])
            h1.write("Série")
            h2.write("Váha (kg)")
            h3.write("Reps")

            for s in range(1, sets + 1):
                c1, c2, c3 = st.columns([1, 2, 2])
                c1.write(f"**{s}.**")
                w = c2.number_input("kg", key=f"w_{selected_day}_{exercise}_{s}", step=2.5, label_visibility="collapsed")
                r = c3.number_input("reps", key=f"r_{selected_day}_{exercise}_{s}", step=1, label_visibility="collapsed")
                if w > 0 and r > 0:
                    new_entries.append({"Datum": datetime.now().strftime("%Y-%m-%d"), "Cvik": exercise, "Váha": w, "Opakování": r, "Série": s})

    if st.button("ULOŽIT TRÉNINK"):
        if new_entries:
            df_history = pd.concat([df_history, pd.DataFrame(new_entries)], ignore_index=True)
            df_history.to_csv(DB_FILE, index=False)
            st.success("Zapsáno! Dobrá práce.")
            st.balloons()

with tab2:
    st.title("Tvé výkony")
    all_ex = sorted(list(set([ex for d in workout_plan.values() for ex, s, i in d])))
    sel = st.selectbox("Vyber cvik:", all_ex)
    plot_data = df_history[df_history["Cvik"] == sel]
    if not plot_data.empty:
        daily_max = plot_data.groupby("Datum")["Váha"].max().reset_index()
        fig = px.line(daily_max, x="Datum", y="Váha", template="plotly_dark", markers=True)
        fig.update_traces(line_color='#e60000', marker=dict(size=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Zatím nemáš pro tento cvik žádná data.")
