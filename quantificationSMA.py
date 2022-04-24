import cv2 as cv
import numpy as np
import math
import xlsxwriter
import os
from pathlib import Path

DICTDATA = {}   # key = filename

def processImage(image, filename, displayImages=False):
    ''' Processes an image by counting total pixels, pixels inside/outside kidney,
        pixels on SMA, and then stores the results in dictionary
    Parameters: 
        image: the image to be processed must be of type NumPy array
        filename: the name of the image file
        displayImages: function will display the pre- and post-processed images if True
    Output:
        Stores number of total pixels, pixels inside/outside kidney, and pixels on SMA
        in a dictionary. Displays pre- and post-processed images to user if displayImages=True
    '''
    # imgData = [filename, total pxls, pxls outside KD, pxls inside KD, pxls on SMA]
    imgData = []         
    imgData.append(filename)
    height, width = image.shape
    total = height * width
    imgData.append(total)

    # remove pixels outside of kidney or on blood vessel
    validKidney = cv.inRange(image, 10, 190) # inRange() takes scalar bounds for grayscale image (only 1 channel)
    totalKidneyCount = cv.countNonZero(validKidney) # counts the number of nonzero elements in matrix
    outsideKidney = total - totalKidneyCount
    imgData.append(outsideKidney)
    imgData.append(totalKidneyCount)

    # count SMA intersections
    threshSMA = cv.inRange(image, 50, 75)
    SMACount = cv.countNonZero(threshSMA)
    imgData.append(SMACount)

    # calc percentage in range (SMA intersection pixels / kidney pixels)
    percent = SMACount / totalKidneyCount * 100

    # store img data in dictionary
    DICTDATA[filename] = imgData

    if displayImages == True:
        cv.imshow("greyscale", image)
        cv.imshow("valid kidney", validKidney)
        cv.imshow("SMA", threshSMA)
        
        cv.waitKey(0)
    return


def calcAverages():
    ''' Calculates the average pixels in KD and average pixels on SMA for all images in a directory
    Parameters: Assumes dictionary already contains pixel values for all images in the directory
    Outputs: The average pixels in KD and average pixels on SMA for images in the directory
    '''
    totPixelsInKD = 0
    totSMA = 0
    for i in DICTDATA:
        totPixelsInKD += DICTDATA[i][3]
        totSMA += DICTDATA[i][4]
    avgPxlsInKD = totPixelsInKD / len(DICTDATA)
    avgTotSMA = totSMA / len(DICTDATA)
    return avgPxlsInKD, avgTotSMA


def writeData(avgPxlsInKD, avgTotSMA):
    ''' Writes all results stored in dictionary into excel sheet
    Parameters:
        avgTotPixels: average total pixels for images in directory
        avgTotSMA: average pixels on SMA for images in directory 
    Output: 
        Creates new excel sheet and writes the data in it
    '''
    columns = ["Filename", "Total Pixels", "Pixels Outside KD", "Pixels Inside KD", "Pixels on SMA",
                "Avg Pixels in KD", "Avg Pixels on SMA"]

    excelName = input("Enter name of excel output (i.e. filename.xlsx, don't include '.xlsx'): ")

    wb = xlsxwriter.Workbook(excelName + ".xlsx")
    worksheet = wb.add_worksheet()
    worksheet.write_row(0, 0, columns)

    rowNum = 1
    for i in DICTDATA:
        imgData = DICTDATA[i]
        worksheet.write_row(rowNum, 0, imgData)
        rowNum += 1
    worksheet.write(rowNum, 5, avgPxlsInKD)
    worksheet.write(rowNum, 6, avgTotSMA)

    wb.close()
    print("Data written to " + excelName + ".xlsx")
    return


def loadFromDir(dirPath):
    ''' Reads all image files in specified directory and stores them in a list as NumPy array
    Parameters:
        dirPath: absolute path of directory
    Outputs:
        Returns the list of all image files in directory
    '''
    images = []
    dirList = os.listdir(dirPath)
    for filename in dirList:
        img = cv.imread(os.path.join(dirPath, filename))
        if img is not None:
            # remove color channel
            copy = img[:,:,2]
            # convert to uint8 from uint16
            copy8bit = cv.normalize(copy, None, 0, 255, cv.NORM_MINMAX, dtype=cv.CV_8U)
            images.append(copy8bit)

    return images


def testSingleImage(filepath):
    ''' Used to test processing on single image
    Parameters:
        filepath: absolute path for the image file
    Output:
        Converts image to 8-bit and returns as type NumPy array
    '''
    img = cv.imread(filepath)
    # remove color channel
    copy = img[:,:,2]
    # convert to uint8 from uint16
    copy8bit = cv.normalize(copy, None, 0, 255, cv.NORM_MINMAX, dtype=cv.CV_8U)
    return copy8bit


def getFolder():
    ''' Retrieves absolute path of directory from user
    Parameters:
        None
    Output:
        Returns absolute path of directory or 'q' if user wants to exit program
    '''
    dirPath = input("Absolute path: ")
    loop = True
    userQuit = False
    while loop == True and userQuit == False:
        isExists = os.path.exists(dirPath)
        if dirPath == "q":
            userQuit = True
        elif isExists == False:
            print("Error: The filepath does not exist, enter valid path or press q to quit")
            dirPath = input("Absolute path: ")
        elif isExists == True:
            loop = False

    return dirPath


def main(): 

    dirPath = getFolder()
    # quit program if user enters q
    if dirPath == "q":
        return
    
    dirList = os.listdir(dirPath)        # list of all files in directory
    dirList = sorted(dirList)            # sort files
    for imgfile in dirList:              # remove non-image files
        if imgfile.find(".tif") == -1:
            dirList.remove(imgfile)

    images = loadFromDir(dirPath)       # container with all images from directory
    
    for i in range(len(dirList)):
        processImage(images[i], dirList[i])

    avgPxlsInKD, avgTotSMA = calcAverages()
    writeData(avgPxlsInKD, avgTotSMA)
   


main()

