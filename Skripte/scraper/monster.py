from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from datetime import datetime

from Skripte.scraper import tools
from scraper import Scraper


class Monster_Scraper(Scraper):
    def __init__(self, jobtitel, suchort="Deutschland", anzahl_seiten=10):
        super().__init__(
            jobtitel=jobtitel, suchort=suchort, anzahl_seiten=anzahl_seiten
        )
        self.scraper_name = "monster"
        self.url = "https://www.monster.de/"

    def suche_sort(self):
        # Webseite aufrufen
        self.driver.get(self.url)

        ## Cookies akzeptieren
        tools.wartezeit(2, 3)
        try:
            self.driver.find_element(
                By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'
            ).click()
        except:
            pass
        tools.wartezeit(2, 3)

        # Suchfeld Jobbezeichnung -> finden und befüllen
        suchfeld_jobtitel = self.driver.find_element(
            By.XPATH, '//*[@id="horizontal-input-one-undefined"]'
        )
        suchfeld_jobtitel.send_keys(self.jobtitel)
        tools.wartezeit(2, 3)

        # Suchfeld Ort -> finden und befüllen
        suchfeld_ort = self.driver.find_element(
            By.XPATH, '//*[@id="horizontal-input-two-undefined"]'
        )
        suchfeld_ort.send_keys(self.suchort)

        # Anfrage mit Enter/Return abschicken
        tools.wartezeit(2, 3)
        #suchfeld_ort.send_keys(Keys.RETURN)
        self.driver.find_element(By.CLASS_NAME, "sc-jdUcAg").click()
        tools.wartezeit(2, 3)

        # Fenster größe verkleiner zum scrallen und damit auflisten der Stellenanzeigen
        self.driver.set_window_size(800, 600)

        # Seite für weitere Stellenanzeigen nach unten Scrollen
        for i in range(10):
            self.driver.execute_script("window.scrollBy(0, 1000);")
            tools.wartezeit(2, 3)

        # Fenster Maximieren
        self.driver.maximize_window()  # evtl. im Headless-Modus nicht machbar

    def scrape_urls(self):
        # Eingabemaske für Suche ausfüllen und nach Datum absteigend sortieren
        self.suche_sort()

        # Leere Liste erstellen für die Links
        link_liste_scraped = []

        # link_liste_scraped befüllen von erster Seite
        # alte bezeichnungen (sc-chibGv,)
        anzeigen = self.driver.find_elements(By.CLASS_NAME, "sc-gAjuZT")
        for anzeige in anzeigen:
            link_liste_scraped.append(anzeige.get_attribute("href"))

        #print(link_liste_scraped)
        return link_liste_scraped

    def scrape_details(self, url, scraper_instance=None):
        # Aufrufen einer Jobseite Seite
        try:
            self.driver.get(url)
            tools.wartezeit(2, 3)
        except:
            tools.schreibe_log_file(
                self.scraper_name, f"Fehler beim Aufrufen der URL: {url}"
            )



            return

        inhalt_classname = "main-layoutstyles__Layout-sc-1w7iv1n-0"
        #rint(inhalt_classname)
        try:
            inhalt_html = self.driver.find_element(
                By.CLASS_NAME, inhalt_classname
            ).get_attribute("innerHTML")
            inhalt_text = self.driver.find_element(By.CLASS_NAME, inhalt_classname).text

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
        except:
            tools.schreibe_log_file(
                self.scraper_name, f"Konnte Daten nicht extrahieren")

        data_list = []

        for url in scraper_instance.link_liste_scraped:
            df = scraper_instance.scrape_details(url)
        if df is not None:
            data_list.append(df)

        if data_list:
            combined_df = pd.concat(data_list, ignore_index=True)
            # Speichere die Daten in der Datenbank oder tue, was immer du mit den Daten tun möchtest
        print("Daten erfolgreich extrahiert und gespeichert.")

    def scrape(self):
        super().scrape(self.scraper_name)



