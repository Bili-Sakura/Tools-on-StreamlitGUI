from pdf2image import convert_from_path
import os


def pdf_to_png(pdf_path, output_folder=None, dpi=200):
    """
    Converts each page of the input PDF to a PNG image.

    Args:
        pdf_path (str): Path to the input PDF file.
        output_folder (str, optional): Directory to save PNG images. Defaults to PDF's directory.
        dpi (int, optional): Dots per inch for the output images. Defaults to 200.

    Returns:
        List[str]: List of file paths to the generated PNG images.
    """
    if output_folder is None:
        output_folder = os.path.dirname(pdf_path)
    images = convert_from_path(pdf_path, dpi=dpi)
    output_files = []
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    for i, image in enumerate(images):
        output_file = os.path.join(output_folder, f"{base_name}_page_{i+1}.png")
        image.save(output_file, "PNG")
        output_files.append(output_file)
    return output_files
