import os

class LocalFiles:
    def __init(self, local_path):
        self.local_path = local_path

    def read_local_directory_tree(self):
        """
        Recursively reads all directories and files from the local disk.

        :param start_path: Path to start reading the directory tree
        :return: List of all files and directories
        """
        all_entries = []
        for root, dirs, files in os.walk(self.local_path):
            for directory in dirs:
                all_entries.append(os.path.join(root, directory))
            for file in files:
                all_entries.append(os.path.join(root, file))
        return all_entries