from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import OUTPUT_DIR


def load_font(size):
    possible_fonts = [
        Path(r"C:\Windows\Fonts\segoepr.ttf"),
        Path(r"C:\Windows\Fonts\comic.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    ]

    for font_path in possible_fonts:
        if font_path.exists():
            return ImageFont.truetype(
                str(font_path),
                size,
            )

    return ImageFont.load_default()


def load_bold_font(size):
    possible_fonts = [
        Path(r"C:\Windows\Fonts\segoeuib.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
    ]

    for font_path in possible_fonts:
        if font_path.exists():
            return ImageFont.truetype(
                str(font_path),
                size,
            )

    return load_font(size)


def create_wallpaper(
    todos,
    width,
    height,
):
    image = Image.new(
        "RGB",
        (width, height),
        (15, 14, 15),
    )

    draw = ImageDraw.Draw(image)

    for y in range(height):
        variation = (y * 7) % 5 - 2
        color = (
            15 + variation,
            14 + variation,
            15 + variation,
        )
        draw.line(
            [(15, y), (width, y)],
            fill=color,
        )

    title_font = load_bold_font(max(42, width // 35))
    todo_font = load_font(max(30, width // 55))
    date_font = load_font(max(24, width // 70))
    small_font = load_font(max(20, width // 90))

    margin_x = int(width * 0.10)
    margin_y = int(height * 0.10)

    today = datetime.now()

    draw.text(
        (margin_x, margin_y),
        "TODAY",
        font=title_font,
        fill=(217, 216, 217),
    )

    date_text = today.strftime("%A  •  %d %B %Y")
    date_y = margin_y + title_font.size + 15

    draw.text(
        (margin_x, date_y),
        date_text,
        font=date_font,
        fill=(230, 235, 224),
    )

    line_y = date_y + date_font.size + 35
    
    draw.line(
        [
            (margin_x, line_y),
            (width - margin_x, line_y),
        ],
        fill=(230, 235, 224),
        width=3,
    )

    todo_start_y = line_y + 50

    checkbox_size = max(
        28,
        width // 65,
    )
    line_spacing = max(
        35,
        height // 22,
    )

    for index, todo in enumerate(todos):
        y = todo_start_y + index * line_spacing

        if y + checkbox_size > height - margin_y:
            break

        box_x = margin_x
        box_y = y + 22

        draw.rounded_rectangle(
            [
                box_x,
                box_y,
                box_x + checkbox_size,
                box_y + checkbox_size,
            ],
            radius=6,
            outline=(230, 235, 224),
            width=3,
        )

        text_x = box_x + checkbox_size + 25

        draw.text(
            (text_x, y),
            todo,
            font=todo_font,
            fill=(230, 235, 224),
        )

    footer = "small steps • every day"

    footer_bbox = draw.textbbox(
        (0, 0),
        footer,
        font=small_font,
    )

    footer_width = footer_bbox[2] - footer_bbox[0]
    footer_x = (width - footer_width) // 2
    footer_y = height - margin_y - 15

    draw.text(
        (footer_x, footer_y),
        footer,
        font=small_font,
        fill=(135, 124, 108),
    )

    return image


def save_wallpaper(image):
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = OUTPUT_DIR / f"wallpaper_{timestamp}.png"
    image.save(
        path,
        "PNG",
    )

    return path


def cleanup_old_wallpapers(keep=10):
    if not OUTPUT_DIR.exists():
        return
    
    files = sorted(
        OUTPUT_DIR.glob("wallpaper_*.png"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    for old_file in files[keep:]:
        try:
            old_file.unlink()
        except PermissionError:
            pass
