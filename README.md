# Steps to `🏃‍➡️ run 🏃‍♂️` code

Workflow used by lo-fi channels that `survive` (not avoid) Content ID.

## 🚀 Quick Start (Automated)

The easiest way to use this workflow is with the automated Python script:

### Prerequisites
- Python 3.6+
- FFmpeg installed (see STEP 0 below)

### Generate Noise Files (Optional but Recommended)
```bash
# Generate both rain.wav and vinyl.wav (60 seconds each)
python generate_noise.py

# Or generate individually
python generate_noise.py --rain
python generate_noise.py --vinyl
```

### Process Your Audio
```bash
# Basic usage with default settings
python process_audio.py input.mp3

# Process all audio files in music/ folder with default settings
python process_audio.py --music-folder

# Custom tempo and pitch
python process_audio.py input.mp3 --tempo 0.975 --pitch 0.99

# With custom rain/vinyl files
python process_audio.py input.mp3 --rain my_rain.wav --vinyl my_vinyl.wav

# Create looped version (20 loops)
python process_audio.py input.mp3 --loop 20

# Keep intermediate files for debugging
python process_audio.py input.mp3 --keep-intermediate

# See all options
python process_audio.py --help
```

The script automatically:
1. ✅ Changes tempo (±2–3%)
2. ✅ Changes pitch (±1%)
3. ✅ Adds rain/vinyl noise (if files available)
4. ✅ Applies EQ (reduces mids, boosts warmth)
5. ✅ Optionally creates looped version

---

# 📖 Manual FFmpeg Audio Processing Workflow

*(For Original / Licensed Audio Only)*

This workflow demonstrates how to **subtly transform audio characteristics** (tempo, pitch, texture, EQ) using FFmpeg. It’s commonly used for **lo-fi mastering, ambience layering, and long-form background audio creation**.

---

## 🔧 STEP 0: Install FFmpeg (One-Time Setup)

### Windows

1. Download **FFmpeg (static build)**
2. Extract the archive
3. Add the `bin` folder to your system **PATH**
4. Verify installation:

```bash
ffmpeg -version
```

If the version prints successfully, you’re ready.

---

## 🎵 STEP 1: Adjust Tempo (±2–3%)

Small tempo adjustments can subtly change the feel of a track without affecting pitch.

### Slow Down (example: −2.5%)

```bash
ffmpeg -i input.mp3 -filter:a "atempo=0.975" tempo.wav
```

### Speed Up (example: +2%)

```bash
ffmpeg -i input.mp3 -filter:a "atempo=1.02" tempo.wav
```

📌 Keep changes subtle to preserve musical quality.

---

## 🎼 STEP 2: Adjust Pitch (Without Changing Tempo)

Pitch shifting can be done independently using resampling.

### Pitch Down (−1%)

```bash
ffmpeg -i tempo.wav -filter:a "asetrate=44100*0.99,aresample=44100" pitch.wav
```

### Pitch Up (+1%)

```bash
ffmpeg -i tempo.wav -filter:a "asetrate=44100*1.01,aresample=44100" pitch.wav
```

⚠️ Recommended range: **±1–2% maximum** to avoid artifacts.

---

## 🌧️ STEP 3: Add Ambient Texture (Rain / Vinyl Noise)

Layering subtle ambience can enhance atmosphere and lo-fi character.

### Add Soft Rain Ambience

```bash
ffmpeg -i pitch.wav -i rain.wav -filter_complex \
"[1:a]volume=0.05[a1];[0:a][a1]amix=inputs=2" rain_mix.wav
```

### Add Vinyl Noise Texture

```bash
ffmpeg -i rain_mix.wav -i vinyl.wav -filter_complex \
"[1:a]volume=0.03[a1];[0:a][a1]amix=inputs=2" textured.wav
```

🎧 Keep noise layers very low so they enhance rather than overpower.

---

## 🎚️ STEP 4: Apply Equalization (EQ)

EQ helps shape tone and improve listening comfort.

### Example EQ Settings

```bash
ffmpeg -i textured.wav -filter:a \
"equalizer=f=3000:t=q:w=1:g=-3, equalizer=f=150:t=q:w=1:g=2" final.wav
```

**What this does:**

* −3 dB at ~3 kHz → softens harsh mids
* +2 dB at low frequencies → adds warmth
* Common in lo-fi & ambient mastering

---

## 🔁 STEP 5: Create Long-Form Audio (Looping)

### Simple Loop (Approx. 1 Hour)

```bash
ffmpeg -stream_loop 20 -i final.wav -c copy looped.wav
```

### Smooth Loop with Crossfade (Recommended)

```bash
ffmpeg -stream_loop 20 -i final.wav \
-filter_complex "acrossfade=d=5" looped.wav
```

This creates seamless long-duration playback suitable for livestreams or background audio.

---

## 🧠 Best-Practice Guidelines

✔ Use **only original, licensed, or royalty-free audio**
✔ Keep transformations subtle for quality
✔ Always export a **new master file**
✔ Maintain documentation of licenses if publishing
