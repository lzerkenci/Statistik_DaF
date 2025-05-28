"""Testskript für DataController im Statistik-DaF-Projekt.

Lädt die Daten aus der CSV-Datei und gibt statistische Auswertungen für
Studierende, Promovierende und Mitarbeitende aus.
"""

from app.controller import DataController


def main():
    """Führt den Datenimport durch und gibt Auswertungen auf der Konsole aus."""

    controller = DataController()
    controller.lade_daten()
    print("Daten erfolgreich geladen.\n")

    # Gruppengrößen
    print("Gruppengrößen:")
    print(f"Studierende   : {controller.get_anzahl_studierende()}")
    print(f"Promovierende : {controller.get_anzahl_promovierende()}")
    print(f"Mitarbeitende : {controller.get_anzahl_mitarbeitende()}")

    # Studierende
    print("\nStudiengänge (Studierende):")
    print(controller.get_studiengaenge_studierende())

    print("\nAbschlussarten (Studierende):")
    print(controller.get_abschluesse_studierende())

    print("\nSemesterverteilung (Studierende):")
    print(controller.get_semester_studierende())

    # Promovierende
    print("\nStudiengänge (Promovierende):")
    print(controller.get_studiengaenge_promovierende())

    print("\nSemesterverteilung (Promovierende):")
    print(controller.get_semester_promovierende())

    print("Gesamtübersicht:")
    for key, value in controller.get_gesamtuebersicht().items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
