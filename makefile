#simple makefile for updating the site.

include config.mk

.SUFFIXES: .md .html

all: sitedata

sitedata: $(CONF) $(HTML)

.md.html:
	$(MARKDOWN) $< > $@
	./html $@

clean:
	rm -f $(HTML)

.PHONY: clean sitedata rebuild puttit
