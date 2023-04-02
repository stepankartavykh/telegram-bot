# Telegram bot for browsing hotels.

Telegram bot to find hotels in different countries. Bot allows to get list of hotels, that meet certain criteria.

## Description
Bot utilizes RapidAPI, specifically https://rapidapi.com/apidojo/api/hotels4/<br />
Bot consists of six commands.<br />
/start - command to start a bot.<br />
/help - get list of commands and description.<br />
/low - search hotels by certain parameters with possible lowest prices.<br />
/high - search hotels by certain parameters with possible highest prices.<br />
/custom - hotels with some added agruments (in this command distance and price limits were used)<br />
/history - user gets last requests, in this case commands that were requested by user earlier.<br />

## Dependencies

All neccessary libraries listed in requirements.txt file.

## Installing
Execute next commands in the terminal(Linux) or CMD(Windows).
1) Clone this repository in some directory on your computer.
```
git clone https://github.com/sktvpx/telegram-bot.git
```
2) Create virtual environment and activate.<br />
python == python3 (alias added)
```
python -m venv your_venv_name
source your_venv_name/bin/activate
```
3) Install required libraries.
```
pip install -r requirements.txt
```
## Executing program
Run next command in terminal.
```
python main.py
```

## Authors
Kartavyh Stepan<br />
Telegram: @stepankartavyh
