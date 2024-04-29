import enum
import itertools


class FieldIds(enum.IntEnum):
    TITLE = 0
    ARTIST = 2
    URL = 3
    DESCRIPTION = 4
    NOTES = 5
    TAGS = 6
    CONTENT_TAGS = 7
    META_TAGS = 8
    ARCHIVED = 15
    FAVORITE = 16
    SOURCE = 21
    COMMENTS = 30
    OPTIONAL_AUDIO = 999
    OPTIONAL_VISUALS = 1000
    HAS_MUSIC = 1001
    NEEDS_VISUALS = 1002
    VISUALS = 1003
    CHAPTER_RANGES = 1004
    SKIP_CHAPTERS = 1005
    REQUIRED_AUDIO = 1006
    REQUIRED_VISUALS = 1007


# https://github.com/CyanVoxel/TagStudio/blob/main/tagstudio/src/core/library.py
FIELDS = [
    {"id": FieldIds.TITLE, "name": "Title", "type": "text_line"},
    {"id": 1, "name": "Author", "type": "text_line"},
    {"id": FieldIds.ARTIST, "name": "Artist", "type": "text_line"},
    {"id": FieldIds.URL, "name": "URL", "type": "text_line"},
    {"id": FieldIds.DESCRIPTION, "name": "Description", "type": "text_box"},
    {"id": FieldIds.NOTES, "name": "Notes", "type": "text_box"},
    {"id": FieldIds.TAGS, "name": "Tags", "type": "tag_box"},
    {"id": FieldIds.CONTENT_TAGS, "name": "Content Tags", "type": "tag_box"},
    {"id": FieldIds.META_TAGS, "name": "Meta Tags", "type": "tag_box"},
    {"id": 9, "name": "Collation", "type": "collation"},
    {"id": 10, "name": "Date", "type": "datetime"},
    {"id": 11, "name": "Date Created", "type": "datetime"},
    {"id": 12, "name": "Date Modified", "type": "datetime"},
    {"id": 13, "name": "Date Taken", "type": "datetime"},
    {"id": 14, "name": "Date Published", "type": "datetime"},
    {"id": FieldIds.ARCHIVED, "name": "Archived", "type": "checkbox"},
    {"id": FieldIds.FAVORITE, "name": "Favorite", "type": "checkbox"},
    {"id": 17, "name": "Book", "type": "collation"},
    {"id": 18, "name": "Comic", "type": "collation"},
    {"id": 19, "name": "Series", "type": "collation"},
    {"id": 20, "name": "Manga", "type": "collation"},
    {"id": FieldIds.SOURCE, "name": "Source", "type": "text_line"},
    {"id": 22, "name": "Date Uploaded", "type": "datetime"},
    {"id": 23, "name": "Date Released", "type": "datetime"},
    {"id": 24, "name": "Volume", "type": "collation"},
    {"id": 25, "name": "Anthology", "type": "collation"},
    {"id": 26, "name": "Magazine", "type": "collation"},
    {"id": 27, "name": "Publisher", "type": "text_line"},
    {"id": 28, "name": "Guest Artist", "type": "text_line"},
    {"id": 29, "name": "Composer", "type": "text_line"},
    {"id": FieldIds.COMMENTS, "name": "Comments", "type": "text_box"},
]

CUSTOM_FIELDS = [
    {"id": FieldIds.OPTIONAL_AUDIO, "name": "Optional Audio", "type": "checkbox"},
    {"id": FieldIds.OPTIONAL_VISUALS, "name": "Optional Visuals", "type": "checkbox"},
    {"id": FieldIds.HAS_MUSIC, "name": "Has Music", "type": "checkbox"},
    {"id": FieldIds.NEEDS_VISUALS, "name": "Needs Visuals", "type": "checkbox"},
    {"id": FieldIds.VISUALS, "name": "Visuals", "type": "checkbox"},
    {"id": FieldIds.CHAPTER_RANGES, "name": "Chapter Ranges", "type": "text_box"},
    {"id": FieldIds.SKIP_CHAPTERS, "name": "Skip Chapters", "type": "text_box"},
    {"id": FieldIds.REQUIRED_AUDIO, "name": "Required Audio", "type": "checkbox"},
    {"id": FieldIds.REQUIRED_VISUALS, "name": "Required Visuals", "type": "checkbox"},
]

