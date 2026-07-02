"""Test suite for Volga Transcription API.

This package contains all test modules and fixtures for testing the
Volga Transcription API service.

Fixtures available:
    - mock_audio_file: Valid minimal WAV audio file for testing
    - mock_oversized_file: File exceeding MAX_FILE_SIZE limit
    - mock_invalid_file: Invalid/corrupted audio file
    - test_config: Settings object with test-optimized configuration
    - test_app: FastAPI application instance for testing
    - test_client: TestClient for making HTTP requests
"""
