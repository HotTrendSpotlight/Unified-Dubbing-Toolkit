"""
Main CLI entry point for the Unified Dubbing System
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from core import DubbingPipeline, DubbingTask
from core.utils import ConfigManager, setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Unified Dubbing System - Convert speech in videos to different languages and voices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic dubbing from English to Spanish
  python -m unified_dubbing_system dub input.mp4 output.mp4 --target-lang es
  
  # Use specific models
  python -m unified_dubbing_system dub input.mp4 output.mp4 --target-lang fr --stt-model whisperx --tts-model bark
  
  # With voice cloning
  python -m unified_dubbing_system dub input.mp4 output.mp4 --target-lang de --voice-model reference_voice.wav
  
  # List available models
  python -m unified_dubbing_system list-models
  
  # Process batch of files
  python -m unified_dubbing_system batch input_dir/ output_dir/ --target-lang es
        """
    )
    
    # Global options
    parser.add_argument("--config", "-c", type=str, help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output except errors")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Dub command
    dub_parser = subparsers.add_parser("dub", help="Dub a single video file")
    dub_parser.add_argument("input", type=str, help="Input video/audio file")
    dub_parser.add_argument("output", type=str, help="Output video/audio file")
    dub_parser.add_argument("--target-lang", "-t", type=str, required=True, 
                           help="Target language code (e.g., en, es, fr, de)")
    dub_parser.add_argument("--source-lang", "-s", type=str, 
                           help="Source language code (auto-detect if not specified)")
    dub_parser.add_argument("--stt-model", type=str, default="whisper",
                           help="Speech-to-text model to use")
    dub_parser.add_argument("--tts-model", type=str, default="bark",
                           help="Text-to-speech model to use")
    dub_parser.add_argument("--voice-model", type=str,
                           help="Voice model for voice cloning")
    dub_parser.add_argument("--quality", type=str, choices=["low", "medium", "high"], 
                           default="medium", help="Output quality")
    dub_parser.add_argument("--no-lip-sync", action="store_true",
                           help="Disable lip synchronization")
    
    # List models command
    list_parser = subparsers.add_parser("list-models", help="List available models")
    list_parser.add_argument("--type", "-t", type=str, 
                           choices=["stt", "tts", "voice_cloning", "lip_sync", "all"],
                           default="all", help="Type of models to list")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Process multiple files")
    batch_parser.add_argument("input_dir", type=str, help="Input directory")
    batch_parser.add_argument("output_dir", type=str, help="Output directory")
    batch_parser.add_argument("--target-lang", "-t", type=str, required=True,
                             help="Target language code")
    batch_parser.add_argument("--source-lang", "-s", type=str,
                             help="Source language code")
    batch_parser.add_argument("--stt-model", type=str, default="whisper",
                             help="Speech-to-text model to use")
    batch_parser.add_argument("--tts-model", type=str, default="bark",
                             help="Text-to-speech model to use")
    batch_parser.add_argument("--quality", type=str, choices=["low", "medium", "high"],
                             default="medium", help="Output quality")
    batch_parser.add_argument("--parallel", "-p", type=int, default=1,
                             help="Number of parallel processes")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get information about a model")
    info_parser.add_argument("model_type", type=str, 
                           choices=["stt", "tts", "voice_cloning", "lip_sync"],
                           help="Type of model")
    info_parser.add_argument("model_name", type=str, help="Name of the model")
    
    return parser


async def dub_command(args, pipeline: DubbingPipeline) -> None:
    """Execute dub command"""
    task = DubbingTask(
        input_file=args.input,
        output_file=args.output,
        target_language=args.target_lang,
        source_language=args.source_lang,
        voice_model=args.voice_model,
        stt_model=args.stt_model,
        tts_model=args.tts_model,
        lip_sync=not args.no_lip_sync,
        quality=args.quality
    )
    
    print(f"Starting dubbing: {args.input} -> {args.output}")
    print(f"Target language: {args.target_lang}")
    print(f"Models: STT={args.stt_model}, TTS={args.tts_model}")
    
    try:
        result = await pipeline.process_task(task)
        
        if result["status"] == "completed":
            print(f"✅ Dubbing completed successfully!")
            print(f"Output file: {result['output_file']}")
            
            # Show processing steps
            if "steps" in result:
                print("\nProcessing steps:")
                for step, info in result["steps"].items():
                    status = "✅" if info["status"] == "completed" else "⚠️"
                    print(f"  {status} {step.replace('_', ' ').title()}")
        else:
            print(f"❌ Dubbing failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def list_models_command(args, pipeline: DubbingPipeline) -> None:
    """Execute list-models command"""
    available_models = pipeline.get_available_models()
    
    if args.type == "all":
        for model_type, models in available_models.items():
            if models:
                print(f"\n{model_type.upper()} Models:")
                for model in models:
                    print(f"  - {model}")
            else:
                print(f"\n{model_type.upper()} Models: None available")
    else:
        models = available_models.get(args.type, [])
        print(f"{args.type.upper()} Models:")
        if models:
            for model in models:
                print(f"  - {model}")
        else:
            print("  None available")


def info_command(args, pipeline: DubbingPipeline) -> None:
    """Execute info command"""
    try:
        info = pipeline.get_module_info(args.model_type, args.model_name)
        
        print(f"\nModel Information: {info['name']}")
        print(f"Type: {info['type']}")
        print(f"Description: {info['description']}")
        
        if info.get('supported_languages'):
            print(f"Supported Languages: {', '.join(info['supported_languages'])}")
        
        if info.get('quality_levels'):
            print(f"Quality Levels: {', '.join(info['quality_levels'])}")
        
        if info.get('requirements'):
            print(f"Requirements: {', '.join(info['requirements'])}")
            
    except Exception as e:
        print(f"❌ Error getting model info: {str(e)}")
        sys.exit(1)


async def batch_command(args, pipeline: DubbingPipeline) -> None:
    """Execute batch command"""
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find video files
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(input_dir.glob(f"*{ext}"))
        video_files.extend(input_dir.glob(f"*{ext.upper()}"))
    
    if not video_files:
        print(f"❌ No video files found in {input_dir}")
        sys.exit(1)
    
    print(f"Found {len(video_files)} video files to process")
    
    # Process files
    for i, video_file in enumerate(video_files, 1):
        output_file = output_dir / f"{video_file.stem}_dubbed{video_file.suffix}"
        
        print(f"\n[{i}/{len(video_files)}] Processing: {video_file.name}")
        
        task = DubbingTask(
            input_file=str(video_file),
            output_file=str(output_file),
            target_language=args.target_lang,
            source_language=args.source_lang,
            stt_model=args.stt_model,
            tts_model=args.tts_model,
            quality=args.quality
        )
        
        try:
            result = await pipeline.process_task(task)
            
            if result["status"] == "completed":
                print(f"  ✅ Completed: {output_file.name}")
            else:
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")


async def main_cli() -> None:
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        log_level = "DEBUG"
    elif args.quiet:
        log_level = "ERROR"
    else:
        log_level = "INFO"
    
    setup_logging(log_level)
    
    # Initialize pipeline
    try:
        pipeline = DubbingPipeline(args.config)
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {str(e)}")
        sys.exit(1)
    
    # Execute command
    if args.command == "dub":
        await dub_command(args, pipeline)
    elif args.command == "list-models":
        list_models_command(args, pipeline)
    elif args.command == "info":
        info_command(args, pipeline)
    elif args.command == "batch":
        await batch_command(args, pipeline)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main_cli())