import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- KONFIGURACE ---
st.set_page_config(page_title="Iron & Soul", page_icon="🏋️", layout="centered")

# CSS zůstává stejné...
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stExpander"] { border: 1px solid #222; border-radius: 12px; background-color: #0c0c0c; margin-bottom: 25px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #e60000; color: white; font-weight: bold; border: none; }
    img { border-radius: 10px; filter: contrast(110%) brightness(90%); margin-bottom: 15px; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "workout_history.csv"

# --- CHYTRÉ NAČÍTÁNÍ DNE ---
# Pokud se appka refreshne, zkusí si zapamatovat, kde jsi byl
if 'current_day' not in st.session_state:
    st.session_state.current_day = datetime.now().strftime('%A') # Automaticky nastaví dnešní den

workout_plan = {
    "Pondělí": [("Benchpress", 4, "Benchpress.jpg"), ("Military Press", 3, "Military Press.jpg"), ("Shyby", 4, "Shyby.jpg"), ("Dipy", 3, "Dips.jpg")],
    "Středa": [("Dřep", 4, "Dřep.jpg"), ("Rumunský mrtvý tah", 3, "Rumunský mrtvý tah.jpg"), ("Předkopávání", 3, "Předkopávání.jpg"), ("Lýtka", 4, "Lýtka.jpg")],
    "Pátek": [("Přítahy činky", 4, "Přítahy činky.jpg"), ("Incline DB Press", 3, "Incline DB press.jpg"), ("Facepulls", 3, "Facepulls.jpg"), ("Biceps", 3, "Biceps.jpg")],
    "Neděle": [("Mrtvý tah", 3, "Mrtvý tah.jpg"), ("Legpress", 4, "Legpress.jpg"), ("Výpady", 3, "Výpady.jpg"), ("Plank", 3, "Plank.jpg")]
}

# Pomocná funkce pro okamžité uložení
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
    for i, day in enumerate(workout_plan.keys()):
        if cols[i].button(day):
            st.session_state.current_day = day

    day = st.session_state.current_day
    st.subheader(f"Dnešní výzva: {day}")

    for exercise, sets, img in workout_plan[day]:
        with st.expander(f"🔥 {exercise.upper()}", expanded=True):
            if os.path.exists(img):
                st.image(img)
            
            for s in range(1, sets + 1):
                c1, c2, c3, c4 = st.columns([1, 2, 2, 1.5])
                c1.write(f"{s}.")
                w = c2.number_input("kg", key=f"w_{day}_{exercise}_{s}", step=2.5, label_visibility="collapsed")
                r = c3.number_input("reps", key=f"r_{day}_{exercise}_{s}", step=1, label_visibility="collapsed")
                
                # OKAMŽITÉ TLAČÍTKO PRO KAŽDOU SÉRII
                if c4.button("Log", key=f"log_{day}_{exercise}_{s}"):
                    if w > 0 and r > 0:
                        save_data({"Datum": datetime.now().strftime("%Y-%m-%d"), "Cvik": exercise, "Váha": w, "Opakování": r, "Série": s})
                        st.toast(f"Série {s} uložena!", icon="✅")
                    else:
                        st.error("Doplň váhu a reps!")

st.caption("Tip: Klikni na 'Log' po každé sérii. Data už nezmizí ani při refreshu.")
