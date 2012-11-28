# -*- coding: utf-8 -*-
'''
Created on Nov 27, 2012

@author: geraud
'''

import sys
from  DiffImage import rmsdiff
import os
import codecs
import uuid

if __name__ == '__main__':
    base1 = sys.argv[1]
    base2 = sys.argv[2]
    urls_file = sys.argv[3]
    
    with codecs.open(urls_file, encoding = 'utf-8') as f:
        line = f.readline()
        summary = []

        with codecs.open('result.html', mode='w', encoding='utf-8') as result:
            result.write('<html><head><link rel=stylesheet type=text/css href="results.css"/></head><body>')
            result.write('<div class="notice"><ul><li>A gauche : %s</li>' % base1);
            result.write('<li>A droite : %s</li></ul></div>' % base2);
            while line:
                url = line.split(';')[0].strip('"')
                name = line.split(';')[1].strip('\n').strip('"')
                
                results = '/'.join(['results', name])
                os.makedirs(results)
                
                params = '&'.join([url.strip('"'), 'idCalques=1'])
                url1 = '/'.join([base1, params]) 
                url2 = '/'.join([base2, params])
                (filename1, filename2, rms, time1, time2) = rmsdiff(url1, url2, prefix=results)
                print 'Diff between %s... and %s... : %d' % (url1[0:60],  url2[0:60], rms)
                if rms > 500:
                    classname = 'alert'
                elif rms > 200:
                    classname = 'warning'
                else:
                    classname = 'success'
                lineuuid = uuid.uuid1()
                summary.append((name, classname, lineuuid, rms, time1, time2))
                result.write('<h1 id="%s" class="%s">%s</h1>' % (lineuuid, classname, name))
                result.write('<span id="rms" class="%s">RMS: %d</span>' %(classname,rms))
                result.write('<div class="cartes">')
                result.write('<div class="carte1 carte">')
                result.write('<a href="%s" target="_blank"><img src="%s"/></a>' % (url1, filename1))
                result.write('</div>')
                result.write('<div class="carte2 carte">')
                result.write('<a href="%s" target="_blank"><img src="%s"/></a>' % (url2, filename2))
                result.write('</div>')
                result.write('</div>')
                result.write('<div class="params"><ul>')
                for param in params.split('?')[1].split('&'):
                    result.write('<li>%s</li>'% param)
                result.write('</ul></div>')
                result.write('<br/>')
                line = f.readline()

            result.write(u'<h1 id="summary">Résumé</h1>')
            result.write('<table class="summary"><thead><tr><th>Nom</th><th>Status</th><th>RMS</th><th>Temps ancien <br/>(en ms)</th><th>Temps nouveau <br/>(en ms)</th></tr></thead>')
            result.write('<tbody>')
            for (name, classname, lineuuid, rms, time1, time2) in summary:
                result.write('<tr><td><a href="#%s">%s</a></td><td class="%s">%s</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (lineuuid, name, classname, classname, rms, time1, time2))
            result.write('</tbody>')
            result.write('</table>')
            result.write('</body></html>')
            