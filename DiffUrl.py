# -*- coding: utf-8 -*-
'''
Created on Nov 27, 2012

@author: geraud
'''

import sys
from  DiffImage import DiffImage
import os
import codecs
import uuid
import time
import shutil
import cv

if __name__ == '__main__':
    base1 = sys.argv[1]
    base2 = sys.argv[2]
    urls_file = sys.argv[3]
    output_dir = sys.argv[4]
    
    misc_measures={'CORREL': cv.CV_COMP_CORREL, 'CHISQR': cv.CV_COMP_CHISQR, 'INTERSECT' : cv.CV_COMP_INTERSECT, 'BHATTACHARYYA': cv.CV_COMP_BHATTACHARYYA}
    
    with codecs.open(urls_file, encoding = 'utf-8') as f:
        line = f.readline()
        summary = []

        results = '/'.join([output_dir, 'results'])
        os.makedirs(results)
        shutil.copy('results.css', output_dir)

        with codecs.open('/'.join([output_dir, 'result.html']), mode='w', encoding='utf-8') as result:
            result.write(u'''
            <html>
                <head>
                    <link rel="stylesheet" href="http://code.jquery.com/ui/1.9.2/themes/base/jquery-ui.css" />
                    <script src="http://code.jquery.com/jquery-1.8.3.js"></script>
                    <script src="http://code.jquery.com/ui/1.9.2/jquery-ui.js"></script>
                    <link rel=stylesheet type=text/css href="results.css"/>
                </head>
            <body>''')
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
                diff = DiffImage(url1, url2, prefix=results)
                (filename1, filename2, rms, time1, time2) = diff.rmsdiff()
#                print 'Diff between %s... and %s... : %d' % (url1[0:60],  url2[0:60], rms)
                print 'Diff between %s... and %s... : %d' % (url1,  url2[0:60], rms)
                if rms > 300:
                    classname = 'alert'
                elif rms > 150:
                    classname = 'warning'
                else:
                    classname = 'success'
                lineuuid = uuid.uuid1()
                misc = {}
                for (measure, algo) in misc_measures.items():
                    (_, _, value, _, _) = diff.diff2(algo=algo)
                    misc[measure] = value

                summary.append((name, classname, lineuuid, rms, time1, time2, misc))
                result.write(u'<h1 id="%s" class="%s">%s</h1>' % (lineuuid, classname, name))
                result.write(u'<div id="stats-%s">' %(lineuuid))
                result.write(u'<h3>RMS</h3>')
                result.write(u'<ul><li class="%s">RMS: %d</li></ul>'%(classname,rms))
                
                result.write(u'<h3>Autres stats</h3>')
                result.write(u'<ul>')
                for measure in sorted(misc.keys()):
                    result.write(u'<li class="%s">%s: %f</li>' %('',measure, misc[measure]))
                result.write(u'</ul>')
                result.write(u'<h3>Paramètres</h3>' % lineuuid)
                result.write(u'<ul>')
                for param in params.split('?')[1].split('&'):
                    result.write(u'<li>%s</li>'% param)
                result.write(u'</ul>')

                result.write(u'</div><br/>')

                result.write(u'<div class="cartes">')
                result.write(u'<div class="carte1 carte">')
                result.write(u'<a href="%s" target="_blank"><img src="%s"/></a>' % (url1, filename1.replace(output_dir,'.',1)))
                result.write(u'</div>')
                result.write(u'<div class="carte2 carte">')
                result.write(u'<a href="%s" target="_blank"><img src="%s"/></a>' % (url2, filename2.replace(output_dir,'.',1)))
                result.write(u'</div>')
                result.write(u'</div>')
                result.write(u'<br/>')
                line = f.readline()

            result.write(u'<h1 id="summary">Résumé</h1>')
            result.write(u'<table class="summary"><thead><tr><th>Nom</th><th>Status</th><th>RMS</th><th>Temps ancien <br/>(en ms)</th><th>Temps nouveau <br/>(en ms)</th>')
            for measure in sorted(misc_measures.keys()):
                result.write(u'<th>%s</th>' % measure)

            result.write(u'</tr></thead>')
            result.write(u'<tbody>')
            for (name, classname, lineuuid, rms, time1, time2, misc) in summary:
                result.write(u'<tr><td><a href="#%s">%s</a></td><td class="%s">%s</td><td>%d</td><td>%d</td><td>%d</td>' % (lineuuid, name, classname, classname, rms, time1, time2))
                for measure in sorted(misc.keys()):
                    result.write(u'<td>%f</td>'% misc[measure])
                result.write(u'</tr>')
            result.write(u'</tbody>')
            result.write(u'</table>')

            result.write(u'<script>')
            for (_, _, lineuuid, _, _, _, _) in summary:
                result.write(u'''
                    $( "#stats-%s" ).accordion({
                        collapsible: true,
                        heightStyle: "content",
                    });
                    ''' % lineuuid)
            result.write(u'</script>')

            result.write(u'</body></html>')
            
