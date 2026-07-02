import pytest
from fastapi.testclient import TestClient
from io import BytesIO

from app import create_app
from app.config import Settings


@pytest.fixture
def test_config():
    """Test configuration with optimized settings for testing.

    Returns a Settings instance configured for fast test execution:
    - Smaller model size for quicker model loading
    - CPU device for CI/CD compatibility
    - Reduced MAX_FILE_SIZE for testing file validation
    """
    return Settings(
        MODEL_SIZE="base",
        DEVICE="cpu",
        COMPUTE_TYPE="int8",
        MAX_FILE_SIZE=10 * 1024 * 1024,  # 10 MB for testing
    )


@pytest.fixture
def test_settings(test_config):
    """Alias for test_config - provides backwards compatibility."""
    return test_config


@pytest.fixture
def test_app():
    """Create FastAPI app instance for testing."""
    return create_app()


@pytest.fixture
def app(test_app):
    """Alias for test_app - provides backwards compatibility."""
    return test_app


@pytest.fixture
def test_client(test_app):
    """Create test client for making HTTP requests during tests."""
    return TestClient(test_app)


@pytest.fixture
def client(test_client):
    """Alias for test_client - provides backwards compatibility."""
    return test_client


@pytest.fixture
def mock_audio_file():
    """Create a minimal mock audio file (WAV format).

    This is a valid ~1 second WAV file with silence.
    """
    # WAV header for 1 second of silence at 16kHz
    wav_data = bytes([
        # RIFF header
        0x52, 0x49, 0x46, 0x46,  # "RIFF"
        0x24, 0x00, 0x00, 0x00,  # Chunk size
        0x57, 0x41, 0x56, 0x45,  # "WAVE"
        # fmt subchunk
        0x66, 0x6d, 0x74, 0x20,  # "fmt "
        0x10, 0x00, 0x00, 0x00,  # Subchunk1Size
        0x01, 0x00,              # AudioFormat (1 = PCM)
        0x01, 0x00,              # NumChannels
        0x80, 0x3e, 0x00, 0x00,  # SampleRate (16000)
        0x00, 0x7d, 0x00, 0x00,  # ByteRate
        0x02, 0x00,              # BlockAlign
        0x10, 0x00,              # BitsPerSample
        # data subchunk
        0x64, 0x61, 0x74, 0x61,  # "data"
        0x00, 0x00, 0x00, 0x00,  # Subchunk2Size (0 for silence)
    ])
    return BytesIO(wav_data)


@pytest.fixture
def mock_oversized_file(test_settings):
    """Create a mock file that exceeds MAX_FILE_SIZE."""
    # Create file that's larger than test MAX_FILE_SIZE (10 MB)
    return BytesIO(b"x" * (test_settings.MAX_FILE_SIZE + 1024))


@pytest.fixture
def mock_invalid_file():
    """Create a mock file with invalid format."""
    return BytesIO(b"This is not an audio file")
