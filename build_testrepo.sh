#!/bin/bash


rm -rf repo
mkdir repo
cd repo
../papr/cli.py init


n=1
for i in $(curl -sq 'https://arxiv.org/list/cs/pastweek?show=50' | perl -ne 'print if s/.*href="\/(abs\/[0-9.]+).*/\1/'); do
	u=https://arxiv.org/$i
	echo $n $u
	n=$(($n+1))
	../papr/cli.py fetch $u
done

exit 0


for i in 1812.06081 1812.06080 1812.06071 1812.06061 1812.06060 1812.06055 1812.06051 1812.06050 1812.06038; do
	../papr/cli.py fetch https://arxiv.org/abs/$i
done
