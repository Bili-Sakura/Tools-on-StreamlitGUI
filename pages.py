import streamlit as st
import os
import tempfile
import zipfile
from io import BytesIO
from tools import (
    pptx_to_png,
    pdf_to_png,
    pptx_to_pdf,
    m4a_to_mp3,
    mp4_to_mp3,
    audio_to_subtitle,
)
from tools import process_srt_file
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv(override=True)


# Create a temporary directory for processing files
@st.cache_resource
def get_temp_dir():
    """Get or create a temporary directory for file processing"""
    temp_dir = tempfile.mkdtemp()
    return temp_dir


def chat_llm_page():
    st.header("Chat with LLM (Bailian Aliyun)")
    from openai import OpenAI

    # Check if API key is available
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        st.warning(
            "⚠️ DASHSCOPE_API_KEY environment variable is not set. Please configure your API key to use this feature."
        )
        st.info(
            "To use this feature in Streamlit Cloud, add your API key in the app's secrets management."
        )
        return

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    user_input = st.text_input("You:", key="chat_input")
    if st.button("Send", key="chat_send") and user_input.strip():
        st.session_state["chat_history"].append({"role": "user", "content": user_input})

        # Prepare messages for OpenAI API
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state["chat_history"]
        ]

        # Use Bailian Aliyun DashScope API
        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
            response = client.chat.completions.create(
                model="qwen-max",  # or your preferred DashScope model
                messages=messages,
                # temperature=0.7,
                # max_tokens=4096,
            )
            assistant_reply = response.choices[0].message.content.strip()
        except Exception as e:
            assistant_reply = f"Error: {e}"

        st.session_state["chat_history"].append(
            {"role": "assistant", "content": assistant_reply}
        )

    # Display chat history
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Assistant:** {msg['content']}")


def pdf_to_png_page():
    st.header("PDF to PNG Converter")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        # Use temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(uploaded_file.getbuffer())
            temp_pdf_path = temp_pdf.name

        if st.button("Convert to PNG"):
            try:
                # Create temporary output directory
                temp_output_dir = tempfile.mkdtemp()
                png_files = pdf_to_png(temp_pdf_path, temp_output_dir)

                st.success(f"Converted {len(png_files)} page(s) to PNG.")

                # Create zip file with all PNGs for bulk download
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for png_file in png_files:
                        zip_file.write(png_file, os.path.basename(png_file))

                # Display images and provide individual downloads
                for png_file in png_files:
                    st.image(png_file, caption=os.path.basename(png_file), width=400)
                    with open(png_file, "rb") as img_f:
                        st.download_button(
                            label=f"Download {os.path.basename(png_file)}",
                            data=img_f.read(),
                            file_name=os.path.basename(png_file),
                            mime="image/png",
                            key=f"download_{os.path.basename(png_file)}",
                        )

                # Bulk download button
                pdf_base_name = os.path.splitext(uploaded_file.name)[0]
                st.download_button(
                    label="Download All PNG Files (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name=f"{pdf_base_name}_pages.zip",
                    mime="application/zip",
                )

                # Clean up temporary files
                for png_file in png_files:
                    if os.path.exists(png_file):
                        os.remove(png_file)
                os.rmdir(temp_output_dir)

            except Exception as e:
                st.error(f"Conversion failed: {str(e)}")
            finally:
                # Clean up temp PDF
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)


def pptx_to_pdf_page():
    st.header("PPTX to PDF Converter")
    uploaded_file = st.file_uploader("Upload a PPTX file", type=["pptx"])

    if uploaded_file is not None:
        # Use temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as temp_pptx:
            temp_pptx.write(uploaded_file.getbuffer())
            temp_pptx_path = temp_pptx.name

        if st.button("Convert to PDF"):
            try:
                # Create temporary output directory
                temp_output_dir = tempfile.mkdtemp()
                pdf_file = pptx_to_pdf(temp_pptx_path, temp_output_dir)

                st.success(f"Converted to PDF: {os.path.basename(pdf_file)}")

                # Provide download
                with open(pdf_file, "rb") as pdf_f:
                    pptx_base_name = os.path.splitext(uploaded_file.name)[0]
                    st.download_button(
                        label=f"Download {pptx_base_name}.pdf",
                        data=pdf_f.read(),
                        file_name=f"{pptx_base_name}.pdf",
                        mime="application/pdf",
                    )

                # Clean up temporary files
                if os.path.exists(pdf_file):
                    os.remove(pdf_file)
                os.rmdir(temp_output_dir)

            except Exception as e:
                st.error(f"Conversion failed: {str(e)}")
            finally:
                # Clean up temp PPTX
                if os.path.exists(temp_pptx_path):
                    os.remove(temp_pptx_path)


