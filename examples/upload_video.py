from json import load

from rich import progress

from ytstudio.ytstudio import Studio
from ytstudio.ytstudio.typing import Visibility

file = 'test_video.mp4'

with open('login.json') as fp:
    cookies = load(fp)

with Studio(cookies) as studio:
    # upload file without progress bar and using default fields
    with open(file, 'rb') as data:  # open as byte stream to prevent entire file from being read into memory
        video_id = studio.upload_video(data)
        print(f'Successfully uploaded! videoId: {video_id}')

    # upload file with rich progress bar and using default fields
    with progress.open(file, 'rb') as data:
        video_id = studio.upload_video(data)
        print(f'Successfully uploaded! videoId: {video_id}')

    # upload file with rich progress bar and using custom fields
    with progress.open(file, 'rb') as data:
        video_id = studio.upload_video(data, 'New title', 'New description\nAnd stuff!', Visibility.UNLISTED, draft=False)
        print(f'Successfully uploaded! videoId: {video_id}')

    # upload arbitrary data stream
    data = 'aaaaaaaaaaa BBBBBBBBBBBBBBB ccccccccccccccc'
    video_id = studio.upload_video(data)
    print(f'Successfully uploaded! videoId: {video_id}')
