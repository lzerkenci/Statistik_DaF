import streamlit as st
from app.controller import DataController

st.set_page_config(page_title="DaF Statistik", layout="wide")

# Titel
st.title("📊 Auswertung der DaF-Teilnehmenden")

# Datencontroller initialisieren und laden
controller = DataController()
controller.lade_daten()

# Gesamtzahlen
st.subheader("📌 Gesamtübersicht")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Gesamtanzahl", len(controller.df_valid))
col2.metric("Studierende", controller.get_anzahl_studierende())
col3.metric("Promovierende", controller.get_anzahl_promovierende())
col4.metric("Mitarbeitende", controller.get_anzahl_mitarbeitende())

# Studiengänge
st.subheader("🎓 Studiengänge (Studierende)")
st.dataframe(controller.get_studiengaenge_studierende())

# Abschlussarten
st.subheader("🎓 Abschlussarten (Studierende)")
st.dataframe(controller.get_abschluesse_studierende())

# Semesterverteilung
st.subheader("📚 Semesterverteilung (Studierende)")
st.dataframe(controller.get_semester_studierende())

# Studiengänge Promovierende
st.subheader("📘 Studiengänge (Promovierende)")
st.dataframe(controller.get_studiengaenge_promovierende())

# Semesterverteilung Promovierende
st.subheader("📘 Semesterverteilung (Promovierende)")
st.dataframe(controller.get_semester_promovierende())