def pptx_to_png_page():
    st.header("PPTX to PNG Converter")
    uploaded_file = st.file_uploader(
        "Upload a PPTX file", type=["pptx"], key="pptx_to_png_uploader"
    )

    if uploaded_file is not None:
        # Use temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as temp_pptx:
            temp_pptx.write(uploaded_file.getbuffer())
            temp_pptx_path = temp_pptx.name

        if st.button("Convert to PNG"):
            try:
                # Create temporary output directory
                temp_output_dir = tempfile.mkdtemp()
                png_files = pptx_to_png(temp_pptx_path, temp_output_dir)

                st.success(f"Converted {len(png_files)} slide(s) to PNG.")

                # Create zip file with all PNGs for bulk download
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for png_file in png_files:
                        zip_file.write(png_file, os.path.basename(png_file))

                # Display images and provide individual downloads
                for png_file in png_files:
                    st.image(png_file, caption=os.path.basename(png_file), width=400)
                    with open(png_file, "rb") as img_f:
                        st.download_button(
                            label=f"Download {os.path.basename(png_file)}",
                            data=img_f.read(),
                            file_name=os.path.basename(png_file),
                            mime="image/png",
                            key=f"download_pptx_{os.path.basename(png_file)}",
                        )

                # Bulk download button
                pptx_base_name = os.path.splitext(uploaded_file.name)[0]
                st.download_button(
                    label="Download All PNG Files (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name=f"{pptx_base_name}_slides.zip",
                    mime="application/zip",
                )

                # Clean up temporary files
                for png_file in png_files:
                    if os.path.exists(png_file):
                        os.remove(png_file)
                os.rmdir(temp_output_dir)

            except Exception as e:
                st.error(f"Conversion failed: {str(e)}")
            finally:
                # Clean up temp PPTX
                if os.path.exists(temp_pptx_path):
                    os.remove(temp_pptx_path)


def m4a_to_mp3_page():
    st.header("M4A to MP3 Converter")
    uploaded_file = st.file_uploader("Upload an M4A file", type=["m4a"])

    if uploaded_file is not None:
        # Use temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_m4a:
            temp_m4a.write(uploaded_file.getbuffer())
            temp_m4a_path = temp_m4a.name

        if st.button("Convert to MP3"):
            try:
                # Create temporary output file
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp3"
                ) as temp_mp3:
                    temp_mp3_path = temp_mp3.name

                result_mp3 = m4a_to_mp3(temp_m4a_path, temp_mp3_path)
                st.success(f"Converted to MP3: {uploaded_file.name}")

                # Provide download
                with open(result_mp3, "rb") as mp3_f:
                    m4a_base_name = os.path.splitext(uploaded_file.name)[0]
                    st.download_button(
                        label=f"Download {m4a_base_name}.mp3",
                        data=mp3_f.read(),
                        file_name=f"{m4a_base_name}.mp3",
                        mime="audio/mpeg",
                    )

                # Clean up temporary MP3 file
                if os.path.exists(result_mp3):
                    os.remove(result_mp3)

            except Exception as e:
                st.error(f"Conversion failed: {str(e)}")
            finally:
                # Clean up temp M4A
                if os.path.exists(temp_m4a_path):
                    os.remove(temp_m4a_path)


