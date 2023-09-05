from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from datetime import datetime

from Skripte.scraper import tools
from scraper import Scraper


class Stepstone_Scraper(Scraper):

    def __init__(self, jobtitel, suchort = "Deutschland", anzahl_seiten = 10):
        super().__init__(
            jobtitel=jobtitel, suchort=suchort, anzahl_seiten=anzahl_seiten
        )
        self.scraper_name = "stepstone"
        self.url = "https://www.stepstone.de/"

    def suche_sort(self):
        # Webseite aufrufen
        self.driver.get(self.url)

        # Fenster Maximieren
        self.driver.maximize_window()  # evtl. im Headless-Modus nicht machbar

        # Cookies akzeptieren
        tools.wartezeit(2, 3)
        self.driver.find_element(By.XPATH, '//*[@id="ccmgt_explicit_accept"]').click()
        tools.wartezeit(2, 3)

        ## Suchfelder finden, anwählen und befüllen
        # Suchfeld Jobbezeichnung -> finden und befüllen
        suchfeld_jobtitel = self.driver.find_element(
            By.XPATH, '//*[@id="stepstone-autocomplete-162"]'
        )
        suchfeld_jobtitel.send_keys(self.jobtitel)
        tools.wartezeit(2, 3)

        # Suchfeld Ort -> finden und befüllen
        suchfeld_ort = self.driver.find_element(
            By.XPATH, '//*[@id="stepstone-form-element-173-input"]'
        )
        suchfeld_ort.send_keys(self.suchort)
        tools.wartezeit(2, 3)

        # Anfrage mit Enter/Return abschicken
        suchfeld_ort.send_keys(Keys.RETURN)
        tools.wartezeit(2, 3)

        ## nach Datum sortieren
        # erst Filterfeld dann Datum klicken
        self.driver.find_element(By.CLASS_NAME, "res-1vztcyh").click()
        tools.wartezeit(2, 3)
        self.driver.find_element(By.XPATH, '//*[@id="date"]/span/span[2]').click()
        tools.wartezeit(2, 3)

    def scrape_urls(self):
        # Eingabemaske für Suche ausfüllen und nach Datum absteigend sortieren
        self.suche_sort()

        # Leere Liste erstellen für die Links
        link_liste_scraped = []

        # name für den Container der alle Stellenanzeigen enthält
        class_name_anzeige_link = "res-kyg8or"

        # name für den Container für alle URLs der einzelnen Stellenanzeigen
        # da es meherer Namen gibt, mit Schleife herausfinde welche es gibt
        for class_name in ["res-3yv1ty", "res-2cltag"]:
            if self.driver.find_elements(By.CLASS_NAME, class_name) != []:
                class_name_url_link = class_name

        ## Aus den Stellenanzeigen die Links zu den Stellenanzeigen finden und in eine Liste packen
        anzeigen = self.driver.find_elements(By.CLASS_NAME, class_name_anzeige_link)

        # in jeder Stellenanzeige die URL heraussuchen
        for anzeige in anzeigen:
            try:
                for link in anzeige.find_elements(By.CLASS_NAME, class_name_url_link):
                    link_liste_scraped.append(link.get_attribute("href"))
            except:
                tools.schreibe_log_file(
                    self.scraper_name,
                    f"Link in Anzeige auf erster Seite nicht gefunden",
                )
                continue

        # weitere Seiten aufrufen
        for i in range(self.anzahl_seiten - 1):
            # Link zur nächsten seite finden und aufrufen
            try:
                self.driver.get(
                    self.driver.find_elements(By.CLASS_NAME, "res-1w7ajks")[
                        1
                    ].get_attribute("href")
                )
            except:
                tools.schreibe_log_file(
                    self.scraper_name,
                    "Class-Name nicht gefunden für nächsten seite der Stellenanzeigen",
                )
                pass
            # Warten auf den Aufbau der Seite
            tools.wartezeit(2, 3)

            # alle Stellenanzeigen auf der seite finden
            anzeigen = self.driver.find_elements(By.CLASS_NAME, class_name_anzeige_link)

            # in jeder Stellenanzeige die URL heraussuchen
            for anzeige in anzeigen:
                for link in anzeige.find_elements(By.CLASS_NAME, class_name_url_link):
                    link_liste_scraped.append(link.get_attribute("href"))
        return link_liste_scraped

    def scrape_details(self, url):
        # Aufrufen einer Jobseite Seite
        try:
            self.driver.get(url)
            tools.wartezeit(2, 3)
        except:
            tools.schreibe_log_file(
                self.scraper_name, f"Fehler beim Aufrufen der URL: {url}"
            )

        # Prüfen ob ein bestimmter Text auf der Seite steht, der auf die nicht mehr existierende Anzeige hindeutet
        try:
            stellenanzeige_nicht_verfuegbar = (
                self.driver.find_element(
                    By.CLASS_NAME, "listing-content-provider-1qtvd67"
                ).text
                == "Diese Stellenanzeige ist nicht mehr verfügbar."
            )
        except:
            tools.schreibe_log_file(
                self.scraper_name, f"Stellenanzeige nicht mehr verfügbar:  {url}"
            )
            return

        # Falls Stellenanzeige noch existiert
        if not stellenanzeige_nicht_verfuegbar:
            inhalt_html = self.driver.find_element(
                By.CLASS_NAME, "reb-main"
            ).get_attribute("innerHTML")
            inhalt_text = self.driver.find_element(By.CLASS_NAME, "reb-main").text

            tools.schreibe_log_file(self.scraper_name, f"Daten wurden gezogen: {url}")
            d = {
                "seite": self.scraper_name,
                "seiten_inhalt_html": inhalt_html,
                "seiten_inhalt": inhalt_text,
                "url": url,
                "datum": datetime.now(),
                "storno": False,
            }
            return pd.DataFrame(data=[d])
        else:
            tools.schreibe_log_file(
                self.scraper_name, f"Stellenanzeige nicht verfügbar:  {url}"
            )
    def scrape(self):

        super().scrape(self.scraper_name)