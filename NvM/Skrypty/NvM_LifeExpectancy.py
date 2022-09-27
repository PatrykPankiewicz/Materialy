# Author Patryk Pankiewicz
# Script for NvM life expectancy calculations and localizing NvM functions usages
# In order to use -> fill in the CODEBASE_PATH with project name
# Export NvM configuration in a CSV format and provide the path in NVM_CONFIG_FILE_EXPORT variable
# The data format of the csv is defined in lines 164-173, the headers of colums define the data.

import csv
import math
import os
import re

BLOCK_INFO_SIZE_BYTES = 16
CRC16_SIZE_BYTES = 2
CRC32_SIZE_BYTES = 4
BLOCK_ALIGNMENT_BYTES = 4

FREQUENCY_OF_WRITE_ALL_PER_SECOND = (0.00001157 * 4) #to get 4 per day
FREQUENCY_OF_WRITE_ALL_PER_HOUR = (FREQUENCY_OF_WRITE_ALL_PER_SECOND * 3600)
FREQUENCY_OF_WRITE_ALL_PER_DAY = (FREQUENCY_OF_WRITE_ALL_PER_HOUR * 24)
FREQUENCY_OF_WRITE_ALL_PER_YEAR = (FREQUENCY_OF_WRITE_ALL_PER_DAY * 365)

FREQUENCY_RATIO_SECONDS_TO_YEARS = (1/3600/24/365)

FEE_SECTION_SIZE = 65536
MAX_ERASE_CYCLES = 10000
AMOUNT_OF_SECTIONS = 2

CODEBASE_PATH = "Y:\project"
NVM_CONFIG_FILE_EXPORT = "NvM_Config_06_07_2022.txt"

class ClassNvmBlock:
    def __init__(self, name):
        self._name = name
        self._blockId = 0
        self._priority = 0
        self._length = 0
        self._numberOfCopies = 0
        self._blockType = ""
        self._crcSetting = ""
        self._readAllEnabled = ""
        self._writeAllEnabled = ""
        self._writeFrequency = 0
        self._requiredMemoryPerSecond = 0
        
    def printBlockInfo(self):
        print(self._name)

    def calculateBlockSize(self):
        blockSize = 0
        crcSize = 0
        dataSize = 0

        if(self._crcSetting == "NVM_CRC16"):
            crcSize = CRC16_SIZE_BYTES
        elif (self._crcSetting == "NVM_CRC32"):
            crcSize = CRC32_SIZE_BYTES
        else:
            crcSize = 0

        dataSize = (crcSize + self._length + BLOCK_INFO_SIZE_BYTES)
        alignedSize = math.ceil(dataSize/BLOCK_ALIGNMENT_BYTES) * BLOCK_ALIGNMENT_BYTES
        blockSize = alignedSize * self._numberOfCopies
        #print("BlockId: " + str(self._blockId) + " length: " +  str(blockSize))
        
        return blockSize

def calculateRawBlocksSize(blocksList: list):
    totalSize = 0
    for block in blocksList:
        totalSize += block._length

    print("Total Raw blocks size: " + str(totalSize))
    return totalSize

def calculateBlocksSize(blocksList: list):
    totalSize = 0
    writeAllSize = 0
    #readAllSize = 0
    nonWriteAllSize = 0
    #nonReadAllSize = 0
    blockSize = 0
    
    for block in blocksList:
        blockSize = block.calculateBlockSize()
        totalSize += blockSize
    
    print("Total size in bytes: " + str(totalSize))
    return totalSize
    
def calculateReadAllBlocksSize(blocksList: list):
    readAllSize = 0
    nonReadAllSize = 0 
    blockSize = 0

    for block in blocksList:
        blockSize = block.calculateBlockSize()
        if(block._readAllEnabled == "true"):
            readAllSize += blockSize
        else:
            nonReadAllSize += blockSize

    print("Total size of readAll blocks in bytes: " + str(readAllSize))
    print("Total size of non-ReadAll blocks in bytes: " + str(nonReadAllSize))
    return readAllSize
    
