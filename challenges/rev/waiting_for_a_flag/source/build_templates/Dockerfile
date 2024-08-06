FROM ubuntu:22.04 AS build

ARG KEY
ENV SCRIPT_AES256_ENCRYPTION_KEY=$KEY

RUN apt update && apt install -y \
  build-essential \
  scons \
  pkg-config \
  libx11-dev \
  libxcursor-dev \
  libxinerama-dev \
  libgl1-mesa-dev \
  libglu-dev \
  libasound2-dev \
  libpulse-dev \
  libudev-dev \
  libxi-dev \
  libxrandr-dev \
  git \
  mingw-w64

RUN git clone https://github.com/godotengine/godot -b 4.2

WORKDIR /godot

RUN scons platform=linuxbsd target=template_release arch=x86_64
RUN scons platform=linuxbsd target=template_debug arch=x86_64

RUN echo 1 | update-alternatives --config x86_64-w64-mingw32-gcc
RUN echo 1 | update-alternatives --config x86_64-w64-mingw32-g++
RUN scons platform=windows target=template_release arch=x86_64
RUN scons platform=windows target=template_debug arch=x86_64

FROM scratch AS binaries

COPY --from=build /godot/bin /
