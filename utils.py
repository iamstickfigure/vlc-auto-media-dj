import logging
from typing import Dict, List, Optional
from constants import ALL_TAGS_BY_ID
import urllib.parse
import urllib
import cachetools


def get_logger(name: str):
    # The filehandler should be at the debug level, the streamhandler at the info level
    filehandler = logging.FileHandler("app.log")
    filehandler.setLevel(logging.DEBUG)

    streamhandler = logging.StreamHandler()
    streamhandler.setLevel(logging.INFO)

    # Create a formatter and add it to the filehandler
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    print_formatter = logging.Formatter("%(message)s")
    filehandler.setFormatter(formatter)
    streamhandler.setFormatter(print_formatter)

    # Add the handlers to the logger
    logger = logging.getLogger(name)
    logger.addHandler(filehandler)
    logger.addHandler(streamhandler)

    # Set the logger level
    logger.setLevel(logging.DEBUG)

    return logger


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
