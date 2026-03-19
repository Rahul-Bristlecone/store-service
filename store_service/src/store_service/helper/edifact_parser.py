def parse_edifact(file_path: str) -> dict:
    """
    Reads an EDIFACT .edi file and returns parsed segments as a dict.
    """
    segments = {}
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # EDIFACT segments are usually separated by `'`
    for segment in content.split("'"):
        segment = segment.strip()
        if not segment:
            continue
        parts = [part.strip() for part in segment.split("+")]
        tag = parts[0]
        segments[tag] = parts
    return segments
