from typing import Any, Dict, List, Optional, Tuple
from functools import cached_property
from pydantic import BaseModel, computed_field
from constants import (
    ALL_FIELDS_BY_ID,
    DJMode,
    FieldIds,
    PlaybackMode,
    TagId,
)
import os

from utils import mrl_from_path, search_for_tag


class VlcPlayerDataSnapshot(BaseModel):
    data: Dict[str, Any]

    @property
    def filename(self) -> Optional[str]:
        meta = self.metadata

        if meta is None:
            return None

        filename = meta.get("filename")

        if filename is None:
            return None

        return filename.encode("latin1").decode("utf-8")

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

    def has_meta_tag(self, tag_id: int) -> bool:
        return search_for_tag(tag_id, self.meta_tags)

    @computed_field
    def is_archived(self) -> bool:
        return self.get_checkbox_val(FieldIds.ARCHIVED) or self.has_meta_tag(
            TagId.ARCHIVED
        )

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
    volume: float = 1.0
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

    def __str__(self) -> str:
        info = [
            f"{self.entry.filename} ({self.entry.id})",
        ]

        if self.chapter_range is not None:
            info.append(f" - chapter_range: {self.chapter_range}")

        if self.skip_chapters is not None:
            info.append(f" - skip_chapters: {self.skip_chapters}")

        if self.is_muted:
            info.append(f" - is_muted: {self.is_muted}")

        if self.volume != 1.0:
            info.append(f" - volume: {self.volume}")

        return "\n".join(info)
