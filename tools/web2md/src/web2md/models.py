from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class ConversionConfig:
    url: str
    output_path: Path
    no_images: bool = False
    no_tables: bool = False
    chunk_by_heading: bool = False
    metadata: bool = False
    verbose: bool = False


def url_to_slug(url: str) -> str:
    """Convert a URL to a filesystem-safe slug for use as a filename stem.

    https://docs.example.com/guide/intro/ → docs-example-com_guide_intro
    """
    parsed = urlparse(url)
    netloc = parsed.netloc.replace(".", "-")
    path_part = parsed.path.strip("/")
    path_part = re.sub(r"[^\w/-]", "", path_part)
    path_part = path_part.replace("/", "_")
    if path_part:
        return f"{netloc}_{path_part}"
    return netloc
