import logging
from pathlib import Path

from app.config import settings

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

logger = logging.getLogger(__name__)


class WhisperService:
    """Handles audio transcription using Whisper model."""

    _model_instance = None

    @classmethod
    def load_model(cls):
        """Load Whisper model (lazy singleton).

        Returns:
            WhisperModel instance

        Raises:
            RuntimeError: If faster_whisper is not installed
        """
        if cls._model_instance is None:
            if WhisperModel is None:
                raise RuntimeError("faster_whisper not installed")

            logger.info(
                f"Loading Whisper model: size={settings.MODEL_SIZE}, "
                f"device={settings.DEVICE}, compute_type={settings.COMPUTE_TYPE}"
            )

            cls._model_instance = WhisperModel(
                model_size_or_path=settings.MODEL_SIZE,
                device=settings.DEVICE,
                compute_type=settings.COMPUTE_TYPE,
            )

        return cls._model_instance

    @staticmethod
    def transcribe(audio_path: str) -> dict:
        """Transcribe audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with transcription results

        Raises:
            FileNotFoundError: If audio file not found
            RuntimeError: If transcription fails
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            model = WhisperService.load_model()
            segments, info = model.transcribe(audio_path, beam_size=5)

            transcript_list = []
            segment_list = []

            for segment in segments:
                text = segment.text.strip()
                transcript_list.append(text)
                segment_list.append(
                    {
                        "start": segment.start,
                        "end": segment.end,
                        "text": text,
                    }
                )

            duration = segment_list[-1]["end"] if segment_list else 0.0

            return {
                "language": info.language,
                "duration_seconds": duration,
                "transcript": " ".join(transcript_list),
                "segments": segment_list,
            }

        except Exception as ex:
            logger.error(f"Transcription failed: {str(ex)}", exc_info=True)
            raise RuntimeError(f"Failed to transcribe audio: {str(ex)}") from ex

    @staticmethod
    def get_language(audio_path: str) -> str:
        """Detect language from audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Language code (e.g., 'en', 'es', 'fr')

        Raises:
            FileNotFoundError: If audio file not found
            RuntimeError: If language detection fails
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            model = WhisperService.load_model()
            _, info = model.transcribe(audio_path, beam_size=5)
            language = info.language or "unknown"
            logger.info(f"Detected language: {language}")
            return language

        except Exception as ex:
            logger.error(f"Language detection failed: {str(ex)}", exc_info=True)
            raise RuntimeError(f"Failed to detect language: {str(ex)}") from ex

    @staticmethod
    def unload_model():
        """Unload model to free memory."""
        WhisperService._model_instance = None
        logger.info("Whisper model unloaded")
