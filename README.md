# Youtube Studio

Unofficial YouTube Studio API. Set of features limited or not provided by official YouTube API!

The biggest difference between the two is that this one is synchronous. My reasoning is that it significantly reduces the complexity of both the code and the usage of the project. Also, using the library asynchronously would not benefit upload speed as the majority of users will be limited by their internet speed rather than a limit of the YouTube API, so uploading multiple videos at once would have little to no benefit.

> This is a fork of the original ytstudio project by yusufusta [here](https://github.com/yusufusta/ytstudio)!

## Installation

For now, you can install with PIP.

`pip install git+https://github.com/JamieBra/ytstudio`

## Features

- Fully typed!
- Names reflecting the official Youtube GUI in browser!
- [List Playlists/Videos](examples/list_items.py)
    - Automatic pagination.
    - Specify all or some number of the results.
    - Specify what attributes to retrieve.
- [Get Playlist(s)/Video(s)](examples/get_items.py) (playlists not implemented)
    - Get any number of specific results by ID.
    - Specify what attributes to retrieve.
- [Create Playlist](examples/create_playlist.py)
    - Specify title and privacy setting.
- [Create Video](examples/create_video.py) (**NOT LIMITED** - official API's videos.insert charges you 1600 quota units)
    - Ability to upload arbitrary data.
    - Ability to add custom fields to support changes in the API and more advanced options.
    - Specify default fields.
- [Delete Playlist/Video](examples/delete_item.py) (not implemented yet)
- [Edit Playlist](examples/edit_playlist.py) (not implemented yet)
- [Edit Video](examples/edit_video.py) (includes scheduling uploads)
    - Easy to use fields for every option that is editable in browser before pressing 'SHOW MORE'. This is mainly due to how many fields there are and the variations therein.
    - Ability to add custom fields to support changes in the API and more advanced options.

## Login

You need cookies for login. Use an cookie manager([EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?hl=tr)) for [needed cookies.](examples/login.json).

Also you need SESSION_TOKEN for (upload/edit/delete) video. [How to get Session Token?](https://github.com/adasq/youtube-studio#preparing-authentication)

Examples of how to create a Studio instance can be found [here](examples/create_studio.py).

## TO-DO

- [ ] Better documentation
- [ ] Finish examples
- [ ] Tests
- [ ] Create PIP package
- [ ] Find session token automatically from cookies / add OAuth flow
- [ ] Implement missing functions
- [ ] Implement for listing functions:
    - [ ] Better method for specifying masks?
    - [ ] Listing order
- [ ] Implement for Studio.edit_video():
    - [ ] Set as Premiere
    - [ ] Better method for specifying extra fields?
    - [ ] Subtitles?
    - [ ] End Screens?
    - [ ] Cards?