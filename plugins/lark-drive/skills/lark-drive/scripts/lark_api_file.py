"""Lark Drive file CRUD operations — list, meta, create, copy, move, delete."""

from typing import Optional, List, Dict, Any
from lark_api_base import LarkAPIBase


class LarkDriveFileClient(LarkAPIBase):
    """File operations: list, get meta, batch meta, create, copy, move, delete.
    All methods require 'type' param — mismatched type fails silently."""

    def list_files(
        self,
        folder_token: str,
        page_size: int = 200,
        page_token: Optional[str] = None,
        order_by: str = "EditedTime",
        direction: str = "DESC"
    ) -> Dict[str, Any]:
        """List files in a folder. Max page_size=200.

        Args:
            folder_token: Target folder token (prefix: fld).
            page_size: Items per page (max 200).
            page_token: Pagination cursor from previous response.
            order_by: Sort field — EditedTime, CreatedTime, Name.
            direction: ASC or DESC.

        Returns:
            {files: [...], next_page_token: str, has_more: bool}
        """
        params: Dict[str, Any] = {
            "folder_token": folder_token,
            "page_size": min(page_size, 200),
            "order_by": order_by,
            "direction": direction,
        }
        if page_token:
            params["page_token"] = page_token
        data = self._call_api("GET", "/drive/v1/files", params=params)
        return {
            "files": data.get("files") or [],
            "has_more": data.get("has_more", False),
            "next_page_token": data.get("next_page_token"),
        }

    def get_file_meta(self, file_token: str, file_type: str) -> Dict[str, Any]:
        """Get file metadata by token. type is mandatory.

        Args:
            file_token: File token (prefix varies by type).
            file_type: doc, docx, sheet, bitable, mindnote, file, folder.

        Returns:
            {name, token, type, parent_token, url, ...}
        """
        return self._call_api(
            "GET", f"/drive/v1/files/{file_token}",
            params={"type": file_type}
        )

    def batch_query_meta(
        self,
        request_docs: List[Dict[str, str]],
        with_url: bool = False,
        user_id_type: str = "open_id"
    ) -> Dict[str, Any]:
        """Batch get metadata for up to 200 files.

        Args:
            request_docs: [{doc_token, doc_type}], max 200 items.
            with_url: Include access URL in response.
            user_id_type: open_id, union_id, or user_id.

        Returns:
            {metas: [...], failed_list: [...]}
        """
        if len(request_docs) > 200:
            raise ValueError("batch_query_meta: max 200 items per request")
        data: Dict[str, Any] = {
            "request_docs": request_docs,
            "user_id_type": user_id_type,
        }
        if with_url:
            data["with_url"] = True
        return self._call_api("POST", "/drive/v1/metas/batch_query", data=data)

    def create_file(
        self,
        folder_token: str,
        title: str,
        file_type: str
    ) -> Dict[str, Any]:
        """Create an online document (doc/sheet/mindnote/bitable) in a folder.

        Args:
            folder_token: Parent folder token.
            title: Document title.
            file_type: doc, docx, sheet, mindnote, or bitable.

        Returns:
            {url, token, type}
        """
        return self._call_api(
            "POST", f"/drive/explorer/v2/file/{folder_token}",
            data={"title": title, "type": file_type}
        )

    def copy_file(
        self,
        file_token: str,
        name: str,
        file_type: str,
        folder_token: str
    ) -> Dict[str, Any]:
        """Copy a file to another folder. Name is required (not auto-generated).

        Args:
            file_token: Source file token.
            name: New file name (required).
            file_type: Type of the source file.
            folder_token: Destination folder token.

        Returns:
            {file: {token, name, type, parent_token, url}}
        """
        return self._call_api(
            "POST", f"/drive/v1/files/{file_token}/copy",
            data={
                "name": name,
                "type": file_type,
                "folder_token": folder_token,
            }
        )

    def move_file(
        self,
        file_token: str,
        file_type: str,
        folder_token: str
    ) -> Dict[str, Any]:
        """Move a file or folder to a new location.

        Folder move is async — response may contain task_id.
        Poll /drive/v1/files/task_check?task_id=<id> for completion.

        Args:
            file_token: File/folder token to move.
            file_type: Type of the item being moved.
            folder_token: Destination folder token.

        Returns:
            {} or {task_id: str} for folder moves (async).
        """
        return self._call_api(
            "POST", f"/drive/v1/files/{file_token}/move",
            data={"type": file_type, "folder_token": folder_token}
        )

    def delete_file(self, file_token: str, file_type: str) -> Dict[str, Any]:
        """Delete a file (moves to recycle bin).

        Folder delete is async — response contains task_id.
        Poll /drive/v1/files/task_check?task_id=<id> for completion.

        Args:
            file_token: File/folder token to delete.
            file_type: Type of item (required query param).

        Returns:
            {} or {task_id: str} for folder deletes (async).
        """
        return self._call_api(
            "DELETE", f"/drive/v1/files/{file_token}",
            params={"type": file_type}
        )
