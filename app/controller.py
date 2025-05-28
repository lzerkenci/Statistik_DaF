import pandas as pd
from app import config



class DataController:
    """Verwaltet das Einlesen, Filtern und Auswerten der DaF-Teilnehmerdaten."""

    def __init__(self):
        self.df_raw = pd.DataFrame()
        self.df_valid = pd.DataFrame()
        self.df_studierende = pd.DataFrame()
        self.df_promovierende = pd.DataFrame()
        self.df_mitarbeitende = pd.DataFrame()


    def lade_daten(self):
        """Lädt und verarbeitet die CSV-Daten, filtert gültige Einträge und klassifiziert nach Gruppen."""

        # Rohdaten laden
        # self.df_raw = pd.read_csv(config.DATA_PATH, sep=";")

        """Lädt und verarbeitet mehrere CSV-Dateien aus einem Verzeichnis."""

        # Alle CSVs laden und zusammenführen
        alle_dfs = []
        for path in config.DATA_PATHS:
            df = pd.read_csv(path, sep=";")
            alle_dfs.append(df)

        self.df_raw = pd.concat(alle_dfs, ignore_index=True)


        # Nur gültige autor*innen mit Vor- und Nachnamen behalten
        self.df_valid = self.df_raw[
            self.df_raw[config.COLUMN_VORNAME].notna() &
            self.df_raw[config.COLUMN_NACHNAME].notna() &
            (self.df_raw[config.COLUMN_STATUS] == "autor")
        ].copy()

        # Eindeutige ID pro Person: wir verwenden die E-Mail-Adresse
        self.df_valid["person_id"] = self.df_valid[config.COLUMN_EMAIL].str.strip().str.lower()

        # Mitarbeitende vor dem Explode sichern (kein Studiengang angegeben)
        df_mitarbeiter_kandidaten = self.df_valid[
            self.df_valid[config.COLUMN_STUDIENGANG].isna()
        ]

        # HBK-Studierende ohne Studiengang vor dem Entfernen sichern
        df_hbk_ohne_studiengang = self.df_valid[
            self.df_valid[config.COLUMN_STUDIENGANG].isna() &
            self.df_valid[config.COLUMN_EMAIL].str.contains("@hbk", case=False, na=False)
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
            ~self.df_valid["person_id"].isin(self.df_promovierende["person_id"])
        ]

        # HBK-Studierende ohne Studiengang hinzufügen
        self.df_studierende = pd.concat([
            self.df_studierende,
            df_hbk_ohne_studiengang
        ], ignore_index=True)

        # Mitarbeitende aus ursprünglichen Kandidaten ableiten
        self.df_mitarbeitende = df_mitarbeiter_kandidaten[
            ~df_mitarbeiter_kandidaten["person_id"].isin(self.df_studierende["person_id"]) &
            ~df_mitarbeiter_kandidaten["person_id"].isin(self.df_promovierende["person_id"])
        ]


    # ------------------- Auswertungsmethoden -------------------

    def get_anzahl_studierende(self):
        """Gibt die Anzahl eindeutiger Studierender zurück."""
        return self.df_studierende["person_id"].drop_duplicates().nunique()

    def get_studiengaenge_studierende(self):
        """Gibt die Häufigkeit der Studiengänge unter Studierenden zurück."""
        return self.df_studierende[config.COLUMN_STUDIENGANG_CLEAN].value_counts()

    """
    """
    def get_abschluesse_studierende(self):
        """Zählt gültige Abschlussarten unter Studierenden."""
        df_unique = self.df_studierende.drop_duplicates(subset=["person_id", config.COLUMN_ABSCHLUSSART])
        df_gefiltert = df_unique[df_unique[config.COLUMN_ABSCHLUSSART].isin(config.GUELTIGE_ABSCHLUSSARTEN)]
        return df_gefiltert[config.COLUMN_ABSCHLUSSART].value_counts()

    """
    def get_abschluesse_studierende_genau(self):
    Zählt alle belegten Abschlüsse (auch mehrfach pro Person).
    df_gefiltert = self.df_studierende[self.df_studierende[config.COLUMN_ABSCHLUSSART].isin(config.GUELTIGE_ABSCHLUSSARTEN)]
    return df_gefiltert[config.COLUMN_ABSCHLUSSART].value_counts()
    """

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

    def get_gesamtuebersicht(self):
        """Gibt eine Gesamtübersicht aller relevanten Kennzahlen zurück."""
        uebersicht = {
            "Teilnehmer:innen (gesamt)": len(self.df_valid),
            "Studierende": self.get_anzahl_studierende(),
            "Promovierende": self.get_anzahl_promovierende(),
            "Mitarbeitende": self.get_anzahl_mitarbeitende(),
            "Studiengänge": self.df_studierende[config.COLUMN_STUDIENGANG_CLEAN].nunique(),
            "Abschlussarten": self.df_studierende[config.COLUMN_ABSCHLUSSART].nunique(),
            "Semesterangaben": self.df_studierende[config.COLUMN_SEMESTER].nunique(),
            "Studiengangseinträge": len(self.df_studierende),
        }
        return uebersicht



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
