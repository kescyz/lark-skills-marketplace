"""
Lark Calendar API client.
Handles Calendar events and attendee management.
"""

from typing import Optional, Dict, Any, List
from lark_api_base import LarkAPIBase


class LarkCalendarClient(LarkAPIBase):
    """Client for Lark Calendar APIs."""

    def list_events(self, calendar_id: str, start_time_ms: int, end_time_ms: int) -> List[Dict[str, Any]]:
        """List events in calendar within time range.

        Note: Calendar API uses SECONDS, but this function accepts milliseconds
        for consistency with Task API. Conversion is done internally.
        """
        start_sec = start_time_ms // 1000
        end_sec = end_time_ms // 1000
        params = {
            "start_time": str(start_sec),
            "end_time": str(end_sec)
        }
        data = self._call_api("GET", f"/calendar/v4/calendars/{calendar_id}/events", params=params)
        return data.get("items", [])

    def create_event(self, calendar_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create calendar event. Auto-adds creator and other attendees."""
        attendees = event_data.pop("attendees", []) or []

        if self.user_id:
            creator_exists = any(
                a.get("user_id") == self.user_id or a.get("is_organizer")
                for a in attendees
            )
            if not creator_exists:
                attendees.insert(0, {"type": "user", "user_id": self.user_id})

        result = self._call_api("POST", f"/calendar/v4/calendars/{calendar_id}/events", data=event_data)

        if attendees and result.get("event", {}).get("event_id"):
            event_id = result["event"]["event_id"]
            self.add_event_attendees(calendar_id, event_id, attendees)

        return result

    def add_event_attendees(self, calendar_id: str, event_id: str, attendees: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add attendees to an existing event. Uses user_id format."""
        attendee_data = {"attendees": attendees}
        return self._call_api(
            "POST",
            f"/calendar/v4/calendars/{calendar_id}/events/{event_id}/attendees",
            data=attendee_data,
            params={"user_id_type": "user_id"}
        )

    def update_event(self, calendar_id: str, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update calendar event."""
        return self._call_api("PATCH", f"/calendar/v4/calendars/{calendar_id}/events/{event_id}", data=event_data)

    def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """Delete calendar event."""
        self._call_api("DELETE", f"/calendar/v4/calendars/{calendar_id}/events/{event_id}")
        return True
