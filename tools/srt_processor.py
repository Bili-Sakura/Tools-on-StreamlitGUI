"""
Unified SRT processing module combining resegmentation and translation functionality.
"""

import os
import re
import concurrent.futures
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env if present
load_dotenv(override=True)


# ============================================================================
# Core SRT Utilities
# ============================================================================


def read_srt(file_path: str) -> str:
    """Read SRT file content."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_srt(file_path: str, content: str) -> None:
    """Write content to SRT file."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def parse_srt_blocks(srt_content: str) -> List[Tuple[str, str, List[str]]]:
    """
    Parse SRT content into blocks.
    Returns list of (index, time, text_lines).
    """
    blocks = re.split(r"\n\s*\n", srt_content.strip(), flags=re.MULTILINE)
    parsed: List[Tuple[str, str, List[str]]] = []
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue
        index = lines[0].strip()
        time_line = lines[1].strip()
        text_lines = [line.rstrip() for line in lines[2:]]
        parsed.append((index, time_line, text_lines))
    return parsed


def parse_srt_block(block: str) -> Optional[Tuple[str, str, List[str]]]:
    """Parse a single SRT block."""
    lines = block.strip().splitlines()
    if len(lines) < 3:
        return None
    index = lines[0]
    time = lines[1]
    text_lines = lines[2:]
    return index, time, text_lines


def build_srt_block(index: int, start_time: str, end_time: str, text: str) -> str:
    """Build SRT block with index, time range, and text."""
    return f"{index}\n{start_time} --> {end_time}\n{text}"


def build_srt_block_from_lines(index: str, time: str, text_lines: List[str]) -> str:
    """Build SRT block from parsed components."""
    return f"{index}\n{time}\n" + "\n".join(text_lines)


# ============================================================================
# Time Utilities
# ============================================================================


def extract_times(time_line: str) -> Tuple[str, str]:
    """Extract start and end times from time line."""
    # Expected format: HH:MM:SS,mmm --> HH:MM:SS,mmm
    parts = [p.strip() for p in time_line.split("-->")]
    if len(parts) != 2:
        raise ValueError(f"Invalid time line: {time_line}")
    return parts[0], parts[1]


def time_str_to_ms(t: str) -> int:
    """Convert time string to milliseconds."""
    # HH:MM:SS,mmm
    hms, ms = t.split(",")
    hours, minutes, seconds = hms.split(":")
    total_ms = (
        int(hours) * 3600 * 1000
        + int(minutes) * 60 * 1000
        + int(seconds) * 1000
        + int(ms)
    )
    return total_ms


def ms_to_time_str(ms: int) -> str:
    """Convert milliseconds to time string."""
    if ms < 0:
        ms = 0
    hours = ms // (3600 * 1000)
    ms %= 3600 * 1000
    minutes = ms // (60 * 1000)
    ms %= 60 * 1000
    seconds = ms // 1000
    millis = ms % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


# ============================================================================
# Text Processing Utilities
# ============================================================================


def ends_with_preferred_punctuation(text: str) -> bool:
    """Check if text ends with preferred punctuation."""
    stripped = text.rstrip()
    return stripped.endswith(".") or stripped.endswith(",")


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    return re.sub(r"\s+", " ", text).strip()


def count_chars(text: str) -> int:
    """Count characters including spaces after normalization."""
    return len(text)


def split_text_into_chunks_by_chars_with_punctuation(
    text: str, max_chars: int
) -> List[str]:
    """Split text into chunks respecting punctuation boundaries."""
    text = normalize_whitespace(text)
    chunks: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        remaining = text[i:]
        if len(remaining) <= max_chars:
            chunks.append(remaining.strip())
            break
        window = remaining[:max_chars]
        # Prefer last '.' or ',' within the window
        last_dot = window.rfind(".")
        last_comma = window.rfind(",")
        cut_at = max(last_dot, last_comma)
        if cut_at != -1:
            end = cut_at + 1
        else:
            # If no punctuation found, look for the last space to avoid cutting words
            last_space = window.rfind(" ")
            if last_space != -1:
                end = last_space
            else:
                # If no space found, we have to cut at max_chars (single long word)
                end = max_chars
        chunk = remaining[:end].strip()
        if chunk:
            chunks.append(chunk)
        i += end
        # Skip any following spaces before next chunk
        while i < n and text[i] == " ":
            i += 1
    return [c for c in chunks if c]


# ============================================================================
# Translation Functionality
# ============================================================================


