#!/bin/bash

rm -f urls.txt

t=$(mktemp)
curl -sq "https://arxiv.org/list/cs/pastweek?show=100" > $t
for i in $(cat $t | perl -ne 'print if s/.*href="\/(abs\/[0-9.]+).*/\1/' | head -n 100); do 
	echo https://arxiv.org/$i >> urls.txt
done


