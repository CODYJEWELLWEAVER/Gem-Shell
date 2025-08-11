from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.box import Box

from pathlib import Path
from modules.desktop_app import DesktopApp
from modules.app_element import AppElement


ESCAPE_KEY_CODE = 65307
APPLICATION_DIR = Path("/usr/share/applications")
if not APPLICATION_DIR.exists() or not APPLICATION_DIR.is_dir():
    raise FileNotFoundError("User applications directory does not exist.")


class Runner(Window):
    def __init__(self, **kwargs):
        super().__init__(
            layer="overlay",
            anchor="center",
            exclusivity="none",
            keyboard_mode="exclusive",
            title="Gem-Runner",
            **kwargs,
        )

        self.connect("key-press-event", self.on_key_press)

        self.app_list = Box(
            spacing=20,
            orientation="v",
            v_expand=True,
            name="app-list",
            children=self.get_app_elements()
        )
        scrolled_window = ScrolledWindow(
            name="runner-scrolled-window",
            v_align=True,
            child=self.app_list,
        )

        self.add(
            Box(
                name="runner-content-box",
                children=scrolled_window
            )
        )

    def on_key_press(self, widget, event):
        if event.keyval == ESCAPE_KEY_CODE:
            exit(0)
        else:
            return False

    def get_app_elements(self) -> list[AppElement]:
        paths = self.get_app_paths()

        desktop_apps = self.get_desktop_apps(paths)

        return [AppElement(app) for app in desktop_apps]

    def get_app_paths(self) -> list[Path]:
        paths = []

        for posix_path in APPLICATION_DIR.glob("*.desktop"):
            if not posix_path.is_file():
                return

            path = posix_path.resolve()
            paths.append(path)

        return paths

    def get_desktop_apps(self, paths: list[Path]) -> list[DesktopApp]:
        return [DesktopApp.from_path(path) for path in paths]
