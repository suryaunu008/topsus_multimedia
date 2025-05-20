import asyncio
from typing import AsyncGenerator, Dict
import torch
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

def calculate_audio_duration(audio_path: str) -> float:
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0  # Convert milliseconds to seconds
    except Exception as e:
        print(f"Error calculating audio duration: {e}")
        return 0.0

class CoquiTTS:
    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            # Add all required classes to safe globals to allow model loading
            torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])
            self.tts = TTS(model_name).to(self.device)
        except Exception as e:
            print(f"Error initializing Coqui TTS model: {e}")
            self.tts = None

    async def save(self, text: str, audio_path: str, language: str = "en", speaker: str = "Aaron Dreschner") -> bool:
        if not self.tts:
            print("TTS model not initialized.")
            return False
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.tts.tts_to_file(text=text, file_path=audio_path, language=language, speaker=speaker)
            )
            return True
        except Exception as e:
            print(f"Error generating TTS audio: {e}")
            return False

    async def stream(self, text: str) -> AsyncGenerator[Dict, None]:
        for word in text.split():
            await asyncio.sleep(0)
            yield {'type': 'WordBoundary', 'text': word, 'offset': 0}
