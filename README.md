# Tools-on-StreamlitGUI

A simple web-based toolset for file conversion, powered by Streamlit.  
**Convert your files easily in your browser!**

## Features

- **PDF to PNG**: Convert each page of a PDF file into PNG images.
- **PPTX to PDF**: Convert PowerPoint presentations (`.pptx`) to PDF documents.
- **PPTX to PNG**: Convert each slide of a PowerPoint presentation into PNG images.
- **M4A to MP3**: Convert audio files from M4A format to MP3.
- **MP4 to MP3**: Extract the audio from MP4 videos as MP3 files.

## Installation

```bash
conda create -n tools python=3.10 -y
conda activate tools
pip install -r requirements.txt
```

## Run

```bash
streamlit run main.py
```

## Usage

1. Open your browser to the Streamlit app (usually at `http://localhost:8501`).
2. Use the sidebar to select a tool.
3. Upload your file and choose an output folder (or use the default).
4. Click the convert button and download your results!

---
