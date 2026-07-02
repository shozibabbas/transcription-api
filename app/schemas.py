from pydantic import BaseModel, Field
from typing import List, Optional


class TranscriptionRequest(BaseModel):
    """Transcription request parameters."""

    language: Optional[str] = Field(None, description="ISO 639-1 language code (e.g., 'en', 'es'). If not specified, language is auto-detected.")
    temperature: float = Field(0.0, description="Sampling temperature (0-1). Higher values increase variability.", ge=0, le=1)
    response_format: str = Field("json", description="Output format: 'json', 'text', 'srt', 'vtt', or 'verbose_json'")


class SegmentSchema(BaseModel):
    """Timestamped transcription segment."""

    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Transcribed text")


class TranscriptionResponse(BaseModel):
    """Transcription result response."""

    id: str = Field(..., description="Unique transcription ID")
    language: str = Field(..., description="Detected language code")
    duration_seconds: float = Field(..., description="Total audio duration")
    transcript: str = Field(..., description="Full transcript")
    segments: List[SegmentSchema] = Field(..., description="Timestamped segments")


class UploadResponse(BaseModel):
    """File upload response with metadata."""

    id: str = Field(..., description="Unique upload ID")
    original_filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    extension: str = Field(..., description="File extension")
    size_bytes: int = Field(..., description="File size in bytes")
    sha256: str = Field(..., description="SHA256 hash of file")
    temp_file_path: str = Field(..., description="Path to temporary file")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")


class AsyncTranscriptionResponse(BaseModel):
    """Async transcription job response."""

    job_id: str = Field(..., description="Unique job ID for async transcription")
    status: str = Field(default="queued", description="Job status")
    message: str = Field(default="Job queued for processing", description="Status message")
