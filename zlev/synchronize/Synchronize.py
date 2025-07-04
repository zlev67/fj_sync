import json
import os

from zlev.local.LocalFiles import LocalFiles
from zlev.filejump.FileJumpApi import FileJumpApi
from zlev.synchronize.SyncData import SyncData
from zlev.tools.Tools import Tools


class Synchronize:
    def __init__(self):
        """
        Initializes the Synchronize class with LocalFiles and FileJumpApi instances.

        :param local_path: Path to the local directory
        :param filejump_token: Token for FileJump API authentication
        """
        self.local_files = LocalFiles()
        self.filejump_api = FileJumpApi()
        self.local_file_list = []
        self.filejump_file_list = []

    def synchronize(self):
        """
        Compares the local and FileJump file lists and synchronizes based on the strategy.

        :param strategy: Synchronization strategy. If "update_fj", updates FileJump.
        :return: Dictionary of synchronization results.
        """
        sd = SyncData.get_instance()
        local_file_list = sd.selected_local_files
        fj_file_list = sd.selected_fj_files
        direction = sd.direction
        collision_resolution = sd.collision_resolution
        delete_dest_files = sd.delete_at_destination

        in_first, in_second, in_both = self.compare_files(local_file_list, fj_file_list)
        if direction == "local_to_fj":
            if delete_dest_files:
                delete = in_second + in_both
            else:
                delete = in_second
            self.f fj.delete(delete)  # Delete files only in FileJump
            fj.upload(in_first+in_both)
        elif direction == "fj_to_local":
            local.delete(in_first + in_both)
            fj.download(in_second + in_both)
        elif direction == "both":
            fj.download(in_second + in_both)
            fj.upload(in_second + in_both)


    @staticmethod
    def compare_files(files1, files2):
        """
        Compare two lists of file dicts (with path, name, ctime/mtime, and size).
        Returns:
            in_first: files in files1 but not in files2
            in_second: files in files2 but not in files1
            in_both: files in both, but different (by size or mtime)
        """
        def file_key(entry):
            # Use relative path + name as unique key
            return (entry.get("ppath", ""), entry.get("name", ""))

        dict1 = {file_key(f): f for f in files1 or []}
        dict2 = {file_key(f): f for f in files2 or []}

        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())

        in_first = [dict1[k] for k in keys1 - keys2]
        in_second = [dict2[k] for k in keys2 - keys1]

        in_both = []
        for k in keys1 & keys2:
            f1 = dict1[k]
            f2 = dict2[k]
            # Compare by size and mtime (or ctime if mtime not available)
            size1 = f1.get("size")
            size2 = f2.get("size")
            mtime1 = f1.get("mtime")
            mtime2 = f2.get("mtime")
            sha1 = f1.get("sha256")
            sha2 = f2.get("sha256")
            if size1 != size2 or mtime1 != mtime2 or sha1 != sha2:
                in_both.append((f1, f2))
        return in_first, in_second, in_both
