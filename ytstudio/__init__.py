from __future__ import annotations

from base64 import b64encode
from datetime import datetime
from hashlib import sha1
from operator import itemgetter
from os.path import getsize
from sys import maxsize
from time import time
from typing import TYPE_CHECKING, Any, Mapping, MutableMapping, Self, cast
from uuid import uuid4

from httpx import Client
from httpx._types import CookieTypes, RequestContent
from js2py import EvalJs  # type: ignore
from lxml.html import HtmlElement  # type: ignore
from pyquery import PyQuery  # type: ignore

from .templates import (CREATE_PLAYLIST, LIST_PLAYLISTS, LIST_VIDEOS,
                        METADATA_UPDATE, UPLOAD_VIDEO, generate)
from .typing import (ANY_TUPLE, MASK, OPT_BOOL, OPT_STR_ITER, OPT_VISIBILITY,
                     Visibility)

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 5000
MAX_PLAYLIST_TITLE_LENGTH = 150
METADATA_SUCCESS = dict(resultCode='UPDATE_SUCCESS')
YT_STUDIO_URL = 'https://studio.youtube.com'


class Studio(Client):
    @staticmethod
    def validate_string(string: str, max_length: int) -> str:
        if len(string) > max_length:
            print(f'{string} is greater than {max_length} characters. This will likely fail!')
        if '<' in string or '>' in string:
            print(f'{string} contains "<" or ">". This will likely fail!')
        return string

    def __init__(
            self,
            cookies: CookieTypes,
            session_token: str = '',
            login: bool = True
    ) -> None:
        super().__init__(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                'X-Origin': YT_STUDIO_URL
            },
            cookies=cookies,
            http2=True,
            base_url='https://studio.youtube.com/youtubei/v1/'
        )

        sapisid_hash = self.generate_sapisid_hash()

        self.auto_login = login
        self.headers.update(dict(Authorization=f'SAPISIDHASH {sapisid_hash}'))
        self.session_token = session_token or self.cookies['SESSION_TOKEN']

        self.js = EvalJs()
        self.js.execute(  # type: ignore
            'var window = {ytcfg: {}};'
        )

    def __enter__(self) -> Self:
        self = super().__enter__()
        if self.auto_login:
            self.login()
        return self

    def generate_sapisid_hash(self) -> str:
        sapisid = self.cookies['SAPISID']
        current_time = round(time())
        hash = f'{current_time} {sapisid} {YT_STUDIO_URL}'
        sifrelenmis = sha1(hash.encode()).hexdigest()
        return f'{current_time}_{sifrelenmis}'

    def login(self) -> None:
        '''
        Login to your youtube account
        '''
        page = self.get(YT_STUDIO_URL).text
        query = PyQuery(page)
        script = query('script')
        if len(script) < 1:
            raise Exception('Failed to find script. Can you check your cookies?')
        script = cast(HtmlElement, script[0])
        self.js.execute(  # type: ignore
            f'{script.text} window.ytcfg = ytcfg;'
        )

        channel_id = self.js.window.ytcfg.data_.CHANNEL_ID
        on_behalf_of_user = self.js.window.ytcfg.data_.DELEGATED_SESSION_ID
        if channel_id is None or on_behalf_of_user is None:
            raise Exception('Unable to find CHANNEL_ID or DELEGATED_SESSION_ID. Can you check your cookies?')
        generate(self.session_token, channel_id, on_behalf_of_user)

    def check_response(self, name: Any, response: Mapping[Any, Any], *check_present: Any, **check_expected: Any) -> Any:
        try:
            if not (check_expected.items() <= response.items()):
                raise KeyError()
            if check_present:
                return itemgetter(*check_present)(response)
            return response
        except KeyError:
            raise KeyError(f'Failed: {name}!', response)

    def post_endpoint(self, endpoint: str, json: Any, *check_present: str, **check_expected: Any) -> Any:
        response = super().post(endpoint, json=json).json()
        return self.check_response(endpoint, response, *check_present, **check_expected)

    def list_endpoint(self, endpoint_type: str, template: MutableMapping[str, Any], max_items: int = maxsize, **masks: MASK) -> ANY_TUPLE:
        template.update(
            mask=masks,
            pageSize=min(500, max_items),
            pageToken=''
        )
        endpoint = f'creator/list_creator_{endpoint_type}'

        items: list[Any] = []
        while len(items) < max_items and template['pageToken'] is not None:
            response = self.post_endpoint(endpoint, template)
            items += response[endpoint_type]
            template['pageToken'] = response.get('nextPageToken', None)

        return tuple(self.check_response(endpoint, item, *masks) for item in items)

    def list_playlists(self, max_playlists: int = maxsize, **masks: MASK) -> ANY_TUPLE:
        '''
        Returns a list of playlists in your channel. If max_playlists is not specified, all playlists are returned. Returns a tuple with items in the order specified by masks.
        '''
        return self.list_endpoint('playlists', LIST_PLAYLISTS, max_playlists, **masks)

    def list_videos(self, max_videos: int = maxsize, **masks: MASK) -> ANY_TUPLE:
        '''
        Returns a list of videos in your channel. If max_videos is not specified, all videos are returned. Returns a tuple with items in the order specified by masks.
        '''
        return self.list_endpoint('videos', LIST_VIDEOS, max_videos, **masks)

    def upload_video(
        self,
        content: RequestContent,
        title: str = '',
        description: str = '',
        visibility: OPT_VISIBILITY = None,
        draft: OPT_BOOL = None,
        **extra_fields: Any
    ) -> str:
        '''
        Uploads a video to youtube.
        '''
        Studio.validate_string(title, MAX_TITLE_LENGTH)
        Studio.validate_string(description, MAX_DESCRIPTION_LENGTH)

        frontend_upload_id = f'innertube_studio:{uuid4()}:0'

        upload_request = self.post(
            'https://upload.youtube.com/upload/studio',
            headers={
                'x-goog-upload-command': 'start',
                'x-goog-upload-protocol': 'resumable'
            },
            json=dict(frontendUploadId=frontend_upload_id)
        )
        scotty_resource_id, url = self.check_response('initialize upload (step 1)', upload_request.headers, 'X-Goog-Upload-Header-Scotty-Resource-Id', 'x-goog-upload-url')

        response = self.post(
            url,
            content=content,
            headers={
                'x-goog-upload-command': 'upload, finalize',
                'x-goog-upload-offset': '0'
            }
        ).json()
        self.check_response('initialize upload (step 2)', response, status='STATUS_SUCCESS')

        UPLOAD_VIDEO.update(
            frontendUploadId=frontend_upload_id,
            initialMetadata=dict(
                description=dict(newDescription=description),
                draftState=dict(isDraft=draft),
                title=dict(newTitle=title),
                privacy=dict(newPrivacy=visibility)
            ),
            resourceId=dict(scottyResourceId=dict(id=scotty_resource_id)),
            **extra_fields
        )
        videoId = self.post_endpoint('upload/createvideo', UPLOAD_VIDEO, 'videoId')

        return videoId

    def delete_video(self, video_id: str) -> NotImplementedError:
        '''
        Delete video from your channel.
        '''
        return NotImplementedError()  # TODO

    def get_video(self, video_id: str) -> NotImplementedError:
        '''
        Get video data.
        '''
        return NotImplementedError()  # TODO

    def create_playlist(self, title: str, visibility: OPT_VISIBILITY = None) -> str:
        '''
        Create a new playlist.
        '''
        CREATE_PLAYLIST.update(
            privacyStatus=visibility,
            title=Studio.validate_string(title, MAX_PLAYLIST_TITLE_LENGTH)
        )
        return self.post_endpoint('playlist/create', CREATE_PLAYLIST, 'playlistId')

    def edit_video(
            self,
            video_id: str,
            title: str = '',
            description: str = '',
            thumbnail: FileDescriptorOrPath | int | None = None,
            add_to_playlist_ids: OPT_STR_ITER = None,
            delete_from_playlist_ids: OPT_STR_ITER = None,
            visibility: datetime | int | OPT_VISIBILITY = None,
            made_for_kids: OPT_BOOL = None,
            restrict_video: OPT_BOOL = None,
            **extra_fields: Any
    ) -> None:
        '''
        Edit video metadata.
        '''

        data: dict[str, Any] = dict(
            encryptedVideoId=video_id,
            addToPlaylist=dict(
                addToPlaylistIds=add_to_playlist_ids,
                deleteFromPlaylistIds=delete_from_playlist_ids
            ),
            **METADATA_UPDATE,
            **extra_fields
        )

        if Studio.validate_string(title, MAX_TITLE_LENGTH):
            data.update(title=dict(newTitle=title))
        if Studio.validate_string(description, MAX_DESCRIPTION_LENGTH):
            data.update(description=dict(newDescription=description))

        if isinstance(thumbnail, int):
            data.update(videoStill=dict(
                operation='SET_AUTOGEN_STILL',
                newStillId=thumbnail
            ))
        elif thumbnail:
            if getsize(thumbnail) > 2097152:
                print(f'{thumbnail} is greater than 2 MB. This will likely fail!')
            with open(thumbnail, 'rb') as fp:
                image_64_encode = b64encode(fp.read()).decode()
            data.update(videoStill=dict(
                operation='UPLOAD_CUSTOM_THUMBNAIL',
                image=dict(dataUri=f'data:image/png;base64,{image_64_encode}')
            ))

        if isinstance(visibility, datetime):
            visibility = int(visibility.timestamp())
        if isinstance(visibility, int):
            data.update(scheduledPublishing=dict(set=dict(
                privacy=Visibility.PUBLIC,
                timeSec=visibility
            )))
            visibility = Visibility.PRIVATE
        if visibility:
            data.update(privacy=dict(newPrivacy=visibility))

        if made_for_kids is not None:
            data.update(madeForKids=dict(
                operation='MDE_MADE_FOR_KIDS_UPDATE_OPERATION_SET',
                newMfk=f'MDE_MADE_FOR_KIDS_TYPE_{"" if made_for_kids else "NOT_"}MFK'
            ))
        if restrict_video is not None:
            data.update(racy=dict(
                operation='MDE_RACY_UPDATE_OPERATION_SET',
                newRacy=f'MDE_RACY_TYPE_{"" if restrict_video else "NOT_"}RESTRICTED'
            ))

        self.post_endpoint('video_manager/metadata_update', data, overallResult=METADATA_SUCCESS)
