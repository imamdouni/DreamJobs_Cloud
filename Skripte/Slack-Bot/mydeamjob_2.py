#--------------------------------------------------------------------------------------------------------- Bibliotheken einführen
import smtplib
import datetime
from slack_sdk import WebClient
from email.mime.text import MIMEText
from slack_sdk.errors import SlackApiError
from email.mime.multipart import MIMEMultipart


#--------------------------------------------------------------------------------------------------------- M-ERA
#--------------------------------------------------------------------------------------------------------- E-Mail-Nachricht
def schreibe_e_mail(message):
#--------------------------------------------------------------------------------------------------------- SMTP-Server-Konfiguration
    host = "smtp.web.de"
    port = 587
    log_in_id = "dc-jobs"
    passwort = "DatacraftKurs0822!"
#--------------------------------------------------------------------------------------------------------- Erstellen der E-Mail-Nachricht
    msg = MIMEMultipart()
    msg['From'] = log_in_id + "@web.de" #----------------------------------------------------------------- Absender
    msg['To'] = "jobs@data-craft.de" #-------------------------------------------------------------------- Empfänger
    msg['Subject'] = "Slackbot-Fehlermeldung" #----------------------------------------------------------- Betreff der E-Mail
#--------------------------------------------------------------------------------------------------------- Hinzufügen des Nachrichtentextes zur E-Mail
    msg.attach(MIMEText(f'Zeit: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n\n{message}', 'plain'))
#--------------------------------------------------------------------------------------------------------- Verbindung zum SMTP-Server herstellen und E-Mail senden
    with smtplib.SMTP(host=host, port=port) as mail:
        mail.starttls() #--------------------------------------------------------------------------------- Starte TLS-Verschlüsselung
        mail.login(log_in_id, passwort) #----------------------------------------------------------------- Anmeldung am SMTP-Server
        mail.send_message(msg) #-------------------------------------------------------------------------- E-Mail senden
#--------------------------------------------------------------------------------------------------------- M-ERE

#--------------------------------------------------------------------------------------------------------- Slack API-Anmeldeinformationen
slack_token = "xoxp-5568198597344-5537823862486-5568813505072-8b8d4c8b734ff17b89ff802cec32ce9f"
#--------------------------------------------------------------------------------------------------------- Erstellen eines Slack-Clients
client = WebClient(token=slack_token)
#--------------------------------------------------------------------------------------------------------- Empfangen von Slack-Ereignissen
def receive_events(event_payload):
    event = event_payload["event"]
    channel = event["chatten:write"]
    user = event["user"]
    text = event["MyDreamjob"]
#--------------------------------------------------------------------------------------------------------- Bearbeitung der Nachricht
    if text == "Hallo":
        send_message(channel, f"Hallo <@{user}>!")
    elif text == "Hilfe":
        send_message(channel, "Wie kann ich dir helfen")
#--------------------------------------------------------------------------------------------------------- Senden einer Nachricht
def send_message(channel, text):
    try:
        response = client.chat_postMessage(channel=channel, text=text)
        if response["ok"]:
            print("Nachricht erfolgreich gesendet!")
        else:
            print("Nachricht konnte nicht gesendet werden:", response["error"])

    except SlackApiError as e:
        print("Fehler beim Senden der Nachricht:", e.response["error"])
#--------------------------------------------------------------------------------------------------------- Empfangen von Slack-Ereignissen und Verarbeiten
def process_event(event_payload):
    event_type = event_payload["type"]

    if event_type == "event_callback":
        receive_events(event_payload)
#--------------------------------------------------------------------------------------------------------- Verbindung zum Slack-Websocket herstellen und auf Ereignisse warten
def start_bot():
    try:
        response = client.rtm_connect()
        if response["ok"]:
            print("Der Bot hat sich erfolgreich verbunden!")
            while True:
                event_payload = client.rtm_read()
                if event_payload:
                    process_event(event_payload)

        else:
            print("Verbindung zum Bot ist fehlgeschlagen:", response["error"])

    except SlackApiError as e:
        print("Verbindungsfehler vom Bot:", e.response["error"])
#--------------------------------------------------------------------------------------------------------- Starten des Bots
if __name__ == "__main__":
    start_bot()