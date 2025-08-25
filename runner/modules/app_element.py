from fabric.widgets.box import Box
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.utils.helpers import exec_shell_command_async, truncate

from modules.desktop_app import DesktopApp
from helpers import add_hover_cursor
import string


class AppElement(Button):
    def __init__(self, app: DesktopApp, **kwargs):
        self.app = app

        super().__init__(
            style_classes="app-element", on_clicked=self.run_app, **kwargs
        )

        box = Box(
            style_classes="app-element-button-box",
            spacing=20,
            orientation="h",
        )

        if app.icon_pixbuf is not None:
            box.add(Image(pixbuf=app.icon_pixbuf, style_classes="app-element-pixbuf"))

        box.add(
            Label(style_classes="app-element-name-label", label=truncate(app.name, 24))
        )

        self.add(box)

        add_hover_cursor(self)

    def run_app(self, *args):
        exec_shell_command_async(f"gtk-launch {self.app.path.name}")
        exit(0)
        

class AppElementList:
    def __init__(self, app_elements: list[AppElement]):
        self.app_table = {element.app.name: element for element in app_elements}

    def get_all_elements(self) -> list[AppElement]:
        return list(self.app_table.values())

    def search(self, query: str) -> list[AppElement]:
        query = query.lower()
        scored_apps = {}

        for app_name, _ in self.app_table.items():
            score = self._score_name(app_name.lower(), query)
            if score is not None:
                scored_apps[app_name] = score

        scored_apps = sorted(
            scored_apps.items(), key=lambda item: item[1], reverse=False
        )

        return [self.app_table[app_name] for app_name, _ in scored_apps]

    def _score_name(self, name: str, query: str) -> int | None:
        query_score = name.find(query)

        if query_score != -1:
            return query_score

        char_score = 0
        for char in query:
            if char in string.whitespace:
                continue

            char_index = name.find(char)
            if char_index != -1:
                char_score += char_index
            else:
                return None

        return char_score
