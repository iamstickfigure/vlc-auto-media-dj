import os
from dj import AutoMediaDJ
import dotenv
from vlc_ext import HttpVLCExt


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
