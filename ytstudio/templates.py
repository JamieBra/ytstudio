from typing import Any

ALL_TRUE = dict(all=True)

UPDATE_SUCCESS = dict(resultCode='UPDATE_SUCCESS')

EMPTY_DICT = {}
CONTEXT: dict[str, Any] = dict(
    context=dict(
        request=dict(sessionInfo=EMPTY_DICT),
        user=EMPTY_DICT,
        client=dict(
            clientName=62,
            clientVersion='1.20230621.01.01'
        )
    )
)

CREATE_PLAYLIST = CONTEXT.copy()
LIST_ITEMS = CONTEXT.copy()
METADATA_UPDATE = CONTEXT.copy()
UPLOAD_VIDEO = CONTEXT.copy()


def generate(token: Any, channel_id: Any, on_behalf_of_user: Any) -> None:
    CONTEXT['context']['request']['sessionInfo']['token'] = token
    CONTEXT['context']['user']['onBehalfOfUser'] = on_behalf_of_user
    LIST_ITEMS['channelId'] = UPLOAD_VIDEO['channelId'] = channel_id
