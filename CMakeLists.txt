# vim: smartindent tabstop=4 shiftwidth=4 expandtab number colorcolumn=100
#
# This file is part of the IT Best Practices Project
#
# Copyright (C) 2016 - Alan Robertson <alanr@unix.sh>
#
#
#   This project relies on these commands during installation:
#
#       getent
#       adduser
#
cmake_minimum_required(VERSION 2.6.4)
project(itbp NONE)
set (BASEVERSION "1.0.0")
#
#	PYBIN		    Where we install our python files
#	USRSHARE		/usr/share - or the equivalent - where we put our best practice JSON files
#	USRSHAREITBP	Our 'itbp' subdirectory under /usr/share (effectively our "database")
#	WEBUSERID		The user id to run the flask program as
#   BPRULESDIR      source directory for our rules
#	

set (CMAKE_INSTALL_PREFIX /usr)
set (USRSHARE ${DESTDIR}${CMAKE_INSTALL_PREFIX}/share)
set (USRSHAREITBP ${USRSHARE}/${PROJECT_NAME})
set (PYBIN ${DESTDIR}${CMAKE_INSTALL_PREFIX}/bin)
set (CONFIGDIR ${DESTDIR}/etc)
set (BPRULESDIR rules)
set (VIEWERDIR tools/viewer)
#
if (NOT WEBUSERID)
    set(WEBUSERID ${PROJECT_NAME})
endif (NOT WEBUSERID)
  
#Totally wrong placeholder comments ;-)
#Probably good to have a 'test' script to run which does everything that needs doing
#makes a temporary directory, does an install, then runs tests - that kind of thing
#
#add_custom_target(tests # ALL
#testify cma.tests -v
#WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
#COMMENT "Make install must be done first. Also, port 1984 must be available (free)" VERBATIM
#)

# Create our user id at install time as part of the CMA component
install (CODE "execute_process ( COMMAND /bin/sh -c \"getent passwd ${WEBUSERID} >/dev/null || adduser --system --no-create-home --shell /bin/false ${WEBUSERID}\" )")

install (DIRECTORY ${BPRULESDIR} DESTINATION ${USRSHAREITBP})
install (FILES ${VIEWERDIR}/itbp.cfg DESTINATION ${CONFIGDIR})
install (PROGRAMS ${VIEWERDIR}/itbp.py DESTINATION ${PYBIN})
