# telegram downloader cli
**telegram downloader cli is a program to download files from channels that prevent the forwarding of messages to a bot, allowing the download of files using the personal account via the command line**




## Use


### Configs (Envs)
- `BOT_TOKEN` - Get it by contacting to [BotFather](https://t.me/botfather)
- `APP_ID` - Get it by creating app on [my.telegram.org](https://my.telegram.org/apps)
- `API_HASH` - Get it by creating app on [my.telegram.org](https://my.telegram.org/apps)
- `CHANNELS` - List of channel/group usernames, seperated by space.
- `STRING_SESSION` - Pyrogram string session. run docker-compose run --rm telegram-download-cli --session
- `MSG_ID` - Message ID of COUNTS_EDIT_CHANNEL.
- `CHANNELS` - ID of CHANNELS. Example "CHANNELS=-10014417,-10014418,-10014419".

### Use 
```sh 
docker-compose run --rm telegram-download-cli -h
docker-compose run --rm telegram-download-cli --list
docker-compose run --rm telegram-download -l 10 --chat-id -1001578311130 -d
docker-compose run --rm telegram-download-cli --channel 2 -d

```

