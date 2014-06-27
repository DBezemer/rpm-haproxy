#!/bin/sh

if [ -e "SOURCES/$1" ]
  then echo "SOURCES/$1 present, skipping download"
else
  ( cd SOURCES/ && wget $2 -O $1 )
fi
