"""API endpoint tests."""

import pytest
from pathlib import Path


class TestHealth:
    """Health check endpoint tests."""

    def test_health(self, client):
        """Test health endpoint returns 200 with status and version."""
        response = client.post("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert data["version"] == "1.0.0"


class TestTranscribeValidFile:
    """Test transcription with valid audio files."""

    def test_transcribe_valid_file(self, client, mock_audio_file):
        """Test transcribing a valid audio file returns transcription data."""
        response = client.post(
            "/api/transcribe",
            files={"file": ("test.wav", mock_audio_file, "audio/wav")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "language" in data
        assert "duration_seconds" in data
        assert "transcript" in data
        assert "segments" in data
        assert isinstance(data["segments"], list)


class TestTranscribeInvalidFile:
    """Test transcription with invalid file types."""

    def test_transcribe_invalid_file(self, client, mock_invalid_file):
        """Test transcribing an unsupported file type returns 400."""
        response = client.post(
            "/api/transcribe",
            files={"file": ("test.txt", mock_invalid_file, "text/plain")},
        )
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_transcribe_invalid_extension(self, client, mock_audio_file):
        """Test transcribing with unsupported extension returns 400."""
        response = client.post(
            "/api/transcribe",
            files={"file": ("test.xyz", mock_audio_file, "audio/wav")},
        )
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_transcribe_wrong_content_type(self, client, mock_audio_file):
        """Test transcribing with wrong content type returns 400."""
        response = client.post(
            "/api/transcribe",
            files={"file": ("test.wav", mock_audio_file, "text/plain")},
        )
        assert response.status_code == 400
        assert "detail" in response.json()


class TestTranscribeOversizedFile:
    """Test transcription with oversized files."""

    def test_transcribe_oversized_file(self, client, mock_oversized_file):
        """Test transcribing an oversized file returns 400 or 500."""
        response = client.post(
            "/api/transcribe",
            files={"file": ("large.wav", mock_oversized_file, "audio/wav")},
        )
        # File validation may fail at FileService.stream_to_temp_file or during transcription
        assert response.status_code in (400, 500)
        assert "detail" in response.json()


class TestTranscribeUnsupportedFormat:
    """Test transcription with unsupported audio formats."""

    def test_transcribe_unsupported_format(self, client):
        """Test transcribing with unsupported format returns 400."""
        response = client.post(
            "/api/transcribe",
            files={"file": ("test.zip", b"fake zip data", "application/zip")},
        )
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_transcribe_missing_extension(self, client, mock_audio_file):
        """Test transcribing a file with no extension returns 400."""
        response = client.post(
            "/api/transcribe",
            files={"file": ("testfile", mock_audio_file, "audio/wav")},
        )
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_transcribe_no_filename(self, client):
        """Test transcribing without filename returns 400 or 422."""
        response = client.post(
            "/api/transcribe",
            files={"file": ("", b"data", "audio/wav")},
        )
        assert response.status_code in (400, 422)


class TestRealAudio:
    """Tests with real audio file (if available)."""

    @pytest.mark.skipif(
        not Path("/Users/shozibsayyed/Projects/volgatest/scene_001.wav").exists(),
        reason="Real audio file not available",
    )
    def test_transcribe_real_audio(self, client):
        """Test transcribing real audio file returns complete transcription."""
        audio_path = Path("/Users/shozibsayyed/Projects/volgatest/scene_001.wav")

        with open(audio_path, "rb") as f:
            response = client.post(
                "/api/transcribe",
                files={"file": ("scene_001.wav", f, "audio/wav")},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["id"]
        assert data["language"]
        assert data["duration_seconds"] > 0
        assert data["transcript"]
        assert isinstance(data["segments"], list)
        if data["segments"]:
            seg = data["segments"][0]
            assert "start" in seg
            assert "end" in seg
            assert "text" in seg
