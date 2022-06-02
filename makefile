#simple makefile for updating the site.

include config.mk

.SUFFIXES: .md .html

all: sitedata

total: sitedata puttit

sitedata: $(CONF) $(HTML)

.md.html:
	$(MARKDOWN) $< > $@
	./html $@

rebuild:
	make -C code/

puttit: rebuild
	make -C code/ puttit

clean:
	rm -f $(HTML)
	make -C code/ clean

.PHONY: clean sitedata rebuild puttit
