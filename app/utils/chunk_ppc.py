from pathlib import Path
import json

CHUNK_SIZE = 2000


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE):
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end
    return chunks


def chunk_ppct(input_folder: str, output_folder: str):
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True, parents=True)

    md_files = list(input_path.glob("*.md"))

    if not md_files:
        print(f"No .md found in {input_folder}")
        return

    for i, md_file in enumerate(md_files, 1):
        json_output_path = output_path / f"{md_file.stem}_chunks.json"

        if json_output_path.exists():
            print(f"[{i}/{len(md_files)}] Skipping {md_file.name} (JSON exists)")
            continue

        print(f"[{i}/{len(md_files)}] Processing: {md_file.name}")

        try:
            text = md_file.read_text(encoding="utf-8")
            chunks = chunk_text(text)
            data = [
                {"id": f"{md_file.stem}_{idx}", "text": chunk, "source": md_file.name}
                for idx, chunk in enumerate(chunks)
            ]
            with open(json_output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"    Saved chunks: {json_output_path}")

        except Exception as e:
            print(f"    Error processing {md_file.name}: {e}\n")
            continue


if __name__ == "__main__":
    chunk_ppct(input_folder="data/markdown", output_folder="data/chunks")
