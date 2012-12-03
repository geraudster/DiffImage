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
import time
import shutil

if __name__ == '__main__':
    base1 = sys.argv[1]
    base2 = sys.argv[2]
    urls_file = sys.argv[3]
    output_dir = sys.argv[4]
    
    with codecs.open(urls_file, encoding = 'utf-8') as f:
        line = f.readline()
        summary = []

        results = '/'.join([output_dir, 'results'])
        os.makedirs(results)
        shutil.copy('results.css', output_dir)

        with codecs.open('/'.join([output_dir, 'result.html']), mode='w', encoding='utf-8') as result:
            result.write(u'<html><head><link rel=stylesheet type=text/css href="results.css"/></head><body>')
            result.write(u'<div class="generated">Généré le %s</div>' % time.strftime('%d/%m/%y %H:%M'))
            result.write(u'<div class="notice"><ul><li>A gauche : %s</li>' % base1)
            result.write(u'<li>A droite : %s</li></ul></div>' % base2)
            while line:
                url = line.split(';')[0].strip('"')
                name = line.split(';')[1].strip('\n').strip('"')
                
                results = '/'.join([output_dir, 'results', name])
                os.makedirs(results)
                
                params = '&'.join([url.strip('"'), 'idCalques=1'])
                url1 = '/'.join([base1, params])
                url2 = '/'.join([base2, params])
                (filename1, filename2, rms, time1, time2) = rmsdiff(url1, url2, prefix=results)
#                print 'Diff between %s... and %s... : %d' % (url1[0:60],  url2[0:60], rms)
                print 'Diff between %s... and %s... : %d' % (url1,  url2[0:60], rms)
                if rms > 300:
                    classname = 'alert'
                elif rms > 150:
                    classname = 'warning'
                else:
                    classname = 'success'
                lineuuid = uuid.uuid1()
                summary.append((name, classname, lineuuid, rms, time1, time2))
                result.write(u'<h1 id="%s" class="%s">%s</h1>' % (lineuuid, classname, name))
                result.write(u'<span id="rms" class="%s">RMS: %d</span>' %(classname,rms))
                result.write(u'<div class="cartes">')
                result.write(u'<div class="carte1 carte">')
                result.write(u'<a href="%s" target="_blank"><img src="%s"/></a>' % (url1, filename1.replace(output_dir,'.',1)))
                result.write(u'</div>')
                result.write(u'<div class="carte2 carte">')
                result.write(u'<a href="%s" target="_blank"><img src="%s"/></a>' % (url2, filename2.replace(output_dir,'.',1)))
                result.write(u'</div>')
                result.write(u'</div>')
                result.write(u'<div class="params"><ul>')
                for param in params.split('?')[1].split('&'):
                    result.write(u'<li>%s</li>'% param)
                result.write(u'</ul></div>')
                result.write(u'<br/>')
                line = f.readline()

            result.write(u'<h1 id="summary">Résumé</h1>')
            result.write(u'<table class="summary"><thead><tr><th>Nom</th><th>Status</th><th>RMS</th><th>Temps ancien <br/>(en ms)</th><th>Temps nouveau <br/>(en ms)</th></tr></thead>')
            result.write(u'<tbody>')
            for (name, classname, lineuuid, rms, time1, time2) in summary:
                result.write(u'<tr><td><a href="#%s">%s</a></td><td class="%s">%s</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (lineuuid, name, classname, classname, rms, time1, time2))
            result.write(u'</tbody>')
            result.write(u'</table>')
            result.write(u'</body></html>')
            
