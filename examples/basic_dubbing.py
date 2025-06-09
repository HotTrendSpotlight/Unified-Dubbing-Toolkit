"""
Basic Dubbing Example
=====================

This example demonstrates how to use the Unified Dubbing System
to dub a video file from one language to another.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import DubbingPipeline, DubbingTask


async def basic_dubbing_example():
    """Basic dubbing example"""
    print("🎬 Unified Dubbing System - Basic Example")
    print("=" * 50)
    
    # Initialize the dubbing pipeline
    print("📋 Initializing dubbing pipeline...")
    try:
        pipeline = DubbingPipeline()
        print("✅ Pipeline initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        return
    
    # Show available models
    print("\n🔧 Available models:")
    available_models = pipeline.get_available_models()
    for model_type, models in available_models.items():
        if models:
            print(f"  {model_type.upper()}: {', '.join(models)}")
        else:
            print(f"  {model_type.upper()}: None available")
    
    # Create a dubbing task
    print("\n🎯 Creating dubbing task...")
    task = DubbingTask(
        input_file="input_video.mp4",  # Replace with actual input file
        output_file="output_dubbed.mp4",
        target_language="es",  # Spanish
        source_language="en",  # English
        stt_model="whisper",
        tts_model="bark",
        quality="medium"
    )
    
    print(f"  Input: {task.input_file}")
    print(f"  Output: {task.output_file}")
    print(f"  Language: {task.source_language} → {task.target_language}")
    print(f"  Models: STT={task.stt_model}, TTS={task.tts_model}")
    
    # Check if input file exists
    if not Path(task.input_file).exists():
        print(f"\n⚠️  Input file '{task.input_file}' not found.")
        print("   Please provide a valid video file to test the dubbing process.")
        print("   You can modify this script to use your own video file.")
        return
    
    # Process the dubbing task
    print(f"\n🚀 Starting dubbing process...")
    try:
        result = await pipeline.process_task(task)
        
        if result["status"] == "completed":
            print(f"\n✅ Dubbing completed successfully!")
            print(f"📁 Output file: {result['output_file']}")
            
            # Show processing steps
            if "steps" in result:
                print(f"\n📊 Processing steps:")
                for step, info in result["steps"].items():
                    status = "✅" if info["status"] == "completed" else "⚠️"
                    print(f"   {status} {step.replace('_', ' ').title()}")
            
            # Show metrics if available
            if "metrics" in result and result["metrics"]:
                print(f"\n📈 Metrics:")
                for metric, value in result["metrics"].items():
                    print(f"   {metric}: {value}")
                    
        else:
            print(f"\n❌ Dubbing failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Error during dubbing: {str(e)}")


async def test_individual_modules():
    """Test individual modules to see what's available"""
    print("\n🧪 Testing individual modules...")
    print("=" * 50)
    
    # Test STT modules
    print("\n🎤 Testing STT modules:")
    try:
        from modules.stt import get_available_models as get_stt_models
        stt_models = get_stt_models()
        for name, model in stt_models.items():
            available = "✅" if model.is_available() else "❌"
            print(f"   {available} {name}: {model.description}")
    except Exception as e:
        print(f"   ❌ Error loading STT modules: {e}")
    
    # Test TTS modules
    print("\n🔊 Testing TTS modules:")
    try:
        from modules.tts import get_available_models as get_tts_models
        tts_models = get_tts_models()
        for name, model in tts_models.items():
            available = "✅" if model.is_available() else "❌"
            print(f"   {available} {name}: {model.description}")
    except Exception as e:
        print(f"   ❌ Error loading TTS modules: {e}")
    
    # Test Voice Cloning modules
    print("\n🎭 Testing Voice Cloning modules:")
    try:
        from modules.voice_cloning import get_available_models as get_vc_models
        vc_models = get_vc_models()
        for name, model in vc_models.items():
            available = "✅" if model.is_available() else "❌"
            print(f"   {available} {name}: {model.description}")
    except Exception as e:
        print(f"   ❌ Error loading Voice Cloning modules: {e}")
    
    # Test Lip Sync modules
    print("\n💋 Testing Lip Sync modules:")
    try:
        from modules.lip_sync import get_available_models as get_ls_models
        ls_models = get_ls_models()
        for name, model in ls_models.items():
            available = "✅" if model.is_available() else "❌"
            print(f"   {available} {name}: {model.description}")
    except Exception as e:
        print(f"   ❌ Error loading Lip Sync modules: {e}")


async def main():
    """Main function"""
    print("🎬 Unified Dubbing System - Example Script")
    print("=" * 60)
    
    # Test individual modules first
    await test_individual_modules()
    
    # Run basic dubbing example
    await basic_dubbing_example()
    
    print(f"\n🎉 Example completed!")
    print(f"\n💡 Next steps:")
    print(f"   1. Install required dependencies: pip install -r requirements.txt")
    print(f"   2. Download model files (see README.md)")
    print(f"   3. Provide a test video file")
    print(f"   4. Run the CLI: python -m unified_dubbing_system dub input.mp4 output.mp4 --target-lang es")


if __name__ == "__main__":
    asyncio.run(main())