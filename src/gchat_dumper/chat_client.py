from typing import Any, Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/chat.messages.readonly"]


class ChatClient:
    """Thin wrapper around Google Chat API using a service account."""

    def __init__(self, service_account_json: str):
        self._creds = service_account.Credentials.from_service_account_file(
            service_account_json,
            scopes=SCOPES,
        )
        self._service = build("chat", "v1", credentials=self._creds, cache_discovery=False)

    def list_spaces(self, include_dms: bool = True) -> List[Dict[str, Any]]:
        """Return a list of spaces visible to the app."""
        spaces: List[Dict[str, Any]] = []
        page_token: Optional[str] = None

        while True:
            req = self._service.spaces().list(
                pageToken=page_token,
                pageSize=1000,
            )
            resp = req.execute()
            for space in resp.get("spaces", []):
                space_type = space.get("spaceType")
                if not include_dms and space_type == "DIRECT_MESSAGE":
                    continue
                spaces.append(space)

            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        return spaces

    def list_messages(
        self,
        space_name: str,
        filter_str: Optional[str] = None,
        page_size: int = 1000,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List messages for a space; returns dict with 'messages' and 'nextPageToken'."""
        kwargs: Dict[str, Any] = {
            "parent": space_name,
            "pageSize": page_size,
            "orderBy": "ASCENDING",
        }
        if page_token:
            kwargs["pageToken"] = page_token
        if filter_str:
            kwargs["filter"] = filter_str

        req = self._service.spaces().messages().list(**kwargs)
        return req.execute()
