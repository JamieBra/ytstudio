from http.cookiejar import MozillaCookieJar
from pprint import pprint

from ytstudio.ytstudio import Studio
from ytstudio.ytstudio.templates import ALL_TRUE

jar = MozillaCookieJar('cookies.txt')
jar.load()
with open('token') as fp:
    token = fp.read()

with Studio(jar, token) as studio:
    # get 10 videos, but do not retrieve any attributes
    videos = studio.list_videos(10)
    pprint(videos)

    # get 50 videos, and retrieve scheduling information, titles, and video IDs
    videos = studio.list_videos(
        50,
        scheduledPublishingDetails=ALL_TRUE,
        title=True,
        videoId=True
    )
    pprint(videos)
