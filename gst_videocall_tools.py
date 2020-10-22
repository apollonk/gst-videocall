import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GObject, Gtk
import platform

class VideoWidget(Gtk.Box):
    """ A Gtk video widget linked to a gstreamer pipeline """
    def __init__(self, videobin):
        super().__init__()
        # Only setup the widget after the window is shown.
        self.connect('realize', self._on_realize)

        self.videobin = videobin
        self.pipeline = None
        self._on_start = lambda: None
        self._on_stop = lambda: None

    def _on_realize(self, widget):
        self.pipeline = Gst.Pipeline()
        gtksink = self.pipeline.get_factory().make('gtksink')
        self.pipeline.add(self.videobin)
        self.pipeline.add(gtksink)
        self.videobin.link(gtksink)
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)
        self.pack_start(gtksink.props.widget, True, True, 0)
        gtksink.props.widget.show()

    def connect(self, message, func):
        if message == "start":
            self._on_start = func
        elif message == "stop":
            self._on_stop = func

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)
            self._on_start()
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
            self.pipeline.set_state(Gst.State.NULL)
            self._on_stop()

    def on_sync_message(self, bus, message):
        struct = message.get_structure()
        if not struct:
            return
        message_name = struct.get_name()
        if message_name == "prepare-xwindow-id":
            # Assign the viewport
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_xwindow_id(self.movie_window.window.xid)

    def start_video(self):
        if self.pipeline is not None:
            self.pipeline.set_state(Gst.State.PLAYING)
        else:
            self._on_realize(self)

    def stop_video(self):
        if self.pipeline is not None:
            self.pipeline.set_state(Gst.State.NULL)

def camera_bin():
    # Source is OS-dependent
    if platform.system() == "Linux":
        camera = "v4l2src"
    elif platform.system() == "Darwin":
        camera = "avfvideosrc"
    elif platform.system() == "Windows":
        print("This tool does not support Windows [yet]")
        sys.exit(1)
    timeoverlay = "timeoverlay name=timeoverlay halignment=right valignment=bottom text=Stream\ time:"
    timeoverlay += " shaded-background=true font-desc='Courier, 24' silent=true"
    return Gst.parse_bin_from_description(f"{camera} ! {timeoverlay}", True)

