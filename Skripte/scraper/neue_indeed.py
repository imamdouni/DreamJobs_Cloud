from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from datetime import datetime
from Skripte.scraper import tools


class BaseScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()  # Hier kannst du den Webdriver deiner Wahl verwenden
    def close_driver(self):
        self.driver.quit()
class Scraper(BaseScraper):
    def __init__(self, jobtitel, suchort="Deutschland", anzahl_seiten=10):
        super().__init__()
        self.jobtitel = jobtitel
        self.suchort = suchort
        self.anzahl_seiten = anzahl_seiten
class Indeed_Scraper(Scraper):
    def __init__(self, jobtitel, suchort="Deutschland", anzahl_seiten=10):
        super().__init__(
            jobtitel=jobtitel, suchort=suchort, anzahl_seiten=anzahl_seiten
        )
        self.scraper_name = "indeed"
        self.url = "https://www.indeed.de/"
    def suche_sort(self):
        # Webseite aufrufen
        self.driver.get(self.url)
        # Fenster Maximieren
        self.driver.maximize_window()  # evtl. im Headless-Modus nicht machbar
        # Cookies akzeptieren
        tools.wartezeit(0.5, 1)
        try:
            self.driver.find_element(
                By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'
            ).click()
        except:
            pass
        tools.wartezeit(0.5, 1)
        # Suchfeld Jobbezeichnung -> finden und befüllen
        try:
            suchfeld_jobtitel = self.driver.find_element(
                By.XPATH, '//*[@id="text-input-what"]'
            )
            suchfeld_jobtitel.send_keys(self.jobtitel)
            tools.wartezeit(0.5, 1)
            # Suchfeld Ort -> finden und befüllen
            suchfeld_ort = self.driver.find_element(
                By.XPATH, '//*[@id="text-input-where"]'
            )
            suchfeld_ort.send_keys(self.suchort)
            # Anfrage mit Enter/Return abschicken
            suchfeld_ort.send_keys(Keys.RETURN)
        except:
            tools.schreibe_log_file(
                self.scraper_name,
                f"Suchdaten eingeben nicht möglich: Jobtitel:-{self.jobtitel}; Suchort-{self.suchort}",
            )
            return
        tools.wartezeit(0.5, 1)
        # nach Datum sortieren
        self.driver.find_element(
            By.XPATH,
            '//*[@id="jobsearch-JapanPage"]/div/div/div[5]/div[1]/div[4]/div/div/div[1]/span[2]/a',
        ).click()
        tools.wartezeit(0.5, 1)
        # Einblendung entfernen
        try:
            self.driver.find_element(
                By.XPATH, '//*[@id="mosaic-desktopserpjapopup"]/div[1]/button'
            ).click()
        except:
            pass
        tools.wartezeit(0.5, 1)
    def scrape_urls(self):
        # Eingabemaske für Suche ausfüllen und nach Datum absteigend sortieren
        self.suche_sort()
        # Leere Liste erstellen für die Links
        link_liste_scraped = []
        ## link_liste_scraped befüllen von erster Seite
        anzeigen = self.driver.find_elements(By.CLASS_NAME, "jcs-JobTitle")
        for anzeige in anzeigen:
            link_liste_scraped.append(anzeige.get_attribute("href"))
        # auf "nächste Seite" Button klicken
        try:
            self.driver.find_element(
                By.XPATH,
                '//*[@id="jobsearch-JapanPage"]/div/div/div[5]/div[1]/nav/div[6]/a',
            ).click()
        except:
            pass
        ## von weiter Seiten die Links holen
        for i in range(self.anzahl_seiten - 1):
            anzeigen = self.driver.find_elements(By.CLASS_NAME, "jcs-JobTitle")
            for anzeige in anzeigen:
                link_liste_scraped.append(anzeige.get_attribute("href"))
            # auf "nächste Seite" Button klicken
            try:
                self.driver.find_element(
                    By.XPATH,
                    '//*[@id="jobsearch-JapanPage"]/div/div/div[5]/div[1]/nav/div[7]/a',
                ).click()
            except:
                pass
        tools.wartezeit(0.5, 1)
    def scrape_details(self, url):
        # Aufrufen einer Jobseite Seite
        try:
            self.driver.get(url)
            tools.wartezeit(1, 3)
        except:
            tools.schreibe_log_file(
                self.scraper_name, f"Fehler beim Aufrufen der URL: {url}"
            )
            return
        # Scrapen der daten
        try:
            inhalt_html = self.driver.find_element(
                By.CLASS_NAME, "jobsearch-JobComponent"
            ).get_attribute("innerHTML")
            inhalt_text = self.driver.find_element(
                By.CLASS_NAME, "jobsearch-JobComponent"
            ).text
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
            tools.schreibe_log_file(self.scraper_name, "Konnte Daten nicht extrahieren")
if __name__ == "__main__":
    jobtitel = "Data Analyst"  # Hier den gewünschten Jobtitel eintragen
    suchort = "Berlin"  # Hier den gewünschten Suchort eintragen
    anzahl_seiten = 10  # Hier die gewünschte Anzahl von Seiten eintragen
    # Die folgende Zeile bleibt unverändert, wenn du das neue Skript ausführst
    scraper_instance = Indeed_Scraper(jobtitel, suchort, anzahl_seiten)
    scraper_instance.suche_sort()
    scraper_instance.scrape_urls()
    # Loop durch die Links und Details sammeln
    for url in scraper_instance.link_liste_scraped:
        df = scraper_instance.scrape_details(url)
        if df is not None:
            # Speichere die Daten in der Datenbank oder tue, was immer du mit den Daten tun möchtest
            print("Daten erfolgreich extrahiert und gespeichert.")
    # Hier endet der Hauptteil deines Skripts
    # Entferne die folgenden Zeilen, da sie im neuen Skript nicht verwendet werden
    print("fertig")