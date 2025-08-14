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
- **SRT Translator**: Translate subtitle files using AI (OpenAI or Aliyun DashScope)
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
- Format: `DASHSCOPE_API_KEY = "your_key_here"` or `OPENAI_API_KEY = "your_key_here"`

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

## API Keys (Optional Features)

Some features require API keys:
- **Chat LLM**: Requires `DASHSCOPE_API_KEY` from Aliyun
- **Audio to Subtitles**: Requires `OPENAI_API_KEY` from OpenAI
- **SRT Translator**: Requires either `DASHSCOPE_API_KEY` or `OPENAI_API_KEY`

---
