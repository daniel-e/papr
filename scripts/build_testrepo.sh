#!/bin/bash

N=10

papr init

n=1
for i in $(curl -sq "https://arxiv.org/list/cs/pastweek?show=$N" | perl -ne 'print if s/.*href="\/(abs\/[0-9.]+).*/\1/' | head -n $N); do
	u=https://arxiv.org/$i
	echo $n: $u
	n=$(($n+1))
	papr fetch $u
done
