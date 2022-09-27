# Author Patryk Pankiewicz
# Script for count of amount of text data sent via DLT

import re
import os

stringDcTrace = "DC_Trace"
stringLog = "LOG_"
stringJson = "\"Text\":"


regexLog = stringDcTrace + ".*(\".*\")"
regexLog1 = stringLog + ".*(\".*\")"
regexJsonMsg = stringJson + ".*(\".*\")"


# assign directory
directory = '.'

count = 0
countMsgs = 0
# iterate over files in
# that directory
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        print(f)
        srcFile = open(f, 'r')
        Lines = srcFile.readlines()

        for line in Lines:
            #if (stringDcTrace in line):
            #    matches = re.finditer(regexLog, line, re.MULTILINE)
            #    for match in matches:
            #       count += (len(match[1])-2)
            #       countMsgs += 1

            #if (stringLog in line):
            #    matches = re.finditer(regexLog1, line, re.MULTILINE)
            #    for match in matches:
            #       count += (len(match[1])-2)
            #       countMsgs += 1
            if (stringJson in line):
                matches = re.finditer(regexJsonMsg, line, re.MULTILINE)
                for match in matches:
                   count += (len(match[1])-2)
                   countMsgs += 1

print(count)
print(countMsgs)






