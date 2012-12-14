# -*- coding: utf-8 -*-
'''
Created on Oct 16, 2012

@author: geraud
'''

import math, operator
import sys
import Image

import os
import magic
import urllib2
import lxml.html
from datetime import datetime
import ImageDraw
import tempfile
import cookielib
import shutil
import cv2
import cv
import numpy as np

MODE="RGBA"

class DiffImage(object):
    def __init__(self, file1, file2, prefix= '.'):
        self.file1=file1
        self.file2=file2
        (self.filename1, self.time1) = self.getimage(self.file1, '1', prefix)
        (self.filename2, self.time2) = self.getimage(self.file2, '2', prefix)

    def _getUrlContent(self, url, filename=None, buffer_size=1024):
        cookiejar = cookielib.CookieJar()
        urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
        f = urlOpener.open(url)
        if filename is None: 
            filename = tempfile.NamedTemporaryFile().name
        
        with open(filename, 'w+b') as tmp_file:
            b = f.read(buffer_size)
            while b != b'':
                tmp_file.write(b)
                b = f.read(buffer_size)
    
        return filename
    
    def getimage(self, filename, suffix, prefix=u'.'):
        elapsed_time = 0
        if filename.startswith('http://'):
            try:
                # By default
                realfilename = '/'.join([prefix, 'failed.png'])
                
                start_time = datetime.now()
                retrfilename = self._getUrlContent(filename) 
    
                filetype = magic.from_file(retrfilename, mime=True)
                print filetype
                if filetype.startswith('image'):
                    realfilename = '/'.join([prefix, os.path.basename(retrfilename)])
                    realfilename = '.'.join([realfilename, 'png'])
                    shutil.move(retrfilename, realfilename)
                else:
                    print "Retrieved HTML file into %s (size:%d)" % (retrfilename, os.path.getsize(retrfilename))
    
                    tree = lxml.html.parse(retrfilename).getroot()
                    r = tree.get_element_by_id('viewProduit:imgCarte')
                    title = tree.get_element_by_id('viewProduit:titreCarte').text
                    print title
                    realfilename = '/'.join([prefix, '.'.join([title, suffix, 'png'])])
                    
                    start_time = datetime.now()
                    realfilename = self._getUrlContent(r.attrib['src'], filename=realfilename)
                    
                    try:
                        os.remove(retrfilename)
                    except:
                        pass
    
                    if os.path.getsize(realfilename) == 0:
                        raise RuntimeError('Fichier vide')
    
            except Exception, e:
                print e
                im = Image.new("RGB", (700, 700), "red")
                draw = ImageDraw.Draw(im)
                draw.text((0, 50), unicode('Erreur', 'UTF-8'))
                del draw
                im.save(realfilename, 'PNG')
    
            elapsed_time = (datetime.now() - start_time).microseconds / 1000
            print "Retrieved IMG file into %s (size:%d)" % (realfilename, os.path.getsize(realfilename))
        else:
            realfilename = filename
        return (realfilename, elapsed_time)
        
    def rmsdiff(self):
        "Calculate the root-mean-square difference between two images"
        im1 = Image.open(self.filename1)
        im2 = Image.open(self.filename2)
        h1 = im1.convert(MODE).histogram()
        h2 = im2.convert(MODE).histogram()
    
        result = math.sqrt(reduce(operator.add,
                        map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1))
        return (self.filename1, self.filename2, result, self.time1, self.time2)
    
    def diff2(self, prefix='.', algo=cv.CV_COMP_CORREL):
        '''
        Calculate the difference between two histogramm, using OpenCV
        Available values for algo are : cv.CV_COMP_CHISQR, cv.CV_COMP_INTERSECT, cv.CV_COMP_BHATTACHARYYA 
        '''
        
        # Handle UTF-8 filename
        with open(self.filename1, "rb") as f:
            file1 = np.fromstring(f.read(), dtype='uint8')
        
        with open(self.filename2, "rb") as f:
            file2 = np.fromstring(f.read(), dtype='uint8')
    
        # Image loading
        im1 = cv2.imdecode(file1, flags=cv.CV_LOAD_IMAGE_COLOR)
        im2 = cv2.imdecode(file2, flags=cv.CV_LOAD_IMAGE_COLOR)
    
        # HSV conversion    
        (hsvImage1, hsvImage2) = (None, None)
    
        hsvImage1 = cv2.cvtColor(im1, cv.CV_BGR2HSV)
        hsvImage2 = cv2.cvtColor(im2, cv.CV_BGR2HSV)
        
        # Calculate histograms
        h1, h2 = None, None
        
        channels = [0,1]   # HUE and Saturation
        bins = [30,32]     # 30 for HUE and 32 for Saturation
        h_range = [0, 256] # HUE varies from 0 to 256
        s_range = [0, 180] # Saturation varies from 0 to 180
        
        h1 = cv2.calcHist([hsvImage1], channels, None, bins, h_range + s_range) # TODO: normalize
        h2 = cv2.calcHist([hsvImage2], channels, None, bins, h_range + s_range) # TODO: normalize
        
        # Compare histograms
        result = cv2.compareHist(h1, h2, algo)
        
        return (self.filename1, self.filename2, result, self.time1, self.time2)

def printdiff(value, filename=None):
    if filename:
        print  "RMS %s: %s" % (filename, value)
    else:
        print  value
    

def diffdirectory(dir1, dir2):
    for d in os.listdir(dir1):
        fullpath = '/'.join([dir1, d])
        if os.path.isdir(fullpath):
            diffdirectory(fullpath, '/'.join([dir2, d]))
        else:
            filetype = magic.from_file(fullpath, mime=True)
            if filetype.startswith('image'):
                diff = DiffImage(fullpath, '/'.join([dir2, d]))
                printdiff(diff.rmsdiff(), filename=d)
            else:
                sys.stderr.write("%s skipped: not an image\n" % d)

    
if __name__ == '__main__':
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    if os.path.isdir(file1):
        diffdirectory(file1, file2)
    else:
        diff = DiffImage(file1, file2)
        printdiff(diff.diff2())
        printdiff(diff.rmsdiff())
