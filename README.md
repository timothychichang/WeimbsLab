# SMA Quantification
Created by Tim Chang for Weimbs Lab at UCSB

## Description

This script processes microscopic images to help with the quantification of smooth muscle actin (SMA). 
Using the OpenCV library for image processing tasks, the program takes a collection of microscopic images 
(.tif format) as input and outputs the quantified data to an excel sheet. By detecting the intensity of 
each pixel and determining if they are outside the KD, inside the KD, or on SMA, the program calculates 
the total percentage of SMA in each image. 

## How to Run

```
git clone https://github.com/timothychichang/WeimbsLab-SMA.git
python quantificationSMA.py
```

The program will prompt the user for the absolute path to the directory containing the images of interest.
After entering the input path, the program will then prompt the user to specify a name for the output file
and an optional location for it to be stored (default is the current directory). 

Example:
```
Absolute path: /Users/timothy/Desktop/WeimbsLab/SMALewis/W6.5_10x
Enter name of excel output (i.e. filename.xlsx, don't include '.xlsx'): testResult
Enter 'q' to output to current directory or enter absolute path of destination (folder must already exist)
Absolute path: q
```

