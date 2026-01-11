from fabric.widgets.box import Box
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.image import Image
from fabric.widgets.eventbox import EventBox

from util.ui import add_hover_cursor
from util.helpers import get_pixbuff
from services.theme import ThemeService

from pathlib import Path


class ThemeSettings(Box):
    def __init__(self, on_close, **kwargs):
        super().__init__(
            name="theme-settings",
            style_classes="view-box",
            visible=True,
            orientation="h",
            v_expand=True,
            v_align="center",
            **kwargs,
        )

        self.service = ThemeService.get_instance()

        self.children = [WallpaperViewer()]


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

    def load_wallpapers(self):
        self.wallpapers.children = [
            Wallpaper(path, self.service) for path in self.service.wallpapers
        ]


class Wallpaper(EventBox):
    def __init__(self, wallpaper: Path, service: ThemeService, **kwargs):
        super().__init__(
            events="button-press", 
            child=Image(
                pixbuf=get_pixbuff(str(wallpaper), 400, 320)
            ), 
            **kwargs
        )

        self.service = service
        self.wallpaper = wallpaper

        self.connect("button-press-event", self.on_button_press)
        add_hover_cursor(self)

    def on_button_press(self, widget, event):
        button = event.get_button()[1]

        if button == 1:  # left mouse
            self.service.update_wallpaper(self.wallpaper)
