We don't have access to the legacy databases or filesystems. This
directory contains a script for scraping CompanionSite pages that were
obtained from a wget command.

Directory Structure
-------------------

site_scrapes/
    contains site.do files copied from www.runmycode.org/CompanionSite/site.do?siteId=*
    from running this wget:
    wget -m -olog --random-wait --save-headers http://www.runmycode.org

extractcontent.py
    a python script that runs over the site.do files and extracts
    resulting site metadata in to a file called results.json
