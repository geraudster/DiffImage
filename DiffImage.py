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

MODE="RGBA"

def printdiff(value, filename=None):
    if filename:
        print  "RMS %s: %s" % (filename, value)
    else:
        print  value

def _getUrlContent(url, filename=None, buffer_size=1024):
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

def getimage(filename, suffix, prefix=u'.'):
    elapsed_time = 0
    if filename.startswith('http://'):
        try:
            # By default
            realfilename = '/'.join([prefix, 'failed.png'])
            
            start_time = datetime.now()
            retrfilename = _getUrlContent(filename) 

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
                realfilename = _getUrlContent(r.attrib['src'], filename=realfilename)
                
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
    return (realfilename, Image.open(realfilename), elapsed_time)
    
def rmsdiff(file1, file2, prefix='.'):
    "Calculate the root-mean-square difference between two images"
    (filename1, im1, time1) = getimage(file1, '1', prefix)
    (filename2, im2, time2) = getimage(file2, '2', prefix)
    h1 = im1.convert(MODE).histogram()
    h2 = im2.convert(MODE).histogram()

    rms = math.sqrt(reduce(operator.add,
                    map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1))
    return (filename1, filename2, rms, time1, time2)

def diffdirectory(dir1, dir2):
    for d in os.listdir(dir1):
        fullpath = '/'.join([dir1, d])
        if os.path.isdir(fullpath):
            diffdirectory(fullpath, '/'.join([dir2, d]))
        else:
            filetype = magic.from_file(fullpath, mime=True)
            if filetype.startswith('image'):
                printdiff(rmsdiff(fullpath, '/'.join([dir2, d])), filename=d)
            else:
                sys.stderr.write("%s skipped: not an image\n" % d)

    
if __name__ == '__main__':
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    if os.path.isdir(file1):
        diffdirectory(file1, file2)
    else:
        printdiff(rmsdiff(file1, file2))
