from fabric.widgets.box import Box
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.image import Image
from fabric.widgets.eventbox import EventBox
from fabric.widgets.button import Button
from fabric.widgets.label import Label

from util.ui import add_hover_cursor
from util.helpers import get_pixbuff
from services.theme import ThemeService
import config.icons as Icons

from pathlib import Path


class ThemeSettings(Box):
    def __init__(self, on_close, **kwargs):
        super().__init__(
            name="theme-settings",
            style_classes="view-box",
            spacing=20,
            visible=True,
            orientation="h",
            v_expand=True,
            v_align="center",
            **kwargs,
        )

        self.service = ThemeService.get_instance()

        self.refresh_button = Button(
            child=Label(
                markup=Icons.refresh,
                style_classes="theme-icon",
            ),
            on_clicked=self.service.load_wallpapers,
        )
        add_hover_cursor(self.refresh_button)

        self.wallpaper_viewer = WallpaperViewer()

        self.theme_options = ThemeOptions()

        self.back_button = Button(
            child=Label(markup=Icons.arrow_right, style_classes="theme-icon"),
            on_clicked=on_close,
        )
        add_hover_cursor(self.back_button)

        self.children = [
            self.refresh_button,
            self.wallpaper_viewer,
            self.theme_options,
            self.back_button,
        ]


class WallpaperViewer(ScrolledWindow):
    def __init__(self, **kwargs):
        self.service = ThemeService.get_instance()

        self.wallpapers = Box(
            spacing=20,
            orientation="v",
            v_expand=True,
        )
        self.load_wallpapers()

        super().__init__(
            name="wallpaper-viewer",
            style_classes="wallpaper-viewer-scrolled-window",
            child=self.wallpapers,
            v_expand=True,
            **kwargs,
        )

        self.service.connect("notify::wallpapers", self.load_wallpapers)

    def load_wallpapers(self, *args):
        self.wallpapers.children = [
            Wallpaper(path, self.service) for path in self.service.wallpapers
        ]


class Wallpaper(EventBox):
    def __init__(self, wallpaper: Path, service: ThemeService, **kwargs):
        super().__init__(
            events="button-press",
            child=Image(pixbuf=get_pixbuff(str(wallpaper), 600, 520)),
            **kwargs,
        )

        self.service = service
        self.wallpaper = wallpaper

        self.connect("button-press-event", self.on_button_press)
        add_hover_cursor(self)

    def on_button_press(self, widget, event):
        button = event.get_button()[1]

        if button == 1:  # left mouse
            self.service.update_wallpaper(self.wallpaper)


class ThemeOptions(Box):
    def __init__(self, **kwargs):
        self.service = ThemeService.get_instance()

        super().__init__(
            name="theme-options",
            orientation="v",
            v_expand=True,
            h_epand=True,
            children=[],
            **kwargs,
        )


class ThemeVariantButton(Button):
    def __init__(self, **kwargs):
        super().__init__(label=Label(), on_clicked=lambda *_: None)
