import os
import concurrent.futures
import openai
from dotenv import load_dotenv
import re

# Load environment variables from .env if present
load_dotenv(override=True)

def read_srt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def write_srt(file_path, content):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def parse_srt_blocks(srt_content):
    blocks = re.split(r'\n\s*\n', srt_content.strip(), flags=re.MULTILINE)
    return blocks

def parse_srt_block(block):
    lines = block.strip().splitlines()
    if len(lines) < 3:
        return None
    index = lines[0]
    time = lines[1]
    text_lines = lines[2:]
    return index, time, text_lines

def build_srt_block(index, time, text_lines):
    return f"{index}\n{time}\n" + "\n".join(text_lines)

def translate_text(text, target_lang, model, router="dashscope"):
    if router == "dashscope":
        from openai import OpenAI
        import os
        client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
    else:
        from openai import OpenAI
        client = OpenAI()
    prompt = (
        f"Translate the following subtitle text to {target_lang}. "
        "Do not translate timestamps or numbers. Only translate the spoken text. "
        "Return only the translated text, no explanations or formatting.\n\n"
        f"{text}"
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that translates subtitles.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()

def translate_block(args):
    block, target_lang, model = args
    parsed = parse_srt_block(block)
    if not parsed:
        return block
    index, time, text_lines = parsed
    text = "\n".join(text_lines)
    if text.strip():
        translated_text = translate_text(text, target_lang, model=model)
        translated_text_lines = translated_text.splitlines() or [translated_text]
    else:
        translated_text_lines = text_lines
    translated_block = build_srt_block(index, time, translated_text_lines)
    return translated_block

def translate_srt(input_path, output_path, target_lang, model=None, workers=15):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise RuntimeError("Error: OPENAI_API_KEY not found in environment variables.")

    if not model:
        model = os.getenv("MODEL")
    srt_content = read_srt(input_path)
    blocks = parse_srt_blocks(srt_content)
    block_args = [(block, target_lang, model) for block in blocks]
    translated_blocks = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        for translated_block in executor.map(translate_block, block_args):
            translated_blocks.append(translated_block)
    translated_content = "\n\n".join(translated_blocks)
    write_srt(output_path, translated_content)
    return output_path

# CLI usage preserved for backward compatibility
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Translate SRT subtitle files using OpenAI GPT models."
    )
    parser.add_argument("input", help="Input SRT file")
    parser.add_argument("output", help="Output SRT file")
    parser.add_argument(
        "--target-lang", required=True, help="Target language code (e.g., fr, es, de)"
    )
    parser.add_argument(
        "--model",
        default=None,
        help="model to use (default: value of MODEL in .env)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=15,
        help="Number of concurrent workers for translation (default: 15)",
    )
    args = parser.parse_args()
    translate_srt(args.input, args.output, args.target_lang, args.model, args.workers)
    print(f"Translation complete. Output written to {args.output}")