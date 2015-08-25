#Introduction
This is a proposal for creating a useful common shared best practice recommendations database.  Although our primary emphasis is security, the database is structured to accommodate a variety of domains of best practices.  Possible additional best-practice domains include networking, performance and availability.  It is noteworthy that we are primarily interested in best practices which can be automatically verified - allowing associated vendors to translate these best practices to code.  This database is a key portion of our common “best practices as code” effort.  Because there are a variety of ways of ensuring compliance with these best practices, this database does not contain the details of exactly how one might best verify compliance with these best practices.  Instead we describe the constraint and remedy in text, and leave the implementation details to the individual platforms.


This proposal is being sent out for comments, and is subject to change.
#General Outline
The idea here is to be able to share certain information about best practices in a way which is helpful to end-users.  Here are a few of the design goals of this effort:
* Data will be available to end users via a web server.
* Each collection of data for a given best practice recommendation will have a unique identifier.  A given best practice might have different descriptions for different operating systems, but any given best practice recommendation will have exactly one identifier.
* Multi-language support
It is a requirement that the structure supports multiple languages. Although not every piece of text will be available in multiple languages, it is necessary that the structure we create supports multiple languages.  All text data is encoded in UTF8, which allows for any source language while minimizing the complexity of the implementation.
* More generic and more specific versions of best practice texts are available for various operating systems and distributions.  The web interface will allow the specification of attributes such as operating system, version, and language and it will select the closest available version of the desired text.
* Recommendations will be able to be tagged with external identifiers for the various external agencies which make the same recommendation.
Web Server
Directory and Data structure
The project directory structure is designed to ease management of the body of recommendations and facilitate the work of the web server.  The proposed directory structure is outlined in the next subsection.
Directory Structure
In general, the recommendation data structure is proposed to look something like this:

   * ``<top-level-directory>``
     *  ``<application-name>``.app
       * ``<recommendation-domain>``.domain
         * ``<os-class>``.class (for example posix.class or windows.class)
           * ``<os-type>``.os
            * ``<distribution (if applicable>``.distro
              * ``<optional-major-release-version-level>``.rel

Recommendations potentially exist at any level in the tree below the <recommendation-domain> level.  The web server would take the supplied set of attributes - and return the information which is the closest and most complete match to the request.


For this directory structure, it is expected that the information for a particular security identifier would be normally placed as high in the tree as possible.  Versions should only be placed lower in the tree if the text explaining the recommendation or its remedy differs significantly.


##An example
If a request specified app=os,os=linux,distro=redhat,release=6,id=42,domain=security and the following files existed:
 * security.domain/os.app/posix.class/42.json
 * security.domain/os.app/posix.class/linux.os/42.json
 * security.domain/os.app/posix.class/linux.os/redhat.distro/42.json
The web application would return the information from the file security.domain/os.app/posix.class/linux.os/redhat.distro/42.json.  If the same request was made substituting distro=suse,release=11, then the information found in security.domain/os.app/posix.class/linux.os/42.json would be returned instead.  If this same request was made with os=aix,release=7, then the information found in security.domain/os.app/posix.class/42.json would be returned.
#Proposed File Contents
Each file is named according to a unique identifier for this particular recommendation.  Each file contains up to three different kinds of data:
 * Explanation of the recommendation, how to tell if it’s complied with, and the potential consequences of not being in compliance.
 * Description of how to come into compliance with the recommendation.
 * External tags - references to outside sources which make the same recommendation.
Each file is a valid JSON string.  The first two kinds of fields are also tagged by language.  A sample of this JSON structure follows:


```
{        “tags”: {“cce”: [“12345-6”], “nist”: [“au-9”, “au-11”]},
“text”: {
    “en”: {
        “recommendation”:
                “<tt>/</tt> should be mode 0755”,
        “remedy”:
                “do this <i>as root</i>: <tt>chmod 0755 /</tt>”
    },
    “es”: {
        “recommendation”:
                “<tt>/</tt> debe ser modo 0755”,
        “remedy”:
                “hacerlo <i>como usuario “root”</i>: <tt>chmod 0755 /</tt>”
            }
        }
}
```

#Validation Applications
As tools (like Lynis or Assimilation) validate best practice compliance, they can direct their users to the bestpracticerecommendations.org site to provide them with the information they need to properly understand the recommended best practices and bring their systems into compliance.
Support Infrastructure
We anticipate establishing a github project to host these files, and a web server to serve the data as described.  Towards this end, we have acquired the bestpracticerecommendations.org and bestpracticerecommendations.info and itbestpractices.info domains.  Sadly, most of the obvious variants of bestpractices.org were already taken.  My current thinking is that we’ll advertise only the itbestpractices.info domain, and let the others lapse.


#Open Issues
Application-specific recommendations
It’s clear that different applications will likely have application-specific recommendations, and that we need to support these, and distinguish them from the more general OS-specific recommendations.  For example, it makes sense to categorize specific recommendations for WordPress, for Apache, for nginx, and so on rather than simply having them be all lumped together.