ALL_FIELDS_BY_ID = {
    field["id"]: field for field in itertools.chain(FIELDS, CUSTOM_FIELDS)
}

SHARED_FIELDS = [
    FIELDS[FieldIds.TITLE],
    FIELDS[FieldIds.ARTIST],
    FIELDS[FieldIds.URL],
    FIELDS[FieldIds.TAGS],
    FIELDS[FieldIds.CONTENT_TAGS],
    FIELDS[FieldIds.META_TAGS],
    ALL_FIELDS_BY_ID[FieldIds.OPTIONAL_AUDIO],
    ALL_FIELDS_BY_ID[FieldIds.OPTIONAL_VISUALS],
    ALL_FIELDS_BY_ID[FieldIds.HAS_MUSIC],
    ALL_FIELDS_BY_ID[FieldIds.NEEDS_VISUALS],
]

IMG_TAG = {"name": "Image", "shorthand": "img", "aliases": ["picture"]}
VID_TAG = {"name": "Video", "shorthand": "vid", "aliases": ["movie"]}
AUD_TAG = {"name": "Audio", "shorthand": "aud", "aliases": ["music"]}


class PlaybackMode(enum.StrEnum):
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    GIF = "gif"


class DJMode(enum.StrEnum):
    FUNNY = "funny"
    MUSIC_AND_VISUALS = "music_and_visuals"
    MUSIC_VIDEOS = "music_videos"
    SEXY = "sexy"


class DJState(enum.StrEnum):
    STOPPED = "stopped"
    STARTING = "starting"
    PLAYING = "playing"
    PAUSING = "pausing"
    PAUSED = "paused"
    RESUMING = "resuming"


class TagColor(enum.StrEnum):
    DEFAULT = ""
    BLACK = "black"
    DARK_GRAY = "dark gray"
    GRAY = "gray"
    LIGHT_GRAY = "light gray"
    WHITE = "white"
    LIGHT_PINK = "light pink"
    PINK = "pink"
    MAGENTA = "magenta"
    RED = "red"
    RED_ORANGE = "red orange"
    SALMON = "salmon"
    ORANGE = "orange"
    YELLOW_ORANGE = "yellow orange"
    YELLOW = "yellow"
    MINT = "mint"
    LIME = "lime"
    LIGHT_GREEN = "light green"
    GREEN = "green"
    TEAL = "teal"
    CYAN = "cyan"
    LIGHT_BLUE = "light blue"
    BLUE = "blue"
    BLUE_VIOLET = "blue violet"
    VIOLET = "violet"
    PURPLE = "purple"
    PEACH = "peach"
    BROWN = "brown"
    LAVENDER = "lavender"
    BLONDE = "blonde"
    AUBURN = "auburn"
    LIGHT_BROWN = "light brown"
    DARK_BROWN = "dark brown"
    COOL_GRAY = "cool gray"
    WARM_GRAY = "warm gray"
    OLIVE = "olive"
    BERRY = "berry"


