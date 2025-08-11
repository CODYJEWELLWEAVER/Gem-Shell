from fabric.widgets.box import Box
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.utils.helpers import exec_shell_command_async, truncate

from modules.desktop_app import DesktopApp
from helpers import add_hover_cursor


class AppElement(Button):
    def __init__(self, app: DesktopApp, **kwargs):
        self.app = app

        super().__init__(
            style_classes="app-element",
            on_clicked=self.on_clicked, 
            **kwargs
        )

        box = Box(
            style_classes="app-element-button-box",
            spacing=20,
            orientation="h",
        )

        if app.icon_pixbuf is not None:
            box.add(
                Image(
                    pixbuf=app.icon_pixbuf,
                    style_classes="app-element-pixbuf"
                )
            )

        box.add(
            Label(
                style_classes="app-element-name-label",
                label=truncate(app.name, 24)
            )
        )

        self.add(box)

        add_hover_cursor(self)

    def on_clicked(self, *args):
        exec_shell_command_async(f"gtk-launch {self.app.path.name} & disown")
        exit(0)