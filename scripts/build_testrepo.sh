#!/bin/bash

PTH=/tmp/repo
N=10
BIN=$PWD/papr/cli.py

rm -rf $PTH
mkdir $PTH
cd $PTH
$BIN init

n=1
for i in $(curl -sq "https://arxiv.org/list/cs/pastweek?show=$N" | perl -ne 'print if s/.*href="\/(abs\/[0-9.]+).*/\1/' | head -n $N); do
	u=https://arxiv.org/$i
	echo $n $u
	n=$(($n+1))
	$BIN fetch $u
done
