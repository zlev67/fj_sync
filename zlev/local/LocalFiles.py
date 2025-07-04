import os
import datetime
from zlev.tools.Tools import Tools

class LocalFiles:
    def read_local_directory_tree(self, local_path):
        """
        Recursively reads all directories and files from the local disk.

        :param start_path: Path to start reading the directory tree
        :return: List of dicts with file info
        """
        all_entries = []
        for root, dirs, files in os.walk(local_path):
            root = os.path.normpath(root)
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    created_at = datetime.datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                    updated_at = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    size = os.path.getsize(file_path)
                    sha256 = Tools.calculate_sha256(file_path)
                except Exception:
                    created_at = updated_at = sha256 = ""
                    size = 0
                # Ensure all fields are not None
                name = file if file is not None else ""
                path = root if root is not None else ""
                ppath = os.path.relpath(path, local_path)
                created_at = created_at if created_at is not None else ""
                updated_at = updated_at if updated_at is not None else ""
                sha256 = sha256 if sha256 is not None else ""
                all_entries.append({
                    "name": name,
                    "path": path,
                    "ppath": ppath,
                    "ctime": created_at,
                    "mtime": updated_at,
                    "size": size,
                    "sha256": sha256
                })
        return all_entries

    @staticmethod
    def delete(file_paths):
        """
        Deletes all files in the given list of file paths.
        If a file is the last in its directory, removes the directory too (recursively up).
        :param file_paths: List of file paths to delete.
        """
        # Sort file_paths by descending path length to delete deeper files first
        file_paths = sorted(file_paths, key=lambda p: -len(p))
        deleted_dirs = set()
        for path in file_paths:
            try:
                os.remove(path)
            except Exception:
                pass
            dir_path = os.path.dirname(path)
            # Recursively remove empty parent directories
            while dir_path and os.path.isdir(dir_path):
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        deleted_dirs.add(dir_path)
                        dir_path = os.path.dirname(dir_path)
                    else:
                        break
                except Exception:
                    break
