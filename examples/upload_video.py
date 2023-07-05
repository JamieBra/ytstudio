from json import load
from os.path import getsize
from typing import TYPE_CHECKING, cast

from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from ytstudio.ytstudio import Studio
from ytstudio.ytstudio.typing import Visibility

if TYPE_CHECKING:
    from _typeshed import SupportsRead

file = 'test_video.mp4'

with open('login.json') as fp:
    cookies = load(fp)

with Studio(cookies) as studio:
    # upload file without progress bar and using default fields
    with open(file, 'rb') as data:  # open as byte stream to prevent entire file from being read into memory
        video_id = studio.upload_video(data)
        print(f'Successfully uploaded! videoId: {video_id}')

    # upload file with tqdm progress bar and using default fields
    with open(file, 'rb') as stream, tqdm(total=getsize(file), unit_scale=True) as pbar:
        data = CallbackIOWrapper(pbar.update, stream)
        data = cast(SupportsRead[bytes], data)  # optionally tell type checkers that data supports read()
        video_id = studio.upload_video(data)
        print(f'Successfully uploaded! videoId: {video_id}')

    # upload file with tqdm progress bar and using custom fields
    with open(file, 'rb') as stream, tqdm(total=getsize(file), unit_scale=True) as pbar:
        data = CallbackIOWrapper(pbar.update, stream)
        data = cast(SupportsRead[bytes], data)  # optionally tell type checkers that data supports read()
        video_id = studio.upload_video(data, 'New title', 'New description\nAnd stuff!', Visibility.UNLISTED, draft=False)
        print(f'Successfully uploaded! videoId: {video_id}')

    # upload arbitrary data stream with tqdm progress bar
    random_data = 'aaaaaaaaaaa BBBBBBBBBBBBBBB ccccccccccccccc'
    with tqdm(random_data) as data:
        video_id = studio.upload_video(random_data)
        print(f'Successfully uploaded! videoId: {video_id}')
