# faxii
faxii is the nickname of a little thermal printer on my desk, and this repo has the source code for the Telegram bot that controls it.

[Current version: 1.0](/Releases/v1.0)

[Changelog](changelog.md)

### Required packages:
- python-telegram-bot
- escpos
- tinydb
- datetime
- Pillow
- time
- emoji
- ujson


## Features

- Prints text, images, stickers, and images disguised as documents
- Extracts URLs from text, and prints them as QR codes
- Prints images in portrait layout, unless they'd be super long, then it just prints them landscape
- Print license support, including grant/revoke rights for owner
- Is just generally pretty neat?


## To Do

- Image > ASCII art converter
- Haiku recognition
- Support for re-requesting a print license after it's been revoked
- More feedback for the user
- Logging
- Code comments

## More likely to be up-to-date To Do list
[Trello](https://trello.com/b/Baz3Zo1W/faxiibot)
