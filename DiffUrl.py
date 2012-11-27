# -*- coding: utf-8 -*-
'''
Created on Nov 27, 2012

@author: geraud
'''

import sys
from  DiffImage import printdiff, rmsdiff
import shutil
import os
from string import maketrans
import codecs

if __name__ == '__main__':
    base1 = sys.argv[1]
    base2 = sys.argv[2]
    urls_file = sys.argv[3]
    
    with codecs.open(urls_file, encoding = 'utf-8') as f:
        line = f.readline()
        
        with codecs.open('result.html', mode='w', encoding='utf-8') as result:
            result.write('<html><head><link rel=stylesheet type=text/css href="results.css"/></head><body>')
            while line:
                url = line.split(';')[0].strip('"')
                name = line.split(';')[1].strip('\n').strip('"')
                
                results = '/'.join(['results', name])
                os.makedirs(results)
                url1 = '&'.join(['/'.join([base1, url.strip('"')]), 'idCalques=1']) 
                url2 = '&'.join(['/'.join([base2, url.strip('"')]), 'idCalques=1'])
                (filename1, filename2, rms) = rmsdiff(url1, url2, prefix=results)
                print 'Diff between %s... and %s... : %d' % (url1[0:60],  url2[0:60], rms)
                result.write('<h1>%s</h1>' % name)
                result.write('<span id="rms">RMS: %d</span>' %rms)
                result.write('<div class="cartes">')
                result.write('<div class="carte1">')
                result.write('<a href="%s"><img src="%s"/></a>' % (url1, filename1))
                result.write('</div>')
                result.write('<div class="carte2">')
                result.write('<a href="%s"><img src="%s"/></a>' % (url2, filename2))
                result.write('</div>')
                result.write('</div>')
                result.write('<br/>')
                line = f.readline()

            result.write('</body></html>')
            