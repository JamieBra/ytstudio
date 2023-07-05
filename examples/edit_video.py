from datetime import datetime, timedelta
from json import load

from ytstudio.ytstudio import Studio
from ytstudio.ytstudio.typing import Visibility

with open('login.json') as fp:
    cookies = load(fp)

with Studio(cookies) as studio:
    # update every built-in option and some extra ones
    studio.edit_video(
        'aaaaaaaa',  # video ID
        'new title',  # title
        'new description',  # description
        'new thumbnail.png',  # thumbnail file path (png, jpg, jpeg, <2MB)
        ['aaaaa', 'bbbbbb'],  # add to playlists IDs
        ['ccccc', 'ddddd'],  # delete from playlists IDs
        Visibility.PUBLIC,  # new privacy status
        False,  # made for kids
        True,  # restrict to 18+

        category=dict(newCategoryId=22),  # category
        monetizationSettings=dict(
            newMonetization=True,
            newMonetizeWithAds=True
        ),  # monetization
        tags=dict(newTags=['test', 'test2'])  # tags
    )

    # update a few options but leave the rest the same
    studio.edit_video(
        'aaaaaaaa',  # video ID
        thumbnail=2,  # index of autogenerated thumbnails (1 - 3)
        delete_from_playlist_ids=['ccccc', 'ddddd'],  # delete from playlists IDs
        visibility='UNLISTED',  # new privacy status using a str
    )

    # schedule a video to be published later
    studio.edit_video(
        'aaaaaaaa',  # video ID
        visibility=datetime.now() + timedelta(1)  # schedule the video to be published in exactly a day from now
    )

    # schedule a video to be published later using a timestamp
    studio.edit_video(
        'aaaaaaaa',  # video ID
        visibility=1688097600  # schedule the video to be published June 30, 2023 at 12 AM Eastern Time
    )
