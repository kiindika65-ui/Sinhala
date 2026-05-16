import os
import math
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment
from moviepy.editor import *

WIDTH, HEIGHT = 1080, 1920
OUT_DIR = "output"
os.makedirs(OUT_DIR, exist_ok=True)

FONT_FILE = "NotoSansSinhala-Regular.ttf"
TITLE = "Sinhala Karaoke Song"
PAGE_NAME = "World news in Sinhala"

lyrics = [
    "මගේ හිතේ ආදරේ",
    "නුඹ වෙනුවෙන් ගැයෙනවා",
    "රෑ අහසේ තරු අතරේ",
    "නුඹේ නමම ලියවෙනවා",
    "ආදරේ ආදරේ",
    "මගේ හදේ ගීතයයි",
    "නුඹ නැති මේ ජීවිතේ",
    "තනිවෙලා හඬනවා"
]

NOTES = [261, 293, 329, 349, 392, 440, 392, 349]

def sine_tone(freq, duration_ms, volume=0.35):
    sr = 44100
    t = np.linspace(0, duration_ms / 1000, int(sr * duration_ms / 1000), False)
    wave = np.sin(freq * t * 2 * math.pi)

    fade = int(sr * 0.05)
    if len(wave) > fade * 2:
        wave[:fade] *= np.linspace(0, 1, fade)
        wave[-fade:] *= np.linspace(1, 0, fade)

    audio = (wave * 32767 * volume).astype(np.int16)
    return AudioSegment(
        audio.tobytes(),
        frame_rate=sr,
        sample_width=2,
        channels=1
    )

def make_music_song(path):
    song = AudioSegment.silent(duration=0)

    for i, line in enumerate(lyrics):
        note = NOTES[i % len(NOTES)]

        melody = sine_tone(note, 900, 0.35)
        harmony = sine_tone(note / 2, 900, 0.18)
        bass = sine_tone(90, 900, 0.25)

        part = melody.overlay(harmony).overlay(bass)

        beat = AudioSegment.silent(duration=900)
        kick = sine_tone(65, 120, 0.6)
        clap = sine_tone(180, 80, 0.25)
        beat = beat.overlay(kick, position=0)
        beat = beat.overlay(clap, position=450)

        song += part.overlay(beat)

    song.export(path, format="mp3")
    return len(song) / 1000

def make_frame(text, active=True):
    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 18, 40))
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype(FONT_FILE, 46)
        lyric_font = ImageFont.truetype(FONT_FILE, 72)
        small_font = ImageFont.truetype(FONT_FILE, 36)
    except:
        title_font = ImageFont.load_default()
        lyric_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.text((60, 80), TITLE, font=title_font, fill=(255, 220, 90))
    draw.text((60, 140), PAGE_NAME, font=small_font, fill=(210, 210, 210))

    y = 700
    for line in textwrap.wrap(text, width=18):
        draw.text((80, y), line, font=lyric_font, fill=(255, 235, 60))
        y += 100

    draw.text((80, 1650), "♪ Sinhala Karaoke ♪", font=small_font, fill=(180, 180, 180))

    return img

def make_video(audio_path, video_path):
    clips = []

    for i, line in enumerate(lyrics):
        frame = make_frame(line)
        frame_path = f"{OUT_DIR}/frame_{i}.png"
        frame.save(frame_path)

        clip = ImageClip(frame_path).set_duration(0.9)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(audio_path)

    video = video.set_audio(audio)
    video.write_videofile(
        video_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

def main():
    audio_path = f"{OUT_DIR}/sinhala_song_music.mp3"
    video_path = f"{OUT_DIR}/sinhala_karaoke_song.mp4"

    print("Creating music + singing melody...")
    make_music_song(audio_path)

    print("Creating karaoke video...")
    make_video(audio_path, video_path)

    print("DONE:", video_path)

if __name__ == "__main__":
    main()
