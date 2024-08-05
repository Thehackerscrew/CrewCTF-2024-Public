FROM python:3.11-slim AS chroot

RUN /usr/sbin/useradd --no-create-home -u 1000 user

WORKDIR /home/user

RUN apt-get update && \
    apt-get install -y wget tar socat git && \
    apt-get clean

RUN wget https://github.com/MystenLabs/sui/releases/download/mainnet-v1.27.4/sui-mainnet-v1.27.4-ubuntu-x86_64.tgz
RUN tar -xzvf sui-mainnet-v1.27.4-ubuntu-x86_64.tgz
RUN cp ./sui /usr/bin/sui

COPY run.py .
COPY secrets.py .
ADD ./chall /home/user/chall

COPY run.sh run


RUN chmod +x run

WORKDIR /home/user/chall
RUN sui move build

CMD socat TCP-LISTEN:1337,reuseaddr,fork EXEC:'python /home/user/run.py'