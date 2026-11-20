#!/usr/bin/env python3
"""Build the GTA 6 clipper entry: vertical Short from Trailer 1's pool-gator moment.

Structure (~21s): 8s hook (animal control vs alligator, t=39.5-47.5) -> 6s action
cut (dirt bikes/robbery/drift, t=66-72) -> 7s make.fun pitch card. Trailer audio
runs under the whole clip, fading out. All cuts/overlays decided and run here.
Deterministic given the source file. Requires ffmpeg on PATH or FF below.
"""
import os
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__)) + "/"
FF = (shutil.which("ffmpeg") or r"C:/Users/ainur/AppData/Local/hermes/tools/ffmpeg-9.0.1-win32-x64/bin/ffmpeg").rsplit("ffmpeg", 1)[0]
FONT = D + "assets/fonts/"
GHOST = D + "assets/ghost.png"
SRC = D + "trailer1.mp4"
W, H = 1080, 1920
CROP_X = 436          # subjects sit left of center in the 1920x1080 source
CROP_W = 607          # 1080 * 9/16 source strip, upscaled to 1080x1920


def run(*args):
    r = subprocess.run([FF + args[0]] + list(args[1:]), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{args[0]} failed: {r.stderr[-800:]}")


def font(name, size):
    return ImageFont.truetype(FONT + name, size)


def hook_overlay():
    """Top-of-frame hook text, transparent background."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    t = "ONLY IN VICE CITY"
    f = font("Lato-Black.ttf", 78)
    x = W / 2 - d.textlength(t, font=f) / 2
    for ox in (-4, 0, 4):
        for oy in (-4, 0, 4):
            d.text((x + ox, 150 + oy), t, font=f, fill=(0, 0, 0, 230))
    d.text((x, 150), t, font=f, fill=(255, 255, 255, 255))
    t2 = "GTA 6 pool party crashers"
    f2 = font("Lato-Bold.ttf", 42)
    x2 = W / 2 - d.textlength(t2, font=f2) / 2
    d.text((x2 + 2, 252 + 2), t2, font=f2, fill=(0, 0, 0, 220))
    d.text((x2, 252), t2, font=f2, fill=(255, 220, 80, 255))
    im.save(D + "hook.png")


def pitch_card():
    """Vice City sunset pitch card: ghost + make.fun money pitch + bounty URL."""
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        if t < 0.55:
            k = t / 0.55
            c = (int(255 - 60 * k), int(110 + 40 * k), int(150 - 30 * k))
        else:
            k = (t - 0.55) / 0.45
            c = (int(195 - 110 * k), int(150 - 100 * k), int(120 + 40 * k))
        d.line([(0, y), (W, y)], fill=c)
    # synthwave sun
    d.ellipse([W / 2 - 260, 300, W / 2 + 260, 820], fill=(255, 190, 90))
    for i in range(5):
        yy = 560 + i * 52
        d.rectangle([W / 2 - 260, yy, W / 2 + 260, yy + 8 + i * 3], fill=(230, 90, 130))
    # ghost on top
    g = Image.open(GHOST).convert("RGBA").resize((360, 360), Image.LANCZOS)
    im.paste(g, (int(W / 2 - 180), 330), g)
    lines = [
        ("Make clips like this with AI", "Lato-Black.ttf", 62, (255, 255, 255), 900),
        ("Earn money on make.fun", "Lato-Black.ttf", 74, (255, 235, 245), 1000),
        ("AI agents win real USDC bounties", "Lato-Bold.ttf", 42, (255, 220, 235), 1110),
    ]
    for t, fn, sz, col, y in lines:
        f = font(fn, sz)
        x = W / 2 - d.textlength(t, font=f) / 2
        d.text((x + 3, y + 3), t, font=f, fill=(40, 10, 30))
        d.text((x, y), t, font=f, fill=col)
    url = "make.fun/bounty/gta6-clipper-01"
    f = font("IBMPlexMono-Medium.ttf", 40)
    uw = d.textlength(url, font=f)
    d.rounded_rectangle([W / 2 - uw / 2 - 28, 1230, W / 2 + uw / 2 + 28, 1310],
                        radius=16, fill=(20, 10, 25))
    d.text((W / 2 - uw / 2, 1248), url, font=f, fill=(255, 255, 255))
    im.save(D + "pitch.png")


def build():
    hook_overlay()
    pitch_card()
    vf = f"crop={CROP_W}:1080:{CROP_X}:0,scale={W}:{H}"
    # hook segment: opens directly on the gator struggle (shot starts ~42.3s)
    run("ffmpeg", "-y", "-v", "error", "-ss", "42.4", "-t", "5.6", "-i", SRC,
        "-i", D + "hook.png", "-filter_complex", f"[0:v]{vf}[base];[base][1:v]overlay=0:0[v]",
        "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-r", "30", D + "segA.mp4")
    # action segment
    run("ffmpeg", "-y", "-v", "error", "-ss", "66", "-t", "6", "-i", SRC,
        "-vf", vf, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-r", "30", D + "segB.mp4")
    # pitch card segment
    run("ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", "7", "-i", D + "pitch.png",
        "-vf", f"scale={W}:{H}", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-r", "30", D + "segC.mp4")
    with open(D + "concat.txt", "w") as f:
        f.write("file 'segA.mp4'\nfile 'segB.mp4'\nfile 'segC.mp4'\n")
    run("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", D + "concat.txt",
        "-c", "copy", D + "video_noaudio.mp4")
    # continuous trailer audio under the whole clip, fade out at the end
    run("ffmpeg", "-y", "-v", "error", "-ss", "42.4", "-t", "18.6", "-i", SRC,
        "-vn", "-af", "afade=t=out:st=16.6:d=2", "-c:a", "aac", "-b:a", "160k", D + "audio.m4a")
    run("ffmpeg", "-y", "-v", "error", "-i", D + "video_noaudio.mp4", "-i", D + "audio.m4a",
        "-c:v", "copy", "-c:a", "copy", "-shortest", D + "clip.mp4")
    print("built clip.mp4")


if __name__ == "__main__":
    build()
