from fabric.core.service import Service, Property, Signal
from fabric.utils.helpers import exec_shell_command_async

from config.theme import DEFAULT_COLOR_THEME, DEFAULT_CONTRAST, DEFAULT_VARIANT
from util.singleton import Singleton
from util.theme import (
    ThemeColors,
)
from material_color_utilities import Theme, theme_from_image, Variant
from config.theme import COLOR_STYLESHEET, CURRENT_WALLPAPER_PATH
import re
from PIL import Image


class ThemeService(Service, Singleton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._wallpaper = CURRENT_WALLPAPER_PATH
        self._colors = DEFAULT_COLOR_THEME
        self._variant = DEFAULT_VARIANT
        self._contrast = DEFAULT_CONTRAST
        self._dark = True

        self.update_theme()

        self.connect(
            "theme-changed",
            self.update_theme
        )

    @Signal
    def theme_changed(self) -> None: ...

    @Property(ThemeColors, flags="readable")
    def colors(self) -> ThemeColors:
        return self._colors

    @colors.setter
    def colors(self, colors: ThemeColors) -> None:
        self._colors = colors
        self.theme_changed()

    @Property(Variant, flags="readable")
    def variant(self) -> Variant:
        return self._variant

    @variant.setter
    def variant(self, variant: Variant) -> None:
        self._variant = variant
        self.theme_changed()

    @Property(float, "readable")
    def contrast(self) -> float:
        return self._contrast

    @contrast.setter
    def contrast(self, contrast: float) -> None:
        self._contrast = contrast
        self.theme_changed()

    @Property(bool, "readable", default_value=True)
    def dark(self) -> bool:
        return self._dark

    @dark.setter
    def dark(self, dark: bool) -> None:
        self._dark = dark
        self.theme_changed()

    def update_theme(self):
        self._colors = self.create_colortheme_from_image(
            CURRENT_WALLPAPER_PATH.resolve(), self.contrast, self.variant, self.dark
        )
        self.update_color_styles()

    def create_colortheme_from_image(
        self, image_path: str, contrast: float, variant: Variant, use_dark: bool
    ) -> Theme:
        image = Image.open(image_path)
        theme = theme_from_image(image, contrast=contrast, variant=variant)

        if use_dark:
            mat_colors = theme.schemes.dark
        else:
            mat_colors = theme.schemes.light

        return ThemeColors(
            mat_colors.primary,
            mat_colors.on_surface,
            mat_colors.background,
            mat_colors.surface_container,
            mat_colors.surface_bright,
            mat_colors.tertiary,
            mat_colors.error,
        )

    def update_color_styles(self) -> None:
        try:
            with open(COLOR_STYLESHEET, "r") as color_stylesheet:
                styles = color_stylesheet.read()

            hex_pattern = "#[0-9a-zA-Z]{6,8}"
            styles = re.sub(
                rf"--foreground: {hex_pattern}",
                f"--foreground: {self.colors.foreground}",
                styles,
            )
            styles = re.sub(
                rf"--foreground-alt: {hex_pattern}",
                f"--foreground-alt: {self.colors.foreground_alt}",
                styles,
            )
            styles = re.sub(
                rf"--background: {hex_pattern}",
                f"--background: {self.colors.background}",
                styles,
            )
            styles = re.sub(
                rf"--background-alt: {hex_pattern}",
                f"--background-alt: {self.colors.background_alt}",
                styles,
            )
            styles = re.sub(
                rf"--background-highlight: {hex_pattern}",
                f"--background-highlight: {self.colors.background_highlight}",
                styles,
            )
            styles = re.sub(
                rf"--highlight: {hex_pattern}",
                f"--highlight: {self.colors.highlight}",
                styles,
            )
            styles = re.sub(
                rf"--status-fail: {hex_pattern}",
                f"--status-fail: {self.colors.error}",
                styles,
            )

            with open(COLOR_STYLESHEET, "w") as color_stylesheet:
                color_stylesheet.write(styles)

        except Exception as e:
            print(f"Error: Could not update color styles! {e}")

    def update_wallpaper(self, new_path: str) -> None:
        proc, _ = exec_shell_command_async(
            f"ln -sf {new_path} {CURRENT_WALLPAPER_PATH.absolute()}"
        )

        if proc is not None:
            proc.wait_async(None, lambda _: self.theme_changed(), None)
