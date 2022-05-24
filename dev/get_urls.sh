#!/bin/bash

N=30

rm -f urls.txt

n=1
for i in $(curl -sq "https://arxiv.org/list/cs/pastweek?show=$N" | perl -ne 'print if s/.*href="\/(abs\/[0-9.]+).*/\1/' | head -n $N); do
	u=https://arxiv.org/$i
	echo $u >> urls.txt
done
