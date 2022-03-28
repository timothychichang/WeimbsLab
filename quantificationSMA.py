import cv2 as cv
import numpy as np
import math
import xlsxwriter
import os
from pathlib import Path

dictData = {}   # key = filename

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
    imgData = []
    imgData.append(filename)
    print(filename)

    height, width = image.shape
    total = height * width
    print("\nTotal pixels:\t\t", total)
    imgData.append(total)

    # remove pixels outside of kidney or on blood vessel
    validKidney = cv.inRange(image, 10, 190) # inRange() takes scalar bounds for grayscale image (only 1 channel)
    totalKidneyCount = cv.countNonZero(validKidney) # counts the number of nonzero elements in matrix
    outsideKidney = total - totalKidneyCount
    print("Pixels outside KD:\t", outsideKidney)
    print("Pixels inside KD:\t", totalKidneyCount)
    imgData.append(outsideKidney)
    imgData.append(totalKidneyCount)

    # count SMA intersections
    threshSMA = cv.inRange(image, 50, 75)
    SMACount = cv.countNonZero(threshSMA)
    print("Pixels on SMA:\t\t", SMACount)
    imgData.append(SMACount)

    # calc percentage in range (SMA intersection pixels / kidney pixels)
    percent = SMACount / totalKidneyCount * 100
    print("Percentage in range:\t {0:.4}%".format(percent))
    print("\n")

    dictData[filename] = imgData

    if displayImages == True:
        cv.imshow("greyscale", image)
        cv.imshow("valid kidney", validKidney)
        cv.imshow("SMA", threshSMA)
        
        cv.waitKey(0)
    return


def calcAverages():
    ''' Calculates the average total pixels and average pixels on SMA for a directory of images
    Parameters: Assumes dictionary contains pixel values for images in the directory
    Outputs: The average total pixels and average pixels on SMA for images in the directory
    '''
    totPixels = 0
    totSMA = 0
    for i in dictData:
        totPixels += dictData[i][1]
        totSMA += dictData[i][4]
    avgTotPixles = totPixels / len(dictData)
    avgTotSMA = totSMA / len(dictData)
    return avgTotPixles, avgTotSMA


def writeData(avgTotPixels, avgTotSMA):
    ''' Writes all results stored in dictionary into excel sheet
    Parameters:
        avgTotPixels: average total pixels for images in directory
        avgTotSMA: average pixels on SMA for images in directory 
    Output: 
        Creates new excel sheet and writes the data in it
    '''
    columns = ["Image", "Total Pixels", "Pixels Outside KD", "Pixels Inside KD", "Pixels on SMA",
                "Avg Total Pixels", "Avg Pixels on SMA"]

    wb = xlsxwriter.Workbook("example.xlsx")
    worksheet = wb.add_worksheet()
    worksheet.write_row(0, 0, columns)

    rowNum = 1
    for i in dictData:
        imgData = dictData[i]
        worksheet.write_row(rowNum, 0, imgData)
        rowNum += 1
    worksheet.write(rowNum, 5, avgTotPixels)
    worksheet.write(rowNum, 6, avgTotSMA)

    wb.close()
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



def main(): 

    dirPath = "/Users/timothy/Desktop/WeimbsLab/SMALewis/W6.5_10x/testSMA"
    isExists = os.path.exists(dirPath)
    dirList = os.listdir(dirPath)        # list of all files in directory
    dirList = sorted(dirList)            # sort files
    images = loadFromDir(dirPath)       # container with all images from directory
    
    for i in range(len(dirList)):
        processImage(images[i], dirList[i])

    avgTotPixles, avgTotSMA = calcAverages()
    writeData(avgTotPixles, avgTotSMA)
   


main()


'''
# used for testing individual files
filePath = "/Users/timothy/Desktop/WeimbsLab/SMALewis/W6.5_10x/testSMA/img_000000002_Default_000.tif"
displayImages = True
image8bit = readSingleImage(filePath)
processImage(image8bit, displayImages)
'''




'''
#####################
# test Guassian Blur

blurredCopy = cv.blur(copy8bit2, (3,3))
blurRemoveExtreme = cv.inRange(blurredCopy, 10, 190) # inRange() takes scalar bounds for grayscale image (only 1 channel)
blurTotalKidneyCount = cv.countNonZero(blurRemoveExtreme)   # counts the number of nonzero elements in matrix
print("\ntotal pixels after removing extremes(pixels that make up kidney): ", blurTotalKidneyCount)
blurThresh = cv.inRange(blurredCopy, 50, 75)
blurThreshCount = cv.countNonZero(blurThresh)
print("pixels in range: ", blurThreshCount)
blurPercent = blurThreshCount / blurTotalKidneyCount * 100
print("percentage of in range: {0:.4}%".format(blurPercent))

cv.imshow("blur remove nonkidney", blurRemoveExtreme)
cv.imshow("blur SMA intersections", blurThresh)
cv.imshow("blur original image", blurredCopy)

cv.waitKey(0) # press q to exit image
'''