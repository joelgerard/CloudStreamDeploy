FROM nvidia/cuda:12.6.1-cudnn-devel-ubuntu24.04

# FROM ubuntu:22.04 as base
# RUN apt update -q && apt install -y ca-certificates wget && \
#     wget -qO /cuda-keyring.deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb && \
#     dpkg -i /cuda-keyring.deb && apt update -q

# FROM base as builder
# RUN apt install -y --no-install-recommends git cuda-nvcc-12-2
# RUN git clone --depth=1 https://github.com/nvidia/cuda-samples.git /cuda-samples
# RUN cd /cuda-samples/Samples/1_Utilities/deviceQuery && \
#     make && install -m 755 deviceQuery /usr/local/bin




# FROM base as runtime
# #RUN apt install -y --no-install-recommends libcudnn8 libcublas-12-2
# COPY --from=builder /usr/local/bin/deviceQuery /usr/local/bin/deviceQuery

RUN apt update
RUN apt install -y build-essential yasm cmake libtool libc6 libc6-dev unzip wget libnuma1 libnuma-dev git-all

RUN mkdir /src
WORKDIR /src
RUN git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git
WORKDIR /src/nv-codec-headers
RUN make install
WORKDIR /src
RUN git clone https://github.com/joelgerard/FFmpeg.git
WORKDIR /src/FFmpeg
RUN ./configure --enable-nonfree --enable-cuda-nvcc --enable-libnpp --extra-cflags=-I/usr/local/cuda/include --extra-ldflags=-L/usr/local/cuda/lib64 --disable-static --enable-shared
RUN make -j 8
RUN make install
# TODO: I seem to recall we needed the basic version of this not the secure one?
RUN cp /usr/local/bin/ffmpeg /usr/bin/ffmpeg
RUN cp /usr/local/bin/ffmpeg /usr/bin/ffmpeg_secure

RUN apt install -y python3-pip
RUN mkdir /web
WORKDIR /web
RUN git clone https://github.com/joelgerard/CloudStreamDeploy.git
WORKDIR /web/CloudStreamDeploy
RUN cp -r deploy/* ..
WORKDIR /web
RUN pip install --break-system-packages -r requirements.txt
RUN pip install --break-system-packages gunicorn    

# RUN mkdir /docker
# COPY docker /docker

RUN apt install -y curl
RUN curl -L https://fly.io/install.sh | sh





# CMD ["sleep", "inf"]
CMD ["gunicorn","-w","10", "--bind", "0.0.0.0:8000", "wsgi:app"]
# CMD ["bash","touch","test"]