from docling.document_converter import DocumentConverter
from pathlib import Path


def export_pdfs_to_markdown(input_folder: str, output_folder: str):
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True, parents=True)

    converter = DocumentConverter()
    pdf_files = list(input_path.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF found in {input_folder}")
        return

    for i, pdf_file in enumerate(pdf_files, 1):
        md_filename = pdf_file.stem + ".md"
        md_path = output_path / md_filename

        if md_path.exists():
            print(f"[{i}/{len(pdf_files)}] Skipping {pdf_file.name} (MD exists)")
            continue

        print(f"[{i}/{len(pdf_files)}] Converting: {pdf_file.name}")

        try:
            result = converter.convert(str(pdf_file))
            markdown_text = result.document.export_to_markdown()

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(markdown_text)
            print(f"    Saved: {md_path}")

        except Exception as e:
            print(f"    Error {pdf_file.name}: {e}\n")
            continue


if __name__ == "__main__":
    export_pdfs_to_markdown(input_folder="data/pdf", output_folder="data/markdown")
