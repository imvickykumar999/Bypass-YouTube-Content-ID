#!/usr/bin/env python3
"""
Helper script to generate rain.wav and vinyl.wav noise files.
These are used in STEP 3 of the audio processing workflow.
"""

import argparse
import subprocess
import sys


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


def generate_rain(duration=60, output='rain.wav'):
    """
    Generate rain ambience using FFmpeg noise filter.
    Creates a loopable rain sound.
    """
    print(f"🌧️  Generating rain ambience ({duration}s)...")
    
    # Use noise filter with low frequency emphasis for rain-like sound
    command = f'ffmpeg -f lavfi -i "anoisesrc=duration={duration}:color=white:seed=42" -filter:a "lowpass=f=2000,highpass=f=200,volume=0.3" -y "{output}"'
    
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Rain file created: {output}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating rain: {e.stderr}")
        return False


def generate_vinyl(duration=60, output='vinyl.wav'):
    """
    Generate vinyl crackle/static noise using FFmpeg.
    Creates a very soft vinyl texture sound.
    """
    print(f"💿 Generating vinyl noise ({duration}s)...")
    
    # Use noise filter with emphasis on higher frequencies for vinyl crackle
    command = f'ffmpeg -f lavfi -i "anoisesrc=duration={duration}:color=white:seed=123" -filter:a "highpass=f=1000,lowpass=f=8000,volume=0.2" -y "{output}"'
    
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Vinyl file created: {output}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating vinyl: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate rain.wav and vinyl.wav noise files for audio processing',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--rain', action='store_true',
                       help='Generate rain.wav file')
    parser.add_argument('--vinyl', action='store_true',
                       help='Generate vinyl.wav file')
    parser.add_argument('--duration', type=int, default=60,
                       help='Duration in seconds (default: 60)')
    parser.add_argument('--rain-output', default='rain.wav',
                       help='Output file for rain (default: rain.wav)')
    parser.add_argument('--vinyl-output', default='vinyl.wav',
                       help='Output file for vinyl (default: vinyl.wav)')
    
    args = parser.parse_args()
    
    # If no specific option, generate both
    generate_both = not args.rain and not args.vinyl
    
    # Check FFmpeg
    if not check_ffmpeg():
        print("❌ FFmpeg is not installed or not in PATH")
        print("   Please install FFmpeg first. See README.md for instructions.")
        sys.exit(1)
    
    success = True
    
    if args.rain or generate_both:
        if not generate_rain(args.duration, args.rain_output):
            success = False
    
    if args.vinyl or generate_both:
        if not generate_vinyl(args.duration, args.vinyl_output):
            success = False
    
    if success:
        print("\n✅ All noise files generated successfully!")
        print("   You can now use them with process_audio.py")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()