def mp4_to_mp3_page():
    st.header("MP4 to MP3 Converter")
    uploaded_file = st.file_uploader("Upload an MP4 file", type=["mp4"])

    if uploaded_file is not None:
        # Use temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_mp4:
            temp_mp4.write(uploaded_file.getbuffer())
            temp_mp4_path = temp_mp4.name

        if st.button("Convert to MP3", key="mp4_convert_button"):
            try:
                # Create temporary output file
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp3"
                ) as temp_mp3:
                    temp_mp3_path = temp_mp3.name

                result_mp3 = mp4_to_mp3(temp_mp4_path, temp_mp3_path)
                st.success(f"Converted to MP3: {uploaded_file.name}")

                # Provide download
                with open(result_mp3, "rb") as mp3_f:
                    mp4_base_name = os.path.splitext(uploaded_file.name)[0]
                    st.download_button(
                        label=f"Download {mp4_base_name}.mp3",
                        data=mp3_f.read(),
                        file_name=f"{mp4_base_name}.mp3",
                        mime="audio/mpeg",
                    )

                # Clean up temporary MP3 file
                if os.path.exists(result_mp3):
                    os.remove(result_mp3)

            except Exception as e:
                st.error(f"Conversion failed: {str(e)}")
            finally:
                # Clean up temp MP4
                if os.path.exists(temp_mp4_path):
                    os.remove(temp_mp4_path)


def audio_to_subtitle_page():
    st.header("Audio/Video to Subtitle Converter")
    st.write(
        "Convert audio or video files to SRT subtitle format using OpenAI Whisper API"
    )

    # File uploader for audio/video files
    uploaded_file = st.file_uploader(
        "Upload an audio or video file",
        type=["mp3", "mp4", "m4a", "wav", "flac", "aac", "avi", "mov", "mkv", "webm"],
    )

    # Configuration options
    st.subheader("Configuration")
    chunk_length_minutes = st.slider(
        "Audio chunk length (minutes)",
        min_value=1,
        max_value=30,
        value=10,
        help="Longer chunks may be more accurate but will take longer to process and may hit API limits",
    )

    # OpenAI API Key input (optional)
    api_key = st.text_input(
        "OpenAI API Key (optional)",
        type="password",
        help="If not provided, will use OPENAI_API_KEY environment variable",
    )

    if uploaded_file is not None:
        # Get file extension to create appropriate temp file
        file_extension = os.path.splitext(uploaded_file.name)[1]

        # Use temporary file for processing
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=file_extension
        ) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_file_path = temp_file.name

        st.info(f"File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")

        if st.button("Generate Subtitles", key="subtitle_convert_button"):
            with st.spinner(
                "Converting audio/video to subtitles... This may take a while for long files."
            ):
                try:
                    # Convert to subtitles
                    chunk_length_ms = chunk_length_minutes * 60 * 1000
                    srt_content = audio_to_subtitle(
                        temp_file_path,
                        chunk_length_ms=chunk_length_ms,
                        api_key=api_key if api_key.strip() else None,
                    )

                    st.success(f"Subtitles generated successfully!")

                    # Display preview of subtitles
                    st.subheader("Subtitle Preview")
                    lines = srt_content.split("\n")
                    preview_lines = lines[: min(20, len(lines))]  # Show first 20 lines
                    st.text("\n".join(preview_lines))
                    if len(lines) > 20:
                        st.info(
                            f"Showing first 20 lines. Full file has {len(lines)} lines."
                        )

                    # Download button
                    file_base_name = os.path.splitext(uploaded_file.name)[0]
                    st.download_button(
                        label=f"Download {file_base_name}.srt",
                        data=srt_content,
                        file_name=f"{file_base_name}.srt",
                        mime="text/plain",
                    )

                except Exception as e:
                    st.error(f"Subtitle generation failed: {e}")
                    st.error("Please check your OpenAI API key and try again.")
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)


