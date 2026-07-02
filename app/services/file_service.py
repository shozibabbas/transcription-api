import hashlib
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from app.config import settings


class FileService:
    """Handles audio file validation and storage."""

    @staticmethod
    def validate_audio_file(filename: str, content_type: str) -> None:
        """Validate file extension and content type.

        Args:
            filename: Name of the uploaded file
            content_type: MIME type of the file

        Raises:
            ValueError: If file is invalid
        """
        if not filename:
            raise ValueError("Filename is required")

        extension = Path(filename).suffix.lower()

        if extension not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension: {extension}")

        if content_type not in settings.ALLOWED_CONTENT_TYPES:
            raise ValueError(f"Unsupported content type: {content_type}")

    @staticmethod
    def stream_to_temp_file(file_chunks: bytes) -> tuple[str, int, str]:
        """Stream file to temporary location and compute metadata.

        Args:
            file_chunks: File content as bytes

        Returns:
            Tuple of (temp_file_path, size_bytes, sha256_hash)

        Raises:
            ValueError: If file exceeds MAX_FILE_SIZE
        """
        temp_file = NamedTemporaryFile(delete=False, suffix=".tmp")
        sha256 = hashlib.sha256()
        size = 0

        try:
            size = len(file_chunks)

            if size > settings.MAX_FILE_SIZE:
                raise ValueError(
                    f"File size {size} exceeds maximum {settings.MAX_FILE_SIZE}"
                )

            temp_file.write(file_chunks)
            sha256.update(file_chunks)
            temp_file.close()

            return temp_file.name, size, sha256.hexdigest()

        except Exception:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)
            raise

    @staticmethod
    def get_file_metadata(file_path: str) -> dict:
        """Get file metadata including size, hash, and extension.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file metadata (filename, size_bytes, extension, sha256_hash, exists)
        """
        path = Path(file_path)
        sha256 = hashlib.sha256()

        metadata = {
            "filename": path.name,
            "exists": path.exists(),
        }

        if metadata["exists"]:
            # Get file size
            metadata["size_bytes"] = path.stat().st_size

            # Calculate hash
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)

            metadata["sha256_hash"] = sha256.hexdigest()
            metadata["extension"] = path.suffix.lower()

        return metadata

    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """Delete temporary file.

        Args:
            file_path: Path to the file to delete
        """
        if os.path.exists(file_path):
            os.remove(file_path)
