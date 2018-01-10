#!/bin/sh

julius -C ~/julius-kits/dictation-kit-v4.4/recog2.jconf -module > /dev/null &
echo $!
sleep 3