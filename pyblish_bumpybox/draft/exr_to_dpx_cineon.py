import sys

if __name__ == '__main__':
    sys.path.append(r'\\192.168.145.8\deadlinerepository_7\draft\Windows\64bit')

import Draft
from DraftParamParser import *

# The argument name/types we're expecting from the command line arguments
expectedTypes = dict()
expectedTypes['taskStartFrame'] = '<string>'
expectedTypes['taskEndFrame'] = '<string>'
expectedTypes['inFile'] = '<string>'
expectedTypes['outFile'] = '<string>'

# Parse the command line arguments
params = ParseCommandLine(expectedTypes, sys.argv)

# Path to the Deadline Repository root
inFilePattern = params['inFile']
outFilePattern = params['outFile']
taskStartFrame = int(params['taskStartFrame'])
taskEndFrame = int(params['taskEndFrame'])

lut = Draft.LUT.CreateCineon()

for frameNumber in range(taskStartFrame, taskEndFrame + 1):
    inFile = ReplaceFilenameHashesWithNumber(inFilePattern, frameNumber)
    img = Draft.Image.ReadFromFile(inFile)

    lut.Apply(img)

    outFile = ReplaceFilenameHashesWithNumber(outFilePattern, frameNumber)
    img.WriteToFile(outFile)
