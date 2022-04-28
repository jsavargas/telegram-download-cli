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

__version__ = "VERSION 0.0.30"


BOT_NAME = os.environ['BOT_NAME']

API_HASH = os.environ['API_HASH']
APP_ID = int(os.environ['APP_ID'])
CHANNELS = os.environ['CHANNELS']
STRING_SESSION = os.environ['STRING_SESSION']
PUID = os.environ['PUID'] if 'PUID' in os.environ else 0
PGID = os.environ['PGID'] if 'PGID' in os.environ else 0

CHANNELS = [i for i in CHANNELS.split(',')]


DOWNLOAD_TEMP_PATH = "/download"
DOWNLOAD_PATH = "/download"
PATH_CONFIG = '/config/config.ini'
JSON_FILENAME = '/config/downloads.json'

# Running bot
xbot = Client(api_id=APP_ID, api_hash=API_HASH, session_name=STRING_SESSION)

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

    parser.add_argument('--channel', type=int, help='set channel for download')
    parser.add_argument('--list', action='store_true', default=False, help='list channels in compose')
    parser.add_argument('--caption', action='store_true', default=False, help='use caption in name')
    parser.add_argument('--simple', action='store_true', default=False, help='show less details')
    parser.add_argument('-f','--force', action='store_true', default=False, help='show less details')

    parser.add_argument('-b', '--begin-id-message', type=int, help='the begin id message')
    parser.add_argument('-e', '--end-id-message', type=int, help='the end id of sa for destination')

    args = parser.parse_args()
    return args



# Main script
async def runbot(args,_chat_id, _channel_count=1):
    async with xbot:

        if "-" in str(_chat_id):
            if not "-100" in str(_chat_id):
                _chat_id = int(str(_chat_id).replace("-", "-100"))

        chat_id = int(_chat_id)
        DOWNLOAD_PATH = getDownloadPath(chat_id)
        f = await xbot.get_history(chat_id)
        chat = await xbot.get_chat(chat_id)
        print(f"\n\n>>>>>>>>> [{_channel_count}][{chat_id}][{chat.title}][{DOWNLOAD_PATH}]")

        if args.list:
            return

        if args.begin_id_message:
            foo = []
            if not args.end_id_message:
                for i in range(args.begin_id_message,args.begin_id_message+20):
                    foo.append(i)
            elif args.end_id_message:
                for i in range(args.begin_id_message,args.end_id_message):
                    foo.append(i)
            print(f"Begind and End [{_channel_count}][{chat_id}][{chat.title}][{DOWNLOAD_PATH}]")
            f = await xbot.get_messages(chat_id,foo)

        elif args.message_id:
            f = await xbot.get_messages(chat_id,[args.message_id])
            #print(f"\n\n\n >>>>>>>>> message_id [{f}][{args.message_id}]")
        else:
            f = await xbot.get_history(chat_id, limit=args.limit)

        #print(f"ME [{f}]")
        print(f"DOWNLOAD_PATH >>>> [{DOWNLOAD_PATH}]\n")
        for message in f:
            if message.media == "video":
                #print(f"\n\n\n >>>>>>>>> [{ message }]")
                file_name = ""
                file_rename = ""
                if  message.video.file_name:
                    file_name = message.video.file_name
                    file_rename = message.video.file_name
                    filename, file_extension = os.path.splitext(file_name)

                    if args.caption: file_rename = f"{message.caption}{file_extension}"
                else:
                    file_rename = message.caption
                
                file_rename = file_rename.replace("/","-")
                temp_file_path = os.path.join(DOWNLOAD_TEMP_PATH,file_rename)
                file_path = os.path.join(DOWNLOAD_PATH,file_rename)

                
                if not args.simple:
                    _details = f"""
    chat title: {message.chat.title}
    message_id: {message.message_id}
    media type: {message.media}
    file_name: {file_name}
    file rename: {file_rename}
    resolution: {message.video.width}x{message.video.height}
    caption: {message.caption}
    file_size: {sizeof_fmt(message.video.file_size)}
    download path: {DOWNLOAD_PATH}
    downloaded: {readjson(chat_id, message.message_id)}
    is downloaded: {isDownloaded(chat_id, file_rename)}
"""
                else:
                    _details = f"[{readjson(chat_id, message.message_id)}][{isDownloaded(chat_id, file_rename)}][{message.message_id}][{sizeof_fmt(message.video.file_size)}][{file_rename}]"

                print(_details)

                if readjson(chat_id, message.message_id) and not args.force: 
                    continue

                #print(f"VIDEO >> [{message.message_id}][{message.media}][{file_name}][{message.video.width}x{message.video.height}][{sizeof_fmt(message.video.file_size)}]")
                    
                if args.download and isDownloaded(chat_id, file_rename) and not os.path.exists(file_path) or args.force :
                    try:
                        #await xbot.download_media(message.video.file_id,file_name="/download/", progress=progress)
                        print(f"\tdownload in: {temp_file_path}")
                        await xbot.download_media(message,file_name=temp_file_path, progress=progress)
                        print(f"\tmove to: {file_path}")
                        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
                        os.chown(temp_file_path, int(PUID), int(PGID))
                        shutil.move(temp_file_path, file_path)
                        os.chown(file_path, int(PUID), int(PGID))
                
                        if BOT_NAME: await xbot.send_message(BOT_NAME,f"download file: {file_rename}, {sizeof_fmt(message.video.file_size)}")

                        print(f"\tVIDEO FINISH >> [{file_path}]")
                        writejsondata(chat_id, message.message_id)
                    except Exception as e:
                        if BOT_NAME: await xbot.send_message(BOT_NAME,f"Exception: {_chat_id}, {message.message_id}")


                #exit()
      

