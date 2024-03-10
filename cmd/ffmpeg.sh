input_file="$1"
ffmpeg -user_agent 'Mozilla/5.0 (Windows NT 10.0; rv:108.0) Gecko/20100101 Firefox/108.0' \
    -headers 'Referer: https://streameast.top/\r\nOrigin: https://streameast.top\r\n' \
    -i "$input_file" \
    -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 \
    -codec: copy -f hls hls/embed-ufc.m3u8 \
    2> etc/error.log