def translate_text(
    text: str, target_lang: str, model: str, router: str = "dashscope"
) -> str:
    """Translate text using specified provider."""
    if router == "dashscope":
        client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
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

    elif router == "openrouter":
        client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
        prompt = (
            f"Translate the following subtitle text to {target_lang}. "
            "Do not translate timestamps or numbers. Only translate the spoken text. "
            "Return only the translated text, no explanations or formatting.\n\n"
            f"{text}"
        )
        # Optional attribution headers
        extra_headers = {}
        referer = os.getenv("OPENROUTER_SITE_URL")
        app_title = os.getenv("OPENROUTER_APP_TITLE")
        if referer:
            extra_headers["HTTP-Referer"] = referer
        if app_title:
            extra_headers["X-Title"] = app_title
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
            extra_headers=extra_headers,
        )
        return response.choices[0].message.content.strip()

    elif router == "openai":
        client = OpenAI()
        prompt = (
            f"Translate the following subtitle text to {target_lang}. "
            "Do not translate timestamps or numbers. Only translate the spoken text. "
            "Return only the translated text, no explanations or formatting.\n\n"
            f"{text}"
        )
        try:
            # Use Responses API for newer models (e.g., gpt-4.1, gpt-4o)
            if model and (model.startswith("gpt-4.1") or model.startswith("gpt-4o")):
                response = client.responses.create(
                    model=model,
                    input=prompt,
                    instructions="You are a helpful assistant that translates subtitles.",
                    temperature=0.3,
                    max_output_tokens=1024,
                )
                # Prefer helper if available
                try:
                    return response.output_text.strip()
                except Exception:
                    # Fallback parsing if helper is unavailable
                    try:
                        segments = []
                        if hasattr(response, "output") and response.output:
                            for content_item in response.output[0].content:
                                text_val = getattr(content_item, "text", None)
                                if text_val:
                                    segments.append(text_val)
                        if segments:
                            return "\n".join(segments).strip()
                    except Exception:
                        pass
                    return str(response).strip()
            else:
                # Backward compatibility: use Chat Completions for older models
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
        except Exception as e:
            # Last-resort fallback to ensure we return something
            return str(e)
    else:
        return f"Unsupported provider: {router}"


def translate_block(args: Tuple[str, str, str, str]) -> str:
    """Translate a single SRT block."""
    block, target_lang, model, router = args
    parsed = parse_srt_block(block)
    if not parsed:
        return block
    index, time, text_lines = parsed
    text = "\n".join(text_lines)
    if text.strip():
        translated_text = translate_text(text, target_lang, model=model, router=router)
        translated_text_lines = translated_text.splitlines() or [translated_text]
    else:
        translated_text_lines = text_lines
    translated_block = build_srt_block_from_lines(index, time, translated_text_lines)
    return translated_block


def translate_srt(
    input_path: str,
    output_path: str,
    target_lang: str,
    model: Optional[str] = None,
    workers: int = 15,
    router: str = "dashscope",
) -> str:
    """Translate SRT file using specified provider."""
    # Check API keys based on router
    if router == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Error: OPENAI_API_KEY not found in environment variables."
            )
        if not model:
            model = os.getenv("MODEL") or "gpt-4.1"
    elif router == "openrouter":
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_key:
            raise RuntimeError(
                "Error: OPENROUTER_API_KEY not found in environment variables."
            )
        if not model:
            model = os.getenv("MODEL") or "openai/gpt-4o"
    elif router == "dashscope":
        dashscope_key = os.getenv("DASHSCOPE_API_KEY")
        if not dashscope_key:
            raise RuntimeError(
                "Error: DASHSCOPE_API_KEY not found in environment variables."
            )
        if not model:
            model = os.getenv("MODEL") or "qwen-max"
    else:
        raise RuntimeError(
            f"Error: Unknown provider '{router}'. Expected one of: openai, openrouter, dashscope."
        )

    srt_content = read_srt(input_path)
    blocks = re.split(r"\n\s*\n", srt_content.strip(), flags=re.MULTILINE)
    block_args = [(block, target_lang, model, router) for block in blocks]
    translated_blocks = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        for translated_block in executor.map(translate_block, block_args):
            translated_blocks.append(translated_block)
    translated_content = "\n\n".join(translated_blocks)
    write_srt(output_path, translated_content)
    return output_path


# ============================================================================
# Resegmentation Functionality
# ============================================================================


