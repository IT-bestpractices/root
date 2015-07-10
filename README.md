# root
This is the source code repository for the
<a href="http://itbestpractices.info">_IT best practices_</a> open source project.
Our project collects and curates information about a variety of mechanically-verifiable IT best practices,
with our initial emphasis being on security.
From a security perspective, most of these rules will effectively be _hardening_ rules.
We expect most of our checks to be server related, we are open to security best practices
for other IT devices such as switches and routers.

This effort is in support of _"best practices as code"_ efforts, even though it's
not currently our intent to provide this code as part of this project.

Verifying that a particular practice is followed is typically as simple as checking
to see that a particular feature is turned off or on, or that some value matches
some regular expression.
However _explaining_ these best practices is much more difficult and time-consuming.
It is our intent primarily to collect and curate these bodies of text and leave the
implementation of the checks to the various tools involved
(for example, Lynis and the <a href="http://assimilationsystems.com">Assimilation Project</a>.

This allows us to share the difficult work of explaining these practices,
and avoids arguing about the best method for implementing these checks in
a particular environment might be.

<h2>Our Principles</h2>
Our guiding principles are simple:
 - Create a community and collaborate around collecting _mechanically verifable_ security rules
 - Share freely and with minimal restrictions (Apache 2 or MIT or similar licenses)
 - Curate security rules and provide with basic general guidance on importance.
 - Not responsible for what you our any vendor does with the rules we collect.
 - Stick with simple solutions 
 - We prefer JSON over XML
 - We should be multi-language compatible (even if we don't have any/many translations _yet_).
 - (eventually) Provide our information through a web interface with a well-known URL structure

We expect to collect as much as possible from other public sources. In particular,
the NIST STIGs (named below),
and the <a href="https://github.com/LeamHall/SecComFrame">SecComFrame</a>,
and <a href="https://github.com/CISOfy/lynis">Lynis</a> projects are also good potential sources.

It's worth noting that the Center for Internet Security Benchmarks have a number of checklists,
but they are not freely-available (i.e., they are _"Available to CIS Security Benchmarks Members"_),

The basic idea here is to collect and cross-reference all freely available sources in one
freely-available (FOSS) repository.

Many NIST STIGs are freely available, but some are not publicly available ("Official Use Only").
The NIST National Vulnerability Database lists 9 Tier IV checklists
<https://web.nvd.nist.gov/view/ncp/repository?tier=4&startIndex=0> and
72 Tier III checklists
<https://web.nvd.nist.gov/view/ncp/repository?tier=3&startIndex=0>.

The proposal for this project and an explanation of the directory structure can be found [Here](Proposal.md)

This project will be first presented publicly at the OSCON 2015 conference. More information can be found
<a href="http://assimilationsystems.com/events/oscon-2015/">here</a>.
