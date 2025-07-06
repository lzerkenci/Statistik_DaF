import streamlit as st
from app.controller import DataController
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="DaF Statistik", layout="wide")

# Titel
st.title("📊 Auswertung der DaF-Teilnehmenden")

# Datencontroller initialisieren und laden
controller = DataController()
controller.lade_daten()

# Gesamtzahlen
st.subheader("📌 Gesamtübersicht")
col1, col2, col3 = st.columns(3)
col1.metric("Gesamtanzahl", len(controller.df_valid))
col2.metric("Studierende (gesamt)", controller.get_anzahl_alle_studierende())
col3.metric("Mitarbeitende", controller.get_anzahl_mitarbeitende())

st.markdown(
    f"**Davon TU-Studierende:** {controller.get_anzahl_tu_studierende()} &nbsp;&nbsp;|&nbsp;&nbsp;"
    f"**HBK-Studierende:** {controller.get_anzahl_hbk_studierende()} &nbsp;&nbsp;|&nbsp;&nbsp;"
    f"**Promovierende:** {controller.get_anzahl_promovierende()}"
)

# Auswahlfilter hinzufügen (direkt nach dem Setzen des Titels)
gruppe = st.radio(
    "Welche Gruppe soll angezeigt werden?",
    options=["Alle", "Studierende", "Promovierende"],
    horizontal=True
)

# Daten anhand der Auswahl laden
controller.lade_daten()
df_valid = controller.df_valid


if gruppe == "Studierende":
    df = controller.df_studierende
elif gruppe == "Promovierende":
    df = controller.df_promovierende
else:
    df = controller.df_valid

### 🎓 Studiengänge
df_studiengaenge = controller.get_studiengaenge_studierende().reset_index()
df_studiengaenge.columns = ["studiengang", "anzahl"]
df_studiengaenge = df_studiengaenge.sort_values("anzahl", ascending=False)
df_studiengaenge.index += 1

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("🎓 Studiengänge (Studierende)")
    st.data_editor(df_studiengaenge, disabled=True, use_container_width=True)
with col2:
    st.subheader("Top 10 Studiengänge + Andere")
    top_df = df_studiengaenge[:10]
    rest_sum = df_studiengaenge["anzahl"][10:].sum()
    pie_df = pd.concat([top_df, pd.DataFrame([["Andere", rest_sum]], columns=["studiengang", "anzahl"])])
    fig = px.pie(pie_df, names="studiengang", values="anzahl", hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

# Abschlussarten & Semesterverteilung (Studierende)
df_abschluesse = controller.get_abschluesse_studierende().reset_index()
df_abschluesse.columns = ["abschlussart", "anzahl"]
df_abschluesse = df_abschluesse.sort_values("anzahl", ascending=False)
df_abschluesse.index += 1

df_semester = controller.get_semester_studierende().reset_index()
df_semester.columns = ["semester", "anzahl"]
df_semester = df_semester.sort_values("anzahl", ascending=False)
df_semester.index += 1

col3, col4 = st.columns([1, 1])
with col3:
    st.subheader("🎓 Abschlussarten (Studierende)")
    st.data_editor(df_abschluesse, disabled=True, use_container_width=True)

with col4:
    st.subheader("📚 Semesterverteilung (Studierende)")
    st.data_editor(df_semester, disabled=True, use_container_width=True, height=220)


# Studiengänge Promovierende
### 🎓 Studiengänge
df_studiengaenge = controller.get_studiengaenge_promovierende().reset_index()
df_studiengaenge.columns = ["studiengang", "anzahl"]
df_studiengaenge = df_studiengaenge.sort_values("anzahl", ascending=False)
df_studiengaenge.index += 1

col5, col6 = st.columns([1, 1])
with col5:
    st.subheader("🎓 Studiengänge (Promovierende)")
    st.data_editor(df_studiengaenge, disabled=True, use_container_width=True)
with col6:
    st.subheader("Top 10 Studiengänge + Andere")
    top_df = df_studiengaenge[:10]
    rest_sum = df_studiengaenge["anzahl"][10:].sum()
    pie_df = pd.concat([top_df, pd.DataFrame([["Andere", rest_sum]], columns=["studiengang", "anzahl"])])
    fig = px.pie(pie_df, names="studiengang", values="anzahl", hole=0.3)
    st.plotly_chart(fig, use_container_width=True)


# Semesterverteilung Promovierende
df_semester = controller.get_semester_promovierende().reset_index()
df_semester.columns = ["semester", "anzahl"]
df_semester = df_semester.sort_values("anzahl", ascending=False)
df_semester.index += 1

col7, _ = st.columns([1, 1])

with col7:
    st.subheader("📚 Semesterverteilung (Promovierende)")
    st.data_editor(df_semester, disabled=True, use_container_width=True, height=220)


