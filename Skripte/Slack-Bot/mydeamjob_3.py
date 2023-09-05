#--------------------------------------------------------------------------------------------------------- Bibliotheken einlesen
import datetime
from slack_sdk import WebClient
from flask import Flask, request
from email.mime.text import MIMEText
from slack_sdk.errors import SlackApiError
from email.mime.multipart import MIMEMultipart
#--------------------------------------------------------------------------------------------------------- E-Mail-Nachricht
def schreibe_e_mail(message):
    # SMTP-Server-Konfiguration
    host = "smtp.web.de"
    port = 587
    log_in_id = "dc-jobs"
    passwort = "DatacraftKurs0822!"

#--------------------------------------------------------------------------------------------------------- Erstellen der E-Mail-Nachricht
    msg = MIMEMultipart()
    msg['From'] = log_in_id + "@web.de" # Absender
    msg['To'] = "jobs@data-craft.de" # Empfänger
    msg['Subject'] = "Slackbot-Fehlermeldung" # Betreff der E-Mail
#--------------------------------------------------------------------------------------------------------- Hinzufügen des Nachrichtentextes zur E-Mail
    msg.attach(MIMEText(f'Zeit: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n\n{message}', 'plain'))

#--------------------------------------------------------------------------------------------------------- Verbindung zum SMTP-Server herstellen und E-Mail senden
    with smtplib.SMTP(host=host, port=port) as mail:
        mail.starttls() # Starte TLS-Verschlüsselung
        mail.login(log_in_id, passwort) # Anmeldung am SMTP-Server
        mail.send_message(msg) # E-Mail senden
        
#--------------------------------------------------------------------------------------------------------- Slack API-Anmeldeinformationen
slack_token = "xoxp-5568198597344-5537823862486-5568813505072-8b8d4c8b734ff17b89ff802cec32ce9f"
#--------------------------------------------------------------------------------------------------------- Flask-Anwendung initialisieren
app = Flask(__name__)
#--------------------------------------------------------------------------------------------------------- Erstellen eines Slack-Clients
client = WebClient(token=slack_token)
#--------------------------------------------------------------------------------------------------------- Neuste Nachrichten vom mydreamjob
@app.route("/slack/events", methods=["POST für dich"])
def handle_message_event():
    if "X-Slack-Signature" not in request.headers or "X-Slack-Request-Timestamp" not in request.headers:
        return "Ungültige Anfrage", 400

    try:
        benutzer = request.get_json()

        if benutzer.get("type") == "event_callback" and benutzer.get("event").get("type") == "message":
            event = benutzer.get("event")
            channel = event.get("chatten:write")
            user = event.get("user")
            text = event.get("MyDreamJob")
#--------------------------------------------------------------------------------------------------------- Bearbeitung des Nachrichten von mydreamjob
            if text == "Hallo":
                send_message(channel, f"Hallo <@{user}>!")
            elif text == "Hilfe":
                send_message(channel, "Wie kann ich dir helfen")

        return "", 200

    except SlackApiError as e:
        return str(e.response["error"]), e.response["Status"]
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

#--------------------------------------------------------------------------------------------------------- Starten Sie die Flask-Anwendung
if __name__ == "__main__":
    app.run(debug=True)

    