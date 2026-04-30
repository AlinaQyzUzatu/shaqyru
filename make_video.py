from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import os, math, textwrap

BASE = "/home/user/shaqyru"
OUT  = "/home/user/shaqyru/video_invite.mp4"
W, H  = 1080, 1920
FPS   = 25

# ── Palette ──
GOLD        = (201, 160, 96)
GOLD_DIM    = (160, 120, 60)
WHITE       = (255, 255, 255)
CREAM       = (247, 240, 228)
DARK        = (28,  8,  16)
WINE        = (110, 28, 48)
WINE_LIGHT  = (160, 60, 80)
TRANSP_DARK = (20, 6, 12, 180)

# ── Fonts ──
F1 = f"{BASE}/font1.ttf"   # Ceremonious One  – roman serif
F2 = f"{BASE}/font2.ttf"   # PF Champion Script Pro – script

def font(path, size): return ImageFont.truetype(path, size)

# ── Helpers ──
def load_photo(name):
    img = Image.open(f"{BASE}/{name}").convert("RGB")
    r = img.width / img.height
    t = W / H
    if r > t:
        nw = int(img.height * t); x = (img.width - nw)//2
        img = img.crop((x, 0, x+nw, img.height))
    else:
        nh = int(img.width / t); y = (img.height - nh)//2
        img = img.crop((0, y, img.width, y+nh))
    return img.resize((W, H), Image.LANCZOS)

def darken(img, a=0.50):
    ov = Image.new("RGB", img.size, DARK)
    return Image.blend(img, ov, a)

def blur_bg(img, r=3):
    return img.filter(ImageFilter.GaussianBlur(r))

def cx(draw, text, fnt, y, color, stroke=None, sw=0):
    bb = draw.textbbox((0,0), text, font=fnt)
    tw = bb[2]-bb[0]
    x  = (W - tw)//2
    if stroke:
        draw.text((x,y), text, font=fnt, fill=stroke,
                  stroke_width=sw, stroke_fill=stroke)
    draw.text((x,y), text, font=fnt, fill=color)
    return bb[3]-bb[1]          # returns text height

def gold_line(draw, y, width=320, alpha_ends=True):
    x0 = (W - width)//2; x1 = x0 + width
    for i in range(width):
        t = i/width
        a = math.sin(t*math.pi) if alpha_ends else 1.0
        r,g,b = GOLD
        draw.point((x0+i, y), fill=(r,g,b,int(a*220)))

def ornament_line(img, y, width=320):
    draw = ImageDraw.Draw(img, "RGBA")
    gold_line(draw, y, width)
    # gem in center
    fgem = font(F1, 32)
    bb = draw.textbbox((0,0), "❖", font=fgem)
    gx = (W - (bb[2]-bb[0]))//2
    draw.text((gx, y-16), "❖", font=fgem, fill=GOLD)

def wrap_text(draw, text, fnt, max_w):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line+" "+w).strip()
        bb = draw.textbbox((0,0), test, font=fnt)
        if bb[2]-bb[0] <= max_w:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines

def draw_lines(draw, lines, fnt, start_y, color, gap=12):
    y = start_y
    for l in lines:
        bb = draw.textbbox((0,0), l, font=fnt)
        x  = (W - (bb[2]-bb[0]))//2
        draw.text((x, y), l, font=fnt, fill=color)
        y += (bb[3]-bb[1]) + gap
    return y

# ── Fade helpers ──
def fade(frames_a, frames_b, n_frames=18):
    out = []
    a = np.array(frames_a[-1], dtype=np.float32)
    b = np.array(frames_b[0],  dtype=np.float32)
    for i in range(n_frames):
        t = i/(n_frames-1)
        # smoothstep
        t = t*t*(3-2*t)
        blended = ((1-t)*a + t*b).astype(np.uint8)
        out.append(Image.fromarray(blended))
    return out

def hold(frame_img, seconds):
    n = int(seconds * FPS)
    return [frame_img]*n

