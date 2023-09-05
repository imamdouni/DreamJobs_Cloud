from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from datetime import datetime

from Skripte.scraper import tools
from scraper import Scraper


class Linkedin_Scraper(Scraper):
    def __init__(self, jobtitel, suchort="Deutschland", anzahl_seiten=10):
        super().__init__(
            jobtitel=jobtitel, suchort=suchort, anzahl_seiten=anzahl_seiten
        )
        self.scraper_name = "linkedin"
        self.url = "https://de.linkedin.com/jobs/search?keywords=&location=&geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"

    # Da LinkedIn (zwecks Erkennung auf Bot´s) gerne eine Anmeldung möchte diese Abfangen
    def anmeldemaske_finden(self):
        # Anmeldemaske finden und text Abspeichern
        try:
            return (
                self.driver.find_element(
                    By.CLASS_NAME, "authwall-join-form__title"
                ).text
                == "Mitglied werden"
            )
        except:
            return False

    def suche_sort(self):
        # Webseite aufrufen
        self.driver.get(self.url)

        # Fenster Maximieren
        self.driver.maximize_window()  # evtl. im Headless-Modus nicht machbar

        # Cookies akzeptieren
        tools.wartezeit(5, 10)
        self.driver.find_element(
            By.XPATH,
            '//*[@id="artdeco-global-alert-container"]/div/section/div/div[2]/button[1]',
        ).click()
        tools.wartezeit(5, 10)

        if self.anmeldemaske_finden():
            tools.schreibe_log_file(self.scraper_name, "als Bot erkannt")
            # Schließen des Browsers
            self.driver.quit()
            tools.schreibe_log_file(self.scraper_name, "Browser geschlossen")
            return

        # Suchfeld Jobbezeichnung -> finden und befüllen
        suchfeld_jobtitel = self.driver.find_element(
            By.XPATH, '//*[@id="job-search-bar-keywords"]'
        )
        suchfeld_jobtitel.send_keys(
            self.jobtitel
        )  # "jobtitel" wird an die Funktion übergeben
        tools.wartezeit(5, 10)

        # Suchfeld Ort -> finden und befüllen
        suchfeld_ort = self.driver.find_element(
            By.XPATH, '//*[@id="job-search-bar-location"]'
        )
        suchfeld_ort.clear()
        tools.wartezeit(5, 10)
        suchfeld_ort.send_keys(self.suchort)  # "suchort" wird an die Funktion übergeben
        tools.wartezeit(5, 10)

        # Anfrage mit Enter/Return abschicken
        suchfeld_ort.send_keys(Keys.RETURN)
        tools.wartezeit(5, 10)

        # Überprüfen ob der Suchort noch mit der Eingabe übereinstimmt
        try:
            jobtitel_feld = self.driver.find_element(
                By.XPATH, '//*[@id="job-search-bar-keywords"]'
            ).get_attribute("value")
            suchort_feld = self.driver.find_element(
                By.XPATH, '//*[@id="job-search-bar-location"]'
            ).get_attribute("value")
        except:
            tools.schreibe_log_file(self.scraper_name, "als Bot erkannt")
            return

        if suchort_feld != self.suchort or jobtitel_feld != self.jobtitel:
            tools.schreibe_log_file(
                self.scraper_name,
                f"Der Suchort oder Jobtitel wurde von LinkedIn abgeaendert, evtl. wurden wir als BOT erkannt!!!",
            )
            tools.schreibe_e_mail(
                self.scraper_name,
                f'Der Suchort oder Jobtitel wurde von LinkedIn abgeaendert, evtl. wurden wir als BOT erkannt!!!\n\n>>>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<<<\n\nJobtitel: {self.jobtitel}\nSuchort: {self.suchort}\n\nAutomatisch abgeändert in:\nJobtitel: {jobtitel_feld}\nSuchort: {suchort_feld}',
            )
            tools.wartezeit(5, 10)
            self.driver.quit()
            tools.schreibe_log_file(self.scraper_name, "Browser geschlossen")
            return

        # Log-In Fenster entfernen
        self.driver.find_element(By.XPATH, "/html/body/div[3]/button").click()
        tools.wartezeit(5, 10)

        # Seite für weitere Stellenanzeigen nach unten Scrollen
        for i in range(6):
            self.driver.execute_script(
                "window.scrollBy(0, document.body.scrollHeight);"
            )
            tools.wartezeit(5, 10)

    def scrape_urls(self):
        # Eingabemaske für Suche ausfüllen und nach Datum absteigend sortieren
        try:
            self.suche_sort()
        except:
            return []

        # Leere Liste erstellen für die Links
        link_liste_scraped = []

        anzeigen = self.driver.find_elements(By.CLASS_NAME, "base-card__full-link")

        for anzeige in anzeigen:
            link_liste_scraped.append(anzeige.get_attribute("href"))

        return link_liste_scraped

    def scrape_details(self, url):
        # Aufrufen einer Jobseite Seite
        try:
            self.driver.get(url)
            tools.wartezeit(5, 10)
        except:
            tools.schreibe_log_file(
                self.scraper_name, f"Fehler beim Aufrufen der URL: {url}"
            )
            return

        if self.anmeldemaske_finden():
            return

        # Angaben erweitern
        try:
            self.driver.find_element(
                By.XPATH,
                '//*[@id="main-content"]/section[1]/div/div/section[1]/div/div/section/button[1]',
            ).click()
        except:
            pass
        tools.wartezeit(5, 10)

        # Scrapen der daten
        try:
            inhalt_html = self.driver.find_element(
                By.CLASS_NAME, "details"
            ).get_attribute("innerHTML")
            inhalt_text = self.driver.find_element(By.CLASS_NAME, "details").text

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

    def scrape(self):
        super().scrape(self.scraper_name)