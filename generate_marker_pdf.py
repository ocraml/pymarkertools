'''
ArUco and April-Tag Marker PDF generator

This generates the selected markers on a freely configurable canvas / paper size
    - mm exact configuration of marker size for printout
    - mm exact configuration of distance between markers in x and y
    - marker labeling with marker id and configurable text
    - draws cutmarks for each marker
    - generates multi-page PDF for easy printing when generating large amount of markers

Copyright (c) 2019 Marco Noll, Garmin International,Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from cv2 import aruco
import cv2
import numpy as np
from PIL import Image


class TagGenerator(object):
    def __init__(self):
        #which tags to draw
        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_APRILTAG_36H11)
        #self.aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
        self.firsttag = 0 #tag id of first to draw
        self.lasttag = 119 #tag id of last tag to draw (April 16h5 has 30, 25h9 has 35, 36h10 has 2320, 36h11 has 587)
        self.tagbitwidth = 7 #how many bits including the black frame does the tag have, e.g. for 5x5 this is 5+2=7
        #configure the drawing size parameters
        self.dwidth = 2970 #available print space on the paper in 1/10 mm
        self.dheight = 4200 #available print space on the paper in 1/10 mm
        self.tagsize = 700 #in 1/10 mm
        self.tagframesize = int(self.tagsize/self.tagbitwidth) #distance from tag to cutmark
        self.tagdoubleframe = self.tagframesize*2 #in 1/10 mm, don't change, change tagframesize instead
        self.tagdist_x = self.tagdoubleframe + self.tagsize #distance of same tag-corner to next tag to the right, should be >= tagsize+tagdoubleframe
        self.tagdist_y = 1000 #distance in 1/10 mm of same tag-corner of next tag below, should be >= tagsize+tagdoubleframe
        self.pdfname = "DICT_APRILTAG_36H11.pdf"
        #settings for the tag labels
        self.tagtext_top = " april36h11" #text added to each tag on top
        self.tagtext_bottom = "     s"+ str(self.tagsize) + " dx" + str(self.tagdist_x) + " dy" + str(self.tagdist_y) #text added to each tag on bottom
        self.textoffset = int(self.tagdoubleframe * 0.8)
        self.textsize = self.tagdoubleframe / 150.0
        self.textcolor = (200,200,200)
        #typically don't need to change the following
        self.cutmark = self.create_cutmark(size=self.tagdoubleframe)
        self.quality = 100 #image quality in the pdf
        self.dpi = 254 #254dpi equals 10 dots per mm, this makes the previously defined units to be exact mm in the pdf
        self.cv2font = cv2.FONT_HERSHEY_SIMPLEX
        self.pages = [] #images for printing

    def drawmarks(self):
        #stepsize = self.tagsize + self.tagframe
        stepsize_x = self.tagdist_x
        stepsize_y = self.tagdist_y
        tfsize = self.tagsize + self.tagdoubleframe
        numcol = int((self.dwidth - self.tagdoubleframe) / (stepsize_x))
        numrow = int((self.dheight - self.tagdoubleframe) / (stepsize_y))
        print('Pagelayout columns: ',numcol,' rows:', numrow)
        tagid = self.firsttag
        while tagid < self.lasttag: #breaks when tagid > self.lasttag
            #create a white plane image. similar like a plain sheet of paper
            img = np.full((self.dheight,self.dwidth, 3), 255, dtype=np.uint8)
            #init the counters
            x_offset = y_offset = 0
            #fill the plain image with tags and marks and numbers
            for i in range(0,numcol):
                for j in range(0, numrow):
                    #draw upper left cutmark
                    self.mergeimage(img,self.cutmark,x_offset,y_offset)
                    #draw upper right cutmark
                    self.mergeimage(img,self.cutmark,x_offset + tfsize, y_offset )
                    #draw the tag id
                    cv2.putText(img,str(tagid)+' '+self.tagtext_top,
                                (x_offset+self.textoffset, y_offset+self.textoffset),
                                self.cv2font, self.textsize,self.textcolor,2,cv2.LINE_AA)
                    #draw the tag
                    tagimg = aruco.drawMarker(self.aruco_dict, tagid, self.tagsize)
                    self.mergeimage(img, tagimg, x_offset + self.tagdoubleframe, y_offset + self.tagdoubleframe)
                    #draw lower left cutmark
                    self.mergeimage(img, self.cutmark, x_offset, y_offset + tfsize)
                    # draw lower right cutmark
                    self.mergeimage(img, self.cutmark, x_offset+tfsize, y_offset + tfsize )
                    # draw bottom text
                    cv2.putText(img, self.tagtext_bottom,
                                (x_offset+self.textoffset, y_offset+self.textoffset+ tfsize - int(self.tagdoubleframe / 2)),
                                self.cv2font, self.textsize, self.textcolor, 2, cv2.LINE_AA)
                    y_offset += stepsize_y
                    if tagid >= self.lasttag:
                        break
                    tagid += 1
                y_offset = 0
                x_offset += stepsize_x
                if tagid >= self.lasttag:
                    break
            self.pages.append(Image.fromarray(img))

        #use PILlow to save image as pdf with exact size
        im = self.pages[0]
        if len(self.pages) > 1:
            im.save(self.pdfname,resolution=self.dpi, quality=self.quality,save_all=True,append_images=self.pages[1:])
        else:
            im.save(self.pdfname,resolution=self.dpi, quality=self.quality)

    def mergeimage(self,baseimg,mergeimg,xpos,ypos):
        if len(mergeimg.shape) == 3:
            baseimg[ypos:ypos + mergeimg.shape[0], xpos:xpos + mergeimg.shape[1] ] = mergeimg
        else:
            baseimg[ypos:ypos + mergeimg.shape[0], xpos:xpos + mergeimg.shape[1], 0] = mergeimg
            baseimg[ypos:ypos + mergeimg.shape[0], xpos:xpos + mergeimg.shape[1], 1] = mergeimg
            baseimg[ypos:ypos + mergeimg.shape[0], xpos:xpos + mergeimg.shape[1], 2] = mergeimg
        return baseimg

    #create a cutmark
    def create_cutmark(self, size=9, color=(0,0,0), thickness=1):
        img = np.full((size, size, 3), 255,dtype=np.uint8)
        shalf = int((size-1)/2)
        cv2.line(img,(0,shalf),(size-1,shalf),color,thickness) #add vertical line to the image object
        cv2.line(img, (shalf, 0), (shalf, size - 1), color, thickness) #add horizontal line to the image object
        return img

if __name__ == "__main__":
    tg = TagGenerator()
    tg.drawmarks()
