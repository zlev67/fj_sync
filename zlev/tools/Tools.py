import hashlib

class Tools:
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
