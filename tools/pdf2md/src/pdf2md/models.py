from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class Span:
    text: str
    font_name: str
    font_size: float
    is_bold: bool
    is_italic: bool
    is_monospace: bool


@dataclass
class Block:
    spans: list[Span]
    block_type: Literal["text", "image", "table"]
    bbox: tuple[float, float, float, float]  # x0, y0, x1, y1
    page_number: int
    heading_level: int | None = None  # None = body, 1-3 = H1-H3
    is_code_block: bool = False


@dataclass
class Table:
    cells: list[list[str | None]]  # row-major 2D list; None = empty/merged
    page_number: int
    bbox: tuple[float, float, float, float]


@dataclass
class ExtractedPage:
    page_number: int
    blocks: list[Block] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    image_paths: list[Path] = field(default_factory=list)
    raw_font_sizes: list[float] = field(default_factory=list)


@dataclass
class DocumentStats:
    median_font_size: float
    h1_threshold: float
    h2_threshold: float
    h3_threshold: float


@dataclass
class ConversionConfig:
    input_path: Path
    output_path: Path
    page_range: str | None = None       # e.g. "1-5" or "1,3,5-7"
    no_images: bool = False
    no_tables: bool = False
    no_code_blocks: bool = False
    image_format: Literal["png", "jpg"] = "png"
    chunk_by_heading: bool = False
    metadata: bool = False
    verbose: bool = False
