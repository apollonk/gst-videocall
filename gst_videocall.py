#!/usr/bin/env python

import sys, os
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GObject, Gtk
import platform
from gst_videocall_tools import *


class AppWindow(Gtk.Window):
    """ The main Gtk application window """
    def __init__(self):
        Gtk.Window.__init__(self, title="GST Videocall application")
        #self.set_default_size(500, 400)
        self.connect("destroy", Gtk.main_quit, "WM destroy")

        self.preview = VideoWidget(camera_bin())
        self.preview.set_size_request(320,240)
        self.preview.connect("start", self.start)
        self.buttonStartStop = Gtk.Button(label="Start")
        self.buttonStartStop.connect("clicked", self.start_stop)
        self.buttonQuit = Gtk.Button(label="Quit")
        self.buttonQuit.connect("clicked", self.exit)
        self.buttonSilence = Gtk.Button(label="Show timestamp")
        self.buttonSilence.connect("clicked", self.time_toggle)
        self.buttonSilence.set_sensitive(False)

        self.preview.start_video()

        vbox = Gtk.VBox()

        self.add(vbox)
        vbox.add(self.preview)

        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 0)
        hbox.set_border_width(10)
        hbox.pack_start(Gtk.Label(), False, False, 0)
        hbox.pack_start(self.buttonStartStop, False, False, 0)
        hbox.pack_start(self.buttonQuit, False, False, 0)
        hbox.pack_start(self.buttonSilence, False, False, 0)
        hbox.add(Gtk.Label())

        self.show_all()

    def exit(self, widget, data=None):
        Gtk.main_quit()

    def start_stop(self, w):
        if self.buttonStartStop.get_label() == "Start":
            self.start()
        else:
            self.stop()

    def start(self):
            self.buttonStartStop.set_label("Stop")
            self.preview.start_video()
            self.buttonSilence.set_sensitive(True)

    def stop(self):
            self.buttonStartStop.set_label("Start")
            self.preview.stop_video()
            self.buttonSilence.set_sensitive(False)

    def time_toggle(self, w):
        timeoverlay = self.preview.videobin.get_child_by_name('timeoverlay')
        if timeoverlay:
            timeoverlay.set_property('silent', not (timeoverlay.get_property('silent')))
            if timeoverlay.get_property('silent'):
                self.buttonSilence.set_label("Show timestamp")
            else:
                self.buttonSilence.set_label("Hide timestamp")


if __name__ == '__main__':
    Gst.init(None)
    Gst.init_check(None)
    w = AppWindow()
    p = Gtk.main()
