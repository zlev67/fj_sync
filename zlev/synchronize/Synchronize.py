import hashlib
import json
import os

from zlev.local.LocalFiles import LocalFiles
from zlev.filejump.FileJumpApi import FileJumpApi


class Synchronize:
    def __init__(self, local_path, filejump_token):
        """
        Initializes the Synchronize class with LocalFiles and FileJumpApi instances.

        :param local_path: Path to the local directory
        :param filejump_token: Token for FileJump API authentication
        """

        self.local_files = LocalFiles(local_path)
        self.filejump_api = FileJumpApi()
        self.filejump_api.token = filejump_token
        self.local_file_list = []
        self.filejump_file_list = []

    def read(self):
        """
        Reads the directory trees from both local and FileJump sources.
        """
        self.local_file_list = self.local_files.read_local_directory_tree()
        self.filejump_file_list = self.filejump_api.read_directory_tree()

    @staticmethod
    def calculate_sha256(local_file):
        """
        Calculates the SHA256 hash of a file's content.

        :param local_file: Path to the file
        :return: SHA256 hash as a hexadecimal string
        """
        sha256_hash = hashlib.sha256()
        with open(local_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def upload_file(self, local_file):
        relative_path = os.path.relpath(local_file, self.local_files.local_path)
        response = self.filejump_api.post_file(local_file, None, relative_path)
        entry_id = response
        self.filejump_api.set_description(json.dumps({"SHA256": self.calculate_sha256(local_file)}), relative_path)

    def synchronize(self, strategy=None):
        """
        Compares the local and FileJump file lists and synchronizes based on the strategy.

        :param strategy: Synchronization strategy. If "update_fj", updates FileJump.
        :return: Dictionary of synchronization results.
        """
        local_set = set(self.local_file_list)
        filejump_set = set(entry['name'] for entry in self.filejump_file_list)

        only_in_local = local_set - filejump_set
        only_in_filejump = filejump_set - local_set
        in_both = local_set & filejump_set

        if strategy == "update_fj":
            # Delete files only in FileJump
            for filejump_entry in self.filejump_file_list:
                if filejump_entry['name'] in only_in_filejump:
                    self.filejump_api.delete_file(filejump_entry['id'])

            # Upload files only in local
            for local_file in only_in_local:
                relative_path = os.path.relpath(local_file, self.local_files.local_path)
                self.filejump_api.post_file(local_file, None, relative_path)

            # Update files in both if they differ
            for local_file in in_both:
                local_file_path = os.path.join(self.local_files.local_path, local_file)
                filejump_entry = next(
                    entry for entry in self.filejump_file_list if entry['name'] == local_file
                )
                if not self.files_are_equal(local_file_path, filejump_entry):
                    relative_path = os.path.relpath(local_file_path, self.local_files.local_path)
                    self.filejump_api.post_file(local_file_path, filejump_entry['parent_id'], relative_path)

        return {
            "only_in_local": list(only_in_local),
            "only_in_filejump": list(only_in_filejump),
            "updated": list(in_both)
        }