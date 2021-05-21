# wofljefox
This is the source code for using a Telegram bot with a thermal printer

### Required packages:
- python-telegram-bot
- escpos
- tinydb
- datetime
- Pillow
- emoji
- ujson
- pytz
- random
- os
- requests


## Features

- Prints text, images, stickers, and images disguised as documents
- Extracts URLs from text, and prints them as QR codes
- Prints images in portrait layout, unless they'd be super long, then it just prints them landscape
- Print license support, including grant/revoke rights for owner

## To Do

- Audio to waveform visualisation