import pandas as pd
import re
from app import config

class DataController:
    """Verwaltet das Einlesen, Filtern und Auswerten der DaF-Teilnehmerdaten."""

    def __init__(self):
        self.df_raw = pd.DataFrame()
        self.df_valid = pd.DataFrame()
        self.df_split = pd.DataFrame()
        self.df_studierende = pd.DataFrame()
        self.df_tu_studierende = pd.DataFrame()
        self.df_hbk_studierende = pd.DataFrame()
        self.df_promovierende = pd.DataFrame()
        self.df_mitarbeitende = pd.DataFrame()

    def lade_daten(self):
        # CSVs laden
        alle_dfs = []
        for path in config.DATA_PATHS:
            df = pd.read_csv(path, sep=";")
            alle_dfs.append(df)
        self.df_raw = pd.concat(alle_dfs, ignore_index=True)

        # Gültige autor-Einträge mit Name
        self.df_valid = self.df_raw[
            self.df_raw[config.COLUMN_VORNAME].notna() &
            self.df_raw[config.COLUMN_NACHNAME].notna() &
            (self.df_raw[config.COLUMN_STATUS] == "autor")
        ].copy()

        # ID anlegen
        self.df_valid["person_id"] = self.df_valid[config.COLUMN_EMAIL].str.strip().str.lower()

        # Splitten der Studiengänge
        self.df_split = self.df_valid.copy()
        self.df_split["Studiengang_gesplittet"] = self.df_split[config.COLUMN_STUDIENGANG].str.split(";")
        self.df_split = self.df_split.explode("Studiengang_gesplittet")
        self.df_split = self.df_split[
            self.df_split["Studiengang_gesplittet"].notna() &
            (self.df_split["Studiengang_gesplittet"].str.strip() != "")
        ]

        def ist_y_nummer(val):
            # Prüft, ob Benutzername wie "y12345", "y123456" etc. ist
            return isinstance(val, str) and re.fullmatch(r"y\d{5,8}", val.strip()) is not None

        # Parsing Studiengang-Abschluss-Semester
        def parse_studiengang(zeile):
            if pd.isna(zeile):
                return pd.Series(["", "", ""])
            teile = [t.strip() for t in zeile.split(",")]
            if len(teile) == 4:
                return pd.Series([f"{teile[0]}, {teile[1]}", teile[2], teile[3]])
            elif len(teile) == 3:
                return pd.Series([teile[0], teile[1], teile[2]])
            return pd.Series(["", "", ""])
        self.df_split[[config.COLUMN_STUDIENGANG_CLEAN, config.COLUMN_ABSCHLUSSART, config.COLUMN_SEMESTER]] = \
            self.df_split["Studiengang_gesplittet"].apply(parse_studiengang)
        for col in [config.COLUMN_STUDIENGANG_CLEAN, config.COLUMN_ABSCHLUSSART, config.COLUMN_SEMESTER]:
            self.df_split[col] = self.df_split[col].str.strip()

        # ---- Gruppen filtern ----

        # Promovierende: Abschlussart enthält Promotion
        self.df_promovierende = self.df_split[
            self.df_split[config.COLUMN_ABSCHLUSSART].str.contains("Promotion", case=False, na=False)
        ]
        ids_promovierende = set(self.df_promovierende["person_id"].drop_duplicates())

        # HBK-Studierende: E-Mail @hbk (NICHT Promovierende)
        self.df_hbk_studierende = self.df_valid[
            self.df_valid[config.COLUMN_EMAIL].str.contains("@hbk", case=False, na=False) &
            ~self.df_valid["person_id"].isin(ids_promovierende)
        ]
        ids_hbk = set(self.df_hbk_studierende["person_id"].drop_duplicates())

        # TU-Studierende: Kein @hbk, Studiengang vorhanden/nicht vorhanden, NICHT Promovierende
        # --- TU-Studierende (mit oder ohne Studiengang, aber mit y-Nummer) ---
        # 1. Mit Studiengang (schon im Split)
        tu_mit_studiengang = self.df_split[
            ~self.df_split[config.COLUMN_EMAIL].str.contains("@hbk", case=False, na=False) &
            self.df_split[config.COLUMN_BENUTZERNAME].apply(ist_y_nummer) &
            ~self.df_split["person_id"].isin(ids_promovierende) &
            ~self.df_split["person_id"].isin(ids_hbk)
            ]

        # 2. Ohne Studiengang, aber mit y-Nummer (aus df_valid!)
        tu_ohne_studiengang = self.df_valid[
            ~self.df_valid[config.COLUMN_EMAIL].str.contains("@hbk", case=False, na=False) &
            self.df_valid[config.COLUMN_BENUTZERNAME].apply(ist_y_nummer) &
            (
                    self.df_valid[config.COLUMN_STUDIENGANG].isna() |
                    (self.df_valid[config.COLUMN_STUDIENGANG].str.strip() == "") |
                    (self.df_valid[config.COLUMN_STUDIENGANG].str.strip().str.lower() == "keine angabe")
            ) &
            ~self.df_valid["person_id"].isin(ids_promovierende) &
            ~self.df_valid["person_id"].isin(ids_hbk)
            ]

        self.df_tu_studierende = pd.concat([tu_mit_studiengang, tu_ohne_studiengang]).drop_duplicates(subset=["person_id"])
        ids_tu = set(self.df_tu_studierende["person_id"])
        # Gesamt: Studierende = alle IDs aus TU, HBK, Promotion
        ids_alle_studierende = ids_tu.union(ids_hbk).union(ids_promovierende)
        self.df_studierende = self.df_valid[self.df_valid["person_id"].isin(ids_alle_studierende)]

        # Mitarbeitende: Kein @hbk, Studiengang leer/na, nicht Promovierende
        self.df_mitarbeitende = self.df_valid[
            ~self.df_valid[config.COLUMN_EMAIL].str.contains("@hbk", case=False, na=False) &
            (
                self.df_valid[config.COLUMN_STUDIENGANG].isna() |
                (self.df_valid[config.COLUMN_STUDIENGANG].str.strip() == "")
            ) &
            ~self.df_valid[config.COLUMN_BENUTZERNAME].apply(ist_y_nummer)
        ]

    # ------------------- Auswertungsmethoden -------------------

    def get_anzahl_tu_studierende(self):
        return self.df_tu_studierende["person_id"].drop_duplicates().nunique()

    def get_anzahl_hbk_studierende(self):
        return self.df_hbk_studierende["person_id"].drop_duplicates().nunique()

    def get_anzahl_promovierende(self):
        return self.df_promovierende["person_id"].drop_duplicates().nunique()

    def get_anzahl_alle_studierende(self):
        ids_tu = set(self.df_tu_studierende["person_id"].drop_duplicates())
        ids_hbk = set(self.df_hbk_studierende["person_id"].drop_duplicates())
        ids_promo = set(self.df_promovierende["person_id"].drop_duplicates())
        return len(ids_tu.union(ids_hbk).union(ids_promo))

    def get_studiengaenge_studierende(self):
        return self.df_split[self.df_split["person_id"].isin(self.df_studierende["person_id"])][
            config.COLUMN_STUDIENGANG_CLEAN].value_counts()

    def get_abschluesse_studierende(self):
        df_unique = self.df_tu_studierende.drop_duplicates(subset=["person_id", config.COLUMN_ABSCHLUSSART])
        df_gefiltert = df_unique[df_unique[config.COLUMN_ABSCHLUSSART].isin(config.GUELTIGE_ABSCHLUSSARTEN)]
        return df_gefiltert[config.COLUMN_ABSCHLUSSART].value_counts()

    def get_semester_studierende(self):
        return self.df_split[self.df_split["person_id"].isin(self.df_studierende["person_id"])][
            config.COLUMN_SEMESTER].value_counts()

    def get_studiengaenge_promovierende(self):
        return self.df_promovierende[config.COLUMN_STUDIENGANG_CLEAN].value_counts()

    def get_semester_promovierende(self):
        return self.df_promovierende[config.COLUMN_SEMESTER].value_counts()

    def get_anzahl_mitarbeitende(self):
        return self.df_mitarbeitende["person_id"].drop_duplicates().nunique()

    def setze_datenbasis(self, df):
        self.df_valid = df

    def get_gesamtuebersicht(self):
        uebersicht = {
            "Teilnehmer:innen (gesamt)": len(self.df_valid),
            "Studierende (gesamt)": self.get_anzahl_alle_studierende(),
            " - davon TU": self.get_anzahl_tu_studierende(),
            " - davon HBK": self.get_anzahl_hbk_studierende(),
            "Promovierende": self.get_anzahl_promovierende(),
            "Mitarbeitende": self.get_anzahl_mitarbeitende(),
        }
        return uebersicht

    # Optional: Teilnehmerliste
    # def get_teilnehmerliste(self):
    #     return self.df_valid[[config.COLUMN_VORNAME,
    #                           config.COLUMN_NACHNAME,
    #                           config.COLUMN_EMAIL,
    #                           config.COLUMN_STUDIENGANG_CLEAN,
    #                           config.COLUMN_ABSCHLUSSART,
    #                           config.COLUMN_SEMESTER]]
