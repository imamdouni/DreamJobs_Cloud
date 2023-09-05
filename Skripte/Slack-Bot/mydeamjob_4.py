#--------------------------------------------------------------------------------------------------------- Bibliotheken aufrufen
from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)
#--------------------------------------------------------------------------------------------------------- Azure-Speicher Zugriffsinformationen
#slack_token = "xoxp-5568198597344-5537823862486-5568813505072-8b8d4c8b734ff17b89ff802cec32ce9f"
AZURE_STORAGE_CONNECTION_STRING = 'datacraft-jobs.postgres.database.azure.com'
#--------------------------------------------------------------------------------------------------------- Slash-Befehl-Endpunkt
@app.route('/jobs', methods=['POST'])
def search_jobs():
#--------------------------------------------------------------------------------------------------------- Slack-Anfrageparameter abrufen
    command = request.form.get('command')
    text = request.form.get('text')
#--------------------------------------------------------------------------------------------------------- Job-Suche durchführen
    jobs = perform_job_search(text)
#--------------------------------------------------------------------------------------------------------- Slack-Antwort vorbereiten
    response = {
        'response_type': "chatten:write",
        'text': f'Jobs für "{text}":',
        'attachments': []
    }
#--------------------------------------------------------------------------------------------------------- Jobs als Anhänge zur Antwort hinzufügen
    for job in jobs:
        attachment = {
            'title': job['Data Analyst'],
            'text': job['description'],
            'fields': [
                {
                    'title': 'Firma',
                    'value': job['company'],
                    'short': True
                },
                {
                    'title': 'Standort',
                    'value': job['location'],
                    'short': True
                }
            ]
        }
        response['attachments'].append(attachment)

    return jsonify(response)

#--------------------------------------------------------------------------------------------------------- Job-Suche durchführen (Beispiel-Implementierung)
def perform_job_search(query):
#--------------------------------------------------------------------------------------------------------- Azure Blob Service Client erstellen
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

#--------------------------------------------------------------------------------------------------------- Container und Dateien im Azure-Speicher abrufen
    container_client = blob_service_client.get_container_client('jobs')
    blob_list = container_client.list_blobs()

#--------------------------------------------------------------------------------------------------------- Jobs filtern basierend auf Beruf und Ort
    jobs = []
    for blob in blob_list:
        if blob.name.endswith('.txt'):
            job_data = blob_client.download_blob(blob).readall().decode('utf-8')
            job = parse_job_data(job_data)

            if query.lower() in job['title'].lower() and query.lower() in job['location'].lower():
                jobs.append(job)

    return jobs
#--------------------------------------------------------------------------------------------------------- Job-Daten aus dem Textinhalt parsen (Beispiel-Implementierung)
def parse_job_data(data):
    lines = data.split('\n')
    title = lines[0].strip()
    description = '\n'.join(lines[1:])
    company = 'Unknown Company'
    location = 'Unknown Location'

    return {
        'title': title,
        'description': description,
        'company': company,
        'location': location
    }
#---------------------------------------------------------------------------------------------------------  Starten
if __name__ == '__main__':
    app.run()

    