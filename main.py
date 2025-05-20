import asyncio
import logging
import subprocess
import sys
import math

from modules.config import VIDEO_SIZE, FPS
from modules.utils import setup_logger, validate_environment
from modules.tts_module import CoquiTTS, calculate_audio_duration
from modules.keyword_extractor import extract_keywords
from modules.broll_manager import BRollManager
from modules.video_composition import compose_video
from modules.subtitle_module import generate_srt_from_audio

logger = setup_logger("MainWorkflow")

async def main():
    try:
        # Validate environment variables
        validate_environment()
        logger.info("Environment validation passed.")

        story_text = (
            "A diligent office worker arrived early to prepare for the big presentation. Throughout the day, she collaborated with her team to solve unexpected challenges. Despite the stress, they celebrated their success with laughter and coffee. By evening, everyone felt proud of their hard work and dedication."
        )
        
        # Determine max_keywords and max_clips based on story length
        word_count = len(story_text.split())
        max_keywords = max(10, word_count // 4)
        
        logger.info(f"Max keywords: {max_keywords}")

        audio_path = "./temp/output_audio.wav"
        subtitle_path = "./temp/output_subtitles.srt"
        output_video_path = "./output/final_video.mp4"

        tts = CoquiTTS()

        logger.info("Generating TTS audio...")
        success = await tts.save(story_text, audio_path)
        if not success:
            logger.error("Failed to generate TTS audio.")
            return
        
        logger.info("Generating subtitles...")
        generate_srt_from_audio(audio_path, subtitle_path)
        
        logger.info("Calculating audio duration...")
        audio_duration = calculate_audio_duration(audio_path)
        logger.info(f"Audio duration: {audio_duration} seconds")
        
        max_clips = math.ceil(max(4, audio_duration / 4))
        print(f"Max clips: {max_clips}")

        logger.info("Extracting keywords...")
        keywords = extract_keywords(story_text, max_keywords)
        logger.info(f"Extracted keywords: {keywords}")

        logger.info("Fetching B-roll clips from Pexels...")
        broll_manager = BRollManager()
        broll_clips = await broll_manager.get_clips_for_keywords(keywords, max_clips)
        logger.info(f"Selected B-roll clips: {broll_clips}")

        logger.info("Composing final video...")
        success = await compose_video(
            audio_path,
            subtitle_path,
            broll_clips,
            output_video_path,
            video_size=VIDEO_SIZE,
            fps=FPS
        )
        if success:
            logger.info(f"Video composed successfully: {output_video_path}")
        else:
            logger.error("Failed to compose video.")

    except Exception as e:
        logger.exception(f"An error occurred in the main workflow: {e}")

if __name__ == "__main__":
    asyncio.run(main())
