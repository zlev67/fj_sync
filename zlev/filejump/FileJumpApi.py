import json
import mimetypes
import os
import datetime

from zlev.filejump.Exceptions import FJError
from zlev.filejump.HttpRequest import HttpRequest
from zlev.tools.Tools import Tools


class FileJumpApi:
    base_url = "https://app.filejump.com/api/v1/"
    token = "79|8f7iaYg9LuaSUHiHn6aIWm0Qm2xFBHn3ORGdZ2W2be245f98"

    @staticmethod
    def set_token(token):
        FileJumpApi.token = token

    def get_data(self, query):
        """

        :return:
        :rtype:
        """


        headers = {'Content-Type': 'application/json', "Authorization": f'Bearer {self.token}'}
        request = HttpRequest( self.base_url+query, headers=headers)
        response = request.get_request()
        if response.status_code != 200:
            raise FJError(f"Failed to get data from Lava API: {response.text}")
        data = response.json()
        if not data:
            return None
        return data

    def post_file(self, file_path, parent_id, relative_path):
        """

        :return:
        :rtype:
        """
        url = "uploads"

        headers = {'accept': 'application/json',
                   "Authorization": f'Bearer {self.token}',
                   }

        request = HttpRequest( self.base_url+url, headers=headers)
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"
        creation_time = os.path.getctime(file_path)
        update_time = os.path.getmtime(file_path)
        files = {
            "file": (file_path, open(file_path, "rb"), mime_type),
        }
        data = {
            "parentId": "null",
            "relativePath": relative_path,
            "description": "my sample description",
            "created_at": str(datetime.datetime.fromtimestamp(creation_time).isoformat()),
            "updated_at": str(datetime.datetime.fromtimestamp(creation_time).isoformat()),
        }
        response = request.post_request(data=data, files=files)
        if response.status_code != 201:
            raise FJError(f"Failed to get data from Lava API: {response.text}")
        data = response.json()
        if not data:
            return None
        return data


    def get_files(self, path_id=None):
        files = list()
        if path_id:
            url = "drive/file-entries?perPage=1000&parentIds={path_id}&workspaceId=0&page={{}}".format(path_id=path_id)
        else:
            url = "drive/file-entries?perPage=1000&workspaceId=0&page={}"
        next_page = 0
        while next_page is not None:
            data = self.get_data(url.format(next_page))
            next_page = data.get("next_page", None)
            files.extend(data.get("data", None))
        return files

    def get_file(self, entry_id):
        """
        Retrieves a file from FileJump API by its ID.

        :param entry_id: ID of the file entry to retrieve
        :return: File entry data from the API
        """
        url = f"file-entries/{entry_id}"
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f'Bearer {self.token}'
        }
        request = HttpRequest(self.base_url + url, headers=headers)
        response = request.get_request()
        if response.status_code != 200:
            raise FJError(f"Failed to get file entry: {response.text}")
        return response.content

    def set_description(self, entry_id, description):
        """
        Updates the description of a file entry in FileJump API.

        :param entry_id: ID of the file entry to update
        :param description: New description for the file entry
        :return: Response data from the API
        """
        url = f"file-entries/{entry_id}"
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f'Bearer {self.token}'
        }
        data = {
            "description": description
        }
        request = HttpRequest(self.base_url + url, headers=headers)
        response = request.put_request(data=json.dumps(data))
        if response.status_code != 200:
            raise FJError(f"Failed to update description: {response.text}")
        return response.json()

    def delete_files(self, entry_ids, delete_forever=False):
        """
        Deletes file entries in FileJump API.

        :param entry_ids: List of file entry IDs to delete
        :param delete_forever: Boolean indicating whether to delete files permanently
        :return: Response data from the API
        """
        url = "file-entries"
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f'Bearer {self.token}'
        }
        data = {
            "entryIds": entry_ids,
            "deleteForever": delete_forever
        }
        request = HttpRequest(self.base_url + url, headers=headers)
        response = request.delete_request(data=json.dumps(data))
        if response.status_code != 200:
            raise FJError(f"Failed to delete files: {response.text}")
        return response.json()

    def read_directory_tree(self, path_id=None):
        """
        Recursively reads all directories and files from FileJump API.

        :param api: Instance of FileJumpApi
        :param path_id: ID of the parent directory (optional)
        :return: List of all files and directories
        """
        all_entries = []
        entries = self.get_files(path_id)
        if not entries:
            return all_entries

        for entry in entries:
            all_entries.append(entry)
            if entry.get('type') == 'folder':  # Assuming 'type' indicates file or directory
                all_entries.extend(self.read_directory_tree(entry.get('id')))

        return all_entries

    def get_file_info(self, parent_id, entry_id):
        """
        Retrieves detailed information about a file entry by its ID.

        :param entry_id: ID of the file entry to retrieve
        :return: Detailed file entry data from the API
        """
        files_info = api.get_files(parent_id)
        if files_info:
            for file in files_info:
                if file.get("id") == entry_id:
                    return file
        return None

    @staticmethod
    def delete_files_and_empty_dirs(entry_ids, api=None):
        """
        Deletes all files in the given list of FileJump entry IDs.
        If a file is the last in its directory, removes the directory too (recursively up).
        :param entry_ids: List of file entry IDs to delete.
        :param api: Optional FileJumpApi instance (for recursive folder deletion).
        """
        if not entry_ids:
            return
        if api is None:
            api = FileJumpApi()
        # Delete files
        api.delete_files(entry_ids)
        # Check for empty directories and delete them



    def download(self, files, target_dir):
        """
        Download a list of files from FileJump to the local target directory.
        :param files: List of file dicts (must contain 'id' and 'name')
        :param target_dir: Local directory to save files
        """
        for file in files:
            entry_id = file.get("id")
            name = file.get("name")
            if not entry_id or not name:
                continue
            content = self.get_file(entry_id)
            file_path = os.path.join(target_dir, name)
            with open(file_path, "wb") as f:
                f.write(content)

    def upload(self, files, parent_id=None):
        """
        Upload a list of files to FileJump.
        :param files: List of local file dicts (must contain 'path' and 'name')
        :param parent_id: Optional parent folder id in FileJump
        """
        for file in files:
            file_path = file.get("path")
            name = file.get("name")
            if not file_path or not name:
                continue
            relative_path = file.get("ppath", name)
            self.post_file(file_path, parent_id, relative_path)

if __name__ == '__main__':
    api = FileJumpApi()
    file_name = "c:\\Users\\zlev\\Downloads\\offline-export.png"
    try:
        res = api.post_file(file_name , parent_id=None, relative_path="offline-export.png")
        print(res)

        entry_id = res["fileEntry"]["id"]
        parent_id = res["fileEntry"]["parent_id"]
        file_info = api.get_file_info(parent_id, entry_id)
        desc = json.dumps(
        {
            "SHA256": Tools.calculate_sha256(file_name),
            "ctime": str(datetime.datetime.fromtimestamp(os.path.getctime(file_name))),
            "utime": str(datetime.datetime.fromtimestamp(os.path.getmtime(file_name))),
        })
        api.set_description(entry_id, desc)
        file_info2 = api.get_file_info(parent_id, entry_id)

        file = api.get_file(entry_id)
        print(file)

        files = api.read_directory_tree()
        print(files)

    except FJError as e:
        print(f"Error: {e}")