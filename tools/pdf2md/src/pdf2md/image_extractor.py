from __future__ import annotations

from pathlib import Path
from typing import Literal

from rich.console import Console

from pdf2md.models import Block, ExtractedPage

console = Console(stderr=True)


def extract_images(
    pdf_path: Path,
    pages: list[ExtractedPage],
    image_dir: Path,
    image_format: Literal["png", "jpg"],
    verbose: bool = False,
) -> None:
    """Extract embedded images from the PDF and save to *image_dir*.

    Appends the saved file path to ``page.image_paths`` for each image
    found.  Existing image blocks in ``page.blocks`` are left in place so
    the markdown builder can insert ``![image](path)`` at the correct
    position.
    """
    try:
        import fitz  # type: ignore[import-untyped]
    except ImportError:
        console.print("[yellow]PyMuPDF not available; skipping image extraction.[/]")
        return

    page_map: dict[int, ExtractedPage] = {p.page_number: p for p in pages}

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as exc:
        if verbose:
            console.print(f"[yellow]Cannot reopen {pdf_path} for images: {exc}[/]")
        return

    image_dir.mkdir(parents=True, exist_ok=True)
    ext = image_format.lower()

    try:
        for page_obj in doc:
            page_num = page_obj.number + 1
            extracted = page_map.get(page_num)
            if extracted is None:
                continue

            for img_index, img_info in enumerate(page_obj.get_images(full=True)):
                xref: int = img_info[0]
                try:
                    base_image = doc.extract_image(xref)
                    img_bytes: bytes = base_image["image"]
                    original_ext: str = base_image.get("ext", "png")

                    # Convert to target format via Pixmap when needed
                    if original_ext.lower() != ext:
                        pixmap = fitz.Pixmap(doc, xref)
                        if pixmap.alpha:
                            pixmap = fitz.Pixmap(fitz.csRGB, pixmap)
                        img_bytes = pixmap.tobytes(output=ext)

                    filename = f"page{page_num}_img{img_index + 1}.{ext}"
                    out_path = image_dir / filename
                    out_path.write_bytes(img_bytes)
                    extracted.image_paths.append(out_path)

                    if verbose:
                        console.print(f"  [dim]Saved image: {out_path}[/]")

                except Exception as exc:
                    if verbose:
                        console.print(
                            f"[yellow]Could not extract image xref={xref} on page {page_num}: {exc}[/]"
                        )
    finally:
        doc.close()
