import streamlit as st
import os
from tools import pptx_to_png, pdf_to_png, pptx_to_pdf, m4a_to_mp3, mp4_to_mp3
from tools.translate_srt import translate_srt
import openai
from dotenv import load_dotenv
import re

# Load environment variables from .env if present
load_dotenv(override=True)


def chat_llm_page():
    st.header("Chat with LLM (Bailian Aliyun)")
    import os
    from openai import OpenAI

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    user_input = st.text_input("You:", key="chat_input")
    if st.button("Send", key="chat_send") and user_input.strip():
        st.session_state["chat_history"].append({"role": "user", "content": user_input})

        # Prepare messages for OpenAI API
        messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state["chat_history"]]

        # Use Bailian Aliyun DashScope API
        try:
            client = OpenAI(
                api_key=os.getenv("DASHSCOPE_API_KEY"),
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

        st.session_state["chat_history"].append({"role": "assistant", "content": assistant_reply})

    # Display chat history
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Assistant:** {msg['content']}")
    

def pdf_to_png_page():
    st.header("PDF to PNG Converter")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    default_output_folder = os.path.join(os.getcwd(), "output")
    if "output_folder" not in st.session_state:
        st.session_state["output_folder"] = default_output_folder
    if st.button("Use Current Directory"):
        st.session_state["output_folder"] = default_output_folder
    output_folder = st.text_input(
        label="Paste or type the output folder path:",
        value=st.session_state["output_folder"],
        help="Paste the folder path here. You can click 'Use Current Directory' to autofill with the default output folder (./output in current directory). Leave blank to use the default output directory.",
        key="output_folder_widget",
    )
    if output_folder.strip():
        if os.path.isdir(output_folder):
            st.success(f"Folder exists: {output_folder}")
        else:
            st.warning(f"Folder does not exist: {output_folder}")
    else:
        st.info(f"No folder selected. Will use the default output directory: {default_output_folder}")
    if uploaded_file is not None:
        temp_pdf_path = os.path.join("temp_uploaded.pdf")
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        if st.button("Convert to PNG"):
            base_out_folder = (
                output_folder
                if output_folder.strip() and os.path.isdir(output_folder)
                else default_output_folder
            )
            pdf_name = uploaded_file.name
            pdf_base_name = os.path.splitext(os.path.basename(pdf_name))[0]
            out_folder = os.path.join(base_out_folder, pdf_base_name)
            if not os.path.isdir(out_folder):
                os.makedirs(out_folder, exist_ok=True)
            png_files = pdf_to_png(temp_pdf_path, out_folder)
            st.success(f"Converted {len(png_files)} page(s) to PNG.")
            for png_file in png_files:
                st.image(png_file, caption=os.path.basename(png_file))
                with open(png_file, "rb") as img_f:
                    st.download_button(
                        label=f"Download {os.path.basename(png_file)}",
                        data=img_f,
                        file_name=os.path.basename(png_file),
                        mime="image/png",
                    )
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

def pptx_to_pdf_page():
    st.header("PPTX to PDF Converter")
    uploaded_file = st.file_uploader("Upload a PPTX file", type=["pptx"])
    default_output_folder = os.path.join(os.getcwd(), "output")
    if "pptx_output_folder" not in st.session_state:
        st.session_state["pptx_output_folder"] = default_output_folder
    if st.button("Use Current Directory", key="pptx_use_current_dir"):
        st.session_state["pptx_output_folder"] = default_output_folder
    output_folder = st.text_input(
        label="Paste or type the output folder path:",
        value=st.session_state["pptx_output_folder"],
        help="Paste the folder path here. You can click 'Use Current Directory' to autofill with the default output folder (./output in current directory). Leave blank to use the default output directory.",
        key="pptx_output_folder_widget",
    )
    if output_folder.strip():
        if os.path.isdir(output_folder):
            st.success(f"Folder exists: {output_folder}")
        else:
            st.warning(f"Folder does not exist: {output_folder}")
    else:
        st.info(f"No folder selected. Will use the default output directory: {default_output_folder}")
    if uploaded_file is not None:
        temp_pptx_path = os.path.join("temp_uploaded.pptx")
        with open(temp_pptx_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        if st.button("Convert to PDF"):
            base_out_folder = (
                output_folder
                if output_folder.strip() and os.path.isdir(output_folder)
                else default_output_folder
            )
            pptx_name = uploaded_file.name
            pptx_base_name = os.path.splitext(os.path.basename(pptx_name))[0]
            out_folder = os.path.join(base_out_folder, pptx_base_name)
            if not os.path.isdir(out_folder):
                os.makedirs(out_folder, exist_ok=True)
            try:
                pdf_file = pptx_to_pdf(temp_pptx_path, out_folder)
                st.success(f"Converted to PDF: {os.path.basename(pdf_file)}")
                with open(pdf_file, "rb") as pdf_f:
                    st.download_button(
                        label=f"Download {os.path.basename(pdf_file)}",
                        data=pdf_f,
                        file_name=os.path.basename(pdf_file),
                        mime="application/pdf",
                    )
            except Exception as e:
                st.error(f"Conversion failed: {e}")
        if os.path.exists(temp_pptx_path):
            os.remove(temp_pptx_path)

def pptx_to_png_page():
    st.header("PPTX to PNG Converter")
    uploaded_file = st.file_uploader(
        "Upload a PPTX file", type=["pptx"], key="pptx_to_png_uploader"
    )
    default_output_folder = os.path.join(os.getcwd(), "output")
    if "pptx_png_output_folder" not in st.session_state:
        st.session_state["pptx_png_output_folder"] = default_output_folder
    if st.button("Use Current Directory", key="pptx_png_use_current_dir"):
        st.session_state["pptx_png_output_folder"] = default_output_folder
    output_folder = st.text_input(
        label="Paste or type the output folder path:",
        value=st.session_state["pptx_png_output_folder"],
        help="Paste the folder path here. You can click 'Use Current Directory' to autofill with the default output folder (./output in current directory). Leave blank to use the default output directory.",
        key="pptx_png_output_folder_widget",
    )
    if output_folder.strip():
        if os.path.isdir(output_folder):
            st.success(f"Folder exists: {output_folder}")
        else:
            st.warning(f"Folder does not exist: {output_folder}")
    else:
        st.info(f"No folder selected. Will use the default output directory: {default_output_folder}")
    if uploaded_file is not None:
        temp_pptx_path = os.path.join("temp_uploaded_pptx_to_png.pptx")
        with open(temp_pptx_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        if st.button("Convert to PNG"):
            base_out_folder = (
                output_folder
                if output_folder.strip() and os.path.isdir(output_folder)
                else default_output_folder
            )
            pptx_name = uploaded_file.name
            pptx_base_name = os.path.splitext(os.path.basename(pptx_name))[0]
            out_folder = os.path.join(base_out_folder, pptx_base_name)
            if not os.path.isdir(out_folder):
                os.makedirs(out_folder, exist_ok=True)
            try:
                png_files = pptx_to_png(temp_pptx_path, out_folder)
                st.success(f"Converted {len(png_files)} slide(s) to PNG.")
                for png_file in png_files:
                    st.image(png_file, caption=os.path.basename(png_file))
                    with open(png_file, "rb") as img_f:
                        st.download_button(
                            label=f"Download {os.path.basename(png_file)}",
                            data=img_f,
                            file_name=os.path.basename(png_file),
                            mime="image/png",
                        )
            except Exception as e:
                st.error(f"Conversion failed: {e}")
        if os.path.exists(temp_pptx_path):
            os.remove(temp_pptx_path)

def m4a_to_mp3_page():
    st.header("M4A to MP3 Converter")
    uploaded_file = st.file_uploader("Upload an M4A file", type=["m4a"])
    default_output_folder = os.path.join(os.getcwd(), "output")
    if "m4a_output_folder" not in st.session_state:
        st.session_state["m4a_output_folder"] = default_output_folder
    if st.button("Use Current Directory", key="m4a_use_current_dir"):
        st.session_state["m4a_output_folder"] = default_output_folder
    output_folder = st.text_input(
        label="Paste or type the output folder path:",
        value=st.session_state["m4a_output_folder"],
        help="Paste the folder path here. You can click 'Use Current Directory' to autofill with the default output folder (./output in current directory). Leave blank to use the default output directory.",
        key="m4a_output_folder_widget",
    )
    if output_folder.strip():
        if os.path.isdir(output_folder):
            st.success(f"Folder exists: {output_folder}")
        else:
            st.warning(f"Folder does not exist: {output_folder}")
    else:
        st.info(f"No folder selected. Will use the default output directory: {default_output_folder}")
    if uploaded_file is not None:
        temp_m4a_path = os.path.join("temp_uploaded.m4a")
        with open(temp_m4a_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        if st.button("Convert to MP3"):
            base_out_folder = (
                output_folder
                if output_folder.strip() and os.path.isdir(output_folder)
                else default_output_folder
            )
            m4a_name = uploaded_file.name
            m4a_base_name = os.path.splitext(os.path.basename(m4a_name))[0]
            out_folder = os.path.join(base_out_folder, m4a_base_name)
            if not os.path.isdir(out_folder):
                os.makedirs(out_folder, exist_ok=True)
            mp3_file = os.path.join(out_folder, m4a_base_name + ".mp3")
            try:
                result_mp3 = m4a_to_mp3(temp_m4a_path, mp3_file)
                st.success(f"Converted to MP3: {os.path.basename(result_mp3)}")
                with open(result_mp3, "rb") as mp3_f:
                    st.download_button(
                        label=f"Download {os.path.basename(result_mp3)}",
                        data=mp3_f,
                        file_name=os.path.basename(result_mp3),
                        mime="audio/mpeg",
                    )
            except Exception as e:
                st.error(f"Conversion failed: {e}")
        if os.path.exists(temp_m4a_path):
            os.remove(temp_m4a_path)

def mp4_to_mp3_page():
    st.header("MP4 to MP3 Converter")
    uploaded_file = st.file_uploader("Upload an MP4 file", type=["mp4"])
    default_output_folder = os.path.join(os.getcwd(), "output")
    if "mp4_output_folder" not in st.session_state:
        st.session_state["mp4_output_folder"] = default_output_folder
    if st.button("Use Current Directory", key="mp4_use_current_dir"):
        st.session_state["mp4_output_folder"] = default_output_folder
    output_folder = st.text_input(
        label="Paste or type the output folder path:",
        value=st.session_state["mp4_output_folder"],
        help="Paste the folder path here. You can click 'Use Current Directory' to autofill with the default output folder (./output in current directory). Leave blank to use the default output directory.",
        key="mp4_output_folder_widget",
    )
    if output_folder.strip():
        if os.path.isdir(output_folder):
            st.success(f"Folder exists: {output_folder}")
        else:
            st.warning(f"Folder does not exist: {output_folder}")
    else:
        st.info(f"No folder selected. Will use the default output directory: {default_output_folder}")
    if uploaded_file is not None:
        temp_mp4_path = os.path.join("temp_uploaded.mp4")
        with open(temp_mp4_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        if st.button("Convert to MP3", key="mp4_convert_button"):
            base_out_folder = (
                output_folder if output_folder.strip() and os.path.isdir(output_folder) else default_output_folder
            )
            mp4_name = uploaded_file.name
            mp4_base_name = os.path.splitext(os.path.basename(mp4_name))[0]
            out_folder = os.path.join(base_out_folder, mp4_base_name)
            if not os.path.isdir(out_folder):
                os.makedirs(out_folder, exist_ok=True)
            mp3_file = os.path.join(out_folder, mp4_base_name + ".mp3")
            try:
                result_mp3 = mp4_to_mp3(temp_mp4_path, mp3_file)
                st.success(f"Converted to MP3: {os.path.basename(result_mp3)}")
                with open(result_mp3, "rb") as mp3_f:
                    st.download_button(
                        label=f"Download {os.path.basename(result_mp3)}",
                        data=mp3_f,
                        file_name=os.path.basename(result_mp3),
                        mime="audio/mpeg",
                    )
            except Exception as e:
                st.error(f"Conversion failed: {e}")
        if os.path.exists(temp_mp4_path):
            os.remove(temp_mp4_path)

def translate_srt_page():
    st.header("SRT Subtitle Translator")
    uploaded_file = st.file_uploader("Upload an SRT file", type=["srt"])
    target_lang = st.text_input("Target language code (e.g., fr, es, de, zh)", value="zh")
    model = st.text_input("OpenAI model (leave blank for default)", value="")
    workers = st.number_input("Number of concurrent workers", min_value=1, max_value=50, value=5)
    default_output_folder = os.path.join(os.getcwd(), "output")
    if "srt_output_folder" not in st.session_state:
        st.session_state["srt_output_folder"] = default_output_folder
    if st.button("Use Current Directory", key="srt_use_current_dir"):
        st.session_state["srt_output_folder"] = default_output_folder
    output_folder = st.text_input(
        label="Paste or type the output folder path:",
        value=st.session_state["srt_output_folder"],
        help="Paste the folder path here. You can click 'Use Current Directory' to autofill with the default output folder (./output in current directory).",
        key="srt_output_folder_widget",
    )
    if uploaded_file is not None:
        temp_srt_path = os.path.join("temp_uploaded.srt")
        with open(temp_srt_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        srt_name = uploaded_file.name
        srt_base_name = os.path.splitext(os.path.basename(srt_name))[0]
        out_folder = output_folder if output_folder.strip() and os.path.isdir(output_folder) else default_output_folder
        if not os.path.isdir(out_folder):
            os.makedirs(out_folder, exist_ok=True)
        output_srt_path = os.path.join(out_folder, f"{srt_base_name}_{target_lang}.srt")
        if st.button("Translate SRT"):
            try:
                translate_srt(temp_srt_path, output_srt_path, target_lang, model or None, workers)
                st.success(f"Translation complete. Output written to {output_srt_path}")
                with open(output_srt_path, "rb") as srt_f:
                    st.download_button(
                        label=f"Download {os.path.basename(output_srt_path)}",
                        data=srt_f,
                        file_name=os.path.basename(output_srt_path),
                        mime="text/plain",
                    )
            except Exception as e:
                st.error(f"Translation failed: {e}")
        if os.path.exists(temp_srt_path):
            os.remove(temp_srt_path)

def home_page():
    st.title("Tools-on-StreamlitGUI")
    st.markdown(
        """
        Welcome! Please select a tool from the sidebar to get started.
        """
    )