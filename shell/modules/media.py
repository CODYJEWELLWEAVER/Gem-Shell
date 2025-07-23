from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import truncate, bulk_connect

from gi.repository import Playerctl, GdkPixbuf, GLib

from services.media import MediaService
from widgets.custom_image import CustomImage
from util.ui import add_hover_cursor, toggle_visible
from util.helpers import get_file_path_from_mpris_url
from config.media import HEADPHONES
import config.icons as Icons


""" Side Media control and info module. """


class MediaControl(Box):
    def __init__(self, **kwargs):
        super().__init__(
            name="media-control",
            spacing=10,
            v_align="center",
            h_align="center",
            **kwargs,
        )

        self.media_service = MediaService.get_instance()

        self.media_panel = MediaPanel()

        self.title = Label(
            name="info-box-title",
        )
        self.artist = Label(
            name="info-box-artist",
        )
        self.info_box = Box(
            name="info-box",
            orientation="v",
            v_align="center",
            h_align="center",
            children=[self.title, self.artist],
        )
        self.media_info = EventBox(
            child=self.info_box, visible=False, events=["enter-notify", "leave-notify"]
        )

        bulk_connect(
            self.media_info,
            {
                "enter-notify-event": self.show_media_info_panel,
                "leave-notify-event": self.hide_media_info_panel,
            },
        )

        self.output_control = Button(
            child=Label(style_classes="media-control-icon", markup=Icons.speaker),
            on_clicked=lambda *_: self.media_service.swap_speaker(),
        )
        add_hover_cursor(self.output_control)

        self.prev_track_control = Button(
            child=Label(style_classes="media-control-icon", markup=Icons.skip_prev),
            on_clicked=lambda *_: self.media_service.skip_previous(),
        )
        add_hover_cursor(self.prev_track_control)

        self.play_control_label = Label(
            style_classes="media-control-icon", markup=Icons.play
        )
        self.play_control = Button(
            child=self.play_control_label,
            on_clicked=lambda *_: self.media_service.toggle_play_pause(),
        )
        add_hover_cursor(self.play_control)

        self.next_track_control = Button(
            child=Label(style_classes="media-control-icon", markup=Icons.skip_next),
            on_clicked=lambda *_: self.media_service.skip_next(),
        )
        add_hover_cursor(self.next_track_control)

        mute_label = Label(
            markup=Icons.volume_muted 
            if self.media_service.is_muted 
            else Icons.volume_high,
            style_classes="media-control-icon",
        )
        self.mute_control = Button(
            child=mute_label,
            on_clicked=lambda *_: self.media_service.toggle_mute()
        )
        add_hover_cursor(self.mute_control)

        self.children = [
            self.media_info,
            self.output_control,
            self.prev_track_control,
            self.play_control,
            self.next_track_control,
            self.mute_control,
        ]

        bulk_connect(
            self.media_service,
            {
                "notify::speaker": self.on_notify_speaker,
                "playback-status": self.on_playback_status,
                "metadata": self.on_metadata,
                "notify::is-muted": self.on_notify_is_muted,
            },
        )

    def on_playback_status(self, service, status: Playerctl.PlaybackStatus):
        if status == Playerctl.PlaybackStatus.PLAYING:
            label = Label(style_classes="media-control-icon", markup=Icons.pause)
        else:
            label = Label(style_classes="media-control-icon", markup=Icons.play)

        self.play_control.children = label

    def on_metadata(self, service, metadata: GLib.Variant):
        """
        Update media info on bar and on media panel
        """
        self.update_title(metadata)

        self.update_artist(metadata)

        self.update_media_info_visibility(metadata)

        self.update_album(metadata)

        self.update_art(metadata)

    def update_title(self, metadata: dict):
        if "xesam:title" in metadata.keys() and metadata["xesam:title"] != "":
            self.media_info.set_property("visible", True)

            title_str = metadata["xesam:title"]
            self.title.set_property("label", truncate(title_str, 24))
            self.title.set_property("visible", True)

            self.media_panel.title.set_property("label", title_str)
            self.media_panel.title.set_property("visible", True)

            self.media_info.set_property("visible", True)
        else:
            self.title.set_property("visible", False)
            self.media_panel.title.set_property("visible", False)

    def update_artist(self, metadata: dict):
        if "xesam:artist" in metadata.keys() and metadata["xesam:artist"] != [""]:
            self.media_info.set_property("visible", True)

            artist_str = metadata["xesam:artist"][0]
            # add space and comma between title and artist when title is visible
            if self.title.get_property("visible"):
                self.artist.set_property("label", truncate(artist_str, 24))
            else:
                self.artist.set_property("label", artist_str)
            self.artist.set_property("visible", True)

            self.media_panel.artist.set_property("label", artist_str)
            self.media_panel.artist.set_property("visible", True)

            self.media_info.set_property("visible", True)
        else:
            self.artist.set_property("visible", False)
            self.media_panel.artist.set_property("visible", False)

    def update_media_info_visibility(self, metadata: dict):
        if (
            "xesam:title" in metadata.keys()
            and metadata["xesam:title"] == ""
            and "xesam:artist" in metadata.keys()
            and metadata["xesam:artist"] == [""]
        ):
            self.media_info.set_property("visible", False)

    def update_album(self, metadata: dict):
        if "xesam:album" in metadata.keys() and metadata["xesam:album"] != "":
            self.media_panel.album.set_property("label", metadata["xesam:album"])
            self.media_panel.album.set_property("visible", True)
        else:
            self.media_panel.album.set_property("visible", False)

    def update_art(self, metadata: dict):
        if "mpris:artUrl" in metadata.keys():
            file_path = get_file_path_from_mpris_url(metadata["mpris:artUrl"])
            self_width = self.get_preferred_width().natural_width
            art_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                file_path, self_width - 60, self_width - 60, True
            )
            self.media_panel.art.set_property("pixbuf", art_pixbuf)
            self.media_panel.art.set_property("visible", True)
        else:
            self.media_panel.art.set_property("visible", False)

    def on_notify_speaker(self, *args):
        if self.media_service.speaker.name in HEADPHONES:
            icon = Icons.headphones
        else:
            icon = Icons.speaker

        label = Label(style_classes="media-control-icon", markup=icon)

        self.output_control.children = label

    def on_notify_is_muted(self, *args):
        if self.media_service.is_muted:
            icon = Icons.volume_muted
        else:
            icon = Icons.volume_high

        mute_label = Label(
            markup=icon,
            style_classes="media-control-icon"
        )

        self.mute_control.children = mute_label

    def show_media_info_panel(self, *args):
        toggle_visible(self.media_panel)

    def hide_media_info_panel(self, *args):
        toggle_visible(self.media_panel)


class MediaPanel(Window):
    def __init__(self, **kwargs):
        super().__init__(
            name="media-info-panel",
            layer="overlay",
            anchor="left top",
            exclusivity="none",
            visible=False,
            margin="20px 0px 0px 322px",
            **kwargs,
        )

        self.art = CustomImage(name="media-art", visible=False)

        self.title = Label(
            style_classes="media-info-panel-text", visible=False, line_wrap="word"
        )

        self.artist = Label(
            style_classes="media-info-panel-text", visible=False, line_wrap="word"
        )

        self.album = Label(
            style_classes="media-info-panel-text", visible=False, line_wrap="word"
        )

        self.box = Box(
            name="media-info-panel-box",
            orientation="v",
            v_align="center",
            spacing=10,
            children=[
                Box(
                    name="media-art-box",
                    children=self.art,
                    v_expand=True,
                    h_expand=True,
                ),
                self.title,
                self.artist,
                self.album,
            ],
        )

        self.children = self.box
