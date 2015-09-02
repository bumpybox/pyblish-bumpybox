import sys
import os

import Draft
from DraftParamParser import *

# The argument name/types we're expecting from the command line arguments
expectedTypes = dict()
expectedTypes['inFile'] = '<string>' # expects a path like "path/movie.mov"
expectedTypes['outFile'] = '<string>' # expects a path like "path/image.####.jpeg"
expectedTypes['sourceIn'] = '<string>' # expects a frame number
expectedTypes['sourceOut'] = '<string>' # expects a frame number

# Parse the command line arguments
params = ParseCommandLine(expectedTypes, sys.argv)

in_file = params['inFile']
out_file = params['outFile']
source_in = int(params['sourceIn'])
source_out = int(params['sourceOut'])

# Main encoding loop
decoder = Draft.VideoDecoder(in_file)
frame = Draft.Image.CreateImage(1, 1)

for count in range(source_in, source_out + 1):
    decoder.DecodeFrame(count, frame)
    f = ReplaceFilenameHashesWithNumber(out_file, count)

    frame.WriteToFile(f)
