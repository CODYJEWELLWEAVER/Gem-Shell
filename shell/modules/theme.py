from fabric.widgets.box import Box
from fabric.widgets.scrolledwindow import ScrolledWindow


class ThemeSettings(Box):
    def __init__(self, **kwargs):
        super().__init__(
            name="theme-settings",
            style_classes="view-box",
            visible=True,
            orientation="h",
            v_expand=True,
            v_align="center",
            **kwargs,
        )


class WallpaperViewer(ScrolledWindow):
    def __init__(self, **kwargs):
        self.child_list = Box()

        super().__init__(
            name="wallpaper-viewer",
            child=self.child_list,
            **kwargs
        )

