from __future__ import annotations

from base64 import b64encode
from datetime import datetime
from hashlib import sha1
from http.cookiejar import CookieJar
from operator import itemgetter
from os.path import getsize
from pprint import pprint
from time import time
from typing import TYPE_CHECKING, Any, Iterable, MutableMapping, cast
from urllib.parse import urljoin
from uuid import uuid4

from js2py import EvalJs  # type: ignore
from lxml.html import HtmlElement  # type: ignore
from pyquery import PyQuery  # type: ignore
from requests import Session
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from .templates import (CREATE_PLAYLIST, LIST_PLAYLISTS, LIST_VIDEOS,
                        METADATA_UPDATE, UPLOAD_VIDEO, generate)
from .typing import (ANY_TUPLE, JSON, MASK, AllowCommentsMode,
                     DefaultSortOrder, Privacy)

if TYPE_CHECKING:
    from _typeshed import (FileDescriptorOrPath, SupportsKeysAndGetItem,
                           SupportsRead)

ALL_TRUE = dict(all=True)
METADATA_SUCCESS = dict(resultCode='UPDATE_SUCCESS')
YT_STUDIO_URL = 'https://studio.youtube.com'


class Studio(Session):
    def __init__(
            self,
            cookies: CookieJar | Iterable[tuple[str, str]] | SupportsKeysAndGetItem[str, str],
            session_token: str
    ) -> None:
        super().__init__()
        self.cookies.update(  # type: ignore
            cookies
        )
        self.session_token = session_token

        sapisid = cast(str, self.cookies['SAPISID'])
        sapisid_hash = self.generate_sapisis_hash(sapisid)
        self.headers.update({
            'Authorization': f'SAPISIDHASH {sapisid_hash}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'X-Origin': YT_STUDIO_URL
        })

        self.js = EvalJs()
        self.js.execute(  # type: ignore
            'var window = {ytcfg: {}};'
        )

    def generate_sapisis_hash(self, sapisid: str) -> str:
        current_time = round(time())
        hash = f'{current_time} {sapisid} {YT_STUDIO_URL}'
        sifrelenmis = sha1(hash.encode()).hexdigest()
        return f'{current_time}_{sifrelenmis}'

    def get_main_page(self) -> str:
        page = self.get(YT_STUDIO_URL)
        return page.text

    def login(self) -> None:
        '''
        Login to your youtube account
        '''
        page = self.get_main_page()
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

    def check_response(self, name: Any, response: JSON, *check_present: str, **check_expected: Any) -> Any:
        try:
            if not (check_expected.items() <= response.items()):
                raise KeyError()
            if check_present:
                return itemgetter(*check_present)(response)
        except KeyError:
            pprint(response)
            raise Exception(f'Failed: {name}!')

    def post_endpoint(self, endpoint: str, json: JSON, *check_present: str, **check_expected: Any) -> Any:
        response = super().post(
            urljoin('https://studio.youtube.com/youtubei/v1/', endpoint),
            json=json
        ).json()
        return self.check_response(endpoint, response, *check_present, **check_expected)

    def list_endpoint(self, endpoint_type: str, template: MutableMapping[str, Any], page_size: int, **masks: MASK) -> ANY_TUPLE:
        template.update(
            mask=masks,
            pageSize=page_size
        )
        endpoint = f'creator/list_creator_{endpoint_type}'
        list = self.post_endpoint(endpoint, template, endpoint_type)
        return tuple(self.check_response(endpoint, element, *masks) for element in list)

    def list_playlists(self, page_size: int, **masks: MASK) -> ANY_TUPLE:
        '''
        Returns a list of playlists in your channel. Max page size is 500. Returns a tuple with items in the order specified by masks.
        '''
        return self.list_endpoint('playlists', LIST_PLAYLISTS, page_size, **masks)

    def list_videos(self, page_size: int, **masks: MASK) -> ANY_TUPLE:
        '''
        Returns a list of videos in your channel. Returns a tuple with items in the order specified by masks.
        '''
        return self.list_endpoint('videos', LIST_VIDEOS, page_size, **masks)

    def upload_file_to_youtube(self, url: bytes | str, file: FileDescriptorOrPath) -> None:
        with open(file, 'rb') as fp, tqdm(total=getsize(file), unit_scale=True) as pbar:
            data: SupportsRead[bytes] = CallbackIOWrapper(pbar.update, fp)  # type: ignore
            response = self.post(
                url,
                data,
                headers={
                    'x-goog-upload-command': 'upload, finalize',
                    'x-goog-upload-offset': '0'
                }
            ).json()
            self.check_response('initialize upload (step 2)', response, status='STATUS_SUCCESS')

    def upload_video(
        self,
        file: FileDescriptorOrPath,
        title: str | None = None,
        description: str | None = None,
        privacy: Privacy | None = None,
        draft: bool | None = None,
        **extra_fields: Any
    ) -> str:
        '''
        Uploads a video to youtube.
        '''
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

        self.upload_file_to_youtube(url, file)

        UPLOAD_VIDEO.update(
            frontendUploadId=frontend_upload_id,
            initialMetadata=dict(
                description=dict(newDescription=description),
                draftState=dict(isDraft=draft),
                title=dict(newTitle=title),
                privacy=dict(newPrivacy=privacy)
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

    def create_playlist(self, title: str, privacy: Privacy | None = None) -> str:
        '''
        Create a new playlist.
        '''
        CREATE_PLAYLIST.update(
            privacyStatus=privacy,
            title=title
        )
        playlist_id = self.post_endpoint('playlist/create', CREATE_PLAYLIST, 'playlistId')
        return playlist_id

    def edit_video(
            self,
            video_id: str,
            category_id: int | None = None,
            allow_comments: bool | None = None,
            allow_comments_mode: AllowCommentsMode | None = None,
            can_view_ratings: bool | None = None,
            default_sort_order: DefaultSortOrder | None = None,
            description: str | None = None,
            monetization: bool | None = None,
            privacy: str | None = None,
            tags: list[str] | None = None,
            title: str | None = None,
            videoStill: FileDescriptorOrPath | int | None = None,
            add_to_playlist_ids: list[str] | None = None,
            delete_from_playlist_ids: list[str] | None = None,
            scheduled_time: datetime | None = None,
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
            commentOptions=dict(
                newAllowComments=allow_comments,
                newAllowCommentsMode=allow_comments_mode,
                newCanViewRatings=can_view_ratings,
                newDefaultSortOrder=default_sort_order
            ),
            privacy=dict(newPrivacy=privacy),
            **METADATA_UPDATE,
            **extra_fields
        )

        if category_id:
            data.update(category=dict(newCategoryId=category_id))
        if description:
            data.update(description=dict(newDescription=description))
        if monetization:
            data.update(monetizationSettings=dict(newMonetization=monetization))
        if tags:
            data.update(tags=dict(newTags=tags))
        if title:
            data.update(title=dict(newTitle=title))
        if scheduled_time:
            data.update(scheduledPublishing=dict(set=dict(
                privacy=Privacy.PUBLIC,
                timeSec=int(scheduled_time.timestamp())
            )))
        if isinstance(videoStill, int):
            data.update(videoStill=dict(
                operation='SET_AUTOGEN_STILL',
                newStillId=videoStill
            ))
        elif videoStill:
            with open(videoStill, 'rb') as fp:
                image_64_encode = b64encode(fp.read()).decode()
            data.update(videoStill=dict(
                operation='UPLOAD_CUSTOM_THUMBNAIL',
                image=dict(dataUri=f'data:image/png;base64,{image_64_encode}')
            ))

        self.post_endpoint('video_manager/metadata_update', data, overallResult=METADATA_SUCCESS)
