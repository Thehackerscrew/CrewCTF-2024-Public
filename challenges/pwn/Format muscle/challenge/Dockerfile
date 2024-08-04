FROM alpine:latest
RUN apk add --no-cache socat dash && addgroup -S ctf && adduser -S ctf -G ctf
EXPOSE 1337
WORKDIR /home/ctf
COPY format-muscle libc.so.6 ld-musl-x86_64.so.1 flag.txt .
USER ctf
CMD ["socat", "tcp-l:1337,reuseaddr,fork", "EXEC:./format-muscle"]
