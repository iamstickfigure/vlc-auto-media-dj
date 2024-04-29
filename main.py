import json
import time
from typing import Any, Dict, List, Optional, Tuple
from python_vlc_http import HttpVLC
from functools import cached_property
from pydantic import BaseModel, computed_field
from constants import (
    ALL_FIELDS_BY_ID,
    ALL_TAGS_BY_ID,
    FIELDS,
    DJMode,
    DJState,
    FieldIds,
    PlaybackMode,
    TagId,
)
import urllib.parse
import os
import itertools
import urllib
import cachetools
import random
import python_vlc_http
import dotenv


def windows_path_to_wsl(path: str):
    return path.replace("C:", "/mnt/c").replace("\\", "/")


def wsl_path_to_windows(path: str):
    return path.replace("/mnt/c", "C:").replace("/", "\\")


def mrl_from_path(
    path: str,
    title: Optional[int] = None,
    chapter: Optional[int] = None,
    end_title: Optional[int] = None,
    end_chapter: Optional[int] = None,
    options: Optional[Dict[str, str]] = None,
):
    # Url encode the path, but not C: because it is a drive letter
    path = path.replace("\\", "/")
    path = urllib.parse.quote(path).replace("%3A", ":")

    mrl = f"file:///{path}"

    if title is not None or chapter is not None:
        mrl += "#"

        if title is not None:
            mrl += str(title)

        if chapter is not None:
            mrl += f":{chapter}"

        if end_title is not None or end_chapter is not None:
            mrl += "-"

        if end_title is not None:
            mrl += str(end_title)

        if end_chapter is not None:
            mrl += f":{end_chapter}"

    # TODO: I have no idea if this works. So far, it breaks every time I try to use it
    if options:
        for option, value in options.items():
            mrl += f" :{option}" + (f"={value}" if value else "")

    return mrl


tag_search_cache = cachetools.LRUCache(maxsize=1024)


# Breadth-first search
def search_for_tag(tag_id: int, root_tags: List[int]) -> bool:
    tag_queue_history = set(root_tags)

    if tag_id in tag_queue_history:
        # Return early if the tag blatantly is sitting at the root
        # All logic after this point is to handle subtags
        return True

    root_tags_uncached = list()
    for root_tag_id in root_tags:
        tag_cache_key = f"{tag_id}-{root_tag_id}"

        # Save the root tags that haven't been cached yet
        if tag_cache_key not in tag_search_cache:
            root_tags_uncached.append(root_tag_id)
            continue

        if tag_search_cache[tag_cache_key]:
            # If it has been checked and found to have the tag, return early
            return True

    # Only queue up the root tags that haven't already been cached
    # By this point, we know that none of the cached entries are hits
    tag_queue = root_tags_uncached.copy()

    while tag_queue:
        curr_tag_id = tag_queue.pop(0)
        tag_cache_key = f"{tag_id}-{curr_tag_id}"

        # Check if this tag has already been checked
        if tag_cache_key in tag_search_cache:
            # If it has been checked and found to have the tag, return True
            if tag_search_cache[tag_cache_key]:
                return True

            # If it has been checked and found to not have the tag, skip it
            continue

        if curr_tag_id == tag_id or tag_id in tag_queue_history:
            # Cache the result for the root tag, but only if there was only one root tag that was uncached
            if len(root_tags_uncached) == 1:
                tag_search_cache[f"{tag_id}-{root_tags_uncached[0]}"] = True

            return True

        tag_data = ALL_TAGS_BY_ID[curr_tag_id]
        subtags = tag_data.get("subtag_ids", [])
        subtags_not_already_queued = (
            subtag_id for subtag_id in subtags if subtag_id not in tag_queue_history
        )
        tag_queue.extend(subtags_not_already_queued)
        tag_queue_history.update(subtags)

    # tag_id wasn't found in any of the tags that were queued, so cache that info for all of them
    for missed_tag_id in tag_queue_history:
        tag_search_cache[f"{tag_id}-{missed_tag_id}"] = False

    return False


