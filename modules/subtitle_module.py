import os
import whisper
from pydub import AudioSegment

def format_srt_time(seconds: float) -> str:
    millis = int((seconds - int(seconds)) * 1000)
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = int(seconds) // 3600
    return f"{h:02}:{m:02}:{s:02},{millis:03}"

def generate_srt_from_audio(audio_path: str, srt_path: str, model_name: str = "base"):
    # Load Whisper model
    model = whisper.load_model(model_name, device="cpu")

    # Convert audio to 16kHz mono WAV using pydub (Whisper prefers 16kHz)
    audio = AudioSegment.from_file(audio_path).set_channels(1).set_frame_rate(16000)
    temp_wav = "temp.wav"
    audio.export(temp_wav, format="wav")

    # Transcribe audio with timestamps
    result = model.transcribe(temp_wav, word_timestamps=True)

    srt_lines = []
    for i, segment in enumerate(result["segments"], 1):
        start = segment["start"]
        end = segment["end"]
        text = segment["text"].strip()

        srt_lines.append(str(i))
        srt_lines.append(f"{format_srt_time(start)} --> {format_srt_time(end)}")
        srt_lines.append(text)
        srt_lines.append("")

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))

    os.remove(temp_wav)
