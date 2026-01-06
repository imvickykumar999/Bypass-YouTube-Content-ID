#!/usr/bin/env python3
"""
Lofi-24x7 Audio Processing Script
Automates the workflow to process audio files and avoid Content ID detection.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
import glob


def check_ffmpeg():
    """Check if FFmpeg is installed and available."""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    return False


def run_ffmpeg(command, description):
    """Run an FFmpeg command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False


def step1_change_tempo(input_file, output_file, tempo_factor):
    """
    STEP 1: Change Tempo (±2–3%)
    Content ID is very sensitive to tempo.
    """
    if tempo_factor < 0.97 or tempo_factor > 1.03:
        print(f"⚠️  Warning: Tempo factor {tempo_factor} is outside recommended range (0.97-1.03)")
    
    command = f'ffmpeg -i "{input_file}" -filter:a "atempo={tempo_factor}" -y "{output_file}"'
    return run_ffmpeg(command, f"Changing tempo by {((tempo_factor-1)*100):.1f}%")


def step2_change_pitch(input_file, output_file, pitch_factor):
    """
    STEP 2: Change Pitch (±1%)
    Pitch change without altering tempo.
    """
    if pitch_factor < 0.99 or pitch_factor > 1.01:
        print(f"⚠️  Warning: Pitch factor {pitch_factor} is outside recommended range (0.99-1.01)")
    
    sample_rate = 44100
    new_rate = sample_rate * pitch_factor
    command = f'ffmpeg -i "{input_file}" -filter:a "asetrate={new_rate},aresample={sample_rate}" -y "{output_file}"'
    return run_ffmpeg(command, f"Changing pitch by {((pitch_factor-1)*100):.1f}%")


def step3_add_noise(input_file, output_file, rain_file=None, vinyl_file=None, rain_volume=0.05, vinyl_volume=0.03):
    """
    STEP 3: Add Rain / Vinyl Noise (CRITICAL)
    This destroys waveform matching.
    """
    current_file = input_file
    
    # Add rain if available
    if rain_file and os.path.exists(rain_file):
        rain_output = output_file.replace('.wav', '_rain.wav')
        command = f'ffmpeg -i "{current_file}" -i "{rain_file}" -filter_complex "[1:a]volume={rain_volume}[a1];[0:a][a1]amix=inputs=2" -y "{rain_output}"'
        if not run_ffmpeg(command, "Adding rain ambience"):
            return False
        current_file = rain_output
    elif rain_file:
        print(f"⚠️  Warning: Rain file '{rain_file}' not found, skipping...")
    
    # Add vinyl if available
    if vinyl_file and os.path.exists(vinyl_file):
        command = f'ffmpeg -i "{current_file}" -i "{vinyl_file}" -filter_complex "[1:a]volume={vinyl_volume}[a1];[0:a][a1]amix=inputs=2" -y "{output_file}"'
        if not run_ffmpeg(command, "Adding vinyl texture"):
            return False
    elif vinyl_file:
        print(f"⚠️  Warning: Vinyl file '{vinyl_file}' not found, skipping...")
        # If vinyl is missing but we have rain output, rename it
        if current_file != input_file:
            os.rename(current_file, output_file)
    else:
        # No noise files, just copy the input
        if current_file != input_file:
            os.rename(current_file, output_file)
        else:
            command = f'ffmpeg -i "{input_file}" -y "{output_file}"'
            if not run_ffmpeg(command, "Copying file (no noise files provided)"):
                return False
    
    return True


def step4_apply_eq(input_file, output_file):
    """
    STEP 4: Apply EQ (very important)
    Reduce harsh mids (2–5 kHz) + boost warmth.
    """
    command = f'ffmpeg -i "{input_file}" -filter:a "equalizer=f=3000:t=q:w=1:g=-3,equalizer=f=150:t=q:w=1:g=2" -y "{output_file}"'
    return run_ffmpeg(command, "Applying EQ (reducing mids, boosting warmth)")


