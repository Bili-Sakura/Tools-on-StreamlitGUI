import re
from typing import List, Tuple


def read_srt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_srt(file_path: str, content: str) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def parse_srt_blocks(srt_content: str) -> List[Tuple[str, str, List[str]]]:
    # Returns list of (index, time, text_lines)
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


def extract_times(time_line: str) -> Tuple[str, str]:
    # Expected format: HH:MM:SS,mmm --> HH:MM:SS,mmm
    parts = [p.strip() for p in time_line.split("-->")]
    if len(parts) != 2:
        raise ValueError(f"Invalid time line: {time_line}")
    return parts[0], parts[1]


def time_str_to_ms(t: str) -> int:
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
    if ms < 0:
        ms = 0
    hours = ms // (3600 * 1000)
    ms %= 3600 * 1000
    minutes = ms // (60 * 1000)
    ms %= 60 * 1000
    seconds = ms // 1000
    millis = ms % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def ends_with_preferred_punctuation(text: str) -> bool:
    stripped = text.rstrip()
    return stripped.endswith(".") or stripped.endswith(",")


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def count_chars(text: str) -> int:
    # Count characters including spaces after normalization
    return len(text)


def split_text_into_chunks_by_chars_with_punctuation(text: str, max_chars: int) -> List[str]:
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
            end = max_chars
        chunk = remaining[:end].strip()
        if chunk:
            chunks.append(chunk)
        i += end
        # Skip any following spaces before next chunk
        while i < n and text[i] == " ":
            i += 1
    return [c for c in chunks if c]


def build_srt_block(index: int, start_time: str, end_time: str, text: str) -> str:
    # Keep text as a single line to avoid arbitrary rewrapping
    return f"{index}\n{start_time} --> {end_time}\n{text}"


def resegment_blocks(parsed_blocks: List[Tuple[str, str, List[str]]], max_chars: int) -> List[str]:
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
                build_srt_block(current_index, group_start_time, group_end_time, block_text)
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
            sub_texts = split_text_into_chunks_by_chars_with_punctuation(text, max_chars)
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
    srt_content = read_srt(input_path)
    parsed = parse_srt_blocks(srt_content)
    merged_blocks = resegment_blocks(parsed, max_chars=max_chars)
    output_content = "\n\n".join(merged_blocks) + "\n"
    write_srt(output_path, output_content)
    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Resegment an English SRT so each subtitle segment contains fewer than a given number of characters. "
            "Prefer cutting on ',' or '.' within or between original blocks; otherwise cut at the character limit. "
            "Timings are preserved by merging whole blocks and proportionally splitting overlong blocks."
        )
    )
    parser.add_argument("input", help="Input SRT file path")
    parser.add_argument("output", help="Output SRT file path")
    parser.add_argument(
        "--max-chars",
        dest="max_chars",
        type=int,
        default=125,
        help="Maximum characters per segment (default: 125)",
    )

    args = parser.parse_args()

    out = resegment_srt(args.input, args.output, max_chars=args.max_chars)
    print(f"Resegmented SRT written to {out}") 