def combined_srt_page():
    st.header("SRT Processing")
    uploaded_file = st.file_uploader(
        "Upload an SRT file", type=["srt"], key="combined_srt_uploader"
    )

    # Operation selection
    operation = st.selectbox(
        "Processing Operation",
        options=["Translate only", "Resegment only", "Translate + Resegment"],
        index=2,
        help="Choose what operation to perform on the SRT file",
    )

    # Map operation names to internal values
    operation_map = {
        "Translate only": "translate",
        "Resegment only": "resegment",
        "Translate + Resegment": "both",
    }
    operation_value = operation_map[operation]

    # Translation settings (only show if translation is needed)
    if operation_value in ["translate", "both"]:
        st.subheader("Translation Settings")
        target_lang = st.text_input(
            "Target language code (e.g., fr, es, de, zh)", value="zh"
        )

        # Provider selection
        provider = st.selectbox(
            "Translation Provider",
            options=["Aliyun (DashScope)", "OpenAI", "OpenRouter"],
            index=0,
            help="Choose the translation provider: Aliyun DashScope, OpenAI, or OpenRouter",
        )

        # Model selection based on provider
        if provider == "OpenAI":
            model = st.text_input(
                "OpenAI model (leave blank for default)",
                value="gpt-4.1",
                help="e.g., gpt-4.1, gpt-4o",
            )
        elif provider == "OpenRouter":
            model = st.text_input(
                "OpenRouter model (leave blank for default)",
                value="openai/gpt-4o",
                help="e.g., openai/gpt-4o, anthropic/claude-3.5-sonnet",
            )
        else:
            model = st.text_input(
                "Aliyun model (leave blank for default)",
                value="qwen-max",
                help="e.g., qwen-max, qwen-plus",
            )

        workers = st.number_input(
            "Number of concurrent workers", min_value=1, max_value=50, value=5
        )
    else:
        # Default values when translation is not needed
        target_lang = None
        provider = "dashscope"
        model = None
        workers = 5

    # Resegmentation settings (only show if resegmentation is needed)
    if operation_value in ["resegment", "both"]:
        st.subheader("Resegmentation Settings")
        max_chars = st.number_input(
            "Maximum characters per segment",
            min_value=10,
            max_value=500,
            value=125,
            step=5,
        )
    else:
        # Default value when resegmentation is not needed
        max_chars = 125

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as temp_srt:
            temp_srt.write(uploaded_file.getbuffer())
            temp_srt_path = temp_srt.name

        button_text = f"Process SRT ({operation})"
        if st.button(button_text, key="combined_srt_button"):
            try:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".srt"
                ) as temp_output:
                    output_srt_path = temp_output.name

                # Determine router based on provider selection
                if provider == "OpenAI":
                    router = "openai"
                elif provider == "OpenRouter":
                    router = "openrouter"
                else:
                    router = "dashscope"

                process_srt_file(
                    temp_srt_path,
                    output_srt_path,
                    operation=operation_value,
                    max_chars=int(max_chars),
                    target_lang=target_lang,
                    model=model or None,
                    workers=workers,
                    router=router,
                )

                st.success(f"Processing complete! ({operation})")

                with open(output_srt_path, "r", encoding="utf-8") as srt_f:
                    result_content = srt_f.read()

                srt_base_name = os.path.splitext(uploaded_file.name)[0]

                # Generate appropriate filename based on operation
                if operation_value == "translate":
                    filename = f"{srt_base_name}_{target_lang}.srt"
                    label = f"Download {srt_base_name}_{target_lang}.srt"
                elif operation_value == "resegment":
                    filename = f"{srt_base_name}_resentenced.srt"
                    label = f"Download {srt_base_name}_resentenced.srt"
                else:  # both
                    filename = f"{srt_base_name}_{target_lang}_processed.srt"
                    label = f"Download {srt_base_name}_{target_lang}_processed.srt"

                st.download_button(
                    label=label,
                    data=result_content,
                    file_name=filename,
                    mime="text/plain",
                )

                if os.path.exists(output_srt_path):
                    os.remove(output_srt_path)

            except Exception as e:
                st.error(f"Processing failed: {e}")
            finally:
                if os.path.exists(temp_srt_path):
                    os.remove(temp_srt_path)


def home_page():
    st.title("Tools-on-StreamlitGUI")
    st.markdown(
        """
        Welcome! Please select a tool from the sidebar to get started.
        """
    )
