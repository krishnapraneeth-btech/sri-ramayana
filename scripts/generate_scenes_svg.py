import os
import math
import random
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUT_DIR = "/home/user/ramayana_app/android/assets/www/images"
TMP_SVG = "/tmp/ramayana_svg"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TMP_SVG, exist_ok=True)

COMMON_DEFS = """
  <filter id="glowSoft" x="-200%" y="-200%" width="500%" height="500%">
    <feGaussianBlur stdDeviation="14" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glowStrong" x="-250%" y="-250%" width="600%" height="600%">
    <feGaussianBlur stdDeviation="28" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="blurMed" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="8"/>
  </filter>
  <filter id="blurHeavy" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="24"/>
  </filter>
"""

def stars_svg(seed, count=140, max_y=450, color="#fff6d6"):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x = rng.randint(10, 1270)
        y = rng.randint(10, max_y)
        r = rng.uniform(0.7, 2.3)
        op = rng.uniform(0.2, 0.92)
        out.append(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="{color}" opacity="{op:.2f}"/>')
    return "\n".join(out)

def embers_svg(seed, count=110, x0=20, x1=1260, y0=40, y1=700, color="#ffd166", rmin=1.0, rmax=4.2):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x = rng.randint(x0, x1)
        y = rng.randint(y0, y1)
        r = rng.uniform(rmin, rmax)
        op = rng.uniform(0.18, 0.85)
        blur = ' filter="url(#glowSoft)"' if r > 2.8 else ""
        out.append(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="{color}" opacity="{op:.2f}"{blur}/>')
    return "\n".join(out)

def ornate_mandala(cx, cy, radius, color="#ffd97d", opacity=0.45):
    parts = [f'<g transform="translate({cx},{cy})" opacity="{opacity}">']
    for mult, w, dash in [(1.0, 2.2, ""), (0.92, 1.2, "4,6"), (0.8, 2.0, ""), (0.58, 1.8, ""), (0.36, 1.5, "3,5")]:
        d = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<circle r="{radius*mult:.1f}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>')
    for i in range(24):
        ang = i * 15
        parts.append(f'<ellipse cx="0" cy="{-radius*0.69:.1f}" rx="{radius*0.075:.1f}" ry="{radius*0.21:.1f}" fill="none" stroke="{color}" stroke-width="1.3" transform="rotate({ang})"/>')
    for i in range(12):
        ang = i * 30
        parts.append(f'<path d="M0,{-radius*0.36:.1f} Q{radius*0.1:.1f},{-radius*0.65:.1f} 0,{-radius*0.92:.1f} Q{-radius*0.1:.1f},{-radius*0.65:.1f} 0,{-radius*0.36:.1f}" fill="{color}" fill-opacity="0.16" stroke="{color}" stroke-width="1.1" transform="rotate({ang})"/>')
    parts.append("</g>")
    return "\n".join(parts)

def ornate_temple_palace(x, base_y, scale=1.0, dark="#1b0907", gold="#f4b942"):
    # Multi-tiered curved Dravidian/Nagara shikhara temple silhouette
    parts = [f'<g transform="translate({x},{base_y}) scale({scale})">']
    # Base plinth
    parts.append(f'<rect x="-70" y="-22" width="140" height="22" fill="{dark}" stroke="{gold}" stroke-width="1.2" stroke-opacity="0.5"/>')
    # Stepped curved spire tiers
    for i in range(7):
        w = 112 * (0.86 ** i)
        y = -22 - i * 24
        h = 24
        parts.append(f'<path d="M{-w/2:.1f},{y:.1f} L{w/2:.1f},{y:.1f} L{w*0.42:.1f},{y-h:.1f} L{-w*0.42:.1f},{y-h:.1f} Z" fill="{dark}" stroke="{gold}" stroke-width="1.1" stroke-opacity="0.55"/>')
        # mini dome windows
        for kx in [-w*0.25, 0, w*0.25]:
            parts.append(f'<path d="M{kx-4:.1f},{y-3:.1f} A4,7 0 0,1 {kx+4:.1f},{y-3:.1f} Z" fill="{gold}" opacity="0.45"/>')
    top_y = -22 - 7 * 24
    # Amalaka + Kalasha
    parts.append(f'<ellipse cx="0" cy="{top_y-4:.1f}" rx="16" ry="7" fill="{dark}" stroke="{gold}" stroke-width="1.5"/>')
    parts.append(f'<path d="M-8,{top_y-10:.1f} Q0,{top_y-34:.1f} 8,{top_y-10:.1f} Z" fill="{gold}" opacity="0.85"/>')
    parts.append(f'<line x1="0" y1="{top_y-28:.1f}" x2="0" y2="{top_y-46:.1f}" stroke="{gold}" stroke-width="2.2"/>')
    # Glowing doorway at bottom
    parts.append(f'<path d="M-12,0 L-12,-28 A12,12 0 0,1 12,-28 L12,0 Z" fill="{gold}" opacity="0.45" filter="url(#glowSoft)"/>')
    parts.append("</g>")
    return "\n".join(parts)

def divine_kodanda_bow(cx, cy, scale=1.0, angle=-25, gold="#ffe175"):
    return f"""
    <g transform="translate({cx},{cy}) rotate({angle}) scale({scale})" filter="url(#glowSoft)">
      <path d="M0,-145 Q-52,-75 -24,-12 Q-6,0 -24,12 Q-52,75 0,145" fill="none" stroke="{gold}" stroke-width="8" stroke-linecap="round"/>
      <path d="M0,-145 Q-52,-75 -24,-12 Q-6,0 -24,12 Q-52,75 0,145" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" opacity="0.7"/>
      <line x1="0" y1="-145" x2="0" y2="145" stroke="#fff2b2" stroke-width="1.8" opacity="0.9"/>
      <line x1="-22" y1="0" x2="115" y2="0" stroke="#fff7c2" stroke-width="4" stroke-linecap="round"/>
      <polygon points="122,0 98,-9 104,0 98,9" fill="#ffffff"/>
    </g>"""

def mountain_layers(seed, colors, y_base=460, amp=95):
    rng = random.Random(seed)
    paths = []
    for idx, col in enumerate(colors):
        yb = y_base + idx * 45
        pts = [f"M0,{yb}"]
        steps = 12
        for s in range(1, steps + 1):
            x = int(s * 1280 / steps)
            y = yb - rng.randint(15, amp) + idx * 10
            cx = x - int(1280 / (2 * steps))
            cy = yb - rng.randint(25, amp + 20)
            pts.append(f"Q{cx},{cy} {x},{y}")
        pts.append("L1280,720 L0,720 Z")
        paths.append(f'<path d="{" ".join(pts)}" fill="{col}"/>')
    return "\n".join(paths)

def make_svg(body, defs_extra=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <defs>{COMMON_DEFS}{defs_extra}</defs>
  {body}
</svg>"""

scenes = {}

# Scene 10: Kishkindha — Rishyamukha Golden Dawn & Sacred Signet Ring Seal
scenes["scene_10_kishkindha"] = make_svg(
    defs_extra="""
    <linearGradient id="g10" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#190e33"/><stop offset="45%" stop-color="#6e2537"/><stop offset="85%" stop-color="#df7732"/><stop offset="100%" stop-color="#ffcf6b"/>
    </linearGradient>
    <radialGradient id="s10" cx="50%" cy="55%" r="48%">
      <stop offset="0%" stop-color="#fff8d6"/><stop offset="35%" stop-color="#ffb84d" stop-opacity="0.7"/><stop offset="100%" stop-color="#6e2537" stop-opacity="0"/>
    </radialGradient>""",
    body=f"""
    <rect width="1280" height="720" fill="url(#g10)"/>
    <circle cx="640" cy="390" r="360" fill="url(#s10)"/>
    {ornate_mandala(640, 320, 220, "#ffe599", 0.55)}
    {mountain_layers(101, ["#4d1f2e", "#361420", "#1f0b12"], 440, 120)}
    <ellipse cx="640" cy="540" rx="720" ry="55" fill="#ffbe73" opacity="0.22" filter="url(#blurHeavy)"/>
    <!-- Sacred Golden Signet Ring & Mace Emblem in luminous sun aura -->
    <g transform="translate(640,320)" filter="url(#glowStrong)">
      <ellipse cx="0" cy="0" rx="74" ry="74" fill="none" stroke="#ffe794" stroke-width="12"/>
      <ellipse cx="0" cy="0" rx="64" ry="64" fill="none" stroke="#fff7d6" stroke-width="3"/>
      <polygon points="0,-92 22,-66 0,-46 -22,-66" fill="#ffefad" stroke="#d98218" stroke-width="2"/>
    </g>
    {embers_svg(10, 90, 60, 1220, 60, 660, "#ffe28a")}
    """
)

# Scene 11: Hanuman's Cosmic Leap — Surging Moonlit Ocean & Distant Golden Lanka
scenes["scene_11_hanuman_leap"] = make_svg(
    defs_extra="""
    <linearGradient id="g11" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#030717"/><stop offset="55%" stop-color="#0c2247"/><stop offset="100%" stop-color="#15406b"/>
    </linearGradient>
    <radialGradient id="m11" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffffff"/><stop offset="65%" stop-color="#d8ecff"/><stop offset="100%" stop-color="#4e89c7" stop-opacity="0"/>
    </radialGradient>""",
    body=f"""
    <rect width="1280" height="720" fill="url(#g11)"/>
    {stars_svg(11, 180, 460, "#e6f2ff")}
    <circle cx="880" cy="215" r="240" fill="url(#m11)" opacity="0.32" filter="url(#blurHeavy)"/>
    <circle cx="880" cy="215" r="108" fill="#f7fbff" filter="url(#glowSoft)"/>
    <!-- Golden comet wind arc soaring across the sky -->
    <path d="M120,420 Q470,130 960,260" fill="none" stroke="#ffb838" stroke-width="18" stroke-linecap="round" opacity="0.32" filter="url(#blurHeavy)"/>
    <path d="M120,420 Q470,130 960,260" fill="none" stroke="#ffe68a" stroke-width="5" stroke-linecap="round" filter="url(#glowStrong)"/>
    <path d="M180,455 Q520,180 940,285" fill="none" stroke="#ffd266" stroke-width="2.5" opacity="0.65"/>
    <circle cx="645" cy="218" r="28" fill="#fff5ba" filter="url(#glowStrong)"/>
    <!-- Distant Lanka golden island -->
    <g transform="translate(1070,475)">
      <path d="M-120,25 Q0,-20 120,25 Z" fill="#291a06"/>
      {ornate_temple_palace(-35, 10, 0.42, "#382208", "#ffd466")}
      {ornate_temple_palace(20, 12, 0.55, "#472c0a", "#ffe48f")}
    </g>
    <!-- Layered ocean swells with moonlight shimmer -->
    <path d="M0,475 Q160,445 320,475 T640,475 T960,475 T1280,475 L1280,720 L0,720 Z" fill="#061930"/>
    <path d="M0,520 Q210,480 420,520 T840,520 T1280,505 L1280,720 L0,720 Z" fill="#092747"/>
    <path d="M0,575 Q240,535 480,575 T960,575 T1280,565 L1280,720 L0,720 Z" fill="#0d355e"/>
    <path d="M0,640 Q280,605 560,640 T1120,640 L1280,635 L1280,720 L0,720 Z" fill="#114473"/>
    <ellipse cx="880" cy="560" rx="190" ry="60" fill="#b8ddff" opacity="0.24" filter="url(#blurHeavy)"/>
    {embers_svg(111, 75, 100, 1180, 100, 480, "#ffe48f", 1.2, 3.8)}
    """
)

# Scene 12: Ashoka Vatika — Moonlit Sacred Blossoms & Simshupa Grove
scenes["scene_12_ashoka_vatika"] = make_svg(
    defs_extra="""
    <linearGradient id="g12" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#050d1c"/><stop offset="55%" stop-color="#112838"/><stop offset="100%" stop-color="#14332a"/>
    </linearGradient>
    <radialGradient id="b12" cx="68%" cy="18%" r="68%">
      <stop offset="0%" stop-color="#dff2ff" stop-opacity="0.42"/><stop offset="100%" stop-color="#112838" stop-opacity="0"/>
    </radialGradient>""",
    body=f"""
    <rect width="1280" height="720" fill="url(#g12)"/>
    {stars_svg(12, 110, 380, "#d9f2ff")}
    <circle cx="920" cy="130" r="64" fill="#edf7ff" filter="url(#glowSoft)"/>
    <polygon points="920,130 340,720 880,720" fill="url(#b12)"/>
    <!-- Ancient sweeping Simshupa branches & grove silhouettes -->
    <path d="M0,560 Q320,515 640,560 T1280,535 L1280,720 L0,720 Z" fill="#091a15"/>
    <path d="M220,720 Q280,430 220,160 Q190,80 90,20" fill="none" stroke="#18100c" stroke-width="56" stroke-linecap="round"/>
    <path d="M235,230 Q490,120 810,185" fill="none" stroke="#18100c" stroke-width="26" stroke-linecap="round"/>
    <path d="M240,300 Q460,250 670,285" fill="none" stroke="#18100c" stroke-width="18" stroke-linecap="round"/>
    <ellipse cx="360" cy="115" rx="390" ry="145" fill="#0b261c" opacity="0.92"/>
    <ellipse cx="690" cy="155" rx="250" ry="110" fill="#0f3023" opacity="0.88"/>
    <!-- Sacred Ashoka red blooms & falling golden signet ring light -->
    {embers_svg(120, 65, 120, 860, 40, 260, "#eb4d6a", 3.5, 9.5)}
    <circle cx="585" cy="520" r="115" fill="#ffe08c" opacity="0.18" filter="url(#blurHeavy)"/>
    <circle cx="585" cy="520" r="24" fill="none" stroke="#ffe999" stroke-width="4" filter="url(#glowStrong)"/>
    <line x1="650" y1="220" x2="585" y2="490" stroke="#ffe58f" stroke-width="2" stroke-dasharray="4,7" opacity="0.65"/>
    {embers_svg(122, 85, 80, 1200, 180, 670, "#d4ff8a", 1.5, 4.0)}
    """
)

# Scene 13: Lanka Dahan — Blazing Golden Towers of Lanka
scenes["scene_13_lanka_dahan"] = make_svg(
    defs_extra="""
    <linearGradient id="g13" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#12050b"/><stop offset="45%" stop-color="#4d0d0d"/><stop offset="85%" stop-color="#bd3311"/><stop offset="100%" stop-color="#ff9924"/>
    </linearGradient>
    <radialGradient id="f13" cx="50%" cy="78%" r="62%">
      <stop offset="0%" stop-color="#fff099" stop-opacity="0.95"/><stop offset="45%" stop-color="#ff5e14" stop-opacity="0.68"/><stop offset="100%" stop-color="#4d0d0d" stop-opacity="0"/>
    </radialGradient>""",
    body=f"""
    <rect width="1280" height="720" fill="url(#g13)"/>
    <circle cx="640" cy="590" r="560" fill="url(#f13)"/>
    <rect x="60" y="480" width="1160" height="240" fill="#1d0707" stroke="#ff9e36" stroke-width="1.5" stroke-opacity="0.5"/>
    {ornate_temple_palace(200, 480, 0.95, "#240808", "#ffb347")}
    {ornate_temple_palace(420, 480, 1.2, "#2a0909", "#ffd166")}
    {ornate_temple_palace(640, 480, 1.48, "#300a0a", "#ffe082")}
    {ornate_temple_palace(860, 480, 1.2, "#2a0909", "#ffd166")}
    {ornate_temple_palace(1080, 480, 0.95, "#240808", "#ffb347")}
    <!-- Sweeping fiery comet arc -->
    <path d="M180,260 Q540,80 980,220 Q1140,275 1040,360" fill="none" stroke="#ff5e14" stroke-width="24" stroke-linecap="round" opacity="0.55" filter="url(#blurHeavy)"/>
    <path d="M180,260 Q540,80 980,220 Q1140,275 1040,360" fill="none" stroke="#ffe57f" stroke-width="9" stroke-linecap="round" filter="url(#glowStrong)"/>
    <!-- Rising flames at base -->
    <path d="M0,720 Q140,510 260,625 Q390,410 510,590 Q640,370 770,580 Q910,415 1040,605 Q1160,470 1280,610 L1280,720 Z" fill="#ff5514" opacity="0.6" filter="url(#blurMed)"/>
    <path d="M0,720 Q180,585 330,660 Q480,500 630,645 Q780,480 940,650 Q1110,520 1280,660 L1280,720 Z" fill="#ffc43b" opacity="0.5" filter="url(#blurMed)"/>
    {embers_svg(13, 150, 30, 1250, 30, 690, "#ffd45c", 1.5, 5.2)}
    """
)

# Scene 14: Rama Setu — Dawn Bridge Across the Ocean
scenes["scene_14_rama_setu"] = make_svg(
    defs_extra="""
    <linearGradient id="g14" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#132e5c"/><stop offset="55%" stop-color="#df7938"/><stop offset="100%" stop-color="#ffe18c"/>
    </linearGradient>
    <linearGradient id="sea14" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#15707d"/><stop offset="100%" stop-color="#062336"/>
    </linearGradient>""",
    body=f"""
    <rect width="1280" height="440" fill="url(#g14)"/>
    <circle cx="940" cy="390" r="100" fill="#fff6c7" filter="url(#glowStrong)"/>
    <rect y="430" width="1280" height="290" fill="url(#sea14)"/>
    <polygon points="850,430 1030,430 1210,720 730,720" fill="#ffe082" opacity="0.24" filter="url(#blurHeavy)"/>
    <!-- Floating stone bridge stretching across sea -->
    <path d="M90,720 Q470,545 945,442 L995,445 Q610,565 360,720 Z" fill="#4f3e2e" stroke="#ffd885" stroke-width="2" stroke-opacity="0.6"/>
    <g fill="#6d5843" stroke="#ffd885" stroke-width="1.4" stroke-opacity="0.65">
      <ellipse cx="220" cy="670" rx="52" ry="26"/><ellipse cx="320" cy="622" rx="44" ry="22"/>
      <ellipse cx="420" cy="578" rx="38" ry="19"/><ellipse cx="515" cy="542" rx="34" ry="16"/>
      <ellipse cx="605" cy="512" rx="28" ry="14"/><ellipse cx="695" cy="488" rx="22" ry="11"/>
      <ellipse cx="775" cy="468" rx="18" ry="9"/>
    </g>
    {divine_kodanda_bow(210, 290, 0.85, -18, "#ffe78f")}
    {embers_svg(14, 70, 80, 1200, 100, 680, "#ffe49c")}
    """
)

# Scene 15: Sanjeevani Mountain — Glowing Herb Peak in Starry Sky
scenes["scene_15_sanjeevani"] = make_svg(
    defs_extra="""
    <linearGradient id="g15" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#040818"/><stop offset="60%" stop-color="#0f254f"/><stop offset="100%" stop-color="#19425e"/>
    </linearGradient>
    <radialGradient id="h15" cx="50%" cy="40%" r="50%">
      <stop offset="0%" stop-color="#a8ffbe" stop-opacity="0.88"/><stop offset="45%" stop-color="#2cd49c" stop-opacity="0.38"/><stop offset="100%" stop-color="#0f254f" stop-opacity="0"/>
    </radialGradient>""",
    body=f"""
    <rect width="1280" height="720" fill="url(#g15)"/>
    {stars_svg(15, 160, 520, "#d8f5ff")}
    <circle cx="640" cy="275" r="290" fill="url(#h15)" filter="url(#blurHeavy)"/>
    <!-- Floating glowing Dronagiri Peak -->
    <polygon points="415,340 640,95 865,330 770,368 510,368" fill="#153b31" stroke="#85ffb8" stroke-width="2.8" filter="url(#glowSoft)"/>
    <polygon points="550,200 640,95 725,205 645,250" fill="#276e57"/>
    <path d="M220,455 Q480,430 640,395 Q800,430 1060,455" fill="none" stroke="#8effc1" stroke-width="4" opacity="0.45" filter="url(#glowSoft)"/>
    {embers_svg(155, 75, 450, 830, 120, 355, "#96ffc2", 2.2, 6.0)}
    {mountain_layers(151, ["#091326", "#060b17"], 560, 75)}
    """
)

# Scene 16: Final Brahmastra Celestial Clash
scenes["scene_16_brahmastra_duel"] = make_svg(
    defs_extra="""
    <linearGradient id="g16" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#191038"/><stop offset="50%" stop-color="#5e1922"/><stop offset="100%" stop-color="#0b0612"/>
    </linearGradient>
    <radialGradient id="c16" cx="50%" cy="48%" r="42%">
      <stop offset="0%" stop-color="#ffffff"/><stop offset="30%" stop-color="#ffe066"/><stop offset="65%" stop-color="#ff6b2b" stop-opacity="0.55"/><stop offset="100%" stop-color="#5e1922" stop-opacity="0"/>
    </radialGradient>""",
    body=f"""
    <rect width="1280" height="720" fill="url(#g16)"/>
    {ornate_mandala(280, 340, 210, "#ffe484", 0.48)}
    {ornate_mandala(1000, 340, 190, "#ff7744", 0.32)}
    <circle cx="640" cy="340" r="320" fill="url(#c16)" filter="url(#blurHeavy)"/>
    <!-- Celestial Lightning & Brahmastra Beam -->
    <line x1="270" y1="340" x2="1010" y2="340" stroke="#fff9cc" stroke-width="18" filter="url(#glowStrong)"/>
    <line x1="270" y1="340" x2="1010" y2="340" stroke="#ffbe0b" stroke-width="6"/>
    {divine_kodanda_bow(240, 340, 1.05, 0, "#ffe896")}
    <!-- Dark shattered lightning on right -->
    <path d="M980,80 L940,210 L995,220 L920,340" fill="none" stroke="#ff8247" stroke-width="4" filter="url(#glowSoft)"/>
    <path d="M1080,100 L1020,235 L1065,245 L990,340" fill="none" stroke="#ff9e66" stroke-width="3" opacity="0.8"/>
    <rect y="560" width="1280" height="160" fill="#10060a"/>
    {embers_svg(16, 130, 120, 1160, 80, 580, "#ffd966", 1.5, 4.8)}
    """
)

# Scene 17: Agni Pariksha & Return in Celestial Pushpaka Vimana
scenes["scene_17_agni_pushpaka"] = make_svg(
    defs_extra="""
    <linearGradient id="g17" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#22133d"/><stop offset="55%" stop-color="#a33c32"/><stop offset="100%" stop-color="#ffbe55"/>
    </linearGradient>""",
    body=f"""
    <rect width="1280" height="720" fill="url(#g17)"/>
    {ornate_mandala(640, 265, 230, "#ffe494", 0.42)}
    <g transform="translate(640,245)">
      <ellipse cx="0" cy="42" rx="205" ry="42" fill="#4f2d07" stroke="#ffe07d" stroke-width="3" filter="url(#glowSoft)"/>
      <path d="M-135,32 L-100,-22 L100,-22 L135,32 Z" fill="#7a490c" stroke="#ffe07d" stroke-width="2"/>
      {ornate_temple_palace(0, -22, 0.72, "#63380a", "#ffe999")}
      {ornate_temple_palace(-82, -22, 0.4, "#63380a", "#ffe999")}
      {ornate_temple_palace(82, -22, 0.4, "#63380a", "#ffe999")}
    </g>
    <rect y="565" width="1280" height="155" fill="#1e0a09"/>
    <path d="M445,565 Q535,375 640,465 Q735,365 835,565 Z" fill="#ff9a2e" opacity="0.72" filter="url(#glowStrong)"/>
    <path d="M510,565 Q585,405 640,475 Q695,405 770,565 Z" fill="#fff2a6" opacity="0.9" filter="url(#glowSoft)"/>
    {embers_svg(17, 95, 120, 1160, 70, 620, "#ffe48f", 1.5, 4.5)}
    """
)

# Scene 18: Sri Rama Pattabhishekam — Sacred Royal Canopy & Cosmic Throne Mandala
scenes["scene_18_pattabhishekam"] = make_svg(
    defs_extra="""
    <linearGradient id="g18" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#380c17"/><stop offset="50%" stop-color="#8c2d19"/><stop offset="100%" stop-color="#ffd166"/>
    </linearGradient>
    <radialGradient id="t18" cx="50%" cy="46%" r="50%">
      <stop offset="0%" stop-color="#fff9cc" stop-opacity="0.96"/><stop offset="45%" stop-color="#ffbe3b" stop-opacity="0.5"/><stop offset="100%" stop-color="#380c17" stop-opacity="0"/>
    </radialGradient>""",
    body=f"""
    <rect width="1280" height="720" fill="url(#g18)"/>
    <circle cx="640" cy="330" r="410" fill="url(#t18)"/>
    {ornate_mandala(640, 315, 250, "#fff2a6", 0.65)}
    <!-- Royal Pillars & Carved Temple Arch -->
    <rect x="65" y="0" width="75" height="720" fill="#2a0a0c" stroke="#f7be4f" stroke-width="2.5"/>
    <rect x="1140" y="0" width="75" height="720" fill="#2a0a0c" stroke="#f7be4f" stroke-width="2.5"/>
    <path d="M140,145 Q390,20 640,115 Q890,20 1140,145" fill="none" stroke="#ffd266" stroke-width="6"/>
    <!-- Sacred Royal Throne & Golden Crown Emblem -->
    <polygon points="350,575 930,575 990,720 290,720" fill="#47210a" stroke="#ffd166" stroke-width="2.5"/>
    <path d="M445,575 L465,280 Q640,175 815,280 L835,575 Z" fill="#2d1206" stroke="#ffdc75" stroke-width="4"/>
    <!-- Sacred Traditional Tiered Indian Kirita Mukuta Crown & Lotus -->
    <g transform="translate(640,395)" filter="url(#glowSoft)">
      <ellipse cx="0" cy="48" rx="88" ry="16" fill="#e69a28" stroke="#fff7cc" stroke-width="2"/>
      <path d="M-64,45 L-54,10 L54,10 L64,45 Z" fill="#ffd15c" stroke="#fff7cc" stroke-width="2"/>
      <path d="M-48,10 L-40,-24 L40,-24 L48,10 Z" fill="#ffdf73" stroke="#fff7cc" stroke-width="2"/>
      <path d="M-32,-24 L-22,-54 L22,-54 L32,-24 Z" fill="#ffe885" stroke="#fff7cc" stroke-width="2"/>
      <path d="M-16,-54 Q0,-105 16,-54 Z" fill="#fff3ad" stroke="#fff7cc" stroke-width="2"/>
      <circle cx="0" cy="-98" r="8" fill="#ffffff"/>
      <circle cx="0" cy="28" r="9" fill="#d92638"/>
      <circle cx="-30" cy="28" r="6" fill="#1b9aaa"/>
      <circle cx="30" cy="28" r="6" fill="#1b9aaa"/>
      <circle cx="0" cy="-7" r="7" fill="#d92638"/>
    </g>
    <!-- Glowing oil lamps flanking throne -->
    <ellipse cx="265" cy="590" rx="22" ry="8" fill="#ffd166"/>
    <circle cx="265" cy="570" r="16" fill="#fff299" filter="url(#glowStrong)"/>
    <ellipse cx="1015" cy="590" rx="22" ry="8" fill="#ffd166"/>
    <circle cx="1015" cy="570" r="16" fill="#fff299" filter="url(#glowStrong)"/>
    {embers_svg(18, 120, 120, 1160, 40, 680, "#ffd45c", 2.0, 5.2)}
    """
)

# Scene 19: Valmiki Ashram — Sacred Palm-Leaf Epic & Veena Beside Tamasa River
scenes["scene_19_valmiki_ashram"] = make_svg(
    defs_extra="""
    <linearGradient id="g19" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#173838"/><stop offset="55%" stop-color="#5a946e"/><stop offset="100%" stop-color="#ffe08c"/>
    </linearGradient>""",
    body=f"""
    <rect width="1280" height="720" fill="url(#g19)"/>
    <circle cx="950" cy="220" r="130" fill="#fff7cc" opacity="0.55" filter="url(#blurHeavy)"/>
    <path d="M0,485 Q360,435 720,490 T1280,470 L1280,720 L0,720 Z" fill="#1d5957"/>
    <path d="M0,555 Q330,510 640,580 L640,720 L0,720 Z" fill="#13331f"/>
    <!-- Sacred Thatched Hermitage -->
    <polygon points="145,500 285,355 425,500" fill="#593a19" stroke="#f0c36d" stroke-width="2.2"/>
    <rect x="180" y="500" width="210" height="95" fill="#3a2711"/>
    <circle cx="485" cy="545" r="22" fill="#ff9e2c" filter="url(#glowStrong)"/>
    <!-- Golden Veena & Palm Leaf Manuscript Glow -->
    <g transform="translate(760,340) rotate(-18)" filter="url(#glowSoft)">
      <circle cx="-90" cy="40" r="46" fill="#70360a" stroke="#ffe07d" stroke-width="3"/>
      <line x1="-55" y1="24" x2="115" y2="-54" stroke="#ffe07d" stroke-width="11" stroke-linecap="round"/>
      <circle cx="122" cy="-58" r="22" fill="#70360a" stroke="#ffe07d" stroke-width="2.5"/>
    </g>
    {embers_svg(19, 80, 100, 1180, 90, 620, "#fff2a8", 1.5, 4.2)}
    """
)

# Scene 20: Eternal Sarayu Sunset — Cosmic Light & Peace
scenes["scene_20_sarayu"] = make_svg(
    defs_extra="""
    <linearGradient id="g20" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#120d36"/><stop offset="45%" stop-color="#7c2e54"/><stop offset="80%" stop-color="#f28c38"/><stop offset="100%" stop-color="#ffe58f"/>
    </linearGradient>
    <radialGradient id="p20" cx="50%" cy="54%" r="50%">
      <stop offset="0%" stop-color="#ffffff"/><stop offset="35%" stop-color="#ffe78c" stop-opacity="0.8"/><stop offset="100%" stop-color="#f28c38" stop-opacity="0"/>
    </radialGradient>""",
    body=f"""
    <rect width="1280" height="720" fill="url(#g20)"/>
    {stars_svg(20, 120, 340, "#fff2cc")}
    <circle cx="640" cy="390" r="340" fill="url(#p20)"/>
    {ornate_mandala(640, 340, 235, "#fff4b8", 0.55)}
    {ornate_temple_palace(180, 485, 0.72, "#24111c", "#ffd670")}
    {ornate_temple_palace(1100, 485, 0.72, "#24111c", "#ffd670")}
    <rect y="485" width="1280" height="235" fill="#18102b"/>
    <polygon points="500,485 780,485 990,720 290,720" fill="#ffe17d" opacity="0.48" filter="url(#blurHeavy)"/>
    <!-- Blooming golden cosmic lotus over Sarayu waters -->
    <g transform="translate(640,460)" filter="url(#glowSoft)">
      <ellipse cx="0" cy="15" rx="95" ry="22" fill="#ffe68c" opacity="0.5"/>
      <path d="M-75,8 Q-35,-45 0,0 Q35,-45 75,8 Z" fill="#ffd257"/>
      <path d="M-42,8 Q-15,-65 0,-10 Q15,-65 42,8 Z" fill="#fff099"/>
      <path d="M-20,8 Q0,-80 20,8 Z" fill="#ffffff"/>
    </g>
    {embers_svg(202, 100, 80, 1200, 60, 660, "#fff2ad", 1.5, 4.5)}
    """
)

for name, svg_content in scenes.items():
    svg_path = os.path.join(TMP_SVG, f"{name}.svg")
    png_path = os.path.join(TMP_SVG, f"{name}.png")
    jpg_path = os.path.join(OUT_DIR, f"{name}.jpg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    subprocess.run(["rsvg-convert", "-w", "1280", "-h", "720", svg_path, "-o", png_path], check=True)
    im = Image.open(png_path).convert("RGB")
    # Add subtle atmospheric vignette + fine grain for painterly feel
    arr = np.array(im, dtype=np.float32)
    h, w, _ = arr.shape
    y_idx, x_idx = np.ogrid[:h, :w]
    dist = np.sqrt(((x_idx - w/2)/(w/2))**2 + ((y_idx - h/2)/(h/2))**2)
    vig = np.clip(1.06 - 0.34 * (dist**1.7), 0.55, 1.05)[..., None]
    rng = np.random.default_rng(42)
    grain = rng.normal(0, 2.2, (h, w, 1)).astype(np.float32)
    arr = np.clip(arr * vig + grain, 0, 255).astype(np.uint8)
    Image.fromarray(arr).save(jpg_path, "JPEG", quality=89, optimize=True)
    print("Rendered:", name, os.path.getsize(jpg_path))
