"""Service layer tests."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from app.services.file_service import FileService
from app.services.whisper_service import WhisperService


class TestFileService:
    """FileService unit tests."""

    def test_validate_audio_file_valid(self):
        """Test validation passes for valid audio file."""
        FileService.validate_audio_file("test.wav", "audio/wav")
        FileService.validate_audio_file("test.mp3", "audio/mpeg")

    def test_validate_audio_file_invalid_extension(self):
        """Test validation fails for unsupported extension."""
        with pytest.raises(ValueError, match="Unsupported file extension"):
            FileService.validate_audio_file("test.txt", "text/plain")

    def test_validate_audio_file_invalid_content_type(self):
        """Test validation fails for unsupported content type."""
        with pytest.raises(ValueError, match="Unsupported content type"):
            FileService.validate_audio_file("test.wav", "text/plain")

    def test_validate_audio_file_no_filename(self):
        """Test validation fails without filename."""
        with pytest.raises(ValueError, match="Filename is required"):
            FileService.validate_audio_file("", "audio/wav")

    def test_stream_to_temp_file_success(self, mock_audio_file):
        """Test streaming file to temporary location."""
        file_content = mock_audio_file.read()
        temp_path, size, sha256 = FileService.stream_to_temp_file(file_content)

        assert Path(temp_path).exists()
        assert size > 0
        assert len(sha256) == 64  # SHA256 hex string length

        FileService.cleanup_temp_file(temp_path)

    def test_stream_to_temp_file_oversized(self):
        """Test streaming fails for oversized file."""
        from app.config import settings
        # Create a file larger than MAX_FILE_SIZE
        oversized = b"x" * (settings.MAX_FILE_SIZE + 1024)
        with pytest.raises(ValueError, match="exceeds maximum"):
            FileService.stream_to_temp_file(oversized)

    def test_get_file_metadata(self, mock_audio_file):
        """Test getting file metadata."""
        file_content = mock_audio_file.read()
        temp_path, size, _ = FileService.stream_to_temp_file(file_content)

        metadata = FileService.get_file_metadata(temp_path)
        assert metadata["exists"]
        assert metadata["size_bytes"] > 0
        assert metadata["filename"]

        FileService.cleanup_temp_file(temp_path)

    def test_cleanup_temp_file(self, mock_audio_file):
        """Test cleaning up temporary file."""
        file_content = mock_audio_file.read()
        temp_path, _, _ = FileService.stream_to_temp_file(file_content)

        assert Path(temp_path).exists()
        FileService.cleanup_temp_file(temp_path)
        assert not Path(temp_path).exists()

    def test_cleanup_nonexistent_file(self):
        """Test cleanup handles nonexistent file gracefully."""
        FileService.cleanup_temp_file("/nonexistent/file.tmp")  # Should not raise


class TestWhisperService:
    """WhisperService unit tests."""

    def test_load_model(self):
        """Test model loading."""
        model = WhisperService.load_model()
        assert model is not None

    def test_load_model_singleton(self):
        """Test model loads as singleton."""
        model1 = WhisperService.load_model()
        model2 = WhisperService.load_model()
        assert model1 is model2

    def test_transcribe_missing_file(self):
        """Test transcribe fails for missing file."""
        with pytest.raises(FileNotFoundError):
            WhisperService.transcribe("/nonexistent/audio.wav")

    @pytest.mark.skipif(
        not Path("/Users/shozibsayyed/Projects/volgatest/scene_001.wav").exists(),
        reason="Real audio file not available",
    )
    def test_transcribe_real_audio(self):
        """Test transcribing real audio file."""
        audio_path = "/Users/shozibsayyed/Projects/volgatest/scene_001.wav"
        result = WhisperService.transcribe(audio_path)

        assert "language" in result
        assert "duration_seconds" in result
        assert "transcript" in result
        assert "segments" in result
        assert len(result["transcript"]) > 0
        assert len(result["segments"]) > 0

        # Check segment structure
        for segment in result["segments"]:
            assert "start" in segment
            assert "end" in segment
            assert "text" in segment
            assert segment["start"] < segment["end"]

    def test_unload_model(self):
        """Test model unloading."""
        WhisperService.load_model()
        WhisperService.unload_model()
        assert WhisperService._model_instance is None


# New test cases requested
class TestWhisperServiceLoad:
    """Tests for Whisper service model loading."""

    def test_whisper_service_load(self):
        """Test that WhisperService.load_model successfully loads the model."""
        # Clean up any existing model instance
        WhisperService.unload_model()

        # Load model
        model = WhisperService.load_model()

        # Verify model was loaded
        assert model is not None
        assert WhisperService._model_instance is not None

        # Clean up
        WhisperService.unload_model()

    @patch('app.services.whisper_service.WhisperModel')
    def test_transcribe_with_mock_audio(self, mock_whisper_model):
        """Test transcription with mock audio data."""
        # Setup mock model and transcription result
        mock_model_instance = MagicMock()
        mock_whisper_model.return_value = mock_model_instance

        # Create mock segments and info object
        mock_segment1 = Mock()
        mock_segment1.start = 0.0
        mock_segment1.end = 1.5
        mock_segment1.text = "Hello world"

        mock_segment2 = Mock()
        mock_segment2.start = 1.5
        mock_segment2.end = 3.0
        mock_segment2.text = "This is a test"

        mock_info = Mock()
        mock_info.language = "en"

        # Mock the transcribe method to return segments and info
        mock_model_instance.transcribe.return_value = (
            [mock_segment1, mock_segment2],
            mock_info
        )

        # Reset the singleton to use our mock
        WhisperService._model_instance = None

        # Create a temporary audio file for testing
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(b"RIFF" + b"\x00" * 100)  # Minimal WAV-like data
            tmp_path = tmp.name

        try:
            # Call transcribe
            result = WhisperService.transcribe(tmp_path)

            # Verify result structure
            assert "language" in result
            assert "duration_seconds" in result
            assert "transcript" in result
            assert "segments" in result

            # Verify values
            assert result["language"] == "en"
            assert result["transcript"] == "Hello world This is a test"
            assert len(result["segments"]) == 2
            assert result["segments"][0]["text"] == "Hello world"
            assert result["segments"][1]["text"] == "This is a test"
            assert result["duration_seconds"] == 3.0

        finally:
            # Clean up
            import os
            os.remove(tmp_path)
            WhisperService.unload_model()

    def test_file_validation(self):
        """Test file validation for supported and unsupported formats."""
        # Test valid formats
        valid_cases = [
            ("audio.wav", "audio/wav"),
            ("music.mp3", "audio/mpeg"),
            ("song.flac", "audio/flac"),
            ("podcast.ogg", "audio/ogg"),
            ("video.m4a", "audio/x-m4a"),
        ]

        for filename, content_type in valid_cases:
            # Should not raise
            FileService.validate_audio_file(filename, content_type)

        # Test invalid extension
        with pytest.raises(ValueError, match="Unsupported file extension"):
            FileService.validate_audio_file("document.txt", "text/plain")

        # Test invalid content type
        with pytest.raises(ValueError, match="Unsupported content type"):
            FileService.validate_audio_file("audio.wav", "application/octet-stream")

        # Test empty filename
        with pytest.raises(ValueError, match="Filename is required"):
            FileService.validate_audio_file("", "audio/wav")

    def test_metadata_extraction(self, mock_audio_file):
        """Test extraction of file metadata including size and hash."""
        # Stream the mock audio file to get metadata
        file_content = mock_audio_file.read()
        temp_path, size, sha256_hash = FileService.stream_to_temp_file(file_content)

        try:
            # Extract metadata
            metadata = FileService.get_file_metadata(temp_path)

            # Verify metadata structure
            assert "filename" in metadata
            assert "exists" in metadata
            assert "size_bytes" in metadata
            assert "sha256_hash" in metadata
            assert "extension" in metadata

            # Verify metadata values
            assert metadata["exists"] is True
            assert metadata["size_bytes"] == size
            assert metadata["sha256_hash"] == sha256_hash
            assert len(metadata["sha256_hash"]) == 64  # SHA256 hex string is 64 chars
            assert metadata["extension"] == ".tmp"

            # Verify filename exists
            assert len(metadata["filename"]) > 0

        finally:
            # Clean up
            FileService.cleanup_temp_file(temp_path)
