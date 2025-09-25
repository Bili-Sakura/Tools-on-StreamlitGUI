# Tools-on-StreamlitGUI

A simple web-based toolset for file conversion, powered by Streamlit.  
**Convert your files easily in your browser!**

## 🚀 Live Demo

This app is ready for deployment on Streamlit Cloud! Simply fork this repository and deploy it directly.

## Features

- **PDF to PNG**: Convert each page of a PDF file into PNG images with bulk download
- **PPTX to PDF**: Convert PowerPoint presentations (`.pptx`) to PDF documents
- **PPTX to PNG**: Convert each slide of a PowerPoint presentation into PNG images
- **M4A to MP3**: Convert audio files from M4A format to MP3
- **MP4 to MP3**: Extract the audio from MP4 videos as MP3 files
- **Audio/Video to Subtitles**: Generate SRT subtitles using OpenAI Whisper API
- **SRT Translator**: Translate subtitle files using AI (OpenAI, Aliyun DashScope, or OpenRouter)
- **Chat LLM**: Chat interface with Aliyun Bailian models

## 🌐 Deployment Options

### Streamlit Cloud (Recommended)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account and select this repository
4. Set the main file path to `main.py`
5. Deploy!

For features requiring API keys (Chat LLM, Audio to Subtitles, SRT Translator):

- Add your API keys in the app's "Secrets" section in Streamlit Cloud dashboard
- Format: `DASHSCOPE_API_KEY = "your_key_here"` or `OPENAI_API_KEY = "your_key_here"` or `OPENROUTER_API_KEY = "your_key_here"`

### Local Installation

```bash
conda create -n tools python=3.10 -y
conda activate tools
pip install -r requirements.txt
```

### Local Run

```bash
streamlit run main.py
```

## Usage

1. Open your browser to the Streamlit app (usually at `http://localhost:8501`)
2. Use the sidebar to select a tool
3. Upload your file(s)
4. Configure any necessary settings
5. Click the convert button and download your results!

## Dependencies

- All file conversions work out of the box on Streamlit Cloud
- PDF processing uses `poppler-utils` (automatically installed via `packages.txt`)
- Audio conversion uses `ffmpeg` (automatically installed via `packages.txt`)
- PPTX to PDF uses `libreoffice` (automatically installed via `packages.txt`)

## API Keys and Environment (.env)

Create a `.env` in the project root or set environment variables:

- **Chat LLM (Aliyun)**: `DASHSCOPE_API_KEY`
- **Audio/Video to Subtitles (OpenAI Whisper)**: `OPENAI_API_KEY`
- **SRT Translator**: `DASHSCOPE_API_KEY` (Aliyun) or `OPENAI_API_KEY` (OpenAI) or `OPENROUTER_API_KEY` (OpenRouter)

Optional attribution headers for OpenRouter (used for leaderboard attribution):

- `OPENROUTER_SITE_URL` (maps to `HTTP-Referer`)
- `OPENROUTER_APP_TITLE` (maps to `X-Title`)

Example `.env`:

```env
# Aliyun DashScope (Chat LLM, SRT Translator)
DASHSCOPE_API_KEY=

# OpenAI (Whisper, SRT Translator)
OPENAI_API_KEY=

# OpenRouter (SRT Translator)
OPENROUTER_API_KEY=
# Optional OpenRouter attribution
OPENROUTER_SITE_URL=
OPENROUTER_APP_TITLE=

# Optional: override model for all providers (leave unset to use provider defaults)
# For OpenAI default is gpt-4.1; for DashScope default is qwen-max; for OpenRouter default is openai/gpt-4o
# MODEL=
```

Defaults:

- OpenAI provider default model: `gpt-4.1` (uses Responses API)
- Aliyun DashScope default model: `qwen-max`
- OpenRouter default model: `openai/gpt-4o`

CLI example for SRT translation:

```sh
# OpenAI
python tools/translate_srt.py input.srt output.srt --target-lang zh --provider openai --model gpt-4.1 --workers 5

# OpenRouter
python tools/translate_srt.py input.srt output.srt --target-lang zh --provider openrouter --model openai/gpt-4o --workers 5

# DashScope
python tools/translate_srt.py input.srt output.srt --target-lang zh --provider dashscope --model qwen-max --workers 5
```

---
