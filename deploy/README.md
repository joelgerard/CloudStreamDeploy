This was built with a venv:
- py -3 -m venv .venv

To start working:
- . .venv/bin/activate or .venv/Scripts/activate
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install gunicorn
# if using sw encoders
sudo apt-get install ffmpeg
- pip install --break-system-packages -r requirements.txt
- python main.py and with gunicorn: gunicorn -b 0.0.0.0:8000 -w=10 wsgi:app --certfile=/home/joelgerard/certs/server.crt --keyfile=/home/joelgerard/certs/server.key --daemon
- gunicorn -b 0.0.0.0:8000 -w=10 wsgi:app

To curl:
- Windows:
    curl -X POST -H "Content-Type: application/json" -d "{\"cloudstream-streamkey\":\"password\"}" http://localhost:5000/set-password

    curl -X POST -H "Content-Type: application/json" -d "{\"cloudstream-streamkey\":\"password\"}" http://34.133.166.128:8000/check
pass1

Prod:
ssh-keygen
sudo apt-get update

# nginx
## even need this anymore?
sudo systemctl stop nginx
sudo apt purge nginx
sudo apt autoremove

sudo apt-get install nginx-full

# Nginx
### NOT THIS
sudo apt purge nginx
sudo apt autoremove
sudo apt install -y build-essential libssl-dev zlib1g-dev
sudo apt install -y libpcre3-dev
wget http://nginx.org/download/nginx-1.24.0.tar.gz
tar -xvzf nginx-1.24.0.tar.gz 
wget https://www.zlib.net/zlib-1.3.1.tar.gz
tar -xvf zlib-1.3.1.tar.gz
mv zlib-1.3.1 zlib-1.3
wget https://github.com/PhilipHazel/pcre2/releases/download/pcre2-10.39/pcre2-10.39.tar.bz2
tar -xvjf pcre2-10.39.tar.bz2
sudo mkdir /usr/local/nginx
sudo chown joelgerard /usr/local/nginx
cd nginx-1.24.0
./configure     --sbin-path=/usr/local/nginx/nginx --conf-path=/usr/local/nginx/nginx.conf  --pid-path=/usr/local/nginx/nginx.pid       --with-pcre=../pcre2-10.39     --with-zlib=../zlib-1.3 --with-stream --with-http_flv_module --with-stream --with-http_ssl_module
make
make install
/usr/local/nginx/nginx -c /home/joelgerard/cloudstream/server/nginx.conf

# ffmpeg
-- merge this: https://patchwork.ffmpeg.org/project/ffmpeg/patch/20190925185708.70924-1-unique.will.martin@gmail.com/
-- maybe remove?
sudo apt-get --purge remove ffmpeg
sudo apt-get --purge autoremove

sudo rm /usr/local/bin/ffmpeg
sudo rm /usr/bin/ffmpeg

git checkout rtmp

./configure --enable-nonfree --enable-cuda-nvcc --enable-libnpp --extra-cflags=-I/usr/local/cuda-12.6/include --extra-ldflags=-L/usr/local/cuda-12.6/lib64 --disable-static --enable-shared

make -j 8

sudo make install



-- Need to go through this and figure out the ffmpeg command now with cuda.
https://docs.nvidia.com/video-technologies/video-codec-sdk/12.0/ffmpeg-with-nvidia-gpu/index.html
sudo apt-get install yasm

sudo apt install libavdevice-dev

sudo apt-get update

-- TODO: Logging 


sudo cp /usr/local/bin/ffmpeg /usr/local/bin/ffmpeg_secure 
sudo cp /usr/local/bin/ffmpeg /usr/bin/ffmpeg_secure
sudo cp /usr/local/bin/ffmpeg_open /usr/local/bin/ffmpeg
sudo cp /usr/local/bin/ffmpeg_open /usr/bin/ffmpeg


Merge ffmpeg patch
https://patchwork.ffmpeg.org/project/ffmpeg/patch/20190925185708.70924-1-unique.will.martin@gmail.com/



# medialive
this is interesting: https://aws.amazon.com/blogs/media/awse-quickly-creat-live-streaming-channel-aws-elemental-medialive-workflow-wizard/

# ec2
use g4dn.xlarge

### nvidia driver installer

# from https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=24.04&target_type=deb_network
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-6

# then
sudo apt-get install -y nvidia-open

# finally 
https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#ubuntu
sudo apt-get install linux-headers-$(uname -r)
sudo apt-key del 7fa2af80

wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get install cuda-toolkit
sudo apt-get install nvidia-gds
sudo reboot

nvidia-smi # check driver version
sudo apt-get install cuda-drivers-560

# Don't forget paths in section 15
https://docs.nvidia.com/cuda/cuda-installation-guide-linux/
/usr/local/cuda-12.6/bin
export PATH=/usr/local/cuda-12.6/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib\
                         ${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}



# set password
curl -X POST -H "Content-Type: application/json" -d "{\"cloudstream-streamkey\":\"<password>\"}" http://localhost:5000/set-password


Cert:
openssl genrsa -out server.key 4096
openssl req -x509 -new -nodes -key server.key -sha512 -days 3650 -out server.pem
openssl x509 -outform der -in server.pem -out server.crt

NO!!
sudo setcap CAP_NET_BIND_SERVICE=+eip  /usr/bin/python3

sudo setcap CAP_NET_BIND_SERVICE=+eip /home/joelgerard/.local/bin/gunicorn

Test this: youtube-dl -f best -o - "YOUTUBE_VIDEO_URL" | ffmpeg -i - -c copy -f flv "rtmp://RTMP_ENDPOINT_URL". Probably need to talk to VI about it.
