"""Konfiguration für das Statistik-DaF-Projekt.

Beinhaltet Pfade und standardisierte Spaltennamen für die CSV-Datenanalyse.
"""
import os

# ------------------- Datei- und Datenkonfiguration -------------------

# Pfad zur CSV-Datei mit den Teilnehmendendaten
#DATA_PATH = "data/Teilnehmendenexport_Deutsch_für_den_Beruf_Fit_für_den_Berufsalltag_B2C1.csv"


# Absoluter Pfad zum Ordner mit den Teilnehmerlisten
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # .../app
DATA_FOLDER = os.path.join(BASE_DIR, "..", "data", "teilnehmerliste_export")

# Alle CSV-Dateien im Ordner laden
DATA_PATHS = [
    os.path.join(DATA_FOLDER, f)
    for f in os.listdir(DATA_FOLDER)
    if f.endswith(".csv")
]

# ------------------- Spaltennamen der CSV-Datei -------------------

# Status des Teilnehmers (z.B autor, dozent, tutor)
COLUMN_STATUS = "Status"

# Persönliche Angaben
COLUMN_VORNAME = "Vorname"
COLUMN_NACHNAME = "Nachname"
COLUMN_EMAIL = "E-Mail"
COLUMN_TITEL = "Titel nachgestellt"
COLUMN_MATRIKELNUMMER = "Matrikelnummer"
COLUMN_BENUTZERNAME = "Benutzername"

# Studiengangsinformationen (roh & bereinigt)
COLUMN_STUDIENGANG = "Studiengänge"            # Original aus CSV (evtl. mehrere pro Person)
COLUMN_STUDIENGANG_CLEAN = "Studiengang"       # Gereinigter, einzelner Studiengang

# Studienbezogene Merkmale
COLUMN_ABSCHLUSSART = "Abschluss"
COLUMN_SEMESTER = "Semester"

# Zulässige Abschlussarten
GUELTIGE_ABSCHLUSSARTEN = ["Bachelor", "Master", "Zwei-Fächer-Bachelor", "2-Fächer-Bachelor"]