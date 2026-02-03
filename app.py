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
        filter: grayscale(100%) contrast(115%); 
        margin-bottom: 15px;
    }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "workout_history.csv"

# --- PLÁN S PŘESNÝMI DARK OBRÁZKY ---
workout_plan = {
    "Pondělí": [
        ("Benchpress", 4, "http://googleusercontent.com/image_collection/image_retrieval/13868190095872251997_0"),
        ("Military Press", 3, "http://googleusercontent.com/image_collection/image_retrieval/2134283301185296851_2"),
        ("Shyby", 4, "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?q=80&w=800&auto=format&fit=crop"),
        ("Dipy", 3, "http://googleusercontent.com/image_collection/image_retrieval/14829602002368458561_1")
    ],
    "Středa": [
        ("Dřep", 4, "http://googleusercontent.com/image_collection/image_retrieval/2134283301185296851_0"),
        ("Rumunský mrtvý tah", 3, "http://googleusercontent.com/image_collection/image_retrieval/16090004086812452093_0"),
        ("Předkopávání", 3, "http://googleusercontent.com/image_collection/image_retrieval/12250907081252825406_0"),
        ("Lýtka", 4, "http://googleusercontent.com/image_collection/image_retrieval/11086995219417796900_0")
    ],
    "Pátek": [
        ("Přítahy činky", 4, "http://googleusercontent.com/image_collection/image_retrieval/2297255091226237803_0"),
        ("Incline DB Press", 3, "http://googleusercontent.com/image_collection/image_retrieval/2235228819727505502_0"),
        ("Facepulls", 3, "http://googleusercontent.com/image_collection/image_retrieval/790947403539940402_1"),
        ("Biceps", 3, "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=800&auto=format&fit=crop")
    ],
    "Neděle": [
        ("Mrtvý tah", 3, "http://googleusercontent.com/image_collection/image_retrieval/15447851289251353555_0"),
        ("Legpress", 4, "http://googleusercontent.com/image_collection/image_retrieval/3847194540439646130_0"),
        ("Výpady", 3, "http://googleusercontent.com/image_collection/image_retrieval/2597715352704869837_0"),
        ("Plank", 3, "http://googleusercontent.com/image_collection/image_retrieval/4832884953854308456_0")
    ]
}

# --- LOGIKA A UI ---
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
    for exercise, sets, img_url in workout_plan[selected_day]:
        with st.expander(f"**{exercise.upper()}**", expanded=True):
            st.image(img_url, use_container_width=True)
            
            h1, h2, h3 = st.columns([1, 2, 2])
            h1.markdown("<p style='font-size:12px;'>Série</p>", unsafe_allow_html=True)
            h2.markdown("<p style='font-size:12px;'>Váha (kg)</p>", unsafe_allow_html=True)
            h3.markdown("<p style='font-size:12px;'>Reps</p>", unsafe_allow_html=True)

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
            st.success("Trénink uložen!")
            st.balloons()

with tab2:
    st.title("Progres")
    all_ex = sorted(list(set([ex for d in workout_plan.values() for ex, s, i in d])))
    sel = st.selectbox("Cvik:", all_ex)
    plot_data = df_history[df_history["Cvik"] == sel]
    if not plot_data.empty:
        daily_max = plot_data.groupby("Datum")["Váha"].max().reset_index()
        fig = px.line(daily_max, x="Datum", y="Váha", template="plotly_dark", markers=True)
        fig.update_traces(line_color='#e60000')
        st.plotly_chart(fig, use_container_width=True)
