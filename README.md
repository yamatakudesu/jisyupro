jisyupro
====

## contents
### Usage
#### pigpio
Before running the code using pigpio module like "servo-sample.py", run the following command.

`$ sudo pigpiod`

#### Julius
make an original dictionary

`$ vi recog.yomi`

change the type of the dictionary   

`$ iconv -f utf8 -t eucjp recog.yomi | yomi2voca.pl > ~/julius-kits/dictation-kit-v4.4/recog.dic`

edit the setting file

`$ vim ~/julius-kits/dictation-kit-v4.4/recog.jconf`

start-up julius which reads the original dictionary

`$ julius -C ~/julius-kits/dictation-kit-v4.4/recog.jconf`



## Requirement
- Raspberry Pi 3 Model B
- Python 3.5.3 
- OpenCV 3.3.1
- Numpy
- pigpio
- Julius
- OpenJtalk