xml2rfc ?= xml2rfc -v
kramdown-rfc2629 ?= kramdown-rfc2629
idnits ?= idnits

draft := draft-ietf-rtcweb-jsep

current_ver := $(shell git tag | grep "$(draft)" | tail -1 | sed -e"s/.*-//")
ifeq "${current_ver}" ""
next_ver ?= 00
else
next_ver ?= $(shell printf "%.2d" $$((1$(current_ver)-99)))
endif
next := $(draft)-$(next_ver)

.PHONY: latest submit clean

latest: $(draft).txt $(draft).html

submit: $(next).txt

idnits: $(next).txt
	$(idnits) $<

diff:  $(draft).diff.html

clean:
	-rm -f $(draft).txt $(draft).raw $(draft).old.raw $(draft).html
	-rm -f $(next).txt $(next).raw $(next).html
	-rm -f $(draft)-[0-9][0-9].xml


$(next).xml: $(draft).xml
	sed -e"s/$(basename $<)-latest/$(basename $@)/" $< > $@

#%.xml: %.md
#	$(kramdown-rfc2629) $< > $@

%.txt: %.xml
	$(xml2rfc) $< --text --out $@

%.raw: %.xml
	$(xml2rfc) $< --raw --out $@

%.html: %.xml
	$(xml2rfc) $< --html --out $@

$(draft).diff.html: $(draft).old.raw $(draft).raw 
	htmlwdiff  $^ >  $@

upload: $(draft).html $(draft).txt
	python upload-draft.py $(draft).html
