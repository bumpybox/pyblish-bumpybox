import sys

sys.path.append(r'\\192.168.145.8\deadlinerepository_7\draft\Windows\64bit')

import Draft
from DraftParamParser import ReplaceFilenameHashesWithNumber


frameNum = 1        # What number the first frame (jpeg) will have.
decoder = Draft.VideoDecoder(r'O:\resources\footage\cyw_jaj_ep999_songs\cyw_jaj_farmsong\cyw_jenajim_farmsong_vers1\JEN A JIM V01.55CC755CC7F39.mov')       # Initialize the video decoder.
frame = Draft.Image.CreateImage(1, 1)   # Create an image object.

while decoder.DecodeNextFrame(frame) :
    currFile = ReplaceFilenameHashesWithNumber(r'C:\Users\toke.jepsen\Desktop\New folder\Patches_###.png', frameNum)
    frame.WriteToFile(currFile)
    frameNum += 1
