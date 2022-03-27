# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import octoprint.settings

import threading
import queue
import math


class LocationPollingPlugin(octoprint.plugin.StartupPlugin,
                   octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.SettingsPlugin,
                   octoprint.plugin.AssetPlugin,
                   octoprint.plugin.SimpleApiPlugin):

    def __init__(self):
        self.worker = PollWorker(self)

    def on_after_startup(self):
        self._logger.info("starting location polling plugin")
        self.worker.start()
        
    def get_settings_defaults(self):
        return dict(
            poll_interval = 4,
            enable = True
        )

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    def get_assets(self):
        return dict(
            js=["js/location_polling.js"]
        )

    def on_api_get(self, request):
        self._logger.info("got manual M114 request")
        if self._printer.is_operational():
            self._printer.commands("M114")
        return None
        

class PollWorker(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self, daemon=True)
        self.inbox = queue.Queue()
        self.parent = parent

    def run(self):
        # self.parent._logger.info("worker run method starting")
    
        while True:
            timeout = self.parent._settings.get_float(["poll_interval"])
            enable = self.parent._settings.get_boolean(["enable"])
            
            # even when not enabled, continue looping with timeout of 1
            if not enable or math.isnan(timeout) or timeout < 1:
                timeout = 1
                
            # this works the same way whether enabled or not, operational or not
            try:
                message = self.inbox.get(timeout=timeout)
            except queue.Empty:
                message = ("timeout",)  # timed out waiting for message
            
            # only query M114 if we are enabled, operational, and we got timeout
            if enable and self.parent._printer.is_operational() and message[0] == "timeout":
                self.parent._printer.commands("M114")
                
            # if enable setting or timeout setting changes, parent could send us 
            # a message to abort the current timeout and loop again with updated settings.
            # e.g. if the timeout were 1000 and it were changed to 1, it would take a long
            # time to begin polling quickly.
            # (not implemented)


# version and description are only in setup.py, not here
# name is optional, but names from setup.py have dashes added to them and are ugly
__plugin_name__ = "Location Polling"
__plugin_pythoncompat__ = ">=3,<4"  # only python 3
__plugin_implementation__ = LocationPollingPlugin()