class VlcPlayerDataSnapshot(BaseModel):
    data: Dict[str, Any]

    @property
    def filename(self) -> Optional[str]:
        meta = self.metadata

        if meta is None:
            return None

        return meta.get("filename")

    @property
    def duration(self) -> Optional[str]:
        meta = self.metadata

        if meta is None:
            return None

        return meta.get("duration")

    @property
    def state(self) -> str:
        return self.data.get("state")

    @property
    def stats(self) -> Dict[str, Any]:
        return self.data.get("stats")

    @property
    def information(self) -> Dict[str, Any]:
        return self.data.get("information")

    @property
    def metadata(self) -> Dict[str, Any]:
        info = self.data.get("information")
        if info is None:
            return None

        category = info.get("category")
        if category is None:
            return None

        return category.get("meta")

    @property
    def volume(self) -> float:
        return self.data.get("volume")

    @property
    def position(self) -> float:
        return self.data.get("position")

    @property
    def time(self) -> float:
        return self.data.get("time")

    @property
    def length(self) -> float:
        return self.data.get("length")

    @property
    def loop(self) -> bool:
        return self.data.get("loop")

    @property
    def repeat(self) -> bool:
        return self.data.get("repeat")

    @property
    def random(self) -> bool:
        return self.data.get("random")


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


class Entry(BaseModel):
    entry_dict: Dict[str, Any]

    @computed_field
    def id(self) -> int:
        return self.entry_dict["id"]

    @computed_field
    def filename(self) -> str:
        return self.entry_dict["filename"]

    @computed_field
    def path(self) -> str:
        return self.entry_dict.get("path", "")

    @computed_field
    def content_tags(self) -> List[int]:
        content_tags_key = str(FieldIds.CONTENT_TAGS)
        fields = self.entry_dict.get("fields", [])
        return next(
            (field[content_tags_key] for field in fields if content_tags_key in field),
            [],
        )

    @computed_field
    def meta_tags(self) -> List[int]:
        meta_tags_key = str(FieldIds.META_TAGS)
        fields = self.entry_dict.get("fields", [])
        return next(
            (field[meta_tags_key] for field in fields if meta_tags_key in field),
            None,
        )

    def get_checkbox_val(self, field_id: int) -> bool:
        field = ALL_FIELDS_BY_ID[field_id]

        if field["type"] != "checkbox":
            raise ValueError("Field must be a checkbox")

        field_key = str(field_id)
        fields = self.entry_dict.get("fields", [])
        checkbox_val = next(
            (field[field_key] for field in fields if field_key in field),
            False,
        )
        return checkbox_val

    def has_content_tag(self, tag_id: int) -> bool:
        return search_for_tag(tag_id, self.content_tags)

    @computed_field
    def has_music(self) -> bool:
        # It has music if it's tagged as such
        if self.get_checkbox_val(FieldIds.HAS_MUSIC) or self.has_content_tag(
            TagId.HAS_MUSIC
        ):
            return True

        # It has music if it's tagged as music
        if self.has_content_tag(TagId.MUSIC):
            return True

        return False

    @computed_field
    def is_background_music(self) -> bool:
        # It needs music to be background music
        if not self.has_music:
            return False

        if (
            self.get_checkbox_val(FieldIds.NEEDS_VISUALS)
            or self.get_checkbox_val(FieldIds.OPTIONAL_VISUALS)
            or self.has_content_tag(TagId.NEEDS_VISUALS)
            or self.has_content_tag(TagId.HAS_OPTIONAL_VISUALS)
        ):
            return True

        # If it has music, but the visuals are important, it's not background music
        return False

    @computed_field
    def is_audiovisual(self) -> bool:
        # It's not audiovisual if it's labeled as needing visuals
        if self.get_checkbox_val(FieldIds.NEEDS_VISUALS):
            return False

        # It's audiovisual if it's tagged as such (TODO: Do we need anything beyond this?)
        if self.has_content_tag(TagId.AUDIOVISUAL_VIDEO):
            return True

        # It's not audiovisual if it's a silent video
        if self.has_content_tag(TagId.SILENT_VIDEO):
            return False

        # If it's not tagged as needing visuals, and it's not a silent video, why isn't it tagged as audiovisual?
        # This is a catch-all for anything that doesn't fit the above criteria
        # Most things are audiovisual by default
        return True

    @computed_field
    def is_visual(self) -> bool:
        # It's not visual if it's labeled as needing visuals
        if self.get_checkbox_val(FieldIds.NEEDS_VISUALS) or self.has_content_tag(
            TagId.NEEDS_VISUALS
        ):
            return False

        # It's visual if it's labeled as such or if it has optional audio
        if self.get_checkbox_val(FieldIds.VISUALS) or self.get_checkbox_val(
            FieldIds.OPTIONAL_AUDIO
        ):
            return True

        # Images are only visual
        if self.has_content_tag(TagId.IMAGE):
            return True

        # It's visual if it's tagged as such
        if self.has_content_tag(TagId.VISUALS):
            return True

        # Most things are visual by default (TODO: Needs more disqualifiers?)
        return True