class TagId(enum.IntEnum):
    ARCHIVED = 0
    FAVORITE = 1
    PERSON = 1000
    IMAGE = 1001
    VIDEO = 1002
    AUDIO = 1003
    NSFW = 1004
    MOVIE = 1005
    SILENT_VIDEO = 1006
    MUSIC_VIDEO = 1007
    GAMING_VIDEO = 1008
    YOUTUBE = 1009
    NSFW_MEMES = 1010
    MUSIC = 1011
    GAMING = 1012
    MEME = 1013
    ART_IMAGE = 1014
    PHOTOGRAPHY = 1015
    SCREENSHOT = 1016
    GIF = 1017
    MANGA = 1018
    COMIC = 1019
    CARTOON = 1020
    ANIME = 1021
    ILLUSTRATION = 1022
    FANART = 1023
    COSPLAY = 1024
    PHOTOMANIPULATION = 1025
    _3D_ART = 1026
    PIXEL_ART = 1027
    VECTOR_ART = 1028
    MEME_IMAGE = 1029
    MEME_VIDEO = 1030
    FUNNY = 1031
    STAR_WARS = 1032
    STAR_TREK = 1033
    DR_WHO = 1034
    SCI_FI = 1035
    SPACE = 1036
    YOUTUBE_POOP = 1037
    AI_GENERATION = 1038
    AUDIOVISUAL_VIDEO = 1039
    VID_WITH_MUSIC = 1040
    SATIRE = 1041
    PARODY = 1042
    SARCASM = 1043
    DARK_HUMOR = 1044
    SILLY_HUMOR = 1045
    ADVERTISEMENT = 1046
    POLITICAL = 1047
    NEEDS_CUTS = 1048
    NEEDS_TRIM = 1049
    BROKEN = 1050
    VISUALS = 1051
    HAS_MUSIC = 1052
    NO_MUSIC = 1053
    NEEDS_VISUALS = 1054
    HAS_OPTIONAL_VISUALS = 1055
    PORTRAIT_VIDEO = 1056
    FANTASY = 1057
    NEEDS_WORK = 1058
    ROBOT_CHICKEN = 1059
    REQUIRED_AUDIO = 1060
    REQUIRED_VISUALS = 1061
    PREFERRED_AUDIO = 1062
    PREFERRED_VISUALS = 1063
    BAD_AUDIO = 1064
    BAD_VISUALS = 1065
    OPTIONAL_AUDIO = 1066