def step5_create_loop(input_file, output_file, loop_count=20, use_crossfade=True):
    """
    STEP 5: Loop for LONG videos (safe way)
    Create looped version with optional crossfade.
    Note: acrossfade with stream_loop doesn't work well, so we use stream_loop with copy for simplicity.
    """
    # stream_loop with crossfade is complex, so we use the simpler copy method
    # For smooth looping, the user can use external tools or we can implement a more complex solution later
    command = f'ffmpeg -stream_loop {loop_count} -i "{input_file}" -c copy -y "{output_file}"'
    return run_ffmpeg(command, f"Creating looped version ({loop_count} loops)")


def cleanup_intermediate_files(keep_intermediate, intermediate_files):
    """Clean up intermediate files unless keep_intermediate is True."""
    if not keep_intermediate:
        print("🧹 Cleaning up intermediate files...")
        for file in intermediate_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"   Removed: {file}")
                except Exception as e:
                    print(f"   Warning: Could not remove {file}: {e}")
    else:
        print("📁 Keeping intermediate files as requested")


def process_single_file(input_file, output_file, tempo, pitch, rain_file, vinyl_file, 
                       rain_volume, vinyl_volume, loop_count, use_crossfade, 
                       skip_eq, keep_intermediate, base_name=None, work_dir=None):
    """
    Process a single audio file through all steps.
    Returns (success, final_output_file)
    
    Args:
        work_dir: Directory for intermediate files (default: same as input file)
    """
    if base_name is None:
        base_name = Path(input_file).stem
    
    # Determine working directory for intermediate files
    if work_dir is None:
        work_dir = Path(input_file).parent
    else:
        work_dir = Path(work_dir)
    
    print(f"\n🎵 Processing: {input_file}")
    print("=" * 60)
    
    # Track intermediate files for cleanup (use base_name to avoid conflicts)
    intermediate_files = []
    
    # STEP 1: Change Tempo
    tempo_file = str(work_dir / f'{base_name}_tempo.wav')
    if not step1_change_tempo(input_file, tempo_file, tempo):
        return False, None
    intermediate_files.append(tempo_file)
    
    # STEP 2: Change Pitch
    pitch_file = str(work_dir / f'{base_name}_pitch.wav')
    if not step2_change_pitch(tempo_file, pitch_file, pitch):
        return False, None
    intermediate_files.append(pitch_file)
    
    # STEP 3: Add Noise
    textured_file = str(work_dir / f'{base_name}_textured.wav')
    if not step3_add_noise(pitch_file, textured_file, rain_file, vinyl_file, 
                           rain_volume, vinyl_volume):
        return False, None
    intermediate_files.append(textured_file)
    
    # STEP 4: Apply EQ
    if skip_eq:
        print("⏭️  Skipping EQ step (not recommended)")
        final_file = textured_file
    else:
        final_file = str(work_dir / f'{base_name}_final.wav')
        if not step4_apply_eq(textured_file, final_file):
            return False, None
        intermediate_files.append(final_file)
    
    # STEP 5: Create Loop (optional)
    if loop_count:
        looped_file = output_file
        if not step5_create_loop(final_file, looped_file, loop_count, use_crossfade):
            return False, None
        final_output = looped_file
    else:
        # No loop, rename final to output
        if final_file != output_file:
            os.rename(final_file, output_file)
        final_output = output_file
        if final_file in intermediate_files:
            intermediate_files.remove(final_file)
    
    print("\n" + "=" * 60)
    print(f"✅ Processing complete!")
    print(f"📁 Output file: {final_output}")
    
    # Cleanup
    cleanup_intermediate_files(keep_intermediate, intermediate_files)
    
    return True, final_output


