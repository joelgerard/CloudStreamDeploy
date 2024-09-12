# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

from flask import Blueprint, render_template, request, jsonify

from streamer import controllers
from streamer.auth import auth
from enum import Enum
import json
import bcrypt
import sys
import subprocess
import socket
import os
import psutil
import threading

web = Blueprint("web", __name__)
logger = logging.getLogger(__name__)

tee_ffmpeg_proc = None
twitch_ffmpeg_proc = None
nginx_proc = None

class Password(Enum):
    VALID=1
    INVALID=2
    OPEN=3

# @web.route('/', methods=['GET'])
# @auth.login_required
# def index():
#     logger.debug("index requested")
#     if request.method == "GET":
#         return render_template('index.html',something=controllers.something())

@web.route('/', methods=['GET'])
def index():
    return "OK"

@web.route('/', methods=['POST'])
def index_post():
    action = "";
    try:
        data = get_request_data()
        action = data["action"]
    except Exception as e:
        print(e,file=sys.stderr)
        return "1"
    
    if (action == "start"):
        return start()
    
    if (action == "set-password"):
        return set_password()
    
    if (action == "check"):
        return check();

    return "OK"

@web.route('/cpu', methods=['GET'])
def cpu():
    cpu_util = get_cpu_utilization()
    gpu_util = get_gpu_utilization()

    s = "CPU: "  + str(cpu_util) + "</br>"
    if (gpu_util):
        s = s+ "GPU: "  + str(gpu_util) + "</br>"
    return s,200

def get_cpu_utilization():
  """
  Returns a list of CPU utilization percentages for each core.
  """

  cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
  return cpu_percent

def get_gpu_utilization():
  """
  Gets GPU utilization using nvidia-smi.

  Returns:
    A list of GPU utilization percentages.
  """

  try:
    output = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv'])
    lines = output.decode('utf-8').strip().split('\n')
    headers = lines[0].split(',')
    util_index = headers.index('utilization.gpu [%]')
    gpu_util = [int(line.split(',')[util_index]) for line in lines[1:]]
    return gpu_util
  except:
    return []

@web.route('/start', methods=['POST'])
def start():
    data = get_request_data()
    pass_status = check_password(data["cloudstream-streamkey"])
    if (pass_status == Password.INVALID):
        return "{'result':'unauthorized'}",401
    
    youtube_key = data["youtube-streamkey"]
    twitch_key = data["twitch-streamkey"]
    local_key = data["cloudstream-streamkey"]

    # Need to protect rtmp: https://patchwork.ffmpeg.org/project/ffmpeg/patch/20190925185708.70924-1-unique.will.martin@gmail.com/

    # start_nginx()
    
    # 
    # ffmpeg  -listen 1 -i rtmp://0.0.0.0:1936/live/mystream \
    # -map 0:v -map 0:a -c copy  -f flv "rtmp://a.rtmp.youtube.com/live2/<key>"  \
    # -map 0:v -map 0:a -c:v libx264 -vf scale=1920:1080 -b:v 6000k -c:a copy -f flv "rtmp://live.twitch.tv/app/<key>" \
    ffmpeg_path = "/usr/bin/ffmpeg"
    if (is_localhost()):
        ffmpeg_path = "/opt/homebrew/bin/ffmpeg"

    try:
      kill("ffmpeg")
    except:
      print("Couldn't kill ffmpeg")

    try:
      kill("ffmpeg_secure")
    except:
      print("Couldn't kill ffmpeg_secure")

    script_path = os.path.dirname(os.path.realpath(__file__))
    command = [script_path + "/../stream.sh",local_key,youtube_key,twitch_key]
    tee_command = subprocess.Popen(command)

    # why no worky?
    # start the twitch proc         
    # twitch_command = [ffmpeg_path,"-listen","1","-i","rtmp://0.0.0.0:1937/livestream","","-c:v","h264_nvenc","-g","120","-ar","44100","-b:v","6000k","-vf","scale=1920:1080","-c:a","copy","-f","flv","\"rtmp://live.twitch.tv/app/" + twitch_key + "\""]
    # twitch_ffmpeg_proc = subprocess.Popen(twitch_command)
    # print(" ".join(twitch_command))

    # # start the tee
    # tee_command = [ffmpeg_path,"-listen","1","-i","rtmp://0.0.0.0:1936","-f","flv","-c","copy","rtmp://127.0.0.1:1937","-f","flv","-c","copy","\"rtmp://a.rtmp.youtube.com/live2/"+youtube_key+"\""]
    # tee_ffmpeg_proc = subprocess.Popen(tee_command)
    # print(" ".join(tee_command))

    
    
    secureStr = "secure" if has_password() else "insecure"
    return "{\"result\":\"ok\",\"control-server-status\":\""+control_server_status_text()+"\",\"control-server-security\":\""+secureStr+"\"}", 200

