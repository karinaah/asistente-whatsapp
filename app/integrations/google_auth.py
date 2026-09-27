from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
]


class GoogleAuthService:
    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
    ):
        self.credentials_path = Path(
            credentials_path
        )
        self.token_path = Path(
            token_path
        )

    def get_credentials(self) -> Credentials:
        credentials = None

        if self.token_path.exists():
            credentials = Credentials.from_authorized_user_file(
                str(self.token_path),
                SCOPES,
            )

        if credentials and credentials.expired:
            if credentials.refresh_token:
                credentials.refresh(Request())

        if not credentials or not credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path),
                SCOPES,
            )

            credentials = flow.run_local_server(
                port=0
            )

        self.token_path.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

        return credentials