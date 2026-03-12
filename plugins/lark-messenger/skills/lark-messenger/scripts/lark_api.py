"""Lark Messenger API client. Messages, cards, media, group chats.
All methods use tenant_access_token (bot token)."""

import os
from typing import Optional, Dict, Any, List

from lark_api_base import LarkAPIBase


class LarkMessengerClient(LarkAPIBase):
    """Client for Lark IM APIs. Uses tenant_access_token (bot token)."""

    def __init__(self, access_token: str, user_open_id: str = None, user_id: str = None):
        """Initialize with tenant_access_token from MCP get_tenant_token(app_name)."""
        super().__init__(access_token=access_token, user_open_id=user_open_id or "", user_id=user_id)

    # --- Message methods ---

    def send_message(self, receive_id: str, msg_type: str, content: str,
                     receive_id_type: str = "chat_id", uuid: str = None) -> Dict[str, Any]:
        """Send message. content must be JSON-escaped string (use utils helpers)."""
        body = {"receive_id": receive_id, "msg_type": msg_type, "content": content}
        if uuid:
            body["uuid"] = uuid
        return self._call_api("POST", "/im/v1/messages",
                              data=body, params={"receive_id_type": receive_id_type})

    def reply_message(self, message_id: str, msg_type: str, content: str,
                      reply_in_thread: bool = False, uuid: str = None) -> Dict[str, Any]:
        """Reply to a message by message_id."""
        body = {"msg_type": msg_type, "content": content, "reply_in_thread": reply_in_thread}
        if uuid:
            body["uuid"] = uuid
        return self._call_api("POST", f"/im/v1/messages/{message_id}/reply", data=body)

    def list_messages(self, container_id: str, start_time: int = None, end_time: int = None,
                      container_id_type: str = "chat",
                      sort_type: str = "ByCreateTimeAsc") -> List[Dict[str, Any]]:
        """List messages in chat. Timestamps in SECONDS (not ms)."""
        params = {"container_id_type": container_id_type,
                  "container_id": container_id, "sort_type": sort_type}
        if start_time is not None:
            params["start_time"] = str(start_time)
        if end_time is not None:
            params["end_time"] = str(end_time)
        return self._fetch_all("/im/v1/messages", params=params)

    def get_message(self, message_id: str) -> Dict[str, Any]:
        """Get message by ID. Returns items array (multiple for merge_forward)."""
        return self._call_api("GET", f"/im/v1/messages/{message_id}")

    def delete_message(self, message_id: str) -> bool:
        """Delete a bot-sent message."""
        self._call_api("DELETE", f"/im/v1/messages/{message_id}")
        return True

    def get_read_users(self, message_id: str) -> List[Dict[str, Any]]:
        """Get users who read a bot-sent message. 7-day window only."""
        return self._fetch_all(f"/im/v1/messages/{message_id}/read_users")

    # --- Card methods ---

    def send_card(self, receive_id: str, card_content, receive_id_type: str = "chat_id",
                  uuid: str = None) -> Dict[str, Any]:
        """Send interactive card. card_content: dict (auto-escaped) or JSON string."""
        if isinstance(card_content, dict):
            card_content.setdefault("config", {}).setdefault("update_multi", True)
            content = json.dumps(card_content)
        else:
            content = card_content
        return self.send_message(receive_id, "interactive", content, receive_id_type, uuid)

    def update_card(self, message_id: str, card_content) -> Dict[str, Any]:
        """Update interactive card via PATCH. Max 14 days after send, 5 QPS/message."""
        if isinstance(card_content, dict):
            content = json.dumps(card_content)
        else:
            content = card_content
        return self._call_api("PATCH", f"/im/v1/messages/{message_id}",
                              data={"content": content})

    # --- Media methods ---

    def upload_image(self, image_path: str, image_type: str = "message") -> str:
        """Upload image via multipart. Returns image_key."""
        data = self._upload_multipart("/im/v1/images", image_path,
                                      {"image_type": image_type},
                                      file_field_name="image")
        return data.get("image_key")

    def upload_file(self, file_path: str, file_type: str,
                    file_name: str = None, duration: int = None) -> str:
        """Upload file via multipart. Returns file_key.

        file_type: opus|mp4|pdf|doc|xls|ppt|stream
        """
        fields = {"file_type": file_type,
                  "file_name": file_name or os.path.basename(file_path)}
        if duration:
            fields["duration"] = str(duration)
        data = self._upload_multipart("/im/v1/files", file_path, fields)
        return data.get("file_key")

    # --- Chat methods ---

    def create_chat(self, name: str = None, user_id_list: List[str] = None,
                    chat_type: str = "private", owner_id: str = None,
                    description: str = None) -> Dict[str, Any]:
        """Create group chat. Bot auto-joins as member."""
        body = {}
        if name:
            body["name"] = name
        if user_id_list:
            body["user_id_list"] = user_id_list
        if chat_type:
            body["chat_type"] = chat_type
        if owner_id:
            body["owner_id"] = owner_id
        if description:
            body["description"] = description
        return self._call_api("POST", "/im/v1/chats", data=body,
                              params={"user_id_type": "open_id"})

    def get_chat(self, chat_id: str) -> Dict[str, Any]:
        """Get chat info by chat_id."""
        return self._call_api("GET", f"/im/v1/chats/{chat_id}")

    def list_chats(self, page_size: int = 50) -> List[Dict[str, Any]]:
        """List bot's chats (not user's, since using tenant token)."""
        return self._fetch_all("/im/v1/chats", page_size=page_size)

    def search_chats(self, query: str, page_size: int = 50) -> List[Dict[str, Any]]:
        """Search chats by name. Query max 64 chars."""
        return self._fetch_all("/im/v1/chats/search",
                               params={"query": query}, page_size=page_size)

    def add_chat_members(self, chat_id: str, member_ids: List[str],
                         member_id_type: str = "open_id") -> Dict[str, Any]:
        """Add members to chat. succeed_type=1 for partial success."""
        return self._call_api(
            "POST", f"/im/v1/chats/{chat_id}/members",
            data={"id_list": member_ids},
            params={"member_id_type": member_id_type, "succeed_type": 1})

    def remove_chat_members(self, chat_id: str, member_ids: List[str],
                            member_id_type: str = "open_id") -> Dict[str, Any]:
        """Remove members from chat."""
        return self._call_api(
            "DELETE", f"/im/v1/chats/{chat_id}/members",
            data={"id_list": member_ids},
            params={"member_id_type": member_id_type})
