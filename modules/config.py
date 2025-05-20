from dotenv import load_dotenv
import os

load_dotenv() 

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
COQUI_TTS_MODEL = 'tts_models/multilingual/multi-dataset/xtts_v2'

# Video settings
VIDEO_SIZE = (1280, 720)
FPS = 24
