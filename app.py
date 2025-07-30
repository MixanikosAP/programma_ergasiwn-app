import streamlit as st
import pandas as pd
from datetime import datetime

# Ρύθμιση τίτλου και εικονιδίου εφαρμογής
st.set_page_config(page_title="Ενεργές Εργασίες", page_icon="🔧")

st.title("📅 Έλεγχος Ενεργών Εργασιών Εργοταξίου")

# 📂 Ανέβασμα αρχείου Excel
uploaded_file = st.file_uploader("📂 Ανέβασε το αρχείο Excel", type=["xlsx"])

if uploaded_file:
    try:
        # 📊 Ανάγνωση και μετατροπή ημερομηνιών
        df = pd.read_excel(uploaded_file)

        # Μετατροπή σε datetime
        df["Ημερομηνία Έναρξης"] = pd.to_datetime(df["Ημερομηνία Έναρξης"])
        df["Ημερομηνία Λήξης"] = pd.to_datetime(df["Ημερομηνία Λήξης"])

        # 📆 Επιλογή ημερομηνίας
        selected_date = st.date_input("📌 Διάλεξε ημερομηνία για έλεγχο", value=datetime.today())
        selected_date = pd.to_datetime(selected_date)

        # 🔍 Φιλτράρισμα ενεργών εργασιών
        mask = (df["Ημερομηνία Έναρξης"] <= selected_date) & (df["Ημερομηνία Λήξης"] >= selected_date)
        ενεργές = df[mask]

        # Εμφάνιση αποτελεσμάτων
        if ενεργές.empty:
            st.warning(f"⛔ Δεν υπάρχουν ενεργές εργασίες στις {selected_date.date()}.")
        else:
            st.success(f"✅ Ενεργές εργασίες στις {selected_date.date()}:")
            st.dataframe(ενεργές[["Εργασία", "Συνεργείο", "Ημερομηνία Έναρξης", "Ημερομηνία Λήξης"]])

    except Exception as e:
        st.error(f"⚠️ Σφάλμα στην ανάγνωση του αρχείου: {e}")
else:
    st.info("➕ Περιμένω να ανεβάσεις αρχείο Excel...")
