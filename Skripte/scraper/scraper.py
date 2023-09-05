import pandas as pd
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from Skripte.scraper import tools


class Scraper:
    schema = "jobs"
    tabelle = "rohdaten"
    schema_tabelle = f"{schema}.{tabelle}"

    # driver = None

    def __init__(self, jobtitel, suchort="Deutschland", anzahl_seiten=10):
        self.anzahl_seiten = anzahl_seiten
        self.jobtitel = jobtitel
        self.suchort = suchort
        self.con = tools.connect_db()
        self.scraper_name = "not set"

    def open_browser(self, scraper_name):
        tools.schreibe_log_file(
            scraper_name, f"{self.scraper_name} : Suche nach {self.jobtitel} in {self.suchort}"
        )

        # ChromeOptions erstellen
        chrome_options = webdriver.ChromeOptions()
        # Headless-Modus aktivieren
        # chrome_options.add_argument("--headless")

        # Browserfenster öffnen nach Einstellung in den Optionen
        try:
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=chrome_options,
            )
            tools.wartezeit(2, 3)  # Wartezeit das Browser geladen ist
            tools.schreibe_log_file(scraper_name, f"{self.scraper_name} : Browser geoeffnet")
        except:
            tools.schreibe_log_file(
                scraper_name, f"{self.scraper_name} : Browser konnte nicht geoeffnet werden"
            )
            tools.schreibe_e_mail(
                scraper_name, f'{self.scraper_name} : Browser konnte nicht geoeffnet werden: -- {datetime.datetime.now().strftime("%d.%m.%Y, %H:%M:%S")} --',
            )

    def close_browser(self):
        # Schließen des Browsers
        self.driver.quit()
        tools.schreibe_log_file(self.scraper_name, f"{self.scraper_name} : Browser geschlossen")
        # time.sleep(3)

    def write_to_db(self, anzeigen):
        ## Daten in die Datenbank einfügen
        # Schreibe den bereinigten DataFrame in die Datenbank
        try:
            anzeigen.to_sql(
                name=self.tabelle,
                schema=self.schema,
                con=self.con,
                if_exists="append",
                index=False,
            )
            tools.schreibe_log_file(

                self.scraper_name, f"{self.scraper_name} : Es wurden {len(anzeigen)} Daten von {self.scraper_name} hinzugefügt",
            )
        except:
            tools.schreibe_log_file(

                self.scraper_name, f"{self.scraper_name} : Datenbank konnte nicht gefüllt werden => Dataframe fehlt",
            )
            tools.schreibe_e_mail(

                self.scraper_name, f"{self.scraper_name} : Datenbank konnte nicht gefüllt werden => Dataframe fehlt  -- {datetime.datetime.now()} --",
            )

    def filter_bestehende_urls(self, liste):
        # Lese die bestehenden URLs aus der Datenbank
        existing_urls = pd.read_sql_query(
            f"SELECT url FROM {self.schema_tabelle} where seite='{self.scraper_name}'",
            self.con,
        )
        tools.schreibe_log_file(

            self.scraper_name,f"{ self.scraper_name} : {len(existing_urls)} in der Datenbank bereits vorhanden",
        )
        # Filtere den DataFrame, um nur neue URLs zu behalten
        return [url for url in liste if url not in existing_urls["url"].values]

    def scrape_urls(self):

       # if isinstance(self, Scraper.LinkedIn_Scraper):
           # return self.scrape_urls()
        #elif isinstance(self, Scraper.Monster_Scraper):
         #   return self.scrape_urls()
      #  elif isinstance(self, Scraper.Stepstone_Scraper):
         #   return self.scrape_urls()
       # elif isinstance(self, Scraper.Indeed_Scraper):
           # return self.scrape_urls()
        pass
    def scrape_details(self, url):
       # if isinstance(self, Scraper.LinkedIn_Scraper):
           # return self.scrape_details(url)
        #elif isinstance(self, Scraper.Monster_Scraper):
          #  return self.scrape_details(url)
       # elif isinstance(self, Scraper.Stepstone_Scraper):
         #   return self.scrape_details(url)
       # elif isinstance(self, Scraper.Indeed_Scraper):
           # return self.scrape_details(url)
        pass
    def scrape(self, scraper_name):
        """Öffnet den Browser, holt sich die URLs,
        läuft durch diese durch und speichert die Ergebnisse in der Datenbank
        """
        self.open_browser(scraper_name)

        # URL-Liste mit den Jobs erstellen
        link_liste_scraped = self.scrape_urls()
        #print(link_liste_scraped)
       # print(self)

        # überprüfen ob link_liste_scraped leer ist da evtl. der Classname geändert wurde
        if len(link_liste_scraped) == 0:
            #tools.schreibe_log_file(scraper_name, f"{self.scraper_name} : Abfrage begonnen: Jobtitel => {self.jobtitel}")
            #tools.schreibe_e_mail(scraper_name, f"{self.scraper_name} : Abfrage begonnen: Jobtitel => {self.jobtitel}\n\n Hinweis: Classenname überprüfen für alle Stellenanzeigen!")




            tools.schreibe_log_file(

                self.scraper_name, f"{self.scraper_name} : Keine Links auf gefunden: Jobtitel => {self.jobtitel}",
            )
            tools.schreibe_e_mail(

                self.scraper_name, f"{self.scraper_name} : Keine Links auf Webseite gefunden: Jobtitel => {self.jobtitel}\n\n Hinweis: Classenname überprüfen für alle Stellenanzeigen!",
            )
            return

        # Duplikate entfernen
        link_liste_scraped_ohne_duplikate = list(set(link_liste_scraped))
        tools.schreibe_log_file(

            scraper_name, f'{self.scraper_name} : Es wurden {len(link_liste_scraped) - len(link_liste_scraped_ohne_duplikate)} Duplikate in der "Link Liste" entfernt',
        )
        tools.schreibe_log_file(scraper_name, f"{self.scraper_name} : Linkliste erstellt")

        link_liste = self.filter_bestehende_urls(
            liste=link_liste_scraped_ohne_duplikate
        )
        #print(link_liste)
        ## Scrapen der einzelnen URLs
        anzeigen = pd.DataFrame(
            columns=[
                "seite",
                "seiten_inhalt_html",
                "seiten_inhalt",
                "url",
                "datum",
                "storno",
            ]
        )
        try:
            tools.schreibe_log_file(scraper_name, f"{self.scraper_name} : Abfrage begonnen")
            for url in link_liste:
                anzeige = self.scrape_details(url)
                print(anzeige)
                if anzeige is not None:
                    anzeigen = pd.concat([anzeigen, anzeige])
        except:
            tools.schreibe_log_file(scraper_name, f"{self.scraper_name} : Abfrage abgebrochen !!!")
            tools.schreibe_e_mail(

                self.scraper_name, f"{self.scraper_name} : Die Abfrage wurde abgebrochen. -- {datetime.datetime.now()} --",
            )
        tools.schreibe_log_file(scraper_name, f"{self.scraper_name} : Abfrage beendet")

        self.close_browser()
        self.write_to_db(anzeigen)
