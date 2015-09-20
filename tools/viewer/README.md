# IT Best Practices Viewer

This is a simple IT Best Practices viewer written in Python using Flask.
It takes parameterized URLs and constructs a filesystem path from
the request input strings. It outputs either the straight JSON or
pretty printed HTML.

The HTML generated is very rudimentary for now and just demonstrates what
can be done.

The request URLs are of the form
http://127.0.0.1:5000/itbp/v1.0/show?app=os&domain=security&class=posix&os=linux&osname=redhat&tipname=nist_V-57569

# Parameters
The parameters match the file system hierarchy implemented in the IT Best
Practices Rules.
Require parameters include
* app
* domain
* class
* os
* tipname

Optional parameters include
* release (currently unused)
* osname 

# Configuration
The path to the IT Best Practices rules can be set in the itbp.cfg file which
is signalled to the program by setting the ITBP_SETTINGS environment variable.

# APIs Implemented
*show displays the pretty printed HTML output.
*showjson returns the file contents which are assumed to be JSON.

# User stories implemented in this prototype
* I am a system administrator and I want to view the Best Practice in a readable format. I was given the URL by a tool.
* I am a tool and I want to retrieve the raw JSON of a particular Best Practice. I was given the URL by a tool or I generated it myself.

# User story requested but not yet implemented
* I am a system administrator and I want to view one of the best practices by the tag that was shared with my by another system administrator.

# Input Sanitization
The path is constructed out of arguments passed in by the user. Most of these
elements are lowercased, secure_filename is used to sanitize the component 
pieces. normpath is used to normalize the constructed relative path which
is then joined to the path provided by the configuration. 

Input is requested on whether this is sufficient sanitization. 

If the file does not exist, an error is returned. The file is opened read only. 
Typically, the viewer runs as a normal user and only files in the configured 
path will be returned, so sensitive information will not be exposed if the 
user uses the default configuration or configures another path properly.
