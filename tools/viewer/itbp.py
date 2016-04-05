#!/usr/bin/python
# vim: smartindent tabstop=4 shiftwidth=4 expandtab number colorcolumn=80
#
# This file is part of the IT Best Practices project and was derived
# from a file which is part of the Assimilation Project.
#
# Author: Emily Ratliff <eratliff@linuxfoundation.org>
# Author: Alan Robertson <alanr@unix.sh>
# Copyright (C) 2015 - Emily Ratliff
#
#
# The Assimilation software is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The Assimilation software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the Assimilation Project software.
# If not, see http://www.gnu.org/licenses/
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
ITBP_PATH = '../../../root/rules'
ITBP_PATH = '/usr/share/itbp/v1.0/root/rules'
HOST = '127.0.0.1:5000'

class RuleSetDb(object):
    '''
    This class represents a set of rules and a lookup function for selecting
    a rule file based on how well the particular rule matches the given
    selection criteria.

    We're OK with conflicts as long as it's the best match.

    Might not be the best choice right now, but since at the moment there are
    no conflicts, it's probably just fine too ;-).
    '''
    def __init__(self, rootdir):
        '''Create an in-memory database of all the rule names and paths
        The memory for each directory name only occurs once with a potentially
        large reference count for all the rules that occur in a single
        directory. This is probably as good as its going to get and probably
        in practice no more memory than a database needs for its cache
        memory - at least as long as we have not more than tens of thousands
        of rules in the worst case.
        '''
        self.rulesets = {}
        rootchoplen = len(rootdir)+1
        for tuple in os.walk(rootdir, followlinks=True):
            dirpath, _dirnames, rulenames = tuple
            relpath = dirpath[rootchoplen:]
            for rule in rulenames:
                if rule not in self.rulesets:
                    self.rulesets[rule] = []
                self.rulesets[rule].append(relpath.lower())

    @staticmethod
    def _dir_attrs(dirname):
        'Transform a directory name into attribute name/value pairs'
        attrs = {}
        dirs = dirname.split('/')
        for dirname in dirs:
            (prefix, suffix) = os.path.splitext(dirname)
            if suffix != '':
                attrs[suffix] = prefix.lower()
            # The last two components may be osname (like redhat) and release
            elif 'osname' not in attrs:
                attrs['osname'] = prefix.lower()
            elif 'release' not in attrs:
                attrs['release'] = prefix.lower()
        return attrs

    @staticmethod
    def _match_score(dirname, attrs):
        'Return a score of how many attributes match'
        dirattrs = RuleSetDb._dir_attrs(dirname)
        score = 0
        for attr in attrs:
            if attr in dirattrs and dirattrs[attr] == attrs[attr]:
                score += 1
        return score

    def select_rule(self, attributes):
        'Figure out which rule best-matches the requested rule attributes'
        if 'tipname' not in attributes:
            return None
        tipname = attributes['tipname']
        if tipname not in self.rulesets:
            return None
        tiplist = self.rulesets[tipname]
        resultlist = {}
        best_score = -1
        best_name = None
        for dirname in tiplist:
            score = self._match_score(dirname, attributes)
            if score > best_score:
                best_name = dirname
                best_score = score
        return os.path.join(best_name, tipname)


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('ITBP_SETTINGS', silent=True)
ruledb = RuleSetDb(app.config['ITBP_PATH'])
ruledb = RuleSetDb('../../../root/rules')

def validate_params(queryparms):
    '''Parse the input query to find the path
    Release and osname are optional components in the path
    osname, tipname, and release don't have postfixes
    tipname can have capitals
    I trust ITBP_PATH since it is set by the person running the server.'''
    safeparms = {}
    for name in queryparms:
        safename = secure_filename(name)
        safeparms[safename] = secure_filename(queryparms.get(name))
        if safename != 'tipname':
            safeparms[safename] = safeparms[safename].lower()
    #print safeparms
    response_path = ruledb.select_rule(safeparms)
    if response_path is None:
        return None
    #print response_path
    response_path = os.path.join(app.config['ITBP_PATH'], response_path)

    return response_path

@app.route('/')
def hello_world():
    'Render an IT Best Practices query form'
    return render_template('itbpqueryform.html')

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

ttpat=re.compile('^<br>([#$] .*)$', re.MULTILINE)
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
    They all return apparent success, just very simple HTML.
    We are currently restricted to showing one tip per HTML request.
    '''
    itbpfilename = validate_params(request.args)
    if itbpfilename is None or not os.path.isfile(itbpfilename):
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
