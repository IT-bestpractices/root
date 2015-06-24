#!/usr/bin/env python
# vim: smartindent tabstop=4 shiftwidth=4 expandtab number
#
# This file is part of the Assimilation Project.
#
# Author: Alan Robertson <alanr@unix.sh>
# Copyright (C) 2015 - Assimilation Systems Limited
#
#
# The Assimilation software is free software: you can redistribute it and/or
# modify # it under the terms of the GNU General Public License as published by
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
This module is for reading NIST STIGs and reformatting them in a way
that is consistent with the itbestpractices.info "IT best practices as code"
initiative.
'''
import xmltodict
import os, sys, re, json

def dictfromxml(xmlpath):
    'Read in the XML at *path* and return a dict that corresponds to it'
    with open(xmlpath) as ourfd:
        obj = xmltodict.parse(ourfd.read())
        return obj
    raise ValueError('Cannot parse XML file %s' % xmlpath)

def is_dictlike(thing):
    '''
    Return True if this is a dict or something like a dict
    - used only by print_dictstruct'
    '''
    return (hasattr(thing, 'keys') and hasattr(thing, '__setitem__')
            and hasattr(thing, '__contains__') and hasattr(thing, '__iter__'))

def is_listlike(thing):
    '''Return True if this is a list or something like a list
    - used only by print_dictstruct
    '''
    return hasattr(thing, '__iter__')


def print_dictstruct(thing, prefix=''):
    'Not used: print out the structure of the dict we get from XML'
    if prefix != '':
        print prefix
    if is_dictlike(thing):
        for key in thing:
            print_dictstruct(thing[key], '%s.%s' % (prefix, key))
    elif is_listlike(thing):
        j = 0
        for elem in thing:
            print_dictstruct(elem, '%s[%s]' % (prefix, j))
            j += 1
    else:
        print 'PREFIX:%s TYPE=%s' % (prefix, type(thing))
        if isinstance(thing, (str, unicode)):
            print '................', thing


def stig_rules(thing):
    'Extract the STIG rules from the given dict object'
    return thing['Benchmark']['Group']

VUL_PAT = re.compile(r'\<VulnDiscussion>(.*)\</VulnDiscussion>',
                     re.MULTILINE|re.UNICODE|re.IGNORECASE|re.DOTALL)
def filter_description(desc):
    '''Remove all the cruft that we get from the STIG XML yielding only
    the description.
    '''
    match = VUL_PAT.search(desc)
    if not match:
        return desc
    return match.group(1)


def transform_stig_rule(stigrule):
    '''
    Process a STIG rule yielding a simpler JSON-compatible dict with only
    the stuff we care about...

    Here is some of the information we're interested in:

    @id 'V-58901'
    Rule.@severity 'medium'
    Rule.title 'The sudo command must require authentication.'
    Rule.description '<VulnDiscussion>The 'sudo' ...</VulnDiscussion>
    <FalsePositives></FalsePositives><FalseNegatives></FalseNegatives>
    <Documentable>false</Documentable><Mitigations></Mitigations>
    <SeverityOverrideGuidance></SeverityOverrideGuidance>
    <PotentialImpacts></PotentialImpacts><ThirdPartyTools></ThirdPartyTools>
    <MitigationControl></MitigationControl><Responsibility></Responsibility>
    <IAControls></IAControls>'
    Rule.fixtext.#text 'Update the '/etc/sudoers' or other sudo configuration
    files to remove or comment out lines utilizing the 'NOPASSWD' and
    '!authenticate' options.'
    '''
    return {
        'ruleid': stigrule['@id'],
        'severity': stigrule['Rule']['@severity'],
        'title': stigrule['Rule']['title'],
        'description': filter_description(stigrule['Rule']['description']),
        'fixid': stigrule['Rule']['fixtext']['@fixref'],
        'fix': stigrule['Rule']['fixtext']['#text'],
        'checkid': stigrule['Rule']['check']['@system'],
        'check': stigrule['Rule']['check']['check-content'],
    }

def stig_to_itbestpractices(stig):
    '''
    Convert an STIG recommendation to itbestpractices.info format
    '''
    return {
        'tags': {'nist': [stig['ruleid'], stig['checkid'], stig['fixid']]},
        'severity': stig['severity'],
        'text': {
            'en': {
                'short_description':    stig['title'],
                'long_description':     stig['description'],
                'fix':                  stig['fix'],
                'check':                stig['check'],
            }
        }
    }

def stig_to_itbestpractices_file(dirname, stig):
    '''
    Reformat a STIG recommendation into a file, don't replace if it already
    exists.  Warn (and don't replace) it if the new contents would be different.
    Do nothing silently if the new content is the same as the current content.
    For this purpose we will accept it at this level or up to two levels higher
    in the directory structure
    '''
    if not os.path.isdir(dirname):
        os.system('mkdir -p %s' % dirname)
    contents = json.dumps(stig_to_itbestpractices(stig), sort_keys=True,
                          indent=2, separators=(', ', ': '))
    filename = 'nist_' + stig['ruleid']
    pathname = os.path.join(dirname, filename)
    checkpath = None

    # Look to see if this file already exists at this level or a bit higher up
    if os.path.exists(pathname):
        checkpath = pathname
    else:
        pathup = os.path.join(os.path.basename(dirname), filename)
        if os.path.exists(pathup):
            checkpath = pathup
        else:
            pathup = os.path.join(os.path.dirname(os.path.dirname(dirname)),
                                  filename)
            if os.path.exists(pathup):
                checkpath = pathup
    # See if the current contents is the same as our new version...
    if checkpath is not None:
        with open(checkpath, 'r') as chkf:
            curcontents = chkf.read()
            if curcontents != contents:
                print >> sys.stderr, ('File %s NOT replaced - contents differ'
                                      % checkpath)
                return False
            return True
    with open(pathname, 'w') as openf:
        openf.write(contents)

if __name__ == '__main__':
    def main(pathpairs):
        '''
        Our not-very-bright main program
        '''
        for xmlpath, dirname in pathpairs:
            #print_dictstruct(dictfromxml(path))
            for stigrule in stig_rules(dictfromxml(xmlpath)):
                ourrule = transform_stig_rule(stigrule)
                stig_to_itbestpractices_file(dirname, ourrule)
    XMLPATHS = [('U_RedHat_6_V1R7_STIG/U_RedHat_6_V1R7_Manual-xccdf.xml',
                 '../rules/os.app/security.domain/posix.class/linux.os/redhat'),
               ]
    main(XMLPATHS)
