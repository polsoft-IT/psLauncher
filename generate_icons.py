#!/usr/bin/env python3
"""Generate VS Code-style icons for script types"""

from PIL import Image, ImageDraw, ImageFont
import os

# VS Code-like colors for file types
ICON_CONFIG = {
    "python": {"color": "#3572A5", "text": "Py", "ext": ".py"},
    "powershell": {"color": "#012456", "text": "PS", "ext": ".ps1"},
    "batch": {"color": "#C1501E", "text": "Bat", "ext": ".bat"},
    "vbscript": {"color": "#7B42BC", "text": "VBS", "ext": ".vbs"},
    "javascript": {"color": "#F1E05A", "text": "JS", "ext": ".js"},
    "ruby": {"color": "#CC342D", "text": "Rb", "ext": ".rb"},
    "perl": {"color": "#0298C3", "text": "Pl", "ext": ".pl"},
    "shell": {"color": "#89E051", "text": "Sh", "ext": ".sh"},
    "r": {"color": "#198CE7", "text": "R", "ext": ".r"},
    "php": {"color": "#4F5D95", "text": "Php", "ext": ".php"},
    "lua": {"color": "#000080", "text": "Lua", "ext": ".lua"},
    "tcl": {"color": "#E4CC98", "text": "Tcl", "ext": ".tcl"},
    "groovy": {"color": "#4298B8", "text": "Gv", "ext": ".groovy"},
    "swift": {"color": "#F05138", "text": "Sw", "ext": ".swift"},
    "go": {"color": "#00ADD8", "text": "Go", "ext": ".go"},
    "typescript": {"color": "#2B7489", "text": "TS", "ext": ".ts"},
    "awk": {"color": "#555555", "text": "Awk", "ext": ".awk"},
    "sed": {"color": "#555555", "text": "Sed", "ext": ".sed"},
    "default": {"color": "#888888", "text": "File", "ext": ""},
    "pinned": {"color": "#FFD700", "text": "📌", "ext": ""},
}

def create_icon(name, config, size=(32, 32)):
    """Create a VS Code-style icon"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded rectangle background
    color = config["color"]
    # Convert hex to RGB
    color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    # Draw rectangle with rounded corners
    margin = 2
    draw.rounded_rectangle(
        [margin, margin, size[0]-margin, size[1]-margin],
        radius=6,
        fill=color_rgb + (255,)
    )
    
    # Try to use a font, fall back to default
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    # Draw text centered
    text = config["text"]
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    return img

def main():
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    for name, config in ICON_CONFIG.items():
        img = create_icon(name, config)
        filename = f"{name}.png"
        filepath = os.path.join(icons_dir, filename)
        img.save(filepath)
        print(f"Created {filename}")

if __name__ == "__main__":
    main()
