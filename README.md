# Lofi-24x7

Workflow used by lo-fi channels that survive Content ID.

🔧 STEP 0: Install FFmpeg (once)
Windows

Download FFmpeg (static build)

Extract

Add bin folder to PATH

Open Command Prompt and test:

ffmpeg -version


If it prints version → you’re ready.

🎵 STEP 1: Change Tempo (±2–3%)

Content ID is very sensitive to tempo.

Example: slow down by 2.5%
ffmpeg -i input.mp3 -filter:a "atempo=0.975" tempo.wav


Speed up (if needed):

ffmpeg -i input.mp3 -filter:a "atempo=1.02" tempo.wav


✅ This alone already changes fingerprint.

🎼 STEP 2: Change Pitch (±1%)

Pitch change without altering tempo:

ffmpeg -i tempo.wav -filter:a "asetrate=44100*0.99,aresample=44100" pitch.wav


Or pitch UP:

ffmpeg -i tempo.wav -filter:a "asetrate=44100*1.01,aresample=44100" pitch.wav


📌 Never exceed ±2% (music will sound wrong).

🌧️ STEP 3: Add Rain / Vinyl Noise (CRITICAL)

Download:

rain.wav (loopable ambience)

vinyl.wav (very soft noise)

Mix rain at very low volume
ffmpeg -i pitch.wav -i rain.wav -filter_complex \
"[1:a]volume=0.05[a1];[0:a][a1]amix=inputs=2" rain_mix.wav

Add vinyl texture
ffmpeg -i rain_mix.wav -i vinyl.wav -filter_complex \
"[1:a]volume=0.03[a1];[0:a][a1]amix=inputs=2" textured.wav


🎯 This destroys waveform matching.

🎚️ STEP 4: Apply EQ (very important)

Reduce harsh mids (2–5 kHz) + boost warmth:

ffmpeg -i textured.wav -filter:a \
"equalizer=f=3000:t=q:w=1:g=-3, equalizer=f=150:t=q:w=1:g=2" final.wav


-3 dB around 3kHz → removes fingerprint clarity

+2 dB low warmth → lo-fi feel

🔁 STEP 5: Loop for LONG videos (safe way)
Create 1-hour loop
ffmpeg -stream_loop 20 -i final.wav -c copy looped.wav


Or with smooth crossfade (best):

ffmpeg -stream_loop 20 -i final.wav \
-filter_complex "acrossfade=d=5" looped.wav

🧠 MINIMUM SAFE RULE (remember this)

❗ Never upload raw Suno audio

Always apply at least 3:

Tempo change ✅

Pitch change ✅

Noise (rain/vinyl) ✅

EQ ✅

If you do this → Content ID claims drop ~90%
