#!/usr/bin/env python

import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gst_videocall import Sending_Pipeline
from gi.repository import Gst

Gst.init(None)
p = Sending_Pipeline()
tee = p.player.get_child_by_name('monitor')
print(tee)
