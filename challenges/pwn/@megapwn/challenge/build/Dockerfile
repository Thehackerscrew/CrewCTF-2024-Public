FROM ubuntu:22.04
RUN apt-get -y update && apt-get -y install build-essential git gcc-avr avr-libc pkg-config

COPY build/tiny-AES-c.patch /
RUN git clone https://github.com/kokke/tiny-AES-c.git
WORKDIR /tiny-AES-c/
RUN git checkout f06ac37fc31dfdaca2e0d9bec83f90d5663c319b
RUN patch -p1 < ../tiny-AES-c.patch
WORKDIR /

COPY build/printf.patch /
RUN git clone https://github.com/mpaland/printf.git
WORKDIR /printf/
RUN git checkout d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e
RUN patch -p1 < ../printf.patch
WORKDIR /

COPY build/simavr.patch /
RUN git clone https://github.com/buserror/simavr.git
WORKDIR /simavr/
RUN git checkout d51f593d8959fd5b5e7c1b90b46fa3a4b8529465
RUN patch -p1 < ../simavr.patch
RUN make build-simavr
RUN cp simavr/run_avr ..
WORKDIR /

COPY build/Makefile /
COPY build/eeprom.hex /
COPY main.c /
RUN make

CMD make sim
