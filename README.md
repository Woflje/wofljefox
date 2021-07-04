# wofljefox
This is the source code for using a Telegram bot with a thermal printer

### Installation:
Install requirements from `requirements.txt`

Add a `config.json` next to `main.py` and include:
```
{ "token": "<telegram bot token>",
  "admin_id":  <telegram admin id>,
  "port": "/dev/ttyUSB0",
  "baud": 38400,
  "auto_cut": true,
  "max_width": 512,
  "timezone": "Europe/Amsterdam",
  "url_start_tags": ["https://", "http:/"],
  "url_end_tags": [" ", ". ", "\n", ", ", "https://", "http:/"],
  "trello_api_key": "<trello_api_key>",
  "trello_api_secret": "<trello_api_secret>",
  "trello_token": "<trello_token>"}
```

## Features

- Prints text, images, stickers, and images disguised as documents
- Extracts URLs from text, and prints them as QR codes
- Prints images in portrait layout, unless they'd be super long, then it just prints them landscape
- Print license support, including grant/revoke rights for owner
- Prints Trello lists and its cards and checklists

## To Do

- Audio to waveform visualisation
