import smtplib, email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser
import time, datetime, random, os
import sqlalchemy
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

config_datei = "config.ini"


def get_suche_jobtitel(con, scraper_name=None):
    query = "select jobtitel from jobs.ctrl_suchbegriffe"
    if scraper_name is not None:
        query += f" where seite = '{scraper_name}'"
    return pd.read_sql(sql=query, con=con)


# E-Mail - Benachrichtigung bei Fehlern
def schreibe_e_mail(scraper, message, Subject="fehlerhaft"):
    config = configparser.ConfigParser()
    config.read(config_datei)

    # SMTP-Server-Konfiguration
    host = config["email"]["HOST"]
    port = config["email"]["PORT"]
    user = config["email"]["USER"]
    passwort = config["email"]["PASSWORD"]

    # Erstellen der E-Mail-Nachricht
    msg = MIMEMultipart()
    msg["From"] = user + "@web.de"  # Absender
    msg["To"] = "dc-jobs@web.de"  # Empfänger
    msg["Subject"] = f"{scraper} Abfrage {Subject}"  # Betreff der E-Mail

    msg.attach(
        MIMEText(message, "plain")
    )  # Hinzufügen des Nachrichtentextes zur E-Mail

    # Verbindung zum SMTP-Server herstellen und E-Mail senden
    with smtplib.SMTP(host=host, port=port) as mail:
        mail.starttls()  # Starte TLS-Verschlüsselung
        mail.login(user, passwort)  # Anmeldung am SMTP-Server
        mail.send_message(msg)  # E-Mail senden


# Log File
def schreibe_log_file(scraper, log_eintrag):
    datei = f"log-{scraper}.txt"  # Name der Log-Datei
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Überprüfen, ob die Log-Datei bereits existiert
    if not os.path.exists(datei):
        # Wenn die Log-Datei nicht existiert, wird sie erstellt und der Log-Eintrag wird hineingeschrieben
        with open(datei, "w") as file:
            file.write(f"{timestamp}, {log_eintrag}" + "\n")
    else:
        # Wenn die Log-Datei bereits existiert, wird der Log-Eintrag an das Ende der Datei angehängt
        with open(datei, "a") as file:
            file.write(f"{timestamp}, {log_eintrag}" + "\n")


def connect_db(abschnitt="postgres_azure"):
    config = configparser.ConfigParser()
    config.read(config_datei)

    # SQL-Server-Konfiguration
    db_host = config[abschnitt]["HOST"]
    db_name = config[abschnitt]["DATABASE"]
    db_user = config[abschnitt]["USER"]
    db_pw = config[abschnitt]["PASSWORD"]
    db_port = config[abschnitt]["PORT"]
    s = f"postgresql://{db_user}:{db_pw}@{db_host}:{db_port}/{db_name}"
    return sqlalchemy.create_engine(s)


def wartezeit(min_zeit=1.0, max_zeit=3.0):
    """
    Diese Funktion fügt eine zufällige Wartezeit hinzu, bevor sie fortgesetzt wird.

    Parameters
    ----------
        min_zeit (float): die minimale Wartezeit in Sekunden (Standardwert ist 1)
        max_zeit (float): die maximale Wartezeit in Sekunden (Standardwert ist 3)

    Return
    ------
        None
    """
    time.sleep(random.uniform(min_zeit, max_zeit))