BASE_TAGS = [
    {
        "id": TagId.ARCHIVED,
        "name": "Archived",
        "aliases": ["Archive"],
        "color": TagColor.RED,
    },
    {
        "id": TagId.FAVORITE,
        "name": "Favorite",
        "aliases": ["Favorited", "Favorites"],
        "color": TagColor.YELLOW,
    },
    {
        "id": TagId.PERSON,
        "name": "Person",
        "shorthand": "human",
        "aliases": ["people", "human", "person"],
        "color": TagColor.BLUE,
    },
    {
        "id": TagId.IMAGE,
        "name": "Image",
        "shorthand": "img",
        "aliases": ["picture"],
        "subtags": [TagId.REQUIRED_VISUALS, TagId.NO_MUSIC, TagId.BAD_AUDIO],
    },
    {
        "id": TagId.VIDEO,
        "name": "Video",
        "shorthand": "vid",
        "aliases": ["movie"],
    },
    {
        "id": TagId.AUDIO,
        "name": "Audio",
        "shorthand": "aud",
        "aliases": [""],
    },
    {
        "id": TagId.NSFW,
        "name": "NSFW",
        "shorthand": "nsfw",
        "aliases": ["nsfw", "explicit", "adult", "pornographic"],
        "color": TagColor.RED,
    },
    {
        "id": TagId.MOVIE,
        "name": "Movie",
        "shorthand": "movie",
        "aliases": ["film", "cinema"],
        "color": TagColor.BLUE,
        "subtag_ids": [TagId.VIDEO],
    },
    {
        "id": TagId.SILENT_VIDEO,
        "name": "Silent Video",
        "shorthand": "silent_vid",
        "aliases": [""],
        "subtag_ids": [TagId.VIDEO, TagId.NO_MUSIC, TagId.BAD_AUDIO, TagId.VISUALS],
    },
    {
        "id": TagId.MUSIC_VIDEO,
        "name": "Music Video",
        "shorthand": "music_vid",
        "aliases": [""],
        "subtag_ids": [
            TagId.VIDEO,
            TagId.MUSIC,
            TagId.VID_WITH_MUSIC,
            TagId.HAS_MUSIC,
            TagId.PREFERRED_AUDIO,
            TagId.PREFERRED_VISUALS,
        ],
    },
    {
        "id": TagId.GAMING_VIDEO,
        "name": "Gaming Video",
        "shorthand": "game_vid",
        "aliases": ["game"],
        "color": TagColor.LIGHT_GREEN,
        "subtag_ids": [TagId.VIDEO, TagId.GAMING],
    },
    {
        "id": TagId.YOUTUBE,
        "name": "YouTube",
        "shorthand": "yt",
        "aliases": [""],
        "color": TagColor.RED,
        "subtag_ids": [TagId.VIDEO],
    },
    {
        "id": TagId.NSFW_MEMES,
        "name": "NSFW Memes",
        "shorthand": "nsfw_memes",
        "aliases": ["meme_nsfw", "nsfw_meme"],
        "color": TagColor.RED,
        "subtag_ids": [TagId.NSFW, TagId.MEME],
    },
    {
        "id": TagId.MUSIC,
        "name": "Music",
        "shorthand": "music",
        "aliases": [""],
        "color": TagColor.BLUE,
        "subtag_ids": [TagId.VID_WITH_MUSIC, TagId.HAS_MUSIC],
    },
    {
        "id": TagId.GAMING,
        "name": "Gaming",
        "shorthand": "game",
        "aliases": ["game"],
        "color": TagColor.LIGHT_GREEN,
    },
    {
        "id": TagId.MEME,
        "name": "Meme",
        "shorthand": "meme",
        "aliases": ["funny"],
        "color": TagColor.YELLOW,
        "subtag_ids": [TagId.FUNNY],
    },
    {
        "id": TagId.ART_IMAGE,
        "name": "Art Image",
        "shorthand": "art_img",
        "aliases": ["drawing", "painting", "illustration"],
        "color": TagColor.PURPLE,
        "subtag_ids": [TagId.IMAGE],
    },
    {
        "id": TagId.PHOTOGRAPHY,
        "name": "Photography",
        "shorthand": "photo",
        "aliases": ["photo", "photograph"],
        "color": TagColor.CYAN,
        "subtag_ids": [TagId.IMAGE],
    },
    {
        "id": TagId.SCREENSHOT,
        "name": "Screenshot",
        "shorthand": "screenshot",
        "aliases": ["screen", "capture"],
        "color": TagColor.ORANGE,
        "subtag_ids": [TagId.IMAGE],
    },
    {
        "id": TagId.GIF,
        "name": "GIF",
        "shorthand": "gif",
        "aliases": ["animated"],
        "color": TagColor.PINK,
        "subtag_ids": [TagId.IMAGE, TagId.SILENT_VIDEO],
    },
    {
        "id": TagId.MANGA,
        "name": "Manga",
        "shorthand": "manga",
        "aliases": [""],
        "color": TagColor.PURPLE,
        "subtag_ids": [TagId.IMAGE, TagId.COMIC, TagId.ANIME],
    },
    {
        "id": TagId.COMIC,
        "name": "Comic",
        "shorthand": "comic",
        "aliases": [""],
        "color": TagColor.ORANGE,
        "subtag_ids": [TagId.IMAGE],
    },
    {
        "id": TagId.CARTOON,
        "name": "Cartoon",
        "shorthand": "cartoon",
        "aliases": [""],
        "color": TagColor.YELLOW,
        "subtag_ids": [TagId.REQUIRED_VISUALS],
    },
    {
        "id": TagId.ANIME,
        "name": "Anime",
        "shorthand": "anime",
        "aliases": [""],
        "color": TagColor.BLUE,
        "subtag_ids": [TagId.CARTOON],
    },
    {
        "id": TagId.ILLUSTRATION,
        "name": "Illustration",
        "shorthand": "illustration",
        "aliases": [""],
        "color": TagColor.PURPLE,
        "subtag_ids": [TagId.IMAGE],
    },
    {
        "id": TagId.FANART,
        "name": "Fanart",
        "shorthand": "fanart",
        "aliases": [""],
        "color": TagColor.PURPLE,
        "subtag_ids": [TagId.IMAGE],
    },
    {
        "id": TagId.COSPLAY,
        "name": "Cosplay",
        "shorthand": "cosplay",
        "aliases": [""],
        "color": TagColor.CYAN,
    },
    {
        "id": TagId.PHOTOMANIPULATION,
        "name": "Photomanipulation",
        "shorthand": "photomanip",
        "aliases": [""],
        "color": TagColor.CYAN,
    },
    {
        "id": TagId._3D_ART,
        "name": "3D Art",
        "shorthand": "3d_art",
        "aliases": [""],
        "color": TagColor.PURPLE,
    },
    {
        "id": TagId.PIXEL_ART,
        "name": "Pixel Art",
        "shorthand": "pixel_art",
        "aliases": [""],
        "color": TagColor.PURPLE,
    },
    {
        "id": TagId.VECTOR_ART,
        "name": "Vector Art",
        "shorthand": "vector_art",
        "aliases": [""],
        "color": TagColor.PURPLE,
        "subtag_ids": [TagId.IMAGE],
    },
    {
        "id": TagId.MEME_IMAGE,
        "name": "Meme Image",
        "shorthand": "meme_img",
        "aliases": [""],
        "color": TagColor.YELLOW,
        "subtag_ids": [TagId.IMAGE, TagId.MEME],
    },
    {
        "id": TagId.MEME_VIDEO,
        "name": "Meme Video",
        "shorthand": "meme_vid",
        "aliases": [""],
        "color": TagColor.YELLOW,
        "subtag_ids": [TagId.VIDEO, TagId.MEME, TagId.REQUIRED_VISUALS],
    },
    {
        "id": TagId.FUNNY,
        "name": "Funny",
        "shorthand": "funny",
        "aliases": ["lol", "haha", "humour", "humor", "comedy"],
        "color": TagColor.YELLOW,
    },
    {
        "id": TagId.STAR_WARS,
        "name": "Star Wars",
        "shorthand": "star_wars",
        "aliases": [""],
        "color": TagColor.BLUE,
        "subtag_ids": [TagId.SCI_FI, TagId.SPACE],
    },
    {
        "id": TagId.STAR_TREK,
        "name": "Star Trek",
        "shorthand": "star_trek",
        "aliases": [""],
        "color": TagColor.BLUE,
        "subtag_ids": [TagId.SCI_FI, TagId.SPACE],
    },
    {
        "id": TagId.DR_WHO,
        "name": "Dr. Who",
        "shorthand": "dr_who",
        "aliases": ["doctor_who", "doctorwho", "drwho", "doctor"],
        "color": TagColor.BLUE,
        "subtag_ids": [TagId.SCI_FI, TagId.SPACE],
    },
    {
        "id": TagId.SCI_FI,
        "name": "Sci-Fi",
        "shorthand": "sci_fi",
        "aliases": ["science_fiction", "scifi"],
        "color": TagColor.BLUE,
    },
    {
        "id": TagId.SPACE,
        "name": "Space",
        "shorthand": "space",
        "aliases": [""],
        "color": TagColor.BLUE,
    },
    {
        "id": TagId.YOUTUBE_POOP,
        "name": "YouTube Poop",
        "shorthand": "ytp",
        "aliases": [""],
        "color": TagColor.BROWN,
        "subtag_ids": [
            TagId.YOUTUBE,
            TagId.SILLY_HUMOR,
            TagId.REQUIRED_VISUALS,
            TagId.PREFERRED_AUDIO,
        ],
    },
    {
        "id": TagId.AI_GENERATION,
        "name": "AI Generation",
        "shorthand": "ai_gen",
        "aliases": [
            "ai",
            "artificial_intelligence",
            "machine_learning",
            "deep_learning",
            "neural_networks",
            "gen_ai",
            "ai_art",
            "ai_generated",
        ],
        "color": TagColor.GREEN,
    },
    {
        "id": TagId.AUDIOVISUAL_VIDEO,
        "name": "AudioVisual Video",
        "shorthand": "audiovisual_vid",
        "aliases": ["av", "audiovisual"],
        "color": TagColor.BLUE,
        "subtag_ids": [TagId.VIDEO, TagId.PREFERRED_VISUALS],
    },
    {
        "id": TagId.VID_WITH_MUSIC,
        "name": "Video with Music",
        "shorthand": "vid_with_music",
        "aliases": ["has_music"],
        "color": TagColor.BLUE,
        "subtag_ids": [TagId.VIDEO, TagId.HAS_MUSIC],
    },
    {
        "id": TagId.SATIRE,
        "name": "Satire",
        "shorthand": "satire",
        "aliases": ["satirical"],
        "color": TagColor.ORANGE,
    },
    {
        "id": TagId.PARODY,
        "name": "Parody",
        "shorthand": "parody",
        "aliases": ["spoof"],
        "color": TagColor.ORANGE,
        "subtag_ids": [TagId.FUNNY],
    },
    {
        "id": TagId.SARCASM,
        "name": "Sarcasm",
        "shorthand": "sarcasm",
        "aliases": ["sarcastic"],
        "color": TagColor.ORANGE,
    },
    {
        "id": TagId.DARK_HUMOR,
        "name": "Dark Humor",
        "shorthand": "dark_humor",
        "aliases": ["black_comedy", "dark_comedy"],
        "color": TagColor.BROWN,
        "subtag_ids": [TagId.FUNNY],
    },
    {
        "id": TagId.SILLY_HUMOR,
        "name": "Silly Humor",
        "shorthand": "silly_humor",
        "aliases": ["silly", "goofy", "dumb"],
        "color": TagColor.YELLOW,
        "subtag_ids": [TagId.FUNNY],
    },
    {
        "id": TagId.ADVERTISEMENT,
        "name": "Advertisement",
        "shorthand": "ad",
        "aliases": ["commercial"],
        "color": TagColor.GREEN,
        "subtag_ids": [TagId.REQUIRED_VISUALS, TagId.REQUIRED_AUDIO],
    },
    {
        "id": TagId.POLITICAL,
        "name": "Political",
        "shorthand": "political",
        "aliases": ["politics"],
        "color": TagColor.PURPLE,
    },
    {
        "id": TagId.NEEDS_CUTS,
        "name": "Needs Cuts",
        "shorthand": "needs_cut",
        "aliases": [""],
        "color": TagColor.RED_ORANGE,
    },
    {
        "id": TagId.NEEDS_TRIM,
        "name": "Needs Trim",
        "shorthand": "needs_trim",
        "aliases": ["trim_me"],
        "color": TagColor.ORANGE,
    },
    {
        "id": TagId.BROKEN,
        "name": "Broken?",
        "shorthand": "broken",
        "aliases": [""],
        "color": TagColor.GRAY,
    },
    {
        "id": TagId.VISUALS,
        "name": "Visuals",
        "shorthand": "vis",
        "aliases": ["can_mute", "audio_not_needed"],
        "color": TagColor.CYAN,
        "subtag_ids": [TagId.VIDEO, TagId.OPTIONAL_AUDIO],
    },
    {
        "id": TagId.HAS_MUSIC,
        "name": "Has Music",
        "shorthand": "has_music",
        "aliases": ["mute_if_external_music"],
        "color": TagColor.PEACH,
    },
    {
        "id": TagId.NO_MUSIC,
        "name": "No Music",
        "shorthand": "no_music",
        "aliases": ["can_play_w_external_music"],
        "color": TagColor.BLONDE,
    },
    {
        "id": TagId.NEEDS_VISUALS,
        "name": "Needs Visuals",
        "shorthand": "needs_visuals",
        "aliases": ["no_visuals", "boring_image"],
        "color": TagColor.LAVENDER,
        "subtag_ids": [TagId.BAD_VISUALS, TagId.REQUIRED_AUDIO],
    },
    {
        "id": TagId.HAS_OPTIONAL_VISUALS,
        "name": "Has Optional Visuals",
        "shorthand": "opt_vis",
        "aliases": ["can_use_as_music", "can_be_music"],
        "color": TagColor.LAVENDER,
        "subtag_ids": [TagId.VIDEO],
    },
    {
        "id": TagId.PORTRAIT_VIDEO,
        "name": "Portrait Video",
        "shorthand": "portrait_vid",
        "aliases": [""],
        "color": TagColor.LIGHT_PINK,
        "subtag_ids": [TagId.VIDEO],
    },
    {
        "id": TagId.FANTASY,
        "name": "Fantasy",
        "shorthand": "fantasy",
        "aliases": [""],
        "color": TagColor.GREEN,
    },
    {
        "id": TagId.NEEDS_WORK,
        "name": "Needs Work",
        "shorthand": "wip",
        "aliases": [""],
        "color": TagColor.BLACK,
    },
    {
        "id": TagId.ROBOT_CHICKEN,
        "name": "Robot Chicken",
        "shorthand": "robot_chicken",
        "aliases": [""],
        "subtag_ids": [
            TagId.SILLY_HUMOR,
            TagId.PARODY,
            TagId.REQUIRED_VISUALS,
            TagId.PREFERRED_AUDIO,
        ],
        "color": TagColor.LIGHT_GRAY,
    },
    {
        "id": TagId.REQUIRED_AUDIO,
        "name": "Required Audio",
        "shorthand": "req_audio",
        "aliases": ["no_mute", "dont_mute", "audio_required"],
        "color": TagColor.LIGHT_BLUE,
    },
    {
        "id": TagId.REQUIRED_VISUALS,
        "name": "Required Visuals",
        "shorthand": "req_vis",
        "aliases": ["visuals_required"],
        "color": TagColor.LIGHT_PINK,
    },
    {
        "id": TagId.PREFERRED_AUDIO,
        "name": "Preferred Audio",
        "shorthand": "pref_audio",
        "aliases": ["audio_preferred"],
        "color": TagColor.LIGHT_GREEN,
    },
    {
        "id": TagId.PREFERRED_VISUALS,
        "name": "Preferred Visuals",
        "shorthand": "pref_vis",
        "aliases": ["visuals_preferred"],
        "color": TagColor.LIGHT_PINK,
    },
    {
        "id": TagId.BAD_AUDIO,
        "name": "Bad Audio",
        "shorthand": "bad_audio",
        "aliases": ["audio_not_good", "please_mute", "mute"],
        "color": TagColor.RED,
        "subtag_ids": [TagId.VISUALS, TagId.REQUIRED_VISUALS],
    },
    {
        "id": TagId.BAD_VISUALS,
        "name": "Bad Visuals",
        "shorthand": "bad_vis",
        "aliases": ["bad_image", "boring_video", "visuals_not_good"],
        "color": TagColor.LIGHT_PINK,
        "subtag_ids": [TagId.NEEDS_VISUALS],
    },
    {
        "id": TagId.OPTIONAL_AUDIO,
        "name": "Optional Audio",
        "shorthand": "opt_audio",
        "aliases": ["audio_optional", "can_mute"],
        "color": TagColor.LIGHT_BLUE,
        "subtag_ids": [TagId.VISUALS],
    },
]

ALL_TAGS_BY_ID = {tag["id"]: tag for tag in BASE_TAGS}
