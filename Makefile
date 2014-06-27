HOME=$(shell pwd)
VERSION=1.5.1
RELEASE=1

all: build

clean:
	rm -rf ./rpmbuild
	mkdir -p ./rpmbuild/SPECS/ ./rpmbuild/SOURCES/

download-upstream:
	./download haproxy-${VERSION}.tar.gz http://www.haproxy.org/download/1.5/src/haproxy-${VERSION}.tar.gz

build: clean download-upstream
	cp -r ./SPECS/* ./rpmbuild/SPECS/
	cp -r ./SOURCES/* ./rpmbuild/SOURCES/
	rpmbuild -ba SPECS/haproxy.spec \
	--define "ver ${VERSION}" \
	--define "rel ${RELEASE}" \
	--define "_topdir %(pwd)/rpmbuild" \
    --define "_builddir %{_topdir}" \
    --define "_rpmdir %{_topdir}" \
    --define "_srcrpmdir %{_topdir}" \