def resegment_blocks(
    parsed_blocks: List[Tuple[str, str, List[str]]], max_chars: int
) -> List[str]:
    """Resegment SRT blocks based on character limit."""
    output_blocks: List[str] = []

    current_index = 1
    group_start_time: str = ""
    group_end_time: str = ""
    group_text_parts: List[str] = []
    group_char_count = 0

    def flush_group():
        nonlocal current_index, group_start_time, group_end_time, group_text_parts, group_char_count
        if group_char_count > 0 and group_text_parts:
            block_text = normalize_whitespace(" ".join(group_text_parts))
            output_blocks.append(
                build_srt_block(
                    current_index, group_start_time, group_end_time, block_text
                )
            )
            current_index += 1
            group_start_time = ""
            group_end_time = ""
            group_text_parts = []
            group_char_count = 0

    for _, time_line, text_lines in parsed_blocks:
        start_time_str, end_time_str = extract_times(time_line)
        start_ms = time_str_to_ms(start_time_str)
        end_ms = time_str_to_ms(end_time_str)
        duration_ms = max(0, end_ms - start_ms)

        text = normalize_whitespace(" ".join(text_lines))
        if not text:
            continue

        this_count = count_chars(text)

        # If adding this block would exceed the limit, flush the current group first
        if group_char_count > 0 and (group_char_count + this_count) > max_chars:
            flush_group()

        # If the single block itself exceeds max_chars, split it internally
        if this_count > max_chars:
            # Ensure any pending group is flushed before inserting split pieces
            flush_group()
            sub_texts = split_text_into_chunks_by_chars_with_punctuation(
                text, max_chars
            )
            # Distribute timings proportionally by character count
            total_chars = sum(count_chars(st) for st in sub_texts) or 1
            accumulated_ms = 0
            for idx, st in enumerate(sub_texts):
                chars_in_chunk = count_chars(st) or 1
                # compute chunk duration (last chunk takes remaining to avoid rounding drift)
                if idx < len(sub_texts) - 1:
                    chunk_ms = int(duration_ms * (chars_in_chunk / total_chars))
                else:
                    chunk_ms = max(0, duration_ms - accumulated_ms)
                chunk_start_ms = start_ms + accumulated_ms
                chunk_end_ms = chunk_start_ms + chunk_ms
                accumulated_ms += chunk_ms

                output_blocks.append(
                    build_srt_block(
                        current_index,
                        ms_to_time_str(chunk_start_ms),
                        ms_to_time_str(chunk_end_ms),
                        st,
                    )
                )
                current_index += 1
            # Done with this overlong block
            continue

        # Otherwise, safe to merge this whole block into the group
        if group_char_count == 0:
            group_start_time = start_time_str
        group_text_parts.append(text)
        group_end_time = end_time_str
        group_char_count += this_count

        # Prefer flushing on punctuation at the end of this block
        if ends_with_preferred_punctuation(text):
            flush_group()
        elif group_char_count >= max_chars:
            flush_group()

    # Flush any remaining group
    if group_char_count > 0:
        flush_group()

    return output_blocks


def resegment_srt(input_path: str, output_path: str, max_chars: int = 125) -> str:
    """Resegment SRT file based on character limit."""
    srt_content = read_srt(input_path)
    parsed = parse_srt_blocks(srt_content)
    merged_blocks = resegment_blocks(parsed, max_chars=max_chars)
    output_content = "\n\n".join(merged_blocks) + "\n"
    write_srt(output_path, output_content)
    return output_path


# ============================================================================
# Combined Processing Functions
# ============================================================================


def process_srt_file(
    input_path: str,
    output_path: str,
    operation: str = "resegment",
    max_chars: int = 125,
    target_lang: Optional[str] = None,
    model: Optional[str] = None,
    workers: int = 15,
    router: str = "dashscope",
) -> str:
    """
    Process SRT file with specified operation.

    Args:
        input_path: Path to input SRT file
        output_path: Path to output SRT file
        operation: "resegment", "translate", or "both"
        max_chars: Maximum characters per segment (for resegmentation)
        target_lang: Target language code (for translation)
        model: Model to use for translation
        workers: Number of concurrent workers for translation
        router: Translation provider ("dashscope", "openai", "openrouter")

    Returns:
        Path to output file
    """
    if operation == "resegment":
        return resegment_srt(input_path, output_path, max_chars)
    elif operation == "translate":
        if not target_lang:
            raise ValueError("target_lang is required for translation")
        return translate_srt(
            input_path, output_path, target_lang, model, workers, router
        )
    elif operation == "both":
        if not target_lang:
            raise ValueError("target_lang is required for translation")
        # First translate, then resegment
        temp_path = output_path + ".temp"
        translate_srt(input_path, temp_path, target_lang, model, workers, router)
        result = resegment_srt(temp_path, output_path, max_chars)
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return result
    else:
        raise ValueError(
            f"Unknown operation: {operation}. Must be 'resegment', 'translate', or 'both'"
        )


# ============================================================================
# CLI Interface (for backward compatibility)
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified SRT processing tool for resegmentation and translation."
    )
    parser.add_argument("input", help="Input SRT file path")
    parser.add_argument("output", help="Output SRT file path")
    parser.add_argument(
        "--operation",
        choices=["resegment", "translate", "both"],
        default="resegment",
        help="Operation to perform (default: resegment)",
    )
    parser.add_argument(
        "--max-chars",
        dest="max_chars",
        type=int,
        default=125,
        help="Maximum characters per segment (default: 125)",
    )
    parser.add_argument(
        "--target-lang", help="Target language code (e.g., fr, es, de, zh)"
    )
    parser.add_argument(
        "--model", help="Model to use for translation (default: value of MODEL in .env)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=15,
        help="Number of concurrent workers for translation (default: 15)",
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "dashscope", "openrouter"],
        default="dashscope",
        help="Translation provider (default: dashscope)",
    )

    args = parser.parse_args()

    try:
        result = process_srt_file(
            args.input,
            args.output,
            operation=args.operation,
            max_chars=args.max_chars,
            target_lang=args.target_lang,
            model=args.model,
            workers=args.workers,
            router=args.provider,
        )
        print(f"Processing complete. Output written to {result}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