# ══════════════════════════════════════════
#  SCENE BUILDERS
# ══════════════════════════════════════════

def scene_hero():
    bg  = darken(blur_bg(load_photo("photo1.jpg"), 2), 0.38)
    img = bg.copy().convert("RGBA")
    draw= ImageDraw.Draw(img, "RGBA")

    f_kyz   = font(F1, 34)
    f_name  = font(F2, 220)
    f_sub   = font(F1, 52)
    f_date  = font(F1, 56)
    f_rule  = font(F1, 28)

    # top label
    cx(draw, "Қ Ы З   Ұ З А Т У   ·   2 0 2 6", f_kyz, 210,
       (255,220,200,220))

    # divider line
    gold_line(draw, 290, 280)

    # Name
    bb = draw.textbbox((0,0), "Алина", font=f_name)
    nx = (W-(bb[2]-bb[0]))//2
    draw.text((nx+4, 314), "Алина", font=f_name,
              fill=(0,0,0,60))                         # shadow
    draw.text((nx,   310), "Алина", font=f_name,
              fill=(255,255,255,250))

    # subtitle
    cx(draw, "Ұ з а т у   т о й ы", f_sub, 560,
       (255,255,255,210))

    # vertical gold line
    draw.rectangle([(W//2-1, 640), (W//2+1, 710)],
                   fill=(201,160,96,180))

    # date
    cx(draw, "0 1   ·   0 8   ·   2 0 2 6", f_date, 730,
       (255,255,255,240))

    return img.convert("RGB")


def scene_invite():
    bg   = darken(blur_bg(load_photo("photo2.jpg"), 4), 0.42)
    img  = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    # card
    cx0, cy0, cx1, cy1 = 60, 260, W-60, H-260
    card = Image.new("RGBA", (cx1-cx0, cy1-cy0), (247,240,228,235))
    img.paste(card, (cx0,cy0), card)

    draw = ImageDraw.Draw(img, "RGBA")
    f_body  = font(F1, 46)
    f_eyeb  = font(F1, 30)
    f_hosts = font(F2, 80)
    f_orn   = font(F1, 36)

    y = cy0 + 60

    # ornament
    gold_line(draw, y+16, 260)
    cx(draw, "❀", f_orn, y-4, GOLD)
    y += 70

    # invite text (wrapped)
    lines1 = wrap_text(draw,
        "Құрметті қонақтар! Сіздерді аяулы",
        f_body, cx1-cx0-120)
    lines2 = wrap_text(draw,
        "қызымыз Алинаның ұзатылу тойына",
        f_body, cx1-cx0-120)
    lines3 = wrap_text(draw,
        "арналған салтанатты ақ дастарханымыздың",
        f_body, cx1-cx0-120)
    lines4 = wrap_text(draw,
        "қадірлі қонағы болуға шақырамыз!",
        f_body, cx1-cx0-120)
    all_lines = lines1+lines2+lines3+lines4

    y = draw_lines(draw, all_lines, f_body, y, (*WINE,240), gap=18)
    y += 40

    # gold hr
    draw.rectangle([(W//2-140,y),(W//2+140,y+1)], fill=(*GOLD,200))
    y += 40

    # hosts
    cx(draw, "Той иелері", f_eyeb, y, (*GOLD_DIM,220))
    y += 44
    cx(draw, "Маржан · Гульнара · Алихан", f_hosts, y, (*WINE,240))

    return img.convert("RGB")


def scene_date():
    bg   = darken(blur_bg(load_photo("photo4.jpg"), 3), 0.40)
    img  = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    card = Image.new("RGBA", (W-120, 580), (247,240,228,238))
    img.paste(card, (60, (H-580)//2), card)

    draw = ImageDraw.Draw(img, "RGBA")
    f_num  = font(F2, 130)
    f_lbl  = font(F1, 32)
    f_orn  = font(F1, 34)

    cy = (H-580)//2
    y  = cy + 50
    gold_line(draw, y+14, 240)
    cx(draw, "✦", f_orn, y, GOLD)
    y += 80

    cells = [("01","Күні"),("08","Тамыз"),("2026","Жыл"),("19:00","Уақыт")]
    cell_w = (W-120)//4
    for i,(num,lbl) in enumerate(cells):
        bx = 60 + i*cell_w + cell_w//2
        # number
        bb = draw.textbbox((0,0), num, font=f_num)
        nx = bx - (bb[2]-bb[0])//2
        draw.text((nx, y), num, font=f_num, fill=(*WINE,240))
        # label
        bb2= draw.textbbox((0,0), lbl, font=f_lbl)
        lx = bx - (bb2[2]-bb2[0])//2
        draw.text((lx, y+(bb[3]-bb[1])+8), lbl, font=f_lbl,
                  fill=(*GOLD_DIM,220))
        # vertical separator
        if i < 3:
            sep_x = 60+(i+1)*cell_w
            draw.rectangle([(sep_x-1,y+10),(sep_x+1,y+170)],
                           fill=(*GOLD,120))
    return img.convert("RGB")


def scene_venue():
    bg   = darken(blur_bg(load_photo("photo5.jpg"), 3), 0.42)
    img  = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    card = Image.new("RGBA", (W-120, 620), (247,240,228,238))
    img.paste(card, (60, (H-620)//2), card)

    draw = ImageDraw.Draw(img, "RGBA")
    f_city  = font(F1, 36)
    f_name  = font(F2, 140)
    f_addr  = font(F1, 38)
    f_orn   = font(F1, 34)

    cy = (H-620)//2
    y  = cy + 55
    gold_line(draw, y+14, 240)
    cx(draw, "✦", f_orn, y, GOLD)
    y += 80

    cx(draw, "Орал қаласы", f_city, y, (*GOLD_DIM,220))
    y += 56
    cx(draw, "Амалия", f_name, y, (*WINE,245))
    y += 148
    cx(draw, "Базарбай Жуманиязов к-сі, 5/1", f_addr, y, (*DARK,210))

    return img.convert("RGB")


def scene_calendar():
    bg   = darken(blur_bg(load_photo("photo1.jpg"), 4), 0.45)
    img  = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    card = Image.new("RGBA", (W-100, 800), (247,240,228,238))
    img.paste(card, (50, (H-800)//2), card)

    draw = ImageDraw.Draw(img, "RGBA")
    f_month = font(F1, 50)
    f_day   = font(F1, 44)
    f_hdr   = font(F1, 34)
    f_orn   = font(F1, 34)

    cy = (H-800)//2
    y  = cy + 50
    gold_line(draw, y+14, 240)
    cx(draw, "❀", f_orn, y, GOLD)
    y += 75
    cx(draw, "Тамыз 2026", f_month, y, (*WINE,240))
    y += 72

    # calendar grid
    days_hdr = ["Дс","Сс","Ср","Бс","Жм","Сб","Жс"]
    grid = [
        [0,0,0,0,0,1,2],
        [3,4,5,6,7,8,9],
        [10,11,12,13,14,15,16],
        [17,18,19,20,21,22,23],
        [24,25,26,27,28,29,30],
        [31,0,0,0,0,0,0],
    ]
    cell_w = (W-100)//7
    # headers
    for i,d in enumerate(days_hdr):
        bb = draw.textbbox((0,0), d, font=f_hdr)
        x  = 50 + i*cell_w + (cell_w-(bb[2]-bb[0]))//2
        draw.text((x, y), d, font=f_hdr, fill=(*GOLD_DIM,220))
    y += 52

    for row in grid:
        for i,d in enumerate(row):
            if d == 0: continue
            bb  = draw.textbbox((0,0), str(d), font=f_day)
            dw  = bb[2]-bb[0]
            dh  = bb[3]-bb[1]
            dx  = 50 + i*cell_w + (cell_w-dw)//2
            if d == 1:
                # highlight circle
                r = 30
                draw.ellipse([(dx-r+dw//2-6, y-8),
                               (dx+r+dw//2-6, y+dh+8)],
                              fill=(*WINE,230))
                draw.text((dx, y), str(d), font=f_day, fill=WHITE)
            else:
                draw.text((dx, y), str(d), font=f_day,
                          fill=(*DARK,210))
        y += 58

    return img.convert("RGB")


def scene_outro():
    bg   = darken(blur_bg(load_photo("photo2.jpg"), 2), 0.35)
    img  = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    f_name  = font(F2, 180)
    f_sub   = font(F1, 50)
    f_date  = font(F1, 52)
    f_small = font(F1, 30)

    cx(draw, "Қ Ы З   Ұ З А Т У", f_small, 340, (255,220,200,200))
    gold_line(draw, 400, 260)

    bb = draw.textbbox((0,0), "Алина", font=f_name)
    nx = (W-(bb[2]-bb[0]))//2
    draw.text((nx+4,424), "Алина", font=f_name, fill=(0,0,0,55))
    draw.text((nx,  420), "Алина", font=f_name, fill=(255,255,255,250))

    gold_line(draw, 640, 260)
    cx(draw, "0 1   ·   0 8   ·   2 0 2 6", f_date, 670,
       (255,255,255,240))
    cx(draw, "Сағат 19:00  ·  Амалия", f_sub, 756,
       (255,220,180,210))

    return img.convert("RGB")


# ══════════════════════════════════════════
#  ASSEMBLE
# ══════════════════════════════════════════
print("Rendering scenes...")
s = [
    scene_hero(),
    scene_invite(),
    scene_date(),
    scene_venue(),
    scene_calendar(),
    scene_outro(),
]
durations = [10, 13, 8, 8, 8, 9]   # seconds each scene is held
fade_frames = 20                    # ~0.8s fade between scenes

all_frames = []
for i, (scene, dur) in enumerate(zip(s, durations)):
    held = hold(scene, dur)
    if i == 0:
        # fade in from black
        black = Image.new("RGB", (W,H), DARK)
        fi = fade([black], held, fade_frames)
        all_frames.extend(fi)
        all_frames.extend(held)
    elif i == len(s)-1:
        # fade in then fade out to black
        prev_last = all_frames[-1]
        all_frames.extend(fade([prev_last], held, fade_frames))
        all_frames.extend(held)
        black = Image.new("RGB", (W,H), DARK)
        all_frames.extend(fade(held, [black], fade_frames))
    else:
        prev_last = all_frames[-1]
        all_frames.extend(fade([prev_last], held, fade_frames))
        all_frames.extend(held)

print(f"Total frames: {len(all_frames)}  (~{len(all_frames)/FPS:.1f}s)")

# ── Export via moviepy ──
print("Encoding video...")
import numpy as np
frames_np = [np.array(f) for f in all_frames]

from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import moviepy.audio.fx

clip = ImageSequenceClip(frames_np, fps=FPS)

audio_path = f"{BASE}/music.mp3"
if os.path.exists(audio_path):
    video_dur = clip.duration
    audio = AudioFileClip(audio_path)
    # loop or trim audio to match video length
    if audio.duration < video_dur:
        n = int(video_dur / audio.duration) + 1
        from moviepy.audio.fx.audio_loop import audio_loop
        audio = audio_loop(audio, n)
    audio = audio.subclipped(0, video_dur)
    # fade in/out audio
    audio = audio.with_effects([
        moviepy.audio.fx.AudioFadeIn(1.5),
        moviepy.audio.fx.AudioFadeOut(2.0)
    ])
    clip = clip.with_audio(audio)

clip.write_videofile(OUT, fps=FPS, codec="libx264",
                     audio_codec="aac", bitrate="4000k",
                     logger=None)
print(f"Done → {OUT}")
