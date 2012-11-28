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
import urllib
import lxml.html
from datetime import datetime

def printdiff(value, filename=None):
    if filename:
        print  "RMS %s: %s"% (filename, value)
    else:
        print  value

def getimage(filename, suffix, prefix = u'.'):
    elapsed_time = 0
    if filename.startswith('http://'):
        opener = urllib.FancyURLopener({})
        (htmlfilename, header) = opener.retrieve(filename)
        print "Retrieved HTML file into %s (size:%d)" % (htmlfilename, os.path.getsize(htmlfilename))
        
        tree = lxml.html.parse(htmlfilename).getroot()
        r = tree.get_element_by_id('viewProduit:imgCarte')
        title = tree.get_element_by_id('viewProduit:titreCarte').text
        print title
        realfilename = '/'.join([prefix, '.'.join([title, suffix, 'png'])])
        
        start_time = datetime.now()
        (realfilename, header) = opener.retrieve(r.attrib['src'], realfilename)
        elapsed_time = (datetime.now() - start_time).microseconds / 1000
        print "Retrieved IMG file into %s (size:%d)" % (realfilename, os.path.getsize(realfilename))
    else:
        realfilename = filename
    return (realfilename, Image.open(realfilename), elapsed_time)
    
def rmsdiff(file1, file2, prefix = '.'):
    "Calculate the root-mean-square difference between two images"
    (filename1, im1, time1) = getimage(file1, '1', prefix)
    (filename2, im2, time2) = getimage(file2, '2', prefix)
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
    return (filename1, filename2, rms, time1, time2)

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