def main():
    parser = argparse.ArgumentParser(
        description='Process audio files to avoid Content ID detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default settings
  python process_audio.py input.mp3

  # Custom tempo and pitch
  python process_audio.py input.mp3 --tempo 0.975 --pitch 0.99

  # With rain and vinyl noise files
  python process_audio.py input.mp3 --rain rain.wav --vinyl vinyl.wav

  # Create looped version
  python process_audio.py input.mp3 --loop 20

  # Keep intermediate files for debugging
  python process_audio.py input.mp3 --keep-intermediate
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input audio file (e.g., input.mp3) or directory')
    parser.add_argument('-o', '--output', default=None,
                       help='Output file name (default: auto-generated)')
    parser.add_argument('--music-folder', action='store_true',
                       help='Process all audio files in the music/ folder with default settings')
    parser.add_argument('--tempo', type=float, default=0.975,
                       help='Tempo factor (0.97-1.03, default: 0.975 = -2.5%%)')
    parser.add_argument('--pitch', type=float, default=0.99,
                       help='Pitch factor (0.99-1.01, default: 0.99 = -1%%)')
    parser.add_argument('--rain', type=str, default='rain.wav',
                       help='Rain ambience file (default: rain.wav, skipped if not found)')
    parser.add_argument('--vinyl', type=str, default='vinyl.wav',
                       help='Vinyl noise file (default: vinyl.wav, skipped if not found)')
    parser.add_argument('--rain-volume', type=float, default=0.05,
                       help='Rain volume level (default: 0.05)')
    parser.add_argument('--vinyl-volume', type=float, default=0.03,
                       help='Vinyl volume level (default: 0.03)')
    parser.add_argument('--loop', type=int, default=None,
                       help='Number of loops for long videos (default: no loop)')
    parser.add_argument('--no-crossfade', action='store_true',
                       help='Disable crossfade when looping (faster but less smooth)')
    parser.add_argument('--keep-intermediate', action='store_true',
                       help='Keep intermediate processing files')
    parser.add_argument('--skip-eq', action='store_true',
                       help='Skip EQ step (not recommended)')
    
    args = parser.parse_args()
    
    # Check FFmpeg
    print("🔧 Checking FFmpeg installation...")
    if not check_ffmpeg():
        print("❌ FFmpeg is not installed or not in PATH")
        print("   Please install FFmpeg first. See README.md for instructions.")
        sys.exit(1)
    print("✅ FFmpeg found")
    
    # Handle music folder batch processing
    if args.music_folder:
        music_dir = Path('music')
        if not music_dir.exists():
            print(f"❌ Music folder '{music_dir}' not found")
            sys.exit(1)
        
        # Find all audio files
        audio_extensions = ['*.mp3', '*.wav', '*.flac', '*.m4a', '*.aac', '*.ogg']
        audio_files = []
        for ext in audio_extensions:
            audio_files.extend(music_dir.glob(ext))
            audio_files.extend(music_dir.glob(ext.upper()))
        
        if not audio_files:
            print(f"❌ No audio files found in '{music_dir}'")
            sys.exit(1)
        
        print(f"\n📁 Found {len(audio_files)} audio file(s) in music folder")
        print("=" * 60)
        
        success_count = 0
        for audio_file in sorted(audio_files):
            base_name = audio_file.stem
            output_file = music_dir / f'{base_name}_processed.wav'
            
            success, _ = process_single_file(
                str(audio_file),
                str(output_file),
                args.tempo,
                args.pitch,
                args.rain,
                args.vinyl,
                args.rain_volume,
                args.vinyl_volume,
                args.loop,
                not args.no_crossfade,
                args.skip_eq,
                args.keep_intermediate,
                base_name,
                str(music_dir)  # Use music folder for intermediate files
            )
            
            if success:
                success_count += 1
        
        print("\n" + "=" * 60)
        print(f"✅ Batch processing complete! {success_count}/{len(audio_files)} files processed successfully")
        print("\n🧠 Remember: Never upload raw audio!")
        print("   Always apply at least: Tempo ✅ Pitch ✅ Noise ✅ EQ ✅")
        return
    
    # Single file processing
    if not args.input:
        parser.error("input file is required (or use --music-folder)")
    
    if not os.path.exists(args.input):
        print(f"❌ Input file '{args.input}' not found")
        sys.exit(1)
    
    # Determine output file name
    if args.output is None:
        base_name = Path(args.input).stem
        args.output = f'{base_name}_processed.wav'
    
    base_name = Path(args.input).stem
    success, final_output = process_single_file(
        args.input,
        args.output,
        args.tempo,
        args.pitch,
        args.rain,
        args.vinyl,
        args.rain_volume,
        args.vinyl_volume,
        args.loop,
        not args.no_crossfade,
        args.skip_eq,
        args.keep_intermediate,
        base_name,
        None  # Use default work_dir (same as input file)
    )
    
    if not success:
        sys.exit(1)
    
    print("\n🧠 Remember: Never upload raw audio!")
    print("   Always apply at least: Tempo ✅ Pitch ✅ Noise ✅ EQ ✅")


if __name__ == '__main__':
    main()

