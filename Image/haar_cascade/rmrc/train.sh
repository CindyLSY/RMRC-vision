#!/bin/bash
python create_descriptor.py
mkdir positives
opencv_createsamples -img pos.png -bg bg.txt -info positives/info.lst -pngoutput positives -maxxangle 0.5 -maxyangle 0.5 -maxzangle 0.5 -num 1950
opencv_createsamples -info positives/info.lst -num 1950 -w 20 -h 20 -vec positives.vec
mkdir data
opencv_traincascade -data data -vec positives.vec -bg bg.txt -numPos 1800 -numNeg 900 -numStages 10 -w 20 -h 20