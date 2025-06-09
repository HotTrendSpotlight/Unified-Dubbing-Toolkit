# Unified Dubbing System

A comprehensive, modular dubbing toolkit that integrates multiple speech-to-text, text-to-speech, voice cloning, and lip sync technologies into a single unified pipeline.

## Features

- **Multi-STT Support**: OpenAI Whisper, WhisperX, Faster Whisper, Whisper.cpp
- **Multi-TTS Support**: Bark TTS, Piper TTS, Kokoro TTS, Speaches TTS
- **Voice Cloning**: Real-Time Voice Cloning, AllVoiceLab, Misaki
- **Lip Sync**: Wav2Lip integration
- **Modular Architecture**: Plugin-based system for easy extension
- **Multiple Interfaces**: CLI, API, and Web UI
- **Batch Processing**: Process multiple files efficiently
- **Quality Control**: Multiple quality presets and settings

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/HotTrendSpotlight/Unified-Dubbing-Toolkit.git
cd Unified-Dubbing-Toolkit
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download required models (see [Model Setup](#model-setup))

### Basic Usage

```bash
# Dub a video from English to Spanish
python -m unified_dubbing_system dub input.mp4 output.mp4 --target-lang es

# Use specific models
python -m unified_dubbing_system dub input.mp4 output.mp4 \
  --target-lang fr \
  --stt-model whisperx \
  --tts-model bark

# With voice cloning
python -m unified_dubbing_system dub input.mp4 output.mp4 \
  --target-lang de \
  --voice-model reference_voice.wav

# List available models
python -m unified_dubbing_system list-models

# Batch processing
python -m unified_dubbing_system batch input_dir/ output_dir/ --target-lang es
```

## Architecture

```
unified-dubbing-system/
├── core/                    # Core pipeline and utilities
│   ├── pipeline.py         # Main orchestration pipeline
│   ├── utils.py            # Utility functions
│   └── __init__.py
├── modules/                # Modular components
│   ├── stt/               # Speech-to-Text modules
│   ├── tts/               # Text-to-Speech modules  
│   ├── voice_cloning/     # Voice cloning modules
│   ├── lip_sync/          # Lip sync modules
│   └── dubbing/           # High-level dubbing workflows
├── interfaces/            # User interfaces
│   ├── cli/              # Command line interface
│   └── api/              # REST API interface
├── config/               # Configuration files
├── models/               # Model storage
���── docs/                 # Documentation
```

## Model Setup

### STT Models

#### OpenAI Whisper
```bash
pip install openai-whisper
```

#### Faster Whisper
```bash
pip install faster-whisper
```

#### WhisperX
```bash
pip install whisperx
```

#### Whisper.cpp
Download and compile whisper.cpp binary from the official repository.

### TTS Models

#### Bark TTS
```bash
pip install bark
```

#### Piper TTS
```bash
pip install piper-tts
```

#### Kokoro TTS
```bash
pip install kokoro
```

### Voice Cloning Models

#### Real-Time Voice Cloning
1. Download pre-trained models:
   - `encoder.pt`
   - `synthesizer.pt` 
   - `vocoder.pt`
2. Place in `models/voice_cloning/`

### Lip Sync Models

#### Wav2Lip
1. Download `wav2lip_gan.pth` checkpoint
2. Place in `checkpoints/`
3. Ensure Wav2Lip repository is available

## Configuration

The system uses YAML configuration files. The main config is in `config/config.yaml`:

```yaml
# Example configuration
models:
  stt:
    default: "whisper"
    whisper:
      model_size: "base"
  tts:
    default: "bark"
    bark:
      voice_preset: "v2/en_speaker_6"
```

## API Usage

```python
from unified_dubbing_system import DubbingPipeline, DubbingTask

# Initialize pipeline
pipeline = DubbingPipeline("config/config.yaml")

# Create dubbing task
task = DubbingTask(
    input_file="input.mp4",
    output_file="output.mp4", 
    target_language="es",
    stt_model="whisper",
    tts_model="bark"
)

# Process task
result = await pipeline.process_task(task)
```

## Supported Languages

- English (en)
- Spanish (es)  
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)
- Arabic (ar)
- Hindi (hi)
- Turkish (tr)
- Polish (pl)
- Dutch (nl)
- Swedish (sv)
- Danish (da)
- Norwegian (no)
- Finnish (fi)

## Quality Settings

### Low Quality
- Video: 480p, 1Mbps
- Audio: 128kbps
- Fast processing

### Medium Quality (Default)
- Video: 720p, 2Mbps
- Audio: 192kbps
- Balanced quality/speed

### High Quality
- Video: 1080p, 4Mbps
- Audio: 320kbps
- Best quality, slower processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your module following the base class patterns
4. Submit a pull request

### Adding New Models

To add a new STT model:

1. Create a new file in `modules/stt/`
2. Inherit from `STTBase`
3. Implement required methods
4. Register in `modules/stt/__init__.py`

Similar patterns apply for TTS, voice cloning, and lip sync modules.

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Install FFmpeg and ensure it's in PATH
2. **Model files missing**: Download required model files
3. **CUDA out of memory**: Reduce batch sizes or use CPU
4. **Audio format errors**: Ensure input audio is supported

### Performance Tips

1. Use GPU acceleration when available
2. Adjust batch sizes based on available memory
3. Use appropriate quality settings for your needs
4. Enable parallel processing for batch jobs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI Whisper team
- Bark TTS by Suno AI
- Wav2Lip authors
- All the open-source projects integrated into this system

## Roadmap

- [ ] Web UI interface
- [ ] Real-time dubbing support
- [ ] More TTS engines
- [ ] Advanced voice cloning
- [ ] Multi-speaker support
- [ ] Translation integration
- [ ] Cloud deployment options