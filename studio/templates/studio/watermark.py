from PIL import Image, ImageDraw, ImageFont
import os

def add_watermark(image_path):
    original = Image.open(image_path)
    watermark = Image.new('RGBA', original.size)
    font = ImageFont.load_default(size=45)
    
    draw = ImageDraw.Draw(watermark)
    draw.text(
        (original.width//2, original.height//2),
        "© YourStudio",
        font=font,
        fill=(255,255,255,128)
    
    return Image.alpha_composite(original.convert('RGBA'), watermark)