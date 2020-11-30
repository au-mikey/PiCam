#!/bin/bash

config="config.ini"

width=$(sed -n -e 's/^\s*width\s*=\s*//p' $config)
height=$(sed -n -e 's/^\s*height\s*=\s*//p' $config)
rotation=$(sed -n -e 's/^\s*rotation\s*=\s*//p' $config)
fps=$(sed -n -e 's/^\s*fps\s*=\s*//p' $config)
bitrate=$(sed -n -e 's/^\s*bitrate\s*=\s*//p' $config)
port=$(sed -n -e 's/^\s*port\s*=\s*//p' config.ini | head -n 1)
directory=$(sed -n -e 's/^\s*directory\s*=\s*//p' $config)
protocol=$(sed -n -e 's/^\s*protocol\s*=\s*//p' $config)

echo "port = "$port
echo "directory = "$directory
echo "protocol = "$protocol


#raspivid -o - -t 0 -rot $rotation -w $width -h $height -fps $fps -b $bitrate | cvlc -vvv stream:///dev/stdin --sout '#rtp{access=udp,sdp=rtsp://:8554/unicast}' :demux=h264

raspivid -o - -t 0 -rot $rotation -w $width -h $height -fps $fps -b $bitrate | cvlc -vvv stream:///dev/stdin --sout '#rtp{access='$protocol',sdp=rtsp://:'$port'/'$directory'}' :demux=h264
