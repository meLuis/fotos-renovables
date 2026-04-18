"""
Convierte .jpg/.jpeg/.avif a .webp conservando la orientación EXIF.
Los .webp quedan en el mismo lugar que los originales.
Los originales se mueven al backup en el Escritorio.

Uso: py convert_to_webp.py
"""

import os, sys, shutil
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    print("Instalando Pillow...")
    os.system(f"{sys.executable} -m pip install Pillow")
    from PIL import Image, ImageOps

ROOT   = Path(__file__).parent
BACKUP = Path.home() / "Desktop" / "backup-fotos-renovables-jpg"
EXTS   = {".jpg", ".jpeg", ".avif"}

# Calidad 85 → ~60-70% menos peso que JPG sin diferencia visual apreciable
QUALITY = 85

def convert(src: Path) -> str:
    """Retorna 'ok', 'skip' o 'error'."""
    dst_webp = src.with_suffix(".webp")

    if dst_webp.exists():
        return "skip"

    try:
        with Image.open(src) as img:
            img = ImageOps.exif_transpose(img)   # corrige rotación EXIF
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")
            img.save(dst_webp, "WEBP", quality=QUALITY, method=6)

        # Mover JPG al backup conservando subcarpeta
        backup_dst = BACKUP / src.relative_to(ROOT)
        backup_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(backup_dst))
        return "ok"

    except Exception as e:
        print(f"    [ERROR] {src.relative_to(ROOT)}: {e}")
        return "error"


def main():
    imgs = sorted(p for p in ROOT.rglob("*")
                  if p.suffix.lower() in EXTS and p.is_file())

    total = len(imgs)
    if total == 0:
        print("No se encontraron archivos .jpg/.jpeg/.avif.")
        return

    print(f"Encontrados : {total} archivos")
    print(f"Backup      : {BACKUP}\n")

    ok = skip = err = 0
    for i, img in enumerate(imgs, 1):
        rel    = img.relative_to(ROOT)
        result = convert(img)
        if result == "ok":
            ok += 1
            print(f"  [{i:>4}/{total}] OK    {rel}")
        elif result == "skip":
            skip += 1
            print(f"  [{i:>4}/{total}] SKIP  {rel.with_suffix('.webp')} (ya existe)")
        else:
            err += 1

    print(f"\n{'='*52}")
    print(f"  Convertidos : {ok}  → .webp en su lugar, original en backup")
    print(f"  Saltados    : {skip}  (el .webp ya existía)")
    print(f"  Errores     : {err}")
    print(f"{'='*52}")


if __name__ == "__main__":
    main()