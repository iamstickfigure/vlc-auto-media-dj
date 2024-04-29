import json
import time
from typing import Any, Dict, List, Optional
from functools import cached_property
from pydantic import BaseModel, computed_field
from constants import (
    FIELDS,
    DJMode,
    DJState,
    PlaybackMode,
)
import os
import itertools
import random
import utils

from models import Entry, PlaybackInfo, VlcPlayerDataSnapshot
from utils import windows_path_to_wsl
from vlc_ext import HttpVLCExt

logger = utils.get_logger(__name__)


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
    def media_choices(self) -> List[Entry]:
        return [entry for entry in self.entries if not entry.is_archived]

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
        return [entry for entry in self.media_choices if entry.is_background_music]

    @computed_field
    @cached_property
    def audiovisual_choices(self) -> List[Entry]:
        return [entry for entry in self.media_choices if entry.is_audiovisual]

    @computed_field
    @cached_property
    def visual_choices(self) -> List[Entry]:
        return [entry for entry in self.media_choices if entry.is_visual]

    def queue_video(self, video_info: PlaybackInfo):
        if video_info.playback_mode == PlaybackMode.AUDIO:
            raise ValueError("Cannot queue audio with this method")

        logger.debug(f"Queueing video: {video_info}")

        mrl_list = video_info.get_mrls()

        for mrl in mrl_list:
            self.vlc.enqueue(mrl)

        self.video_queue.append(video_info)

    def queue_audio(self, audio_info: PlaybackInfo):
        if audio_info.playback_mode != PlaybackMode.AUDIO:
            raise ValueError("Can only queue audio with this method")

        logger.debug(f"Queueing audio: {audio_info}")

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
            logger.debug(f"Waiting for more videos to be queued...")
            return False

        if self.vlc_audio.enabled and len(self.audio_queue) < 2:
            # Wait for more audio to be queued before starting playback
            logger.debug(f"Waiting for more audio to be queued...")
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
                    logger.debug(
                        f"Video ended: {self.video_playing.entry.filename}\n"
                        f" - end_time: {self.video_playing.end_time} => {timestamp} (delta {timestamp - self.video_playing.end_time})\n"
                    )

                    self.play_history.append(self.video_playing)
                    self.video_playing.end_time = timestamp
                    self.video_playing = None

                # If video_playing is None, we need to consume the queue and update the current playback info
                if self.video_playing is None:
                    self.video_playing = self.video_queue.pop(0)
                    logger.info(f"Playing video: {self.video_playing}")

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
                    logger.debug(
                        f"Audio ended: {self.audio_playing.entry.filename}\n"
                        f" - end_time: {self.audio_playing.end_time} => {timestamp} (delta {timestamp - self.audio_playing.end_time})\n"
                    )

                    self.play_history_audio.append(self.audio_playing)
                    self.audio_playing.end_time = timestamp
                    self.audio_playing = None

                # If audio_playing is None, we need to consume the queue and update the current playback info
                if self.audio_playing is None:
                    self.audio_playing = self.audio_queue.pop(0)
                    logger.info(f"Playing audio: {self.audio_playing}")

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
                logger.info("Muting video...")
                self.vlc.set_volume(0)
            elif vid_info and not vid_info.is_muted and video_player_data.volume == 0:
                logger.info("Unmuting video...")
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
                # All players are playing, so continue
                logger.info(
                    "All players are playing\n - updating DJState: STARTING => PLAYING"
                )
                self.state = DJState.PLAYING
                return

            if not vid_info and video_player_data.volume == 0:
                logger.debug("Starting: Unmuting video...")
                self.vlc.set_volume(1)

            if not aud_info and audio_player_data.volume == 0:
                logger.debug("Starting: Unmuting audio...")
                self.vlc_audio.set_volume(1)

            if not is_ready:
                return

            logger.debug("Starting all active players...")
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
                logger.info(
                    "All players have paused\n - updating DJState: PLAYING => PAUSED"
                )
                self.state = DJState.PAUSED
                return

            # If any active player is not playing anymore, initiate a pause
            # Don't return here. Might as well continue to the next state
            logger.info(
                "Some players are not playing, initiate pause\n"
                " - updating DJState: PLAYING => PAUSING"
            )
            self.state = DJState.PAUSING

        # A pause has been initiated
        if self.state == DJState.PAUSING:
            if is_paused:
                # All players have successfully paused
                logger.info(
                    "All players have paused\n - updating DJState: PAUSING => PAUSED"
                )
                self.state = DJState.PAUSED
                return

            # If any active player is still playing, continue pausing
            logger.debug("Pausing all players...")
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
            logger.info(
                "Some players are not paused, initiate resume\n"
                " - updating DJState: PAUSED => RESUMING"
            )
            self.state = DJState.RESUMING

        # A resume has been initiated
        if self.state == DJState.RESUMING:
            if is_playing:
                # All players have successfully resumed
                logger.info(
                    "All players have resumed\n - updating DJState: RESUMING => PLAYING"
                )
                self.state = DJState.PLAYING
                return

            # If any active player is still paused, continue resuming
            # self.vlc.resume()
            logger.debug("Resuming all players...")
            self.vlc.play(muted=vid_info.is_muted)
            self.vlc_audio.play(muted=aud_info.is_muted)
            return

    def start(self):
        # Start the DJ loop
        logger.info("Starting DJ loop...")
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
