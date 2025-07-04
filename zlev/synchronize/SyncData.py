import datetime
import json
import os

from zlev.filejump.FileJumpApi import FileJumpApi
from zlev.local.LocalFiles import LocalFiles
from zlev.tools.Tools import Tools


class SyncData:
    instance = None
    """
    A class to represent synchronization data.
    This class is used to store and manage synchronization information.
    """

    def __init__(self):
        """
        Initializes the SyncData instance with optional data.

        """
        self.selected_local_files = None
        self.local_folders = None

        self.all_fj_entries = None
        self.selected_fj_files = None
        self.all_fj_folders = None
        self.direction = None
        self.fj_folders = None
        self.collision_resolution = "overwrite"
        self.delete_at_destination = False
        SyncData.instance = self

    def set_config(self, direction, local_folders, fj_folders, fj_files):
        """
        Sets the configuration for synchronization.

        :param direction: Direction of synchronization (e.g., 'local_to_fj', 'fj_to_local').
        :param local_folders: List of local folders to be synchronized.
        :param fj_folders: List of FileJump folders to be synchronized.
        :param fj_files: List of FileJump files to be synchronized.
        """
        self.direction = direction
        self.local_folders = local_folders
        self.fj_folders = fj_folders

    def set_local(self, local_folders):
        """
        Sets the local files for synchronization.

        :param local_folders: List of local files to be synchronized.
        """
        self.selected_local_files = list()
        for folder in local_folders:
            local = LocalFiles().read_local_directory_tree(folder)
            self.selected_local_files.extend(local)

    def init_fj(self):
        """

        :return:
        :rtype:
        """
        self.all_fj_entries = FileJumpApi().read_directory_tree()
        self.set_fj_folders()

    def get_fj_folders(self):
        """
        Returns the dict of fj_folders

        :return: dict of fj_folders or an empty list if not set.
        :rtype: dict
        """
        return self.all_fj_folders

    def get_local_files(self):
        """

        :return:
        :rtype:
        """
        return self.selected_local_files

    def get_fj_files(self):
        """

        :return:
        :rtype:
        """
        return self.selected_fj_files

    def set_fj_files(self, starting_folder_list):
        """
        Returns the list of fj_files.

        :return: List of fj_files or an empty list if not set.
        :rtype: list
        """
        self.selected_fj_files = None
        if self.all_fj_entries is None or not starting_folder_list:
            return
        fj_entries = []
        dj_all_folders = self.get_fj_folders()
        for starting_folder_id in starting_folder_list:
            for entry in self.all_fj_entries:
                if (entry.get('type') != 'folder' and
                    (starting_folder_id == "0" or starting_folder_id in entry.get('path').split("/"))):
                    path = entry.get('path', '')
                    _p = path.split("/")
                    _pp = list()
                    for _e in _p:
                        if _e != str(entry["id"]):
                            if int(_e) in dj_all_folders:
                                _pp.append(dj_all_folders[int(_e)])
                            else:
                                _pp.append(_e)
                    _pp.append(entry["name"])
                    ppath = "\\".join(_pp)
                    # path = "/".join([dj_all_folders[int(_e)] for _e in entry.get('path').split("/")])
                    name = entry.get('name', '')
                    ctime = entry.get('created_at', '')
                    mtime = entry.get('updated_at', '')
                    size = entry.get('file_size', '')
                    sha256 = ""
                    desc = entry.get('description', '')
                    if desc:
                        try:
                            desc_json = json.loads(desc)
                            sha256 = desc_json.get("SHA256", "")
                            ctime = desc_json.get("ctime", "")
                            mtime = desc_json.get("utime", "")
                        except Exception:
                            pass
                    fj_entries.append({
                        "path": path,
                        "ppath":ppath,
                        "name": name,
                        "ctime": ctime,
                        "mtime": mtime,
                        "size": size,
                        "sha256": sha256
                    })
        self.selected_fj_files = fj_entries

    def set_fj_folders(self):
        self.all_fj_folders = {0: "root"}
        self.all_fj_folders.update({entry.get("id"):entry.get("name") for entry in self.all_fj_entries
                           if entry.get('type') == 'folder'})



    def save(self):
        dict_data = {
            "local_files": self.selected_local_files,
            "local_folders": self.local_folders,
            "all_fj_entries": self.all_fj_entries,
            "direction": self.direction,
            "fj_folders": self.fj_folders,
            "collision_resolution": self.collision_resolution,
            "delete_at_destination": self.delete_at_destination,
        }
        json.dump(dict_data, open("sync_data.json", "w"), indent=4)

    def restore(self):
        """
        Restores the synchronization data from a JSON file.

        :return: A SyncData instance with restored data.
        :rtype: SyncData
        """
        try:
            dict_data = json.load(open("sync_data.json", "r"))
            self.direction = dict_data.get("direction", None)
            self.fj_folders = dict_data.get("fj_folders", None)
            self.selected_local_files = dict_data.get("local_files", None)
            self.local_folders = dict_data.get("local_folders", None)
            self.all_fj_entries = dict_data.get("all_fj_entries", None)
            self.collision_resolution = dict_data.get("collision_resolution", None)
            self.delete_at_destination = dict_data.get("delete_at_destination", None)

            if all(field is None for field in [self.direction, self.selected_local_files,
                                               self.local_folders, self.all_fj_entries, self.fj_folders]):
                # All fields are None
                return False
            self.set_fj_files(self.fj_folders)
            self.set_fj_folders()
            return True
        except Exception:
            return False


    @staticmethod
    def is_backup():
        return os.path.isfile("sync_data.json")

    @staticmethod
    def get_instance():
        """
        Returns the singleton instance of SyncData.

        :return: The singleton instance of SyncData.
        :rtype: SyncData
        """
        if SyncData.instance is None:
            SyncData.instance = SyncData()
        return SyncData.instance
