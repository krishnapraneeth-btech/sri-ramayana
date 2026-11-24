import os
import subprocess
import numpy as np
from scipy.signal import butter, lfilter

AUDIO_OUT = "/home/user/ramayana_app/android/assets/www/audio"
TMP_WAV = "/tmp/ramayana_wav"
os.makedirs(AUDIO_OUT, exist_ok=True)
os.makedirs(TMP_WAV, exist_ok=True)

SR = 22050  # Warm, clean audio & compact APK footprint

def lowpass(sig, cutoff, order=3):
    nyq = 0.5 * SR
    b, a = butter(order, min(cutoff / nyq, 0.95), btype="low")
    return lfilter(b, a, sig)

def stereo_reverb(mono, decay=0.45, delay_ms=(37, 53, 79, 107)):
    n = len(mono)
    L = mono.copy()
    R = mono.copy()
    for i, d_ms in enumerate(delay_ms):
        d = int(SR * d_ms / 1000)
        g = decay * (0.72 ** i)
        if i % 2 == 0:
            L[d:] += mono[:-d] * g
            R[d + 180:] += mono[:-(d + 180)] * (g * 0.8)
        else:
            R[d:] += mono[:-d] * g
            L[d + 210:] += mono[:-(d + 210)] * (g * 0.8)
    L = lowpass(L, 4800)
    R = lowpass(R, 4800)
    return np.stack([L, R], axis=1)

def tanpura_drone(duration, sa_hz=138.59):  # C#3
    t = np.linspace(0, duration, int(SR * duration), endpoint=False)
    # Pa (3/2), Sa4 (2), Sa4 (2 detuned), Sa3 (1)
    freqs = [sa_hz * 1.5, sa_hz * 2.0, sa_hz * 2.003, sa_hz * 1.0]
    sig = np.zeros_like(t)
    cycle = 4.0  # 4-second pluck cycle
    for idx, f in enumerate(freqs):
        phase_t = (t - idx * (cycle / 4.0)) % cycle
        env = np.exp(-phase_t * 0.78) * (1 - np.exp(-phase_t * 35.0))
        # Rich jawari overtone buzz
        wave = (
            0.55 * np.sin(2 * np.pi * f * t)
            + 0.30 * np.sin(2 * np.pi * 2 * f * t)
            + 0.18 * np.sin(2 * np.pi * 3 * f * t)
            + 0.11 * np.sin(2 * np.pi * 4 * f * t)
            + 0.06 * np.sin(2 * np.pi * 5 * f * t)
        )
        sig += env * wave * 0.22
    # Warm pad undertone
    pad = (
        0.15 * np.sin(2 * np.pi * sa_hz * t)
        + 0.10 * np.sin(2 * np.pi * sa_hz * 1.5 * t)
    )
    return lowpass(sig + pad, 2600)

