import os
import tempfile
from .pptx_to_pdf import pptx_to_pdf
from .pdf_to_png import pdf_to_png


def pptx_to_png(pptx_path, output_folder=None):
    """
    Converts each slide of the input PPTX to a PNG image.

    Args:
        pptx_path (str): Path to the input PPTX file.
        output_folder (str, optional): Directory to save PNG images. Defaults to PPTX's directory.

    Returns:
        List[str]: List of file paths to the generated PNG images.
    """
    # Step 1: Convert PPTX to PDF
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = pptx_to_pdf(pptx_path, temp_dir)
        # Step 2: Convert PDF to PNG
        png_files = pdf_to_png(pdf_path, output_folder)
    return png_files
