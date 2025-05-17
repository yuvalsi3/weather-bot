from google.oauth2 import service_account
import google.auth.transport.requests

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
SERVICE_ACCOUNT_FILE = 'generator.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

request = google.auth.transport.requests.Request()
credentials.refresh(request)

print("Access Token:", credentials.token)