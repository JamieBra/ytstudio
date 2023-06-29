# Youtube Studio

Unofficial YouTube Studio API. Set of features limited or not provided by official YouTube API!

> This is a fork of the original ytstudio project by yusufusta [here](https://github.com/yusufusta/ytstudio)!

## Installation

For now, you can install with PIP.

`pip install git+https://github.com/JamieBra/ytstudio`

## Features

- Fully typed!
- Names reflecting the official Youtube GUI in browser!
- [List Videos](examples/list_playlists.py)
    - Specify page size.
    - Specify what attributes to retrieve.
- [List Playlists](examples/list_videos.py)
    - Specify page size.
    - Specify what attributes to retrieve.
- [Uploading Video](examples/upload_video.py) (**NOT LIMITED** - official API's videos.insert charges you 1600 quota units)
    - Built-in progress bar.
    - Specify default fields.
    - Ability to add custom fields to support changes in the API and more advanced options.
- [Deleting Video](examples/delete_video.py) (not implemented yet)
- [Edit Video](examples/edit_video.py) (includes scheduling uploads)
    - Easy to use fields for every option that is editable in browser before pressing 'SHOW MORE'. This is mainly due to how many fields there are and the variations therein.
    - Ability to add custom fields to support changes in the API and more advanced options.
- [Get Video](examples/get_video.py) (not implemented yet)

## Login

You need cookies for login. Use an cookie manager([EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?hl=tr)) for needed cookies.

Also you need SESSION_TOKEN for (upload/edit/delete) video. [How to get Session Token?](https://github.com/adasq/youtube-studio#preparing-authentication)

## TO-DO

- [ ] Better documentation
- [ ] Better tests
- [ ] Update examples
- [ ] Create PIP package
- [ ] Allow session token to passed in with cookies
- [ ] Implement Studio.delete_video()
- [ ] Implement Studio.get_video()
- [ ] Implement for Studio.list_playlists() and Studio.list_videos():
    - [ ] Better method for specifying masks?
    - [ ] Paging support
    - [ ] Listing order
- [ ] Implement for Studio.upload_video():
    - [ ] Make progress monitoring the user's responsibility to reduce dependencies and increase flexibility of specifying upload data and the actual way progress is monitored
- [ ] Implement for Studio.edit_video():
    - [ ] Set as Premiere
    - [ ] Better method for specifying extra fields?
    - [ ] Subtitles?
    - [ ] End Screens?
    - [ ] Cards?