def download_file(CHANNEL):
    print(CHANNEL)



def getDownloadPath(chat_id):
    config = read_config_file()
    folderFlag=False

    DEFAULT_PATH = config['DEFAULT_PATH']
    for ID in DEFAULT_PATH:
       
        if str(chat_id) == str(ID):
            _DOWNLOAD_PATH = DEFAULT_PATH[ID]
            folderFlag=True
            break
    
    if folderFlag: return _DOWNLOAD_PATH
    else: return DOWNLOAD_PATH

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.2f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

# Keep track of the progress while downloading
def progress(current, total):
    int_value = int(float("{:.2f}".format((current / total) * 100)) // 1)

    if ( (int_value) % 5 == 0): 
        print(f"download: {current * 100 / total:.1f}% ", sep='', end='\r', flush=True)


def config_file():
	config = configparser.ConfigParser()
	if not os.path.exists(PATH_CONFIG):
		print(f'CREATE DEFAULT CONFIG FILE : {PATH_CONFIG}')
	
		config.read(PATH_CONFIG)
			
		config['DEFAULT_PATH'] = {}
		config['DEFAULT_PATH']['pdf'] = '/download/pdf'

		with open(PATH_CONFIG, 'w') as configfile:    # save
			config.write(configfile)
		return config
	else:
		config.read(PATH_CONFIG)

		print(f'READ CONFIG FILE : {PATH_CONFIG}')

		return config

def read_config_file():
    config = configparser.ConfigParser()
    config.read(PATH_CONFIG)
    return config

def isDownloaded(chat_id: str, filename):
    config = read_config_file()
    folderFlag=False
    #print(f"isDownloaded >>>> [{chat_id}][{message_id}]")

    REGEX_DOWNLOAD = config['REGEX_DOWNLOAD']
    if str(chat_id) in REGEX_DOWNLOAD:
        m = re.search('/(.*)/(.*)', REGEX_DOWNLOAD[str(chat_id)])
        if m.group(2) == 'i':
            result = re.search(m.group(1), filename,re.I)
            return True if result else False
            print("result",result)
        else:
            result = re.search(m.group(1), filename)
            return True if result else False
            print("result",result)


        return True
    #print(f"isDownloaded >>>> [{REGEX_DOWNLOAD}]")
    else: return 'D'

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
    #print(f"||||| writejsondata \n\n\n")

    filename = JSON_FILENAME

    try:
        if os.path.exists(filename):
            f = open(filename)
            data = json.load(f)
            #print("writejsondata BBBBBBBBBBBBB", data)
        else:
            data = {}
    except Exception as e:
        print("writejsondata Exception")
        data = {}

    try:
        if not str(chat_id) in data:
            #print("writejsondata AAAAAAAAAAAAAAAA")
            data[str(chat_id)] = []
        data[str(chat_id)].append((message_id))

        json_object = json.dumps(data)
        #print("writejsondata",json_object)

        # Write the initial json object (list of dicts)
        with open(filename, "w") as outfile:
            outfile.write(json_object)
    except Exception as e:
        print("writejsondata Exception")



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




def process(args):
    if not args.chat_id:
        _channel_count=0
        for CHANNEL in CHANNELS:
            _channel_count += 1
            if (args.channel is not None):
                if (args.channel == _channel_count):
                    xbot.run(runbot(args,CHANNEL,_channel_count))
            else:
                xbot.run(runbot(args,CHANNEL,_channel_count))
            

        exit()

    else:
        xbot.run(runbot(args,args.chat_id))

if __name__ == '__main__':

    args = parse_args()

    if args.session:
        session()
        exit()
    print(args,"\n")
    config_file()

    process(args)
    #xbot.run(runbot(args))

