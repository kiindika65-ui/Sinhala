import os
import random
import textwrap
from gtts import gTTS
from moviepy.editor import *
from pydub import AudioSegment
from pydub.generators import Sine
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1920
OUT_DIR = "output"
os.makedirs(OUT_DIR, exist_ok=True)

SONG_TITLE = "Sri Lankan Karaoke Song"
PAGE_NAME = "World news in Sinhala"

lyrics_lines = [
    "මගේ හිතේ රහසක් තියෙනවා",
    "නුඹේ නමින් එය ලියවෙනවා",
    "රෑ අහසේ තරු දිලිසෙනවා",
    "නුඹ නැතිව හිත තනිවෙනවා",
    "",
    "ආදරේ මගේ සිහිනයයි",
    "නුඹ මගේ හද ගීතයයි",
    "අදත් මම බලා ඉන්නවා",
    "නුඹ ආයෙත් එන තුරුමයි",
    "",
    "වැස්ස වැටෙන මේ රාත්‍රියේ",
    "මතක ඇවිත් හිත රිදවන්නේ",
    "කියන්න බැරි හැඟුම් ගොඩක්",
    "ගීතයක් වී අද ගැයෙන්නේ"
]

def make_voice(text, path):
    tts = gTTS(text=text, lang="si")
    tts.save(path)

def make_music(path, duration_ms):
    beat = AudioSegment.silent(duration=duration_ms)

    for i in range(0, duration_ms, 600):
        tone = Sine(130).to_audio_segment(duration=180).apply_gain(-12)
        beat = beat.overlay(tone, position=i)

    for i in range(300, duration_ms, 1200):
        tone = Sine(260).to_audio_segment(duration=150).apply_gain(-18)
        beat = beat.overlay(tone, position=i)

    beat.export(path, format="mp3")

def make_text_image(text, active=False):
    img = Image.new("RGB", (WIDTH, HEIGHT), (12, 18, 35))
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("NotoSansSinhala-Regular.ttf", 64)
        font_small = ImageFont.truetype("NotoSansSinhala-Regular.ttf", 38)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((60, 80), SONG_TITLE, font=font_small, fill=(255, 220, 80))
    draw.text((60, 140), PAGE_NAME, font=font_small, fill=(180, 180, 180))

    y = 420
    wrapped = textwrap.wrap(text, width=24)

    for line in wrapped:
        color = (255, 230, 70) if active else (255, 255, 255)
        draw.text((80, y), line, font=font_big, fill=color)
        y += 90

    return img

def main():
    full_text = "\n".join([l for l in lyrics_lines if l.strip()])

    voice_path = f"{OUT_DIR}/voice.mp3"
    music_path = f"{OUT_DIR}/music.mp3"
    mixed_path = f"{OUT_DIR}/song.mp3"
    video_path = f"{OUT_DIR}/karaoke_song.mp4"

    print("Creating Sinhala voice...")
    make_voice(full_text, voice_path)

    voice = AudioSegment.from_mp3(voice_path)
    duration_ms = len(voice) + 3000

    print("Creating background music...")
    make_music(music_path, duration_ms)

    music = AudioSegment.from_mp3(music_path).apply_gain(-8)
    final_audio = music.overlay(voice.apply_gain(2))
    final_audio.export(mixed_path, format="mp3")

    print("Creating karaoke video...")

    clips = []
    clean_lines = [l for l in lyrics_lines if l.strip()]
    line_duration = max(2.5, duration_ms / 1000 / len(clean_lines))

    for line in clean_lines:
        img = make_text_image(line, active=True)
        img_path = f"{OUT_DIR}/frame_{len(clips)}.png"
        img.save(img_path)

        clip = ImageClip(img_path).set_duration(line_duration)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(mixed_path)
    video = video.set_audio(audio)

    video.write_videofile(
        video_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    print("DONE:", video_path)

if __name__ == "__main__":
    main()
