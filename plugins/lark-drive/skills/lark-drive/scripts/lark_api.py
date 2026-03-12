"""Lark Drive unified client — combines all domain modules via multiple inheritance."""

from lark_api_file import LarkDriveFileClient
from lark_api_upload_download import LarkDriveUploadDownloadClient
from lark_api_permission import LarkDrivePermissionClient


class LarkDriveClient(
    LarkDriveFileClient,
    LarkDriveUploadDownloadClient,
    LarkDrivePermissionClient,
):
    """Unified Lark Drive API client. 15 methods across 3 domains.

    Domains:
        File (7):      list_files, get_file_meta, batch_query_meta,
                       create_file, copy_file, move_file, delete_file
        Upload (4):    get_root_folder, create_folder, upload_file, download_file
        Permission (4):search_files, add_permission, update_permission, delete_permission

    Usage:
        client = LarkDriveClient(access_token=TOKEN, user_open_id=OPEN_ID)
        root = client.get_root_folder()
        files = client.list_files(folder_token=root["token"])
    """
    pass
