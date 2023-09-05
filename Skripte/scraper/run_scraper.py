from Skripte.scraper import tools
from stepstone import Stepstone_Scraper
from monster import Monster_Scraper

from indeed import Indeed_Scraper
from linkedin import Linkedin_Scraper
import datetime


def scrape(scraper_name, con=None, suchort="Deutschland"):
    # falls keine Verbindung zur Datenbank angegeben ist, diese herstellen
    if con is None:
        con = tools.connect_db()

    # Suchbegriffe (jobtitel) aus DB-Tabelle ctrl_suche holen
    suchbegriffe = tools.get_suche_jobtitel(con, scraper_name="stepstone")

    #suchbegriffe = suchbegriffe[:1]
    n = suchbegriffe.shape[0]

    for i, row in suchbegriffe.iterrows():
        job = row["jobtitel"]
        print(
            f'[{datetime.datetime.now().strftime("%H:%M:%S")}] {i+1:2}/{n}: Suche nach "{job}"'
        )
        match scraper_name:
            case "stepstone":
                Stepstone_Scraper(job, suchort).scrape()
            case "indeed":
                Indeed_Scraper(job, suchort).scrape()
            case "linkedin":
                Linkedin_Scraper(job, suchort).scrape()
            case "monster":
                Monster_Scraper(job, suchort).scrape()
            case _:
                print(f"'{scraper_name}' nicht implementiert")


def run(con=None, ort="Deutschland"):
    scraper_names = ["linkedin", "monster", "stepstone", "indeed"]
    if con is None:
        con = tools.connect_db()

    for sn in scraper_names:
        scrape(sn, con=con, suchort="Deutschland")


if __name__ == "__main__":
    run()
