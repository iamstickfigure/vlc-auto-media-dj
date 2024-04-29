import time
from typing import Optional
from python_vlc_http import HttpVLC
import urllib.parse
import urllib
import python_vlc_http

from models import VlcPlayerDataSnapshot


class HttpVLCExt(HttpVLC):
    def __init__(self, host=None, username=None, password=None):
        # super().__init__(host=host, username=username, password=password)
        self.host = host
        self.username = username or ""
        self.password = password or ""
        self.enabled = False

        if self.host is None or self.host == "":
            raise python_vlc_http.MissingHost("Host is empty! Input host to proceed")

        self.fetch_data()

    def enqueue(self, mrl: str):
        mrl = urllib.parse.quote(mrl)
        return self.parse_data(command=f"in_enqueue&input={mrl}")

    def enqueue_and_play(self, mrl: str):
        mrl = urllib.parse.quote(mrl)
        return self.parse_data(command=f"in_play&input={mrl}")

    def fetch_data(self, command=None):
        self._data = self.fetch_status(command)
        return self._data

    def fetch_data_snapshot(self, command=None) -> VlcPlayerDataSnapshot:
        return VlcPlayerDataSnapshot(
            data=self.fetch_data(command),
        )

    @property
    def recent_data(self) -> Optional[VlcPlayerDataSnapshot]:
        if not self.enabled:
            return None

        return VlcPlayerDataSnapshot(
            data=self._data,
        )

    def set_volume(self, volume: float):
        """Set volume level, range 0.0-1.5."""
        new_volume = str(int(volume * 256))
        return self.parse_data(command=f"volume&val={new_volume}")

    def play(self, muted: Optional[bool] = None):
        # response_data = self.fetch_data(command="pl_play")
        # return response_data
        if not self.enabled:
            return None

        if muted is True:
            self.set_volume(0)
        elif muted is False:
            self.set_volume(1)

        return super().play()

    def play_and_fullscreen(self):
        self.play()

        # Keep trying to toggle fullscreen until it is successful, with a timeout of 5 seconds
        attempts = 0
        while not self.is_fullscreen():
            if attempts > 0:
                time.sleep(0.5)

            self.toggle_fullscreen()

            if attempts > 10:
                break
