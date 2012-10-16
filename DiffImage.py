# -*- coding: utf-8 -*-
'''
Created on Oct 16, 2012

@author: geraud
'''

import math, operator
import sys
import Image, ImageStat, ImageChops
import os
import magic

def printdiff(value, filename=None):
    if filename:
        print  "RMS %s: %d"% (filename, value)
    else:
        print  value

def rmsdiff(file1, file2):
    "Calculate the root-mean-square difference between two images"
    im1 = Image.open(file1)
    im2 = Image.open(file2)
    h1 = im1.convert("RGB").histogram()
    h2 = im2.convert("RGB").histogram()

#    print ImageStat.Stat(im1).rms
#    print ImageStat.Stat(im2).rms
#    print ImageStat.Stat(im1.convert("RGB")).rms
#    print ImageStat.Stat(im2.convert("RGB")).rms
#    
#    print "file1 RMS: %d" %ImageStat.Stat(im1).rms[0]
#    print "file2 RMS: %d" %ImageStat.Stat(im2).rms[0]
#    
#    print "file1 histogram size: %d" % len(h1)
#    print "file2 histogram size: %d" % len(h2)
#    
#    print ImageStat.Stat(ImageChops.difference(im1.convert("RGB"), im2)).rms
    
    rms = math.sqrt(reduce(operator.add,
                    map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
    return rms

def diffdirectory(dir1, dir2):
    for d in os.listdir(dir1):
        fullpath = '/'.join([dir1, d])
        if os.path.isdir(fullpath):
            diffdirectory(fullpath, '/'.join([dir2, d]))
        else:
            filetype = magic.from_file(fullpath, mime=True)
            if filetype.startswith('image'):
                printdiff(rmsdiff(fullpath, '/'.join([dir2,d])), filename=d)
            else:
                sys.stderr.write("%s skipped: not an image\n" %d)

    
if __name__ == '__main__':
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    if os.path.isdir(file1):
        diffdirectory(file1, file2)
    else:
        printdiff(rmsdiff(file1, file2))