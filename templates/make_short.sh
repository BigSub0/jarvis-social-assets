#!/usr/bin/env bash
# Usage: templates/make_short.sh <card.jpg> <out.mp4>
# 12s 1080x1920 YouTube Short: slow push-in on the card, silent audio track.
set -e
ffmpeg -y -loglevel error -loop 1 -framerate 30 -i "$1" -f lavfi -i anullsrc=r=44100:cl=stereo \
  -filter_complex "[0:v]scale=2160:3840,zoompan=z='min(1+0.00012*on,1.045)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=360:s=1080x1920:fps=30,format=yuv420p[v]" \
  -map "[v]" -map 1:a -t 12 -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 128k -shortest -movflags +faststart "$2"
