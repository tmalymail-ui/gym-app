import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- KONFIGURACE A STYL ---
st.set_page_config(page_title="Iron & Soul", layout="centered")

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
        /* Filtr jemně doladí tvoje fotky pro jednotný styl */
        filter: contrast(110%) brightness(90%); 
        margin-bottom: 15px;
    }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "workout_history.csv"

# --- TVŮJ PLÁN S PŘESNÝMI NÁZVY TVÝCH SOUBORŮ ---
workout_plan = {
    "Pondělí": [
        ("Benchpress", 4, "Benchpress.jpg"),
        ("Military Press", 3, "Military Press.jpg"),
        ("Shyby", 4, "Shyby.jpg"), # Pokud soubor chybí, appka tě upozorní
        ("Dipy", 3, "Dips.jpg")
    ],
    "Středa": [
        ("Dřep", 4, "Dřep.jpg"),
        ("Rumunský mrtvý tah", 3, "Rumunský mrtvý tah.jpg"),
        ("Předkopávání", 3, "Předkopávání.jpg"),
        ("Lýtka", 4, "Lýtka.jpg")
    ],
    "Pátek": [
        ("Přítahy činky", 4, "Přítahy činky.jpg"),
        ("Incline DB Press", 3, "Incline DB press.jpg"),
        ("Facepulls", 3, "Facepulls.jpg"),
        ("Biceps", 3, "Biceps.jpg")
    ],
    "Neděle": [
        ("Mrtvý tah", 3, "Mrtvý tah.jpg"),
        ("Legpress", 4, "Legpress.jpg"),
        ("Výpady", 3, "Výpady.jpg"),
        ("Plank", 3, "Plank.jpg")
    ]
}

# Načtení historie
if os.path.exists(DB_FILE):
    df_history = pd.read_csv(DB_FILE)
else:
    df_history = pd.DataFrame(columns=["Datum", "Cvik", "Váha", "Opakování", "Série"])

tab1, tab2 = st.tabs(["🏋️ TRÉNINK", "📈 PROGRES"])

with tab1:
    if 'current_day' not in st.session_state: st.session_state.current_day = "Pondělí"
    
    cols_days = st.columns(4)
    days = list(workout_plan.keys())
    for i, day_name in enumerate(days):
        if cols_days[i].button(day_name):
            st.session_state.current_day = day_name

    selected_day = st.session_state.current_day
    st.markdown(f"## {selected_day}")
    
    new_entries = []
    for exercise, sets, img_name in workout_plan[selected_day]:
        with st.expander(f"**{exercise.upper()}**", expanded=True):
            # Kontrola existence tvého nahraného souboru
            if os.path.exists(img_name):
                st.image(img_name, use_container_width=True)
            else:
                st.info(f"Obrázek '{img_name}' zatím chybí. Nahraj ho na GitHub.")
            
            h1, h2, h3 = st.columns([1, 2, 2])
            h1.write("Série")
            h2.write("Váha")
            h3.write("Opak.")

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
            st.success("Trénink úspěšně zapsán!")
            st.balloons()

with tab2:
    st.title("Statistiky")
    all_ex = sorted(list(set([ex for d in workout_plan.values() for ex, s, i in d])))
    sel = st.selectbox("Cvik:", all_ex)
    plot_data = df_history[df_history["Cvik"] == sel]
    if not plot_data.empty:
        daily_max = plot_data.groupby("Datum")["Váha"].max().reset_index()
        fig = px.line(daily_max, x="Datum", y="Váha", template="plotly_dark", markers=True)
        fig.update_traces(line_color='#e60000')
        st.plotly_chart(fig, use_container_width=True)
