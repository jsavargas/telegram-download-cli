import asyncio
import os
import requests
import json
import time
import argparse
import configparser
import shutil
import re


from pyrogram import Client
from pyrogram.errors import FloodWait
from tabulate import tabulate

__version__ = "VERSION 1.0.1"


BOT_NAME = os.environ['BOT_NAME']

API_HASH = os.environ['API_HASH']
APP_ID = int(os.environ['APP_ID'])
CHANNELS = os.environ['CHANNELS']
STRING_SESSION = os.environ['STRING_SESSION']
PUID = os.environ['PUID'] if 'PUID' in os.environ else 0
PGID = os.environ['PGID'] if 'PGID' in os.environ else 0

_CHANNELS = [i for i in CHANNELS.split(',')]


DOWNLOAD_TEMP_PATH = "/download/temp"
DOWNLOAD_PATH = "/download"
PATH_CONFIG = '/config/config.ini'
JSON_FILENAME = '/config/downloads.json'

# Running bot
app = Client(api_id=APP_ID, api_hash=API_HASH, session_name=STRING_SESSION)

print("")

def parse_args():
    parser = argparse.ArgumentParser(description="Telegram Download ")
    parser.add_argument('-v','--version', action='version', version="%(prog)s " + __version__)

    parser.add_argument('-s','--session', action='store_true', default=False, help='get session variable')
                    
    parser.add_argument('-d','--download', action='store_true', default=False, help='enable file download')
    parser.add_argument('-l', '--limit', type=int, default=10, help='return message limit, default=10 ')
    parser.add_argument('-c', '--chat-id', type=int, help='group where you will search for messages')
    parser.add_argument('-m','--message-id', type=int, help='unique id of the message. To download a specific message (video). Requires --chat-id')
    parser.add_argument('--file-type', type=str, help='type of messages to download (disabled)')

    parser.add_argument('--channel', type=str, help='set channel for download')
    parser.add_argument('--list', action='store_true', default=False, help='list channels in compose')
    parser.add_argument('--caption', action='store_true', default=False, help='use caption in name')
    parser.add_argument('--simple', action='store_true', default=False, help='show less details')
    parser.add_argument('-f','--force', action='store_true', default=False, help='show less details')

    parser.add_argument('-b', '--begin-id-message', type=int, help='the begin id message')
    parser.add_argument('-e', '--end-id-message', type=int, help='the end id of sa for destination')

    args = parser.parse_args()
    return args

    
async def main():
    async with app:
        chat_id = 'verdadesocultascap'
        chat_id = -1001548273473

        channels = getCHANNELS()
                
        joined_channels = normalizedChannels([*channels, *_CHANNELS])

        if args.channel:
            DOWNLOAD_PATH = getDownloadPath(args.channel)
            try:

                chat = await app.get_chat(ifDIgit(args.channel))

                print(f"[*] >>>>>>>>> [{chat.id}][{args.channel}][{chat.title}][{DOWNLOAD_PATH}]")

                f = await app.get_history(ifDIgit(args.channel),limit=args.limit)

                await getMedia(args.channel,f)

            except Exception as e:
                print(f'except main {e}')

        else:
            for channel in joined_channels:
                print("\n",'[*]'*20)
                try:

                    #continue
                    DOWNLOAD_PATH = getDownloadPath(channel)

                    chat = await app.get_chat(ifDIgit(channel))

                    print(f"[*] >>>>>>>>> [{chat.id}][{channel}][{chat.title}][{DOWNLOAD_PATH}]")

                    if args.list:
                        return

                    f = await app.get_history(ifDIgit(channel),limit=args.limit)

                    await getMedia(channel,f)

                except Exception as e:
                    print(f'except {e}')
                    break

