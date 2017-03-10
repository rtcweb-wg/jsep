#!/bin/bash

# HTMLTidy cleans up the XML according to tidy.config, but also strips
# newlines between <t> tags, spaces after <xref> tags, and adds trailing
# whitespace. So, we postprocess accordingly.
tidy -config tidy.config < draft-ietf-rtcweb-jsep.xml \
                         | perl -pe 's/(.*<t>)/\n$1/' \
                         | sed -e "s/\(<\/xref>\)\([a-zA-Z\(]\)/\1 \2/g" \
                         | sed -e "s/\(<xref .*\/>\)\([a-zA-Z\(]\)/\1 \2/g" \
                         | sed -e "s/ *$//" \
                         > foo.xml
mv foo.xml draft-ietf-rtcweb-jsep.xml
