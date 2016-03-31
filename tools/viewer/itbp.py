#!/usr/bin/python
# vim: smartindent tabstop=4 shiftwidth=4 expandtab number colorcolumn=100
#
# This file is part of the IT Best Practices project and was derived
# from a file which is part of the Assimilation Project.
#
# Author: Emily Ratliff <eratliff@linuxfoundation.org>
# Author: Alan Robertson <alanr@unix.sh>
# Copyright (C) 2015 - Emily Ratliff
#
#
# The Assimilation software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The Assimilation software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the Assimilation Project software.  If not, see http://www.gnu.org/licenses/
#
#
'''
Prototype code for providing a REST interface for the IT Best Practices project.
'''
import sys
import os, os.path
import re
sys.path.append('..')
from flask import Flask, request, render_template, json, Response, abort
from werkzeug.utils import secure_filename

#configuration
DEBUG = False
TESTING = False
ITBP_PATH = '/usr/share/itbp/v1.0/root/rules'
HOST = '127.0.0.1:5000'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('ITBP_SETTINGS', silent=True)

def validate_params(queryparms):
    '''Parse the input query to find the path
    Release and osname are optional components in the path
    osname, tipname, and release don't have postfixes
    tipname can have capitals
    I trust ITBP_PATH since it is set by the person running the server'''
    app_path = secure_filename(queryparms.get('app', '').lower()) + '.app'
    domain_path = secure_filename(queryparms.get('domain', '').lower()) + '.domain'
    class_path = secure_filename(queryparms.get('class', '').lower()) + '.class'
    os_path = secure_filename(queryparms.get('os', '').lower()) + '.os'
    osname_path = secure_filename(queryparms.get('osname', '').lower())
    release_path = secure_filename(queryparms.get('release', '').lower())
    tipname_path = secure_filename(queryparms.get('tipname', ''))
    response_path = os.path.join(app_path, domain_path, class_path, os_path)
    if not osname_path == "":
        response_path = os.path.join(response_path, osname_path)
    if not release_path == "":
        response_path = os.path.join(response_path, release_path)
    temp_path = os.path.join(response_path, tipname_path)
    response_path = os.path.normpath(temp_path)
    response_path = os.path.join(app.config['ITBP_PATH'], response_path)

    return response_path

@app.route('/')
def hello_world():
    'Dummy code for printing a static string on the root (/) page'
    return 'Nothing to see here... Move along!'

@app.route('/itbp/v1.0/querymeta', methods=['GET'])
def query_meta():
    '''Dummy code for testing the filename composition code'''
    response_path = validate_params(request.args)
    return 'Hello Query Metadata Path: "%s"!'  % response_path

@app.route('/itbp/v1.0/showjson', methods=['GET'])
def showjson():
    '''Prototype code for requestion the JSON of a particular best practice.
    The error cases are not handled correctly yet.
    Open question - do we want to limit the size of the file that we show?
    '''
    itbpfilename = validate_params(request.args)
    if not os.path.isfile(itbpfilename):
        abort(404)
    tipfile = open(itbpfilename, 'r')
    dat = tipfile.read()
    tipfile.close()
    resp = Response(response=dat, status=200, mimetype='application/json')
    return resp

ttpat=re.compile('^<br>(#.*)$', re.MULTILINE)
def html_transform(dobj):
    '''Transform the dict-like object into a more html-friendly form'''
    for key in dobj:
        if key in ('tags'):
            continue
        val = dobj[key]
        if isinstance(val, (str, unicode)):
           if key in ('check', 'fix', 'long_description'):
                val = val.replace('\n', '\n<br>')
                val = ttpat.sub(r'<br><tt>\1</tt>', val)
                dobj[key] = val
        else:
            html_transform(dobj[key])
        
    

@app.route('/itbp/v1.0/show', methods=['GET'])
def show():
    '''Prototype code for showing a human readable HTML rendention
    of and IT Best Practices criteria.
    They all return apparent success, just very poor HTML.
    '''
    itbpfilename = validate_params(request.args)
    if not os.path.isfile(itbpfilename):
        abort(404)
    (startpath, tipfilename) = os.path.split(itbpfilename)
    tipfile = open(itbpfilename, 'r')
    dat = tipfile.read()
    tipfile.close()
    new_obj = json.loads(dat)
    html_transform(new_obj)
    sev = new_obj['severity']
    tiptext = new_obj['text']
    entiptext = tiptext['en']
    shortdesc = entiptext['short_description']
    longdesc = entiptext['long_description']
    fixdesc = entiptext['fix']
    checkdesc = entiptext['check']

    return render_template('tip.html', severity=sev, tipname=tipfilename,
                           shorttiptext=shortdesc, longtiptext=longdesc,
                           checktiptext=checkdesc, fixtiptext=fixdesc)

if __name__ == '__main__':

    app.run(host='0.0.0.0')