async def getMedia(channel,f):
    try:
        DOWNLOAD_PATH = getDownloadPath(channel)

        for message in f:
            if message.media == "video":

                if not message.video.file_name or args.caption:

                    file_rename = f"{message.caption}.{(message.video.mime_type).split('/')[1]}"

                else:
                    
                    file_rename = message.video.file_name


                if args.simple: print(f"was downloaded:[{readjson(message.chat.id, message.message_id)}]\tdownloadable:[{isDownloadable(channel, message)[1]}]\t[{message.message_id}]\t[{sizeof_fmt(message.video.file_size)}]\t[{file_rename}]")
                else: printDetailsMessage(channel,message,DOWNLOAD_PATH)

                filename, bool_getMedia = isDownloadable(channel, message)


                if args.download and bool_getMedia and not readjson(message.chat.id, message.message_id) and not os.path.exists(filename) or args.force :
                #if args.download and bool_getMedia and not os.path.exists(filename) or args.force :
                    await downloadMedia(channel, filename, message)
    except Exception as e:
        print(f'Exception getMedia :: {e}')
        
def printDetailsMessage(channel,message,DOWNLOAD_PATH):
    print(
f''' 
-------------------------------------------------
+   channel: {channel}
+   chat id: {message.chat.id}
+   chat username: {message.chat.username}
+   chat title: {message.chat.title}
+   message_id: {message.message_id}
+   media type: {message.media}
+   resolution: {message.video.width}x{message.video.height}
+   mime_type: {(message.video.mime_type).split('/')[1]}
+   file_name: {message.video.file_name}
+   caption: {message.caption}
+   file_size: {sizeof_fmt(message.video.file_size)}
+   download path: {DOWNLOAD_PATH}
+   was downloaded: {readjson(message.chat.id, message.message_id)}
+   it is downloadable: {isDownloadable(channel, message)[1]}
+   fileOutput: {isDownloadable(channel, message)[0]}
-------------------------------------------------
''')

def ifDIgit(channel):
    #if any(map(str.isdigit,channel)):
    #    return int(channel)
    #else: return channel

    return int(channel) if any(map(str.isdigit,channel)) else channel


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.2f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

# add -100 in channel id
def normalizedChannels(channels):
    for channel in channels:
        try:
            if any(map(str.isdigit,channel)):
                if not '-100' in channel:
                    #print(f'{channel} IS {any(map(str.isdigit,channel))}')
                    channels[channels.index(channel)] = '-100' + str(channel).replace('-','')
        except Exception as e:
            print(f'Exception :: {e}')
            
    #print(f'return normalizedChannels:{list(set(channels))}')
    return list(set(channels))


def getDownloadPath(channel):
    config = read_config_file()
    folderFlag=False

    DEFAULT_PATH = config['DEFAULT_PATH']
    for ID in DEFAULT_PATH:
        if str(ID).lower() == str(channel).lower():
            _DOWNLOAD_PATH = DEFAULT_PATH[ID]
            folderFlag=True
            break
    
    if folderFlag: return _DOWNLOAD_PATH
    else: return DOWNLOAD_PATH


def readjson(chat_id: str, message_id:int):
    #print(f"||||| readjson \n\n\n")

    filename = JSON_FILENAME

    try:
        if os.path.exists(filename):
            f = open(filename)
            data = json.load(f)
            if str(chat_id) in data :
                #print("BBBBBBBBBBBBB", data[str(chat_id)])
                if int(message_id) in data[str(chat_id)]:
                    return True
                else:
                    return False
            else: 
                return False
        else:
            return False
    except Exception as e:
        return False


def writejsondata(chat_id: str, message_id:int):
    filename = JSON_FILENAME
    try:
        if os.path.exists(filename):
            f = open(filename)
            data = json.load(f)
        else:
            data = {}
    except Exception as e:
        print("writejsondata Exception")
        data = {}

    try:
        if not str(chat_id) in data:
            data[str(chat_id)] = []
        data[str(chat_id)].append((message_id))

        json_object = json.dumps(data)
        with open(filename, "w") as outfile:
            outfile.write(json_object)
    except Exception as e:
        print("writejsondata Exception")


