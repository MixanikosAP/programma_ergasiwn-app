import io
from collections import deque

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Domino Effect Καθυστερήσεων", page_icon="🛠", layout="wide")
st.title("⏳ Domino Effect Καθυστερήσεων Εργασιών")

COLUMNS = ["Εργασία", "Ημερομηνία Έναρξης", "Ημερομηνία Λήξης", "Εξαρτάται από"]

uploaded_file = st.file_uploader("📂 Ανέβασε το αρχείο Excel με τις εργασίες", type=["xlsx"])
st.caption("Απαιτούμενες στήλες: " + ", ".join(COLUMNS) +
           ". Αν μια εργασία εξαρτάται από περισσότερες, γράψ' τες χωρισμένες με κόμμα.")


def προκάτοχοι(τιμή):
    """Επιστρέφει τη λίστα εργασιών από τις οποίες εξαρτάται μια εργασία."""
    if pd.isna(τιμή) or str(τιμή).strip() == "":
        return []
    return [x.strip() for x in str(τιμή).split(",") if x.strip()]


def βρες_επηρεαζόμενες(εργασία, df):
    """Βρίσκει όλες τις εργασίες που εξαρτώνται (άμεσα ή έμμεσα) από την εργασία.
    Κάθε εργασία μετράται μία φορά, ακόμη κι αν υπάρχουν κύκλοι στις εξαρτήσεις."""
    παιδιά = {}
    for _, row in df.iterrows():
        for p in προκάτοχοι(row["Εξαρτάται από"]):
            παιδιά.setdefault(p, []).append(row["Εργασία"])
    επηρεαζόμενες, ουρά, είδαμε = [], deque([εργασία]), {εργασία}
    while ουρά:
        τρέχουσα = ουρά.popleft()
        for π in παιδιά.get(τρέχουσα, []):
            if π not in είδαμε:
                είδαμε.add(π)
                επηρεαζόμενες.append(π)
                ουρά.append(π)
    return επηρεαζόμενες


if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        λείπουν = [c for c in COLUMNS if c not in df.columns]
        if λείπουν:
            st.error("⚠️ Λείπουν οι στήλες: " + ", ".join(λείπουν))
            st.stop()
        df["Ημερομηνία Έναρξης"] = pd.to_datetime(df["Ημερομηνία Έναρξης"])
        df["Ημερομηνία Λήξης"] = pd.to_datetime(df["Ημερομηνία Λήξης"])

        εργασία_καθυστέρηση = st.selectbox("Επίλεξε εργασία που καθυστερεί", df["Εργασία"].tolist())
        καθυστέρηση_ημέρες = st.number_input("Καθυστέρηση (ημέρες)", min_value=1, step=1)

        if st.button("Υπολόγισε Νέες Ημερομηνίες"):
            επηρεαζόμενες = βρες_επηρεαζόμενες(εργασία_καθυστέρηση, df)
            αλλαγμένες = [εργασία_καθυστέρηση] + επηρεαζόμενες

            νέο = df.copy()
            νέο["Αρχική Έναρξη"] = df["Ημερομηνία Έναρξης"]
            νέο["Αρχική Λήξη"] = df["Ημερομηνία Λήξης"]
            mask = νέο["Εργασία"].isin(αλλαγμένες)
            νέο.loc[mask, "Ημερομηνία Έναρξης"] += pd.Timedelta(days=int(καθυστέρηση_ημέρες))
            νέο.loc[mask, "Ημερομηνία Λήξης"] += pd.Timedelta(days=int(καθυστέρηση_ημέρες))
            νέο["Μετατοπίστηκε"] = mask.map({True: "Ναι", False: ""})

            st.success("✅ Νέες ημερομηνίες υπολογίστηκαν!")
            c1, c2 = st.columns(2)
            c1.metric("Επηρεαζόμενες εργασίες (Domino)", len(επηρεαζόμενες))
            c2.metric("Μετατόπιση", f"{int(καθυστέρηση_ημέρες)} ημέρες")
            if επηρεαζόμενες:
                st.write("**Εργασίες που επηρεάζονται:** " + ", ".join(map(str, επηρεαζόμενες)))
            st.caption("Ο αριθμός «Επηρεαζόμενες εργασίες» είναι η τιμή που μπαίνει στη στήλη "
                       "«Domino (εργασίες)» της εφαρμογής DII.")

            προβολή = νέο[["Εργασία", "Εξαρτάται από", "Αρχική Έναρξη", "Αρχική Λήξη",
                           "Ημερομηνία Έναρξης", "Ημερομηνία Λήξης", "Μετατοπίστηκε"]].copy()
            for c in ["Αρχική Έναρξη", "Αρχική Λήξη", "Ημερομηνία Έναρξης", "Ημερομηνία Λήξης"]:
                προβολή[c] = προβολή[c].dt.strftime("%d/%m/%Y")
            st.dataframe(προβολή.style.apply(
                lambda r: ["background-color: #F5A62333" if r["Μετατοπίστηκε"] else ""] * len(r), axis=1),
                width="stretch")

            out = io.BytesIO()
            νέο.drop(columns=["Μετατοπίστηκε"]).to_excel(out, index=False)
            st.download_button("📥 Κατέβασε το ενημερωμένο Excel", out.getvalue(), "updated_schedule.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        st.error(f"⚠️ Σφάλμα: {e}")
else:
    st.info("➕ Ανέβασε Excel για να ξεκινήσεις...")