def calculateWriteAllBlocksSize(blocksList: list):
    writeAllSize = 0
    nonWriteAllSize = 0
    blockSize = 0

    for block in blocksList:
        blockSize = block.calculateBlockSize()
        if(block._writeAllEnabled == "true"):
            writeAllSize += blockSize
        else:
            nonWriteAllSize += blockSize

    print("Total size of writeAll blocks in bytes: " + str(writeAllSize))
    print("Total size of non-writeAll blocks in bytes: " + str(nonWriteAllSize))
    
    return writeAllSize

def calculateNonWriteAllBlocksSize(blocksList: list):
    nonWriteAllSize = 0
    blockSize = 0

    for block in blocksList:
        blockSize = block.calculateBlockSize()
        if(block._writeAllEnabled == "false"):
            nonWriteAllSize += blockSize

    #print("Total size of non-writeAll blocks in bytes: " + str(nonWriteAllSize))
    return nonWriteAllSize
    
def calculateLifeExpectancy(blocksList: list):
    blockSize = 0
    frequencyOfWriting = 0
    sectionSwitchTime = 0
    sectionSwitchTimeOfAllBlocks = 0
    totalSize = calculateBlocksSize(blocksList)
    writeAllBlocksSize = calculateWriteAllBlocksSize(nvmBlocksList)
    nonWriteAllBlocksSize = calculateNonWriteAllBlocksSize(nvmBlocksList)
    requiredMemoryNonWriteAllBlocks = 0
    requiredMemoryWriteAllBlocks = 0

    for block in blocksList:
        blockSize = block.calculateBlockSize()
        if(block._writeAllEnabled == "false") and (block._writeFrequency != 0) :
            requiredMemoryNonWriteAllBlocks += block._writeFrequency * blockSize
        #print("Section Switch Time for block " + str(block._blockId) + " is " + str(sectionSwitchTimeOfAllBlocks * FREQUENCY_RATIO_SECONDS_TO_YEARS) + " years.")

    requiredMemoryWriteAllBlocks = writeAllBlocksSize * FREQUENCY_OF_WRITE_ALL_PER_SECOND

    sectionSwitchTime = (FEE_SECTION_SIZE - totalSize) / (requiredMemoryWriteAllBlocks + requiredMemoryNonWriteAllBlocks)
    print("Section Switch Time for all blocks is " + str(sectionSwitchTime * FREQUENCY_RATIO_SECONDS_TO_YEARS) + " years.")
    memoryDurability = sectionSwitchTime * FREQUENCY_RATIO_SECONDS_TO_YEARS * MAX_ERASE_CYCLES * AMOUNT_OF_SECTIONS
    print("Memory durability is " + str(memoryDurability) + " years.")

nvmBlocksList = []

with open(NVM_CONFIG_FILE_EXPORT,'rt') as csvfile:
    csvreader = csv.DictReader(csvfile,delimiter=',')

    for row in csvreader:
        nvmBlocksList.append(ClassNvmBlock(row['Name']))
        nvmBlocksList[-1]._blockId = row['BlockId']
        nvmBlocksList[-1]._priority = row['Priority']
        nvmBlocksList[-1]._length = int(row['Length'])
        nvmBlocksList[-1]._numberOfCopies = int(row['NumberOfCopies'])
        nvmBlocksList[-1]._blockType = row['BlockType']
        nvmBlocksList[-1]._crcSetting = row['CRC']
        nvmBlocksList[-1]._readAllEnabled = row['ReadAllEnabled']
        nvmBlocksList[-1]._writeAllEnabled = row['WriteAllEnabled']      

def findfiles(path, string):
    lineNumber = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.c'):
                fullpath = os.path.join(root, file)
                with open(fullpath, 'r', errors="ignore") as f:
                    for line in f:
                        lineNumber += 1
                        if string in line:
                            print("Line: " + str(lineNumber) + " " + fullpath)
                    lineNumber = 0

calculateLifeExpectancy(nvmBlocksList)
#calculateBlocksSize(nvmBlocksList)
#calculateWriteAllBlocksSize(nvmBlocksList)
#calculateNonWriteAllBlocksSize(nvmBlocksList)
calculateReadAllBlocksSize(nvmBlocksList)
calculateRawBlocksSize(nvmBlocksList)

print("\nNvM WriteAll occurences: ")
findfiles(CODEBASE_PATH , "NvM_WriteAll();")

print("\nNvM Write occurences: ")
findfiles(CODEBASE_PATH , "NvM_ASR42_WritePRAMBlock(")