import os
import tempfile
import requests
from typing import List
from moviepy.editor import (
    VideoFileClip, concatenate_videoclips, AudioFileClip,
    CompositeVideoClip, ColorClip, TextClip
)

def parse_srt_time(time_str: str) -> float:
    try:
        hms, ms = time_str.split(',')
        h, m, s = hms.split(':')
        return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000
    except Exception:
        return 0.0
    
def create_subtitle_clip(text, start, end, video_size, fps):
    # Create the text clip (transparent background)
    txt_clip = TextClip(
        txt=text,
        fontsize=38,
        font='Arial-Bold',
        color='white',
        stroke_color='white',
        stroke_width=2,
        size=(int(video_size[0] * 0.9), None),
        method='caption',
        align='center',
        transparent=True
    ).set_position(('center', int(video_size[1] * 0.80))).set_start(start).set_end(end).set_fps(fps)

    # Create a semi-transparent black background rectangle behind the text
    bg_height = txt_clip.h + 20  # add some padding
    bg_width = txt_clip.w + 20
    bg_clip = ColorClip(size=(bg_width, bg_height), color=(0, 0, 0))
    bg_clip = bg_clip.set_opacity(0.6)  # 60% opacity
    bg_clip = bg_clip.set_position(('center', int(video_size[1] * 0.80) - 10)).set_start(start).set_end(end).set_fps(fps)

    # Composite the background and text clips
    subtitle_clip = CompositeVideoClip([bg_clip, txt_clip], size=video_size).set_start(start).set_end(end).set_fps(fps)

    return subtitle_clip

def create_subtitle_clips(subtitle_path: str, video_size: tuple, fps: int) -> List[TextClip]:
    if not os.path.exists(subtitle_path):
        print(f"Subtitle file not found: {subtitle_path}")
        return []

    subtitle_clips = []
    with open(subtitle_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = content.strip().split('\n\n')
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            time_line = lines[1]
            text_lines = lines[2:]
            start_str, end_str = time_line.split(' --> ')
            start = parse_srt_time(start_str)
            end = parse_srt_time(end_str)
            text = ' '.join(text_lines)

            txt_clip = TextClip(
                txt=text,
                fontsize=38,
                font='Arial-Bold',
                color='white',
                stroke_color='black',
                stroke_width=0.3,
                size=(int(video_size[0] * 0.9), None),
                method='caption',
                align='center'
            ).set_position(('center', int(video_size[1] * 0.80))).set_start(start).set_end(end).set_fps(fps)

            subtitle_clips.append(txt_clip)
    return subtitle_clips

async def compose_video(
    audio_path: str,
    subtitle_path: str,
    broll_clips: List[str],
    output_path: str,
    video_size=(1280, 720),
    fps=24
) -> bool:
    try:
        # Step 1: Cek dan load audio
        if not os.path.exists(audio_path):
            print(f"Audio file not found: {audio_path}")
            return False
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration

        clips = []
        temp_files = []
        num_brolls = len(broll_clips)

        # Jika tidak ada B-roll sama sekali
        if num_brolls == 0:
            blank_clip = ColorClip(size=video_size, color=(0, 0, 0), duration=audio_duration)
            clips = [blank_clip]
        else:
            target_duration = audio_duration / num_brolls

            for clip_path in broll_clips:
                try:
                    if clip_path.startswith("http://") or clip_path.startswith("https://"):
                        resp = requests.get(clip_path, stream=True, timeout=10)
                        resp.raise_for_status()
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                            for chunk in resp.iter_content(chunk_size=8192):
                                if chunk:
                                    tmp_file.write(chunk)
                            tmp_path = tmp_file.name
                        temp_files.append(tmp_path)
                        clip = VideoFileClip(tmp_path)
                    else:
                        clip = VideoFileClip(clip_path)

                    # Resize dan potong clip
                    clip = clip.resize(newsize=video_size)
                    if clip.duration > target_duration:
                        clip = clip.subclip(0, target_duration)
                    else:
                        # Jika clip terlalu pendek, extend dengan freeze frame terakhir
                        freeze = clip.to_ImageClip(duration=target_duration - clip.duration).set_fps(fps)
                        clip = concatenate_videoclips([clip, freeze])

                    clips.append(clip)
                except Exception as e:
                    print(f"Error processing B-roll clip from {clip_path}: {e}")

        # Step 2: Gabungkan semua video clips
        final_video = concatenate_videoclips(clips, method="compose")
        final_video = final_video.set_audio(audio)

        # Step 3: Tambahkan subtitle (jika ada)
        subtitle_clips = create_subtitle_clips(subtitle_path, video_size, fps)
        if subtitle_clips:
            final_video = CompositeVideoClip([final_video, *subtitle_clips])

        # Step 4: Export ke file
        final_video.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac')

        # Cleanup
        final_video.close()
        for clip in clips:
            clip.close()
        audio.close()
        for subclip in subtitle_clips:
            subclip.close()
        for tmp_file in temp_files:
            try:
                os.remove(tmp_file)
            except Exception:
                pass

        return True
    except Exception as e:
        print(f"Error composing video: {e}")
        return False