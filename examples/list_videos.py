from json import load
from pprint import pprint

from ytstudio.ytstudio import Studio
from ytstudio.ytstudio.templates import ALL_TRUE

with open('login.json') as fp:
    cookies = load(fp)

with Studio(cookies) as studio:
    # get 10 videos, but do not retrieve any attributes
    videos = studio.list_videos(10)
    pprint(videos)

    # get all videos, but do not retrieve any attributes
    videos = studio.list_videos()
    pprint(videos)

    # get all videos, and retrieve scheduling information, titles, and video IDs
    videos = studio.list_videos(
        scheduledPublishingDetails=ALL_TRUE,
        title=True,
        videoId=True
    )
    pprint(videos)
