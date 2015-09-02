import sys
import os
import datetime
import copy

import Draft
from DraftParamParser import *

# The argument name/types we're expecting from the command line arguments
expectedTypes = dict()
expectedTypes['frameList'] = '<string>'
expectedTypes['inFile'] = '<string>'
expectedTypes['outFile'] = '<string>'
expectedTypes['fps'] = '<int>'

# Parse the command line arguments
params = ParseCommandLine(expectedTypes, sys.argv)

# Path to the Deadline Repository root
deadlineRepo = params['deadlineRepository']

inFilePattern = params['inFile']
frames = FrameRangeToFrames(params['frameList'])
(outBase, outExt) = os.path.splitext(params['outFile'])

firstImageNumber = FrameRangeToFrames(params['frameList'])[0]
inFile = ReplaceFilenameHashesWithNumber(inFilePattern, firstImageNumber)
firstImage = Draft.Image.ReadFromFile(inFile)
outHeight = firstImage.height
outWidth = firstImage.width

audio = None
for f in os.listdir(os.path.dirname(os.path.dirname(inFile))):
    if 'wav' in os.path.splitext(f)[-1]:
        temp = os.path.join(os.path.dirname(os.path.dirname(inFile)), f)
        if not os.path.exists(temp):
            audio = temp

# Build up the encoders
encoder = None
if audio:
    encoder = Draft.VideoEncoder(outBase + outExt, params['fps'], outWidth,
                                 outHeight, codec="MPEG4", audioFilename=audio)
else:
    encoder = Draft.VideoEncoder(outBase + outExt, params['fps'], outWidth,
                                 outHeight, codec="MPEG4")

# LUTs
alexaToLinear = Draft.LUT.CreateAlexaV3LogC().Inverse()
linearToSRGB = Draft.LUT.CreateSRGB()

# Main encoding loop
progressCounter = 0
for frameNumber in frames:
    print("Processing Frame: %d..." % frameNumber)

    inFile = ReplaceFilenameHashesWithNumber(inFilePattern, frameNumber)
    bgFrame = Draft.Image.ReadFromFile(inFile)

    bgFrame.Resize(outWidth, outHeight)
    alexaToLinear.Apply(bgFrame)
    linearToSRGB.Apply(bgFrame)

    encoder.EncodeNextFrame(bgFrame)

    progressCounter = progressCounter + 1
    progress = progressCounter * 100 / len(frames)
    print("Progress: %i%%" % progress)

# Finalize the encoding process
encoder.FinalizeEncoding()
