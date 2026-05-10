"""
voice_input.py — Addım 11: Mikrofon girişini mətndə çevirir
Primary: SpeechRecognition (Google pulsuz API) 
Fallback: Whisper (OpenAI, lokal model)
"""
import io

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False


def transcribe_audio_bytes(audio_bytes: bytes, language: str = "az-AZ") -> str:
    """
    Streamlit-in audio_input-dan gələn bytes-ı mətndə çevirir.
    language: "az-AZ" (Azərbaycan), "en-US" (İngilis)
    Returns: Tanınmış mətn
    """
    if not SR_AVAILABLE:
        raise RuntimeError("SpeechRecognition qurulmayıb. Terminal: pip install SpeechRecognition")

    recognizer = sr.Recognizer()

    try:
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        # Google pulsuz API
        text = recognizer.recognize_google(audio_data, language=language)
        return text

    except sr.UnknownValueError:
        return ""  # Söz tanınmadı
    except sr.RequestError as e:
        raise RuntimeError(f"Səs tanıma xətası: {e}")
    except Exception as e:
        raise RuntimeError(f"Audio emal xətası: {e}")


def get_supported_languages() -> dict:
    """Dəstəklənən dillər siyahısı."""
    return {
        "Azərbaycan": "az-AZ",
        "English": "en-US",
        "Русский": "ru-RU",
        "Türkçe": "tr-TR",
    }
