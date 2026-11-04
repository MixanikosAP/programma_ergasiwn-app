import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Ρύθμιση τίτλου και εικονιδίου εφαρμογής
st.set_page_config(page_title="Ενεργές Εργασίες", page_icon="🔧", layout="wide")
st.title("📅 Έλεγχος Ενεργών Εργασιών Εργοταξίου")

COLUMNS = ["Εργασία", "Συνεργείο", "Ημερομηνία Έναρξης", "Ημερομηνία Λήξης"]

# 📂 Ανέβασμα αρχείου Excel
uploaded_file = st.file_uploader("📂 Ανέβασε το αρχείο Excel", type=["xlsx"])
st.caption("Απαιτούμενες στήλες: " + ", ".join(COLUMNS))


def gantt(df, selected_date, mask):
    """Διάγραμμα Gantt: οι ενεργές εργασίες χρωματίζονται, η επιλεγμένη ημερομηνία σημειώνεται."""
    d = df.sort_values("Ημερομηνία Έναρξης").reset_index(drop=True)
    active = d["Εργασία"].isin(df.loc[mask, "Εργασία"])
    fig, ax = plt.subplots(figsize=(10, 0.38 * len(d) + 1.2))
    for i, row in d.iterrows():
        start = mdates.date2num(row["Ημερομηνία Έναρξης"])
        width = mdates.date2num(row["Ημερομηνία Λήξης"]) - start
        ax.barh(i, width, left=start, height=0.6,
                color="#2E6DA4" if active.iloc[i] else "#C9D3DD", edgecolor="none")
    ax.axvline(mdates.date2num(selected_date), color="#E4572E", lw=2)
    ax.text(mdates.date2num(selected_date), -0.9, selected_date.strftime("%d/%m/%Y"),
            color="#E4572E", ha="center", va="bottom", fontsize=9)
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels(d["Εργασία"], fontsize=8)
    ax.invert_yaxis()
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.grid(axis="x", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Χρονοδιάγραμμα εργασιών (μπλε: ενεργές την επιλεγμένη ημερομηνία)")
    fig.tight_layout()
    return fig


if uploaded_file:
    try:
        # 📊 Ανάγνωση και μετατροπή ημερομηνιών
        df = pd.read_excel(uploaded_file)
        λείπουν = [c for c in COLUMNS if c not in df.columns]
        if λείπουν:
            st.error("⚠️ Λείπουν οι στήλες: " + ", ".join(λείπουν))
            st.stop()
        df["Ημερομηνία Έναρξης"] = pd.to_datetime(df["Ημερομηνία Έναρξης"])
        df["Ημερομηνία Λήξης"] = pd.to_datetime(df["Ημερομηνία Λήξης"])

        # 📆 Επιλογή ημερομηνίας (προεπιλογή: η έναρξη του έργου)
        αρχή, τέλος = df["Ημερομηνία Έναρξης"].min(), df["Ημερομηνία Λήξης"].max()
        st.write(f"Διάρκεια έργου στο αρχείο: **{αρχή:%d/%m/%Y} – {τέλος:%d/%m/%Y}**")
        selected_date = st.date_input("📌 Διάλεξε ημερομηνία για έλεγχο", value=αρχή.date(), format="DD/MM/YYYY")
        selected_date = pd.to_datetime(selected_date)

        # 🔍 Φιλτράρισμα ενεργών εργασιών
        mask = (df["Ημερομηνία Έναρξης"] <= selected_date) & (df["Ημερομηνία Λήξης"] >= selected_date)
        ενεργές = df[mask]

        # Εμφάνιση αποτελεσμάτων
        if ενεργές.empty:
            st.warning(f"⛔ Δεν υπάρχουν ενεργές εργασίες στις {selected_date:%d/%m/%Y}.")
        else:
            st.success(f"✅ {len(ενεργές)} ενεργές εργασίες στις {selected_date:%d/%m/%Y}:")
            προβολή = ενεργές[COLUMNS].copy()
            for c in ["Ημερομηνία Έναρξης", "Ημερομηνία Λήξης"]:
                προβολή[c] = προβολή[c].dt.strftime("%d/%m/%Y")
            st.dataframe(προβολή, width="stretch", hide_index=True)

        fig = gantt(df, selected_date, mask)
        st.pyplot(fig)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=200, bbox_inches="tight", facecolor="white")
        st.download_button("🖼️ Κατέβασε το διάγραμμα (PNG)", buf.getvalue(), "gantt.png", "image/png")

    except Exception as e:
        st.error(f"⚠️ Σφάλμα στην ανάγνωση του αρχείου: {e}")
else:
    st.info("➕ Περιμένω να ανεβάσεις αρχείο Excel...")