def start_nginx():
    f = open("nginx.template", "r")
    conf = f.read()
    f.close()
    hostname = socket.gethostname()
    ip_address = "127.0.0.1"
    try:
        ip_address = socket.gethostbyname(hostname)
        headers = request.headers
        # log (f"All headers: {headers}")
        if (ip_address.startswith ("10.")):
            ip_address = get_client_ip(request)
    except:
        log("Couldn't get public IP")
    
    conf = conf.replace("$public_ip",ip_address)
    f = open("nginx.conf","w")
    f.write(conf)
    f.close()

    stop_nginx()

    nginx_path = "/usr/local/nginx/nginx"
    if (is_localhost()):
        nginx_path = "/opt/homebrew/bin/nginx"

    command = [nginx_path,"-c",os.getcwd()+ "/nginx.conf"]
    nginx_proc = subprocess.Popen(command)
    log(" ".join(command))
    out, err = nginx_proc.communicate()
    if out:
        log(out)
    if err:
        log(err)

def is_localhost():
    ip = get_client_ip(request)
    return (ip == "127.0.0.1")

def get_client_ip(req):
    x_forwarded_for = req.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = req.remote_addr
    return ip

def stop_nginx():
    kill("nginx")

def kill(proc_name):
    for proc in psutil.process_iter():
        if proc.name() == proc_name:
            try:
                proc.kill()
            except:
                print('Proc kill error', file=sys.stderr)

def control_server_status_text():
    return "running" if is_encoder_running() else "stopped"

def is_encoder_running():
    # is_running("nginx") and 
    return is_running("ffmpeg") and is_running("ffmpeg_secure")

def is_running(proc_name):
    for proc in psutil.process_iter():
        if proc.name() == proc_name:
            return True
    return False



# def monitor_process(process):
#     for line in iter(process.stdout.readline, b''):
#         #output_queue.put(line.decode('utf-8').rstrip())
#         log(line.decode('utf-8').rstrip())

@web.route('/set-password', methods=['POST'])
def set_password():
    
    data = get_request_data()
    pass_status = check_password(data["cloudstream-streamkey"])


    if (pass_status == Password.INVALID):
        return "{'result':'unauthorized'}",401

    f = open("data.txt", "w")
    hashed = hash_password(data["cloudstream-streamkey"])
    f.write(hashed)
    f.close()


    return "{'result':'ok'}", 200

@web.route('/check', methods=['POST'])
def check():
    # log("Check " + request.get_data().decode('utf-8'))
    data = get_request_data()
    pass_status = check_password(data["cloudstream-streamkey"])


    if (pass_status == Password.INVALID):
        return '{"result":"unauthorized","control-server-status":"unauthorized"}',401

    # log("Check result ok")
    # return '{"result":"ok"}', 200
    secureStr = "secure" if has_password() else "insecure"
    streaming_server_status = '"'+('running' if is_encoder_running() else 'stopped') + '"';
    json = '{"result":"ok","control-server-status":"running","control-server-security":"'+secureStr+'","streaming-server-status":'+streaming_server_status+'}'
    return json, 200

def get_request_data():
    data = request.get_data().decode('utf-8')
    vals = json.loads(data)
    return vals

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(password):
    if (not(has_password())):
        return Password.OPEN
    
    stored_hash = get_password()
    if (bcrypt.checkpw(password.encode(), stored_hash)):
        return Password.VALID
    else:
        log(f"Bad password.")
        return Password.INVALID
    
    
def get_password():
    try:
        f = open("data.txt", "r")
        t = f.read()
        f.close()
        return t
    except:
        return ""

def has_password():
    return get_password() != ""

# TODO: Replace with logger.
def log(text):
    return ""
    # f = open("log.txt", "a")
    # f.writelines([text+"\n"])
    # f.close()
