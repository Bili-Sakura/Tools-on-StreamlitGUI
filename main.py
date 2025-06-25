import streamlit as st
import os
from tools import pptx_to_png, pdf_to_png, pptx_to_pdf,m4a_to_mp3


st.set_page_config(page_title="Tools-on-StreamlitGUI", layout="centered")


def pdf_to_png_page():
    st.header("PDF to PNG Converter")

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    # Set default output folder as current directory + ./output
    default_output_folder = os.path.join(os.getcwd(), "output")

    # Use session state to store the output folder
    if "output_folder" not in st.session_state:
        st.session_state["output_folder"] = default_output_folder

    # Button to autofill with current working directory + ./output
    if st.button("Use Current Directory"):
        st.session_state["output_folder"] = default_output_folder

    output_folder = st.text_input(
        label="Paste or type the output folder path:",
        value=st.session_state["output_folder"],
        help="Paste the folder path here. You can click 'Use Current Directory' to autofill with the default output folder (./output in current directory). Leave blank to use the default output directory.",
        key="output_folder_widget",
    )

    # Validate the folder path
    if output_folder.strip():
        if os.path.isdir(output_folder):
            st.success(f"Folder exists: {output_folder}")
        else:
            st.warning(f"Folder does not exist: {output_folder}")
    else:
        st.info(
            f"No folder selected. Will use the default output directory: {default_output_folder}"
        )

    if uploaded_file is not None:
        # Save uploaded PDF to a temporary location
        temp_pdf_path = os.path.join("temp_uploaded.pdf")
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("Convert to PNG"):
            # Use user-specified output folder or default to current directory + ./output
            base_out_folder = (
                output_folder
                if output_folder.strip() and os.path.isdir(output_folder)
                else default_output_folder
            )
            # Get PDF file name without extension
            pdf_name = uploaded_file.name
            pdf_base_name = os.path.splitext(os.path.basename(pdf_name))[0]
            # Create subfolder under output folder with same name as PDF file
            out_folder = os.path.join(base_out_folder, pdf_base_name)
            # Create the output subfolder if it doesn't exist
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

        # Clean up temp file after use
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)


def pptx_to_pdf_page():
    st.header("PPTX to PDF Converter")

    uploaded_file = st.file_uploader("Upload a PPTX file", type=["pptx"])

    # Set default output folder as current directory + ./output
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

    # Validate the folder path
    if output_folder.strip():
        if os.path.isdir(output_folder):
            st.success(f"Folder exists: {output_folder}")
        else:
            st.warning(f"Folder does not exist: {output_folder}")
    else:
        st.info(
            f"No folder selected. Will use the default output directory: {default_output_folder}"
        )

    if uploaded_file is not None:
        # Save uploaded PPTX to a temporary location
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

        # Clean up temp file after use
        if os.path.exists(temp_pptx_path):
            os.remove(temp_pptx_path)


def pptx_to_png_page():
    st.header("PPTX to PNG Converter")

    uploaded_file = st.file_uploader(
        "Upload a PPTX file", type=["pptx"], key="pptx_to_png_uploader"
    )

    # Set default output folder as current directory + ./output
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

    # Validate the folder path
    if output_folder.strip():
        if os.path.isdir(output_folder):
            st.success(f"Folder exists: {output_folder}")
        else:
            st.warning(f"Folder does not exist: {output_folder}")
    else:
        st.info(
            f"No folder selected. Will use the default output directory: {default_output_folder}"
        )

    if uploaded_file is not None:
        # Save uploaded PPTX to a temporary location
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

        # Clean up temp file after use
        if os.path.exists(temp_pptx_path):
            os.remove(temp_pptx_path)

def m4a_to_mp3_page():
    st.header("M4A to MP3 Converter")

    uploaded_file = st.file_uploader("Upload an M4A file", type=["m4a"])

    # Set default output folder as current directory + ./output
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

    # Validate the folder path
    if output_folder.strip():
        if os.path.isdir(output_folder):
            st.success(f"Folder exists: {output_folder}")
        else:
            st.warning(f"Folder does not exist: {output_folder}")
    else:
        st.info(
            f"No folder selected. Will use the default output directory: {default_output_folder}"
        )

    if uploaded_file is not None:
        # Save uploaded M4A to a temporary location
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

        # Clean up temp file after use
        if os.path.exists(temp_m4a_path):
            os.remove(temp_m4a_path)

def home_page():
    st.title("Tools-on-StreamlitGUI")
    st.markdown(
        """
        Welcome! Please select a tool from the sidebar to get started.
        """
    )


# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to", ("Home", "PDF to PNG", "PPTX to PDF", "PPTX to PNG", "M4A to MP3"), index=0
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
