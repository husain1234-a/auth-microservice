import firebase_admin
from firebase_admin import credentials, auth
from .settings import settings

def initialize_firebase():
    if not firebase_admin._apps:
        cred_dict = {
            "type": "service_account",
            "project_id": settings.firebase_project_id,
            "private_key_id": settings.firebase_private_key_id,
            "private_key": settings.firebase_private_key.replace('\\n', '\n'),
            "client_email": settings.firebase_client_email,
            "client_id": settings.firebase_client_id,
            "auth_uri": settings.firebase_auth_uri,
            "token_uri": settings.firebase_token_uri,
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": settings.firebase_client_cert_url
        }
        
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

def get_firebase_auth():
    return auth