class PlaybackInfo(BaseModel):
    entry: Entry
    playback_mode: PlaybackMode
    dj_mode: DJMode
    base_path: str
    index: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    volume: float = 100.0
    is_muted: bool = False
    chapter_range: Optional[Tuple[int, int]] = None
    skip_chapters: Optional[List[int]] = None
    information: Optional[Dict[str, Any]] = None

    @computed_field
    @cached_property
    def chapter_ranges(self) -> Optional[List[Tuple[int, int]]]:
        if self.chapter_range is None:
            return None

        if self.skip_chapters is None:
            return [self.chapter_range]

        chapter_ranges = []
        start_chapter, end_chapter = self.chapter_range
        for skip_chapter in self.skip_chapters:
            if skip_chapter < start_chapter:
                continue

            if skip_chapter > end_chapter:
                break

            chapter_ranges.append((start_chapter, skip_chapter))
            start_chapter = skip_chapter + 1

    def get_mrls(self) -> List[str]:
        kwargs = {}

        # TODO: Investigate if this is possible. Currently it breaks...
        # if self.is_muted:
        #     # kwargs["options"] = {"no-audio": ""}
        #     kwargs["options"] = {"gain": "0"}

        if self.chapter_ranges is not None:
            return [
                mrl_from_path(
                    os.path.join(self.base_path, self.entry.path, self.entry.filename),
                    **{
                        **kwargs,
                        "chapter": start,
                        "end_chapter": end,
                    },
                )
                for start, end in self.chapter_ranges
            ]

        # Construct the MRL based on the entry and playback mode
        # Mute the audio if specified in the playback info
        return [
            mrl_from_path(
                os.path.join(self.base_path, self.entry.path, self.entry.filename),
                **kwargs,
            )
        ]


