info:
	@echo "pypi 		-- uplod to python package index"
	@echo "builddeb		-- build debian (ubuntu 14.04) package"
	@echo "ppa-dev          -- upload to ppa development repo"
	@echo "ppa		-- upload to ppa release repo"

VERSION=1.2.2

pypi:
	python setup.py sdist upload

clean:
	find . -name \*.pyc -exec rm {} \;
	rm -fr build/
	rm -fr dist/
	rm -fr DEBUILD

debianize:
	make clean
	mkdir -p DEBUILD/privacyideaadm.org
	cp -r * DEBUILD/privacyideaadm.org || true
	cp LICENSE DEBUILD/privacyideaadm.org/debian/copyright
	(cd DEBUILD; tar -zcf privacyideaadm_${VERSION}.orig.tar.gz --exclude=privacyideaadm.org/debian  privacyideaadm.org)

builddeb:
	make debianize
	(cd DEBUILD/privacyideaadm.org; debuild)

ppa-dev:
	make debianize
	(cd DEBUILD/privacyideaadm.org; debuild -S)
	# Upload to launchpad:
	dput ppa:privacyidea/privacyidea-dev DEBUILD/privacyideaadm_${VERSION}-?_source.changes

ppa:
	make debianize
	(cd DEBUILD/privacyideaadm.org; debuild -S)
	dput ppa:privacyidea/privacyidea DEBUILD/privacyideaadm_${VERSION}-?_source.changes
