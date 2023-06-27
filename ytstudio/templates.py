from typing import Any

EMPTY_DICT = {}
EMPTY_LIST = []
CONTEXT: dict[str, Any] = dict(
    context=dict(
        clientScreenNonce='',
        user=EMPTY_DICT,
        client=dict(
            clientName=62,
            clientVersion='1.20230621.01.01',
            experimentsToken='',
            gl='US',
            hl='en',
            utcOffsetMinutes=-240
        ),
        request=dict(
            internalExperimentFlags=EMPTY_LIST,
            returnLogEntry=True,
            sessionInfo=EMPTY_DICT
        )
    )
)

CREATE_PLAYLIST: dict[str, Any] = dict(**CONTEXT)
LIST_PLAYLISTS: dict[str, Any] = dict(**CONTEXT)
LIST_VIDEOS: dict[str, Any] = {
    'filter': {
        'and': {
            'operands': [{
                'channelIdIs': {
                    'value': 'UC0gW_FQm0Fn8SfYRPrRFnHw'
                }
            },
                {
                'videoOriginIs': {
                    'value': 'VIDEO_ORIGIN_UPLOAD'
                }
            }]
        }
    },
    'order': 'VIDEO_ORDER_DISPLAY_TIME_DESC',
    **CONTEXT
}
METADATA_UPDATE: dict[str, Any] = dict(**CONTEXT)
UPLOAD_VIDEO: dict[str, Any] = dict(**CONTEXT)


def generate(token: Any, channel_id: Any, on_behalf_of_user: Any) -> None:
    CONTEXT['context']['request']['sessionInfo']['token'] = token
    CONTEXT['context']['user']['onBehalfOfUser'] = on_behalf_of_user
    LIST_PLAYLISTS['channelId'] = UPLOAD_VIDEO['channelId'] = channel_id
