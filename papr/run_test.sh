#!/bin/bash

# Test config.
./papr/tests.py

# =============================================================================================
# 1) Test "papr init"
# =============================================================================================

#a) check that a repository is created in a directory which is not a repository yet
mkdir /tmp/repo
cd /tmp/repo
r=$(papr init)
if [ "$r" != "Repository created." ]; then
    echo "error 1.a: got $r"
    exit 1
else
    echo "ok 1.a"
fi

#b) check that the default repository is set to the current repository
r=$(cat ~/.papr/papr.cfg  | jq -r .default_repo)
if [ "$r" != "/tmp/repo" ]; then
    echo "error 1.b: got $r"
    exit 1
else
    echo "ok 1.b"
fi

#c) check that a repository cannot be created in a directory which already is a repository
r=$(papr init 2>&1)
if [ "$r" != "You are already in a repository." ]; then
    echo "error 1.c: got $r"
    exit 1
else
    echo "ok 1.c"
fi

#./scripts/build_testrepo.sh