def isDownloadable(chat_id: str, message ):
    try:
        config = read_config_file()
        isDownloadable=False

        REGEX_DOWNLOAD = config['REGEX_DOWNLOAD']
        REGEX_CAPTION = config['REGEX_CAPTION']

        ext = f".{(message.video.mime_type).split('/')[1]}"

        if str(chat_id) in REGEX_DOWNLOAD:
            m = re.search('/(.*)/(.*)', REGEX_DOWNLOAD[str(chat_id)])
            if m.group(2) == 'i':
                if re.search(m.group(1), message.video.file_name,re.I): return message.video.file_name,True
            else:
                if re.search(m.group(1), message.video.file_name): return message.video.file_name,True
            
        if not isDownloadable and str(chat_id) in REGEX_CAPTION:
            m = re.search('/(.*)/(.*)', REGEX_CAPTION[str(chat_id)])
            if m.group(2) == 'i':
                result = re.match(m.group(1), message.caption,re.I)
                if result: return f"{(message.video.file_name).replace(ext,'')}_{result.group(1)}{ext}" ,True
                if re.search(m.group(1), message.caption,re.I): return message.caption, True
            else:
                if re.search(m.group(1), message.caption): return True

        if not str(chat_id) in REGEX_DOWNLOAD and not str(chat_id) in REGEX_CAPTION: 
            return message.video.file_name, True
        else: return message.video.file_name, False

    except Exception as e:
        print(f'Exception isDownloadable :: {e}')

async def downloadMedia(channel: str, filename: str, message ):
    try:
        
        DOWNLOAD_PATH = getDownloadPath(channel)

        temp_file_path = os.path.join(DOWNLOAD_TEMP_PATH,filename)
        final_file_path = os.path.join(DOWNLOAD_PATH,filename)

        print(f" ---->\tdownload in: {temp_file_path}")

        await app.download_media(message, file_name=temp_file_path, progress=progress)

        print(f"\n ---->\tmove to: {final_file_path}")
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
        shutil.move(temp_file_path, final_file_path)
        os.chown(final_file_path, int(PUID), int(PGID))

        if BOT_NAME: await app.send_message(BOT_NAME,f"download file: {final_file_path}, {sizeof_fmt(message.video.file_size)}")

        print(f"[+]\tVIDEO FINISH >> [{final_file_path}]")
        writejsondata(message.chat.id, message.message_id)

        return True

    except Exception as e:
        print(f'Exception downloadMedia :: {e}')
        return False


# Keep track of the progress while downloading
def progress(current, total):
    int_value = int(float("{:.2f}".format((current / total) * 100)) // 1)

    if ( (int_value) % 5 == 0): 
        print(f"download: {current * 100 / total:.1f}% ", sep='', end='\r', flush=True)




#with xbot:
#    f = xbot.get_history('AnimesLatinos')
#
#
#
#    common = await xbot.get_common_chats('me')
#    print(common)
#
#    #for message in f:
#    #    print(f"\n\n\n >>>>>>>>> [{ message }]")




def session():
    if not APP_ID: input("Enter Your APP ID: ")
    if not API_HASH: input("Enter Your API HASH: ")

    #api_id = input("Enter Your APP ID: ")
    #api_hash = input("Enter Your API HASH: ")

    with Client("IDN-Coder-X", api_id=int(APP_ID), api_hash=API_HASH) as xbot:
        ssession = f'**String Session**:\n - STRING_SESSION={xbot.export_session_string()}'
        print(f'Your string session has been stored to your saved message => {ssession}')
        xbot.send_message('me', ssession)
        print('Your string session has been stored to your saved message')


def read_config_file():
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(PATH_CONFIG)
    return config


def getCHANNELS():
    config = read_config_file()

    CHANNELS = list(config['CHANNELS'].keys())

    return CHANNELS

if __name__ == '__main__':

    args = parse_args()
    
    if args.session:
        session()
        exit()
    
    app.run(main())
