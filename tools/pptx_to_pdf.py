import os
import sys
import platform
import subprocess


def pptx_to_pdf(pptx_path, output_folder=None):
    """
    Converts a PPTX file to PDF.
    - On Windows: Uses Microsoft PowerPoint via COM automation.
    - On Linux: Uses LibreOffice in headless mode.

    Args:
        pptx_path (str): Path to the input PPTX file.
        output_folder (str, optional): Directory to save the PDF. Defaults to PPTX's directory.

    Returns:
        str: Path to the generated PDF file.
    """
    system = platform.system()
    if output_folder is None:
        output_folder = os.path.dirname(pptx_path)
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(pptx_path))[0]
    pdf_path = os.path.join(output_folder, f"{base_name}.pdf")

    if system == "Windows":
        try:
            import win32com.client
        except ImportError:
            raise ImportError(
                "pywin32 is required on Windows. Install it with 'pip install pywin32'."
            )

        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        powerpoint.Visible = 1

        try:
            presentation = powerpoint.Presentations.Open(pptx_path, WithWindow=False)
            presentation.SaveAs(pdf_path, FileFormat=32)  # 32 for PDF
            presentation.Close()
        finally:
            powerpoint.Quit()

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not created: {pdf_path}")
        return pdf_path

    elif system == "Linux":
        command = [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            output_folder,
            pptx_path,
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError(
                f"LibreOffice conversion failed: {result.stderr.decode()}"
            )
        if not os.path.exists(pdf_path):
            # Sometimes LibreOffice outputs with .PDF (uppercase) or with spaces, so check for alternatives
            for file in os.listdir(output_folder):
                if file.lower() == f"{base_name}.pdf":
                    os.rename(os.path.join(output_folder, file), pdf_path)
                    break
            else:
                raise FileNotFoundError(f"PDF not created: {pdf_path}")
        return pdf_path

    else:
        raise NotImplementedError(f"pptx_to_pdf is not supported on {system}.")