def bansuri_phrase(duration, notes, sa_hz=277.18, tempo_bpm=72, seed=1):
    # notes: list of (semitone_offset_or_None, beats)
    rng = np.random.default_rng(seed)
    beat_sec = 60.0 / tempo_bpm
    total_samples = int(SR * duration)
    out = np.zeros(total_samples)
    cur_sample = 0
    prev_freq = sa_hz
    while cur_sample < total_samples:
        for semi, beats in notes:
            dur = beats * beat_sec
            n_samp = int(dur * SR)
            if cur_sample >= total_samples:
                break
            n_avail = min(n_samp, total_samples - cur_sample)
            if semi is not None:
                target_f = sa_hz * (2.0 ** (semi / 12.0))
                t = np.arange(n_avail) / SR
                # Smooth meend (portamento) at start of note
                glide_len = min(int(0.08 * SR), n_avail)
                freq_curve = np.full(n_avail, target_f)
                if glide_len > 0:
                    freq_curve[:glide_len] = np.linspace(prev_freq, target_f, glide_len)
                # Subtle vibrato after attack
                vib = 1.0 + 0.0055 * np.sin(2 * np.pi * 4.8 * t) * np.clip((t - 0.12) * 3.0, 0, 1)
                phase = 2 * np.pi * np.cumsum(freq_curve * vib) / SR
                wave = (
                    0.72 * np.sin(phase)
                    + 0.16 * np.sin(2 * phase)
                    + 0.05 * np.sin(3 * phase)
                )
                # Gentle breath air noise
                breath = lowpass(rng.normal(0, 0.018, n_avail), 1800)
                atk = min(int(0.09 * SR), n_avail // 3)
                rel = min(int(0.14 * SR), n_avail // 3)
                env = np.ones(n_avail)
                if atk > 0:
                    env[:atk] = np.linspace(0, 1, atk) ** 1.3
                if rel > 0:
                    env[-rel:] = np.linspace(1, 0, rel) ** 1.3
                out[cur_sample:cur_sample + n_avail] += (wave + breath) * env * 0.28
                prev_freq = target_f
            cur_sample += n_samp
    return lowpass(out, 3200)

def veena_plucks(duration, scale_semis, sa_hz=277.18, step_sec=0.55, seed=7):
    rng = np.random.default_rng(seed)
    n_tot = int(SR * duration)
    out = np.zeros(n_tot)
    pos = 0
    while pos < n_tot:
        semi = rng.choice(scale_semis)
        if rng.random() > 0.25:
            f = sa_hz * (2.0 ** (semi / 12.0))
            plen = min(int(1.6 * SR), n_tot - pos)
            t = np.arange(plen) / SR
            env = np.exp(-t * 3.2) * (1 - np.exp(-t * 90))
            wave = (
                0.6 * np.sin(2 * np.pi * f * t)
                + 0.28 * np.sin(2 * np.pi * 2 * f * t)
                + 0.14 * np.sin(2 * np.pi * 3 * f * t)
            )
            out[pos:pos + plen] += env * wave * 0.16
        pos += int(step_sec * SR)
    return lowpass(out, 3600)

def temple_bells(duration, interval_sec=5.5, base_hz=880.0):
    n_tot = int(SR * duration)
    out = np.zeros(n_tot)
    pos = int(1.0 * SR)
    while pos < n_tot:
        blen = min(int(3.2 * SR), n_tot - pos)
        t = np.arange(blen) / SR
        bell = (
            0.5 * np.sin(2 * np.pi * base_hz * t) * np.exp(-t * 1.4)
            + 0.25 * np.sin(2 * np.pi * base_hz * 2.01 * t) * np.exp(-t * 2.4)
            + 0.12 * np.sin(2 * np.pi * base_hz * 2.98 * t) * np.exp(-t * 3.6)
        )
        out[pos:pos + blen] += bell * 0.08
        pos += int(interval_sec * SR)
    return out

def war_percussion(duration, bpm=108):
    n_tot = int(SR * duration)
    out = np.zeros(n_tot)
    beat = 60.0 / bpm
    pattern = [1.0, 0.35, 0.7, 0.45, 0.9, 0.35, 0.75, 0.6]
    idx = 0
    pos = 0
    while pos < n_tot:
        vel = pattern[idx % len(pattern)]
        dlen = min(int(0.32 * SR), n_tot - pos)
        t = np.arange(dlen) / SR
        # Deep kettle/dundubhi pitch drop + punch
        f_drop = 92.0 * np.exp(-t * 12.0) + 48.0
        drum = np.sin(2 * np.pi * np.cumsum(f_drop) / SR) * np.exp(-t * 7.5)
        snap = np.sin(2 * np.pi * 195.0 * t) * np.exp(-t * 24.0) * 0.35
        out[pos:pos + dlen] += (drum + snap) * vel * 0.36
        pos += int((beat / 2.0) * SR)
        idx += 1
    return lowpass(out, 1800)

def seamless_loop(stereo, crossfade_sec=2.0):
    cf = int(crossfade_sec * SR)
    if len(stereo) <= cf * 2:
        return stereo
    core = stereo[:-cf].copy()
    tail = stereo[-cf:]
    alpha = np.linspace(0, 1, cf)[:, None]
    core[:cf] = core[:cf] * alpha + tail * (1.0 - alpha)
    return core

def save_mp3(name, stereo_arr):
    # Normalize softly to -3 dBFS so BGM mixes gently behind speech
    peak = np.max(np.abs(stereo_arr)) + 1e-9
    norm = (stereo_arr / peak) * 0.68
    pcm16 = (np.clip(norm, -1, 1) * 32767).astype(np.int16)
    wav_path = os.path.join(TMP_WAV, f"{name}.wav")
    mp3_path = os.path.join(AUDIO_OUT, f"{name}.mp3")
    import wave
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
        "-codec:a", "libmp3lame", "-b:a", "96k", mp3_path
    ], check=True)
    os.remove(wav_path)
    print("Generated BGM:", name, os.path.getsize(mp3_path))

DUR = 46.0  # 44s seamless loop after 2s crossfade

