import streamlit as st
import os
from tools import pdf_to_png

st.title("PDF to PNG Converter")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
output_folder = st.text_input(
    "Output folder (optional, leave blank to use PDF's directory):"
)

if uploaded_file is not None:
    # Save uploaded PDF to a temporary location
    temp_pdf_path = os.path.join("temp_uploaded.pdf")
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("Convert to PNG"):
        # Use user-specified output folder or default to current directory
        out_folder = output_folder if output_folder.strip() else None
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
