#!/bin/sh

# TODO: Remove logs

# hw encoder
nohup ffmpeg -listen 1 -i rtmp://0.0.0.0:1937/app  -c:v hevc_nvenc -g 120 -ar 44100 -b:v 6000k -vf scale=1920:1080 -c:a copy -f flv "rtmp://live.twitch.tv/app/$3" & # > ~/twitch.log & 

# sw encoder
# nohup ffmpeg -listen 1 -i rtmp://0.0.0.0:1937/livestream  -c:v libx264 -g 120 -ar 44100 -b:v 6000k -vf scale=1920:1080 -c:a copy -f flv "rtmp://live.twitch.tv/app/$1" > ~/twitch.log & 

# copy to yt
nohup ffmpeg_secure -listen 1 -i rtmp://0.0.0.0:1935/app/$1 -f flv -c copy rtmp://127.0.0.1:1937/app -f flv -c copy "rtmp://a.rtmp.youtube.com/live2/$2" & # > ~/tee.log &
