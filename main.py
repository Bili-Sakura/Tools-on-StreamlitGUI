import streamlit as st
from pages import (
    pdf_to_png_page,
    pptx_to_pdf_page,
    pptx_to_png_page,
    m4a_to_mp3_page,
    mp4_to_mp3_page,
    translate_srt_page,
    home_page,
    chat_llm_page,
    audio_to_subtitle_page,
    resegment_srt_page,
)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    (
        "Home",
        "PDF to PNG",
        "PPTX to PDF",
        "PPTX to PNG",
        "M4A to MP3",
        "MP4 to MP3",
        "Audio/Video to Subtitles",
        "SRT Translator",
        "Chat LLM",
        "SRT Resegmentation",
    ),
    index=0,
)

if page == "Home":
    home_page()
elif page == "PDF to PNG":
    pdf_to_png_page()
elif page == "PPTX to PDF":
    pptx_to_pdf_page()
elif page == "PPTX to PNG":
    pptx_to_png_page()
elif page == "M4A to MP3":
    m4a_to_mp3_page()
elif page == "MP4 to MP3":
    mp4_to_mp3_page()
elif page == "Audio/Video to Subtitles":
    audio_to_subtitle_page()
elif page == "SRT Translator":
    translate_srt_page()
elif page == "Chat LLM":  # <-- Add this
    chat_llm_page()
elif page == "SRT Resegmentation":
    resegment_srt_page()
