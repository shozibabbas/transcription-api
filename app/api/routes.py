import logging
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings
from app.schemas import (
    HealthResponse,
    UploadResponse,
    TranscriptionResponse,
    AsyncTranscriptionResponse,
    SegmentSchema,
)
from app.services.file_service import FileService
from app.services.whisper_service import WhisperService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["transcription"])


@router.post("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
    )


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio file.

    Args:
        file: Audio file (WAV, MP3, FLAC, OGG, WebM, MP4, M4A)

    Returns:
        Transcription with timestamped segments

    Raises:
        HTTPException: For validation or processing errors
    """
    upload_id = str(uuid.uuid4())

    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        FileService.validate_audio_file(file.filename, file.content_type or "")

        # Stream file to disk
        file_content = await file.read()
        temp_path, size, sha256 = FileService.stream_to_temp_file(file_content)

        logger.info(
            f"Processing upload {upload_id}: {file.filename} ({size} bytes)"
        )

        # Transcribe
        result = WhisperService.transcribe(temp_path)

        # Clean up temp file
        FileService.cleanup_temp_file(temp_path)

        return TranscriptionResponse(
            id=upload_id,
            language=result["language"],
            duration_seconds=result["duration_seconds"],
            transcript=result["transcript"],
            segments=[SegmentSchema(**seg) for seg in result["segments"]],
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail="Transcription failed")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Internal server error"
        )
    finally:
        await file.close()


@router.post("/transcribe/async", response_model=AsyncTranscriptionResponse)
async def transcribe_audio_async(file: UploadFile = File(...)):
    """Queue audio file for asynchronous transcription.

    Args:
        file: Audio file (WAV, MP3, FLAC, OGG, WebM, MP4, M4A)

    Returns:
        Job ID and status for tracking the async transcription

    Raises:
        HTTPException: For validation or processing errors
    """
    job_id = str(uuid.uuid4())

    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        FileService.validate_audio_file(file.filename, file.content_type or "")

        # Stream file to disk
        file_content = await file.read()
        temp_path, size, sha256 = FileService.stream_to_temp_file(file_content)

        logger.info(
            f"Queued async transcription job {job_id}: {file.filename} ({size} bytes)"
        )

        # TODO: Queue for background processing
        # In a full implementation, this would:
        # 1. Store job metadata in a database
        # 2. Queue the transcription task to a background worker
        # 3. Return immediately with the job_id

        return AsyncTranscriptionResponse(
            job_id=job_id,
            status="queued",
            message="Job queued for processing",
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Internal server error"
        )
    finally:
        await file.close()


@router.post("/upload", response_model=UploadResponse)
async def upload_audio_file(file: UploadFile = File(...)):
    """Upload and validate audio file without transcribing.

    Args:
        file: Audio file

    Returns:
        Upload metadata and temporary file path

    Raises:
        HTTPException: For validation errors
    """
    upload_id = str(uuid.uuid4())

    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        FileService.validate_audio_file(file.filename, file.content_type or "")

        file_content = await file.read()
        temp_path, size, sha256 = FileService.stream_to_temp_file(file_content)

        return UploadResponse(
            id=upload_id,
            original_filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            extension=file.filename[file.filename.rfind(".") :],
            size_bytes=size,
            sha256=sha256,
            temp_file_path=temp_path,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Upload failed")
    finally:
        await file.close()
