import pandas as pd
from app import config


class DataController:
    """Verwaltet das Einlesen, Filtern und Auswerten der DaF-Teilnehmerdaten."""

    def __init__(self):
        """Initialisiert leere DataFrames für Rohdaten und alle Gruppen."""
        self.df_raw = None
        self.df_valid = None
        self.df_studierende = None
        self.df_mitarbeitende = None
        self.df_promovierende = None

    def lade_daten(self):
        """Lädt und verarbeitet die CSV-Daten, filtert gültige Einträge und klassifiziert nach Gruppen."""

        # Rohdaten laden
        self.df_raw = pd.read_csv(config.DATA_PATH, sep=";")

        # Nur gültige autor*innen mit Vor- und Nachnamen behalten
        self.df_valid = self.df_raw[
            self.df_raw[config.COLUMN_VORNAME].notna() &
            self.df_raw[config.COLUMN_NACHNAME].notna() &
            (self.df_raw[config.COLUMN_STATUS] == "autor")
        ].copy()

        # Studierenden-ID generieren
        self.df_valid["studierende_id"] = self.df_valid[config.COLUMN_MATRIKELNUMMER].astype(str).str.strip()
        self.df_valid["studierende_id"] = self.df_valid["studierende_id"].replace("nan", "")

        # Fallback: HBK-Adresse als ID bei fehlender Matrikelnummer
        hbk_mask = self.df_valid["studierende_id"].isin([""]) & \
                   self.df_valid[config.COLUMN_EMAIL].str.contains("@hbk", case=False, na=False)
        self.df_valid.loc[hbk_mask, "studierende_id"] = (
            self.df_valid.loc[hbk_mask, config.COLUMN_EMAIL].str.strip().str.lower()
        )

        # Mitarbeitende vor dem Explode sichern (kein Studiengang angegeben)
        df_mitarbeiter_kandidaten = self.df_valid[
            self.df_valid[config.COLUMN_STUDIENGANG].isna()
        ]

        # Studiengänge aufsplitten (bei Mehrfacheinträgen)
        self.df_valid["Studiengang_gesplittet"] = self.df_valid[config.COLUMN_STUDIENGANG].str.split(";")
        self.df_valid = self.df_valid.explode("Studiengang_gesplittet")

        # Leere Studiengänge ausschließen
        self.df_valid = self.df_valid[
            self.df_valid["Studiengang_gesplittet"].notna() &
            (self.df_valid["Studiengang_gesplittet"].str.strip() != "")
        ]

        # Studiengang, Abschluss und Semester extrahieren
        def parse_studiengang(zeile):
            """Zerlegt einen Studiengangseintrag in Studiengang, Abschlussart und Semester.

            Args:
                zeile (str): Studiengangsdaten (z. B. "Informatik,Bachelor,3")

            Returns:
                pd.Series: [Studiengang, Abschlussart, Semester]
            """
            if pd.isna(zeile):
                return pd.Series(["", "", ""])
            teile = [t.strip() for t in zeile.split(",")]
            if len(teile) == 4:
                return pd.Series([f"{teile[0]}, {teile[1]}", teile[2], teile[3]])
            elif len(teile) == 3:
                return pd.Series([teile[0], teile[1], teile[2]])
            return pd.Series(["", "", ""])

        self.df_valid[[config.COLUMN_STUDIENGANG_CLEAN,
                       config.COLUMN_ABSCHLUSSART,
                       config.COLUMN_SEMESTER]] = self.df_valid["Studiengang_gesplittet"].apply(parse_studiengang)

        # Whitespace bereinigen
        for col in [config.COLUMN_STUDIENGANG_CLEAN, config.COLUMN_ABSCHLUSSART, config.COLUMN_SEMESTER]:
            self.df_valid[col] = self.df_valid[col].str.strip()

        # Promovierende erkennen (Abschluss enthält "Promotion")
        self.df_promovierende = self.df_valid[
            self.df_valid[config.COLUMN_STUDIENGANG_CLEAN].notna() &
            self.df_valid[config.COLUMN_ABSCHLUSSART].str.contains("Promotion", case=False, na=False)
        ]

        # Studierende (mit Studiengang, aber nicht Promotion)
        self.df_studierende = self.df_valid[
            (
                self.df_valid[config.COLUMN_STUDIENGANG_CLEAN].notna() |
                self.df_valid[config.COLUMN_EMAIL].str.contains("@hbk", case=False, na=False)
            ) &
            ~self.df_valid.index.isin(self.df_promovierende.index)
        ]

        # Mitarbeitende aus ursprünglichen Kandidaten ableiten
        self.df_mitarbeitende = df_mitarbeiter_kandidaten[
            ~df_mitarbeiter_kandidaten.index.isin(self.df_studierende.index) &
            ~df_mitarbeiter_kandidaten.index.isin(self.df_promovierende.index)
        ]

    # ------------------- Auswertungsmethoden -------------------

    def get_anzahl_studierende(self):
        """Gibt die Anzahl eindeutiger Studierender zurück."""
        return self.df_studierende["studierende_id"].drop_duplicates().nunique()

    def get_studiengaenge_studierende(self):
        """Gibt die Häufigkeit der Studiengänge unter Studierenden zurück."""
        return self.df_studierende[config.COLUMN_STUDIENGANG_CLEAN].value_counts()

    def get_abschluesse_studierende(self):
        """Zählt gültige Abschlussarten unter Studierenden."""
        df_unique = self.df_studierende.drop_duplicates(subset=["studierende_id", config.COLUMN_ABSCHLUSSART])
        df_gefiltert = df_unique[df_unique[config.COLUMN_ABSCHLUSSART].isin(config.GUELTIGE_ABSCHLUSSARTEN)]
        return df_gefiltert[config.COLUMN_ABSCHLUSSART].value_counts()

    def get_semester_studierende(self):
        """Zählt die Semesterverteilung unter Studierenden."""
        return self.df_studierende[config.COLUMN_SEMESTER].value_counts()

    def get_anzahl_promovierende(self):
        """Gibt die Anzahl der Promovierenden zurück."""
        return len(self.df_promovierende)

    def get_studiengaenge_promovierende(self):
        """Gibt die Häufigkeit der Studiengänge unter Promovierenden zurück."""
        return self.df_promovierende[config.COLUMN_STUDIENGANG_CLEAN].value_counts()

    def get_semester_promovierende(self):
        """Zählt die Semesterverteilung unter Promovierenden."""
        return self.df_promovierende[config.COLUMN_SEMESTER].value_counts()

    def get_anzahl_mitarbeitende(self):
        """Gibt die Anzahl der Mitarbeitenden zurück."""
        return len(self.df_mitarbeitende)

    # Optional: Teilnehmerliste
    """
    def get_teilnehmerliste(self):
        '''Gibt eine Übersichtstabelle aller gültigen Teilnehmer zurück.'''
        return self.df_valid[[
            config.COLUMN_VORNAME,
            config.COLUMN_NACHNAME,
            config.COLUMN_EMAIL,
            config.COLUMN_STUDIENGANG_CLEAN,
            config.COLUMN_ABSCHLUSSART,
            config.COLUMN_SEMESTER
        ]]
    """
