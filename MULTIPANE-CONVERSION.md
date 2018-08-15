# Outline to convert a static guide to the multipane design:

## 1. Create a multipane branch
Important: do not deliver this to the master branch while testing it because it will affect the guide on openliberty.io before it's polished. https://qa-guides.mybluemix.net/ will clone the branch 'multipane' for testing, and then when all of the guides are converted to the new design we can deliver the changes to master.

## 2. Change the layout from 'guide' to 'guide-multipane'

## 3. Include entire source code files
Add the file includes in the asciidoc for files that you want to appear on the right column, with role="code_column" specified for each file. The files included with role="code_column" will be shown in full screen view while the files included already in the guide will be shown in the mobile/single column view where there is no code column. The code column on the right is exactly 90 characters per line and remains a constant width when resizing the width of the browser, so that the code can be written once and always work. The guide column grows and shrinks according to the width of the browser.

The file name should be provided above the file include. The linenums attribute is important for the hotspots (described below) to work.

----
SystemApplication.java
[source,java,linenums,role='code_column']
-----
 include::finish/src/main/java/io/openliberty/guides/rest/SystemApplication.java[tags=**;!comment]
-----
----

#### Other types of code blocks:
For code blocks that are a command, use role='command':

----
[role="command"]
-----
git clone https://github.com/openliberty/guide-rest-intro.git
cd guide-rest-intro
-----
----

For code blocks that are a command referring to creating the code file on the right, use role='code_command':

----
[role="code_command"]
-----
Create the JAX-RS application class in the src/main/java/io/openliberty/guides/rest/SystemApplication.java file:
-----
----

## 4. Hotspots
Code on the right can be highlighted when hovering over certain "hotspots" in the guide. These hotspots can be just text or also a code command, and can be specified using the role='hotspot'. To specify what lines to highlight when hovering over the hotspot, place highlight_lines=<start line>-<end line> above the block in the asciidoc.

Text hotspot example:
----
highlight_lines=1-12
[role="hotspot"]
-----
EndpointTest.java
-----
----


Code command hotspot example:
----
highlight_lines=1-12
[role="code_command hotspot"]
-----
Edit the `src/main/liberty/config/server.xml` file to update the placeholder text to be:
-----
----

This will highlight the lines 1-12 on the right column when hovering over this block. In mobile view, instead of the code column on the right being shown, these lines will be shown instead (right after where the hotspot is).


## 5. Styling included files
For the Getting started / Maven and other included asciidocs that need to be styled, add [role='command'] above it to style it as a command.
----
-----
[role="command"]
 include::{common-includes}/gitclone.adoc[]
-----
----

## 6. Guide Attribution
Add include::https://raw.githubusercontent.com/OpenLiberty/guides-common/multipane/attribution.adoc[subs="attributes"]
at the bottom of the guide somewhere to include the common guide attribution.

## 7. Related Links section
At the end of the guide, there are various links to different related documentation in the design. These can be specified in a section named "Related Links" in the asciidoc.
----
== Related Links
Dive into the MicroProfile config.

https://github.com/microprofile[See MicroProfile Config specs (GitHub)]

https://openliberty.io/docs/ref/microprofile[Another link to MicroProfile specs (openliberty.io)]
----









