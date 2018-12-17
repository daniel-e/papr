#!/bin/bash


rm -rf repo
mkdir repo
cd repo
../paper.py init
cp ../testdata/*.pdf .
for i in *.pdf; do 
	echo $i
	../paper.py add $i
done