# 1. Divine Dawn (Raga Bhupali: 0, 2, 4, 7, 9, 12)
p1 = [(0, 2), (2, 1), (4, 2), (7, 2), (9, 1.5), (7, 1.5), (4, 2), (2, 1), (0, 3),
      (None, 1), (4, 1.5), (7, 1.5), (9, 2), (12, 3), (9, 1.5), (7, 1.5), (4, 2), (2, 2), (0, 3)]
m1 = tanpura_drone(DUR, 138.59) + bansuri_phrase(DUR, p1, 277.18, 66, 1) + temple_bells(DUR, 7.5, 1108.7)
save_mp3("bgm_divine_dawn", seamless_loop(stereo_reverb(m1, 0.48)))

# 2. Royal Court (Raga Yaman: 0, 2, 4, 6, 7, 9, 11, 12)
p2 = [(None, 0.5), (11-12, 1.5), (0, 1.5), (2, 1.5), (4, 2), (6, 1.5), (7, 2.5),
      (9, 1.5), (11, 1.5), (12, 3), (11, 1), (9, 1.5), (7, 2), (6, 1.5), (4, 2), (2, 1.5), (0, 3)]
m2 = tanpura_drone(DUR, 146.83) + bansuri_phrase(DUR, p2, 293.66, 78, 2) + veena_plucks(DUR, [0, 4, 6, 7, 11, 12], 293.66, 0.62, 2) + temple_bells(DUR, 6.0, 1174.6)
save_mp3("bgm_royal_court", seamless_loop(stereo_reverb(m2, 0.44)))

# 3. Sorrow & Exile (Raga Shivaranjani: 0, 2, 3, 7, 9, 12)
p3 = [(7, 2.5), (9, 2), (7, 2), (3, 2.5), (2, 2), (0, 3.5), (None, 1.5),
      (3, 2), (7, 2.5), (9, 2), (12, 3), (9, 2), (7, 2), (3, 2.5), (2, 2), (0, 4)]
m3 = tanpura_drone(DUR, 130.81) * 0.85 + bansuri_phrase(DUR, p3, 261.63, 56, 3)
save_mp3("bgm_sorrow_exile", seamless_loop(stereo_reverb(m3, 0.55)))

# 4. Forest Mystic (Raga Pahadi: 0, 2, 4, 7, 9, 11)
p4 = [(4, 2), (2, 1.5), (0, 2), (-3, 2), (0, 2.5), (None, 1),
      (2, 1.5), (4, 2), (7, 2.5), (9, 2), (7, 1.5), (4, 2), (2, 2), (0, 3)]
m4 = tanpura_drone(DUR, 146.83) * 0.78 + bansuri_phrase(DUR, p4, 293.66, 68, 4) + veena_plucks(DUR, [0, 2, 4, 7, 9, 12], 587.33, 0.85, 4) * 0.75
save_mp3("bgm_forest_mystic", seamless_loop(stereo_reverb(m4, 0.52)))

# 5. Heroic Ocean & Devotion (Raga Hamsadhwani: 0, 2, 4, 7, 11, 12)
p5 = [(0, 1), (2, 1), (4, 1.5), (7, 1.5), (11, 1), (12, 2.5), (11, 1), (7, 1.5), (4, 1.5), (2, 1), (0, 2),
      (None, 0.5), (4, 1), (7, 1), (11, 1.5), (12, 2), (14, 1.5), (12, 2), (7, 1.5), (4, 1.5), (0, 2.5)]
m5 = tanpura_drone(DUR, 146.83) + bansuri_phrase(DUR, p5, 293.66, 92, 5) + veena_plucks(DUR, [0, 4, 7, 11, 12], 293.66, 0.42, 5) + war_percussion(DUR, 92) * 0.42
save_mp3("bgm_heroic_ocean", seamless_loop(stereo_reverb(m5, 0.42)))

# 6. Epic War & Dharma Battle (Raga Bhairav / Veer Rasa: 0, 1, 4, 5, 7, 8, 11, 12)
p6 = [(0, 1), (4, 1), (5, 1), (7, 2), (8, 1), (7, 1.5), (5, 1), (4, 1), (1, 1), (0, 2),
      (7, 1), (8, 1), (11, 1.5), (12, 2.5), (11, 1), (8, 1), (7, 1.5), (4, 1), (1, 1), (0, 2)]
m6 = tanpura_drone(DUR, 138.59) * 1.1 + bansuri_phrase(DUR, p6, 277.18, 108, 6) * 0.85 + veena_plucks(DUR, [0, 1, 4, 7, 8, 12], 277.18, 0.34, 6) * 1.1 + war_percussion(DUR, 108)
save_mp3("bgm_epic_war", seamless_loop(stereo_reverb(m6, 0.38)))