class AutoMediaDJ(BaseModel):
    vlc: HttpVLCExt
    vlc_audio: Optional[HttpVLCExt] = None
    base_path: str
    mode: DJMode = DJMode.MUSIC_AND_VISUALS
    play_history: List[PlaybackInfo] = []
    play_history_audio: List[PlaybackInfo] = []
    video_queue: List[PlaybackInfo] = []
    audio_queue: List[PlaybackInfo] = []
    video_playing: Optional[PlaybackInfo] = None
    audio_playing: Optional[PlaybackInfo] = None
    state: DJState = DJState.STOPPED

    # arbitrary types for pydantic
    class Config:
        arbitrary_types_allowed = True

    @computed_field
    @cached_property
    def tagstudio_data(self) -> Dict[str, Any]:
        tagstudio_file = os.path.join(self.base_path, ".TagStudio", "ts_library.json")
        tagstudio_file = windows_path_to_wsl(tagstudio_file)

        with open(tagstudio_file, "r") as file:
            return json.load(file)

    @computed_field
    @cached_property
    def entries(self) -> List[Entry]:
        return [Entry(entry_dict=entry) for entry in self.tagstudio_data["entries"]]

    @computed_field
    @cached_property
    def tag_lookup_by_id(self) -> Dict[int, Any]:
        return {tag["id"]: tag for tag in self.tagstudio_data["tags"]}

    @computed_field
    @cached_property
    def field_lookup_by_id(self) -> Dict[int, Any]:
        return {
            field["id"]: field
            for field in itertools.chain(FIELDS, self.tagstudio_data["fields"])
        }

    @computed_field
    @cached_property
    def music_choices(self) -> List[Entry]:
        return [entry for entry in self.entries if entry.is_background_music]

    @computed_field
    @cached_property
    def audiovisual_choices(self) -> List[Entry]:
        return [entry for entry in self.entries if entry.is_audiovisual]

    @computed_field
    @cached_property
    def visual_choices(self) -> List[Entry]:
        return [entry for entry in self.entries if entry.is_visual]

    def test(self):
        ads_file = os.path.join(
            self.base_path,
            "star-wars-stuff",
            "youtube-full",
            "ALL STAR WARS CHILE BEER ADS [jSgMWAi9YPA].mp4",
        )
        entries = self.tagstudio_data["entries"]
        ad_chapter = 0

        for entry in entries:
            if entry["id"] < 7:
                continue

            self.vlc.enqueue(
                mrl_from_path(
                    os.path.join(self.base_path, entry["path"], entry["filename"])
                )
            )
            self.vlc.enqueue(
                mrl_from_path(ads_file, chapter=ad_chapter, end_chapter=ad_chapter)
            )
            self.vlc.play()
            ad_chapter += 1

    def queue_video(self, video_info: PlaybackInfo):
        if video_info.playback_mode == PlaybackMode.AUDIO:
            raise ValueError("Cannot queue audio with this method")

        mrl_list = video_info.get_mrls()

        for mrl in mrl_list:
            self.vlc.enqueue(mrl)

        self.video_queue.append(video_info)

    def queue_audio(self, audio_info: PlaybackInfo):
        if audio_info.playback_mode != PlaybackMode.AUDIO:
            raise ValueError("Can only queue audio with this method")

        mrl_list = audio_info.get_mrls()

        for mrl in mrl_list:
            self.vlc_audio.enqueue(mrl)

        self.audio_queue.append(audio_info)

        # TODO: This shouldn't happen until the video is actually playing
        # Add the audio playback info to the play history
        audio_info.index = len(self.play_history_audio)
        audio_info.start_time = time.time()
        self.play_history_audio.append(audio_info)

    def update_playback_info(self):
        if self.vlc.enabled and len(self.video_queue) < 2:
            # Wait for more videos to be queued before starting playback
            return False

        if self.vlc_audio.enabled and len(self.audio_queue) < 2:
            # Wait for more audio to be queued before starting playback
            return False

        video_player_data: Optional[VlcPlayerDataSnapshot] = None
        audio_player_data: Optional[VlcPlayerDataSnapshot] = None

        if self.vlc.enabled:
            video_player_data = self.vlc.fetch_data_snapshot()

        if self.vlc_audio.enabled:
            audio_player_data = self.vlc_audio.fetch_data_snapshot()

        timestamp = time.time()

        if self.state == DJState.PLAYING:
            if video_player_data is not None:
                if (
                    self.video_playing is not None
                    and video_player_data.filename != self.video_playing.entry.filename
                ):
                    # The current video has ended, and the next video has started
                    self.play_history.append(self.video_playing)
                    self.video_playing.end_time = timestamp
                    self.video_playing = None

                # If video_playing is None, we need to consume the queue and update the current playback info
                if self.video_playing is None:
                    self.video_playing = self.video_queue.pop(0)
                    self.video_playing.start_time = timestamp - video_player_data.time
                    self.video_playing.end_time = (
                        self.video_playing.start_time + video_player_data.length
                    )
                    self.video_playing.index = len(self.play_history)
                    self.video_playing.information = video_player_data.information

            if audio_player_data is not None:
                if (
                    self.audio_playing is not None
                    and audio_player_data.filename != self.audio_playing.entry.filename
                ):
                    # The current audio has ended, and the next audio has started
                    self.play_history_audio.append(self.audio_playing)
                    self.audio_playing.end_time = timestamp
                    self.audio_playing = None

                # If audio_playing is None, we need to consume the queue and update the current playback info
                if self.audio_playing is None:
                    self.audio_playing = self.audio_queue.pop(0)
                    self.audio_playing.start_time = timestamp - audio_player_data.time
                    self.audio_playing.end_time = (
                        self.audio_playing.start_time + audio_player_data.length
                    )
                    self.audio_playing.index = len(self.play_history_audio)
                    self.audio_playing.information = audio_player_data.information

        return True

    def update_players(self):
        if self.mode == DJMode.MUSIC_AND_VISUALS:
            self.vlc.enabled = True
            self.vlc_audio.enabled = True

        if self.state == DJState.STOPPED:
            return

        is_playing = True
        is_paused = True
        is_ready = self.update_playback_info()

        vid_info = self.video_playing or next(iter(self.video_queue), None)
        aud_info = self.audio_playing or next(iter(self.audio_queue), None)

        video_player_data = self.vlc.recent_data
        audio_player_data = self.vlc_audio.recent_data

        if video_player_data:
            if vid_info and vid_info.is_muted and video_player_data.volume != 0:
                self.vlc.set_volume(0)
            elif vid_info and not vid_info.is_muted and video_player_data.volume == 0:
                self.vlc.set_volume(1)

            if video_player_data.state != "playing":
                is_playing = False
            else:
                is_paused = False

        if audio_player_data:
            if audio_player_data.state != "playing":
                is_playing = False
            else:
                is_paused = False

        if self.state == DJState.STARTING:
            if is_playing:
                self.state = DJState.PLAYING
                return

            if not vid_info and video_player_data.volume == 0:
                self.vlc.set_volume(1)

            if not aud_info and audio_player_data.volume == 0:
                self.vlc_audio.set_volume(1)

            if not is_ready:
                return

            self.vlc.play(muted=vid_info.is_muted)
            self.vlc_audio.play(muted=aud_info.is_muted)
            return

        # This state means that it has successfully started playing
        if self.state == DJState.PLAYING:
            if is_playing:
                # All players are playing, so continue
                return

            if is_paused:
                # All players suddenly paused, so pause the DJ
                self.state = DJState.PAUSED
                return

            # If any active player is not playing anymore, initiate a pause
            # Don't return here. Might as well continue to the next state
            self.state = DJState.PAUSING

        # A pause has been initiated
        if self.state == DJState.PAUSING:
            if is_paused:
                # All players have successfully paused
                self.state = DJState.PAUSED
                return

            # If any active player is still playing, continue pausing
            self.vlc.pause()
            self.vlc_audio.pause()
            return

        # It has been paused successfully
        if self.state == DJState.PAUSED:
            if is_paused:
                # All players are paused, so continue
                return

            # If any active player is not paused anymore, resume all players
            # Don't return here. Might as well continue to the next state
            self.state = DJState.RESUMING

        # A resume has been initiated
        if self.state == DJState.RESUMING:
            if is_playing:
                # All players have successfully resumed
                self.state = DJState.PLAYING
                return

            # If any active player is still paused, continue resuming
            # self.vlc.resume()
            self.vlc.play(muted=vid_info.is_muted)
            self.vlc_audio.play(muted=aud_info.is_muted)
            return

    def start(self):
        # Start the DJ loop
        self.state = DJState.STARTING
        while True:
            self.think()
            time.sleep(0.5)

    def think(self):
        self.update_players()

        if self.mode == DJMode.MUSIC_AND_VISUALS:
            if len(self.video_queue) > 5 and len(self.audio_queue) > 5:
                # No need to queue so many videos and audio
                return

            # Randomly choose a visual with weighted probability based on play history
            visual_choice = self.weighted_video_choice(self.visual_choices)

            # Create a PlaybackInfo object for the visual choice
            visual_playback_info = PlaybackInfo(
                entry=visual_choice,
                base_path=self.base_path,
                playback_mode=PlaybackMode.VIDEO,
                dj_mode=self.mode,
                is_muted=True,  # Mute the visual
            )

            # Randomly choose a music track with weighted probability based on play history
            music_choice = self.weighted_audio_choice(self.music_choices)

            # Create a PlaybackInfo object for the music choice
            music_playback_info = PlaybackInfo(
                entry=music_choice,
                base_path=self.base_path,
                playback_mode=PlaybackMode.AUDIO,
                dj_mode=self.mode,
            )

            self.queue_video(visual_playback_info)
            self.queue_audio(music_playback_info)
            return

    def weighted_video_choice(self, choices):
        # Calculate weights based on play history
        weights = []
        for choice in choices:
            weight = 1.0  # Default weight

            # Check if the choice has been played before
            for playback_info in self.play_history:
                if playback_info.entry == choice:
                    if playback_info.is_muted:
                        # Reduce the penalty if previously played muted
                        weight *= 0.8
                    else:
                        # Apply a penalty if recently played unmuted
                        weight *= 0.5

            weights.append(weight)

        # Normalize the weights
        total_weight = sum(weights)
        probabilities = [weight / total_weight for weight in weights]

        # Make a weighted random choice
        return random.choices(choices, probabilities)[0]

    def weighted_audio_choice(self, choices):
        # Calculate weights based on play history
        weights = []
        for choice in choices:
            weight = 1.0  # Default weight

            # Check if the choice has been played before
            for playback_info in self.play_history_audio:
                if playback_info.entry == choice:
                    weight *= 0.5

            weights.append(weight)

        # Normalize the weights
        total_weight = sum(weights)
        probabilities = [weight / total_weight for weight in weights]

        # Make a weighted random choice
        return random.choices(choices, probabilities)[0]


if __name__ == "__main__":
    dotenv.load_dotenv()

    # base_host = "http://localhost"
    base_host = os.getenv("VLC_HOST")
    base_audio_host = os.getenv("VLC_AUDIO_HOST", base_host)
    port = os.getenv("VLC_PORT", 8080)
    port_audio = os.getenv("VLC_AUDIO_PORT", 8081)

    password = os.getenv("VLC_PASSWORD")
    password_audio = os.getenv("VLC_AUDIO_PASSWORD", password)

    base_path = os.getenv("BASE_PATH")

    vlc = HttpVLCExt(
        host=f"{base_host}:{port}",
        password=password,
    )
    vlc2 = HttpVLCExt(
        host=f"{base_audio_host}:{port_audio}",
        password=password,
    )

    print(vlc.fetch_playlist())
    print(vlc.fetch_status())
    # print(vlc.fetch_data())

    dj = AutoMediaDJ(
        vlc=vlc,
        vlc_audio=vlc2,
        base_path=base_path,
    )

    dj.start()
