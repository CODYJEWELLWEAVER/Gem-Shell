from PIL import Image
from material_color_utilities import Theme, theme_from_image, Variant
from config.theme import COLOR_STYLESHEET
import re

def create_colortheme_from_image(image_path: str) -> Theme:
    image = Image.open(image_path)
    return theme_from_image(image, variant=Variant.EXPRESSIVE)

def update_color_styles(theme: Theme, use_dark: bool = True) -> None:
    try:
        with open(COLOR_STYLESHEET, "r") as color_stylesheet:
            styles = color_stylesheet.read()

        if use_dark:
            colors = theme.schemes.dark
        else:
            colors = theme.schemes.light
        
        foreground = colors.primary
        foreground_alt = colors.on_surface
        background = colors.background
        background_alt = colors.surface_container
        background_highlight = colors.surface_bright
        highlight = colors.tertiary
        shadow = colors.outline
        error = colors.error

        hex_pattern = "#[0-9a-zA-Z]{6,8}"
        styles = re.sub(fr"--foreground: {hex_pattern}", f"--foreground: {foreground}", styles)
        styles = re.sub(fr"--foreground-alt: {hex_pattern}", f"--foreground-alt: {foreground_alt}", styles)
        styles = re.sub(fr"--background: {hex_pattern}", f"--background: {background}", styles)
        styles = re.sub(fr"--background-alt: {hex_pattern}", f"--background-alt: {background_alt}", styles)
        styles = re.sub(fr"--background-highlight: {hex_pattern}", f"--background-highlight: {background_highlight}", styles)
        styles = re.sub(fr"--highlight: {hex_pattern}", f"--highlight: {highlight}", styles)
        styles = re.sub(fr"--shadow: {hex_pattern}", f"--shadow: {shadow}", styles)
        styles = re.sub(fr"--status-fail: {hex_pattern}", f"--status-fail: {error}", styles)

        with open(COLOR_STYLESHEET, "w") as color_stylesheet:
            color_stylesheet.write(styles)
    except Exception as e:
        print(f"Error: Could not update color styles! {e}")