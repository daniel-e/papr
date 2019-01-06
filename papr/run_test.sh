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

#c) check that the repository is empty
r=$(papr)
if [ "$r" != "Repository is empty." ]; then
    echo "error 1.c: got $r"
    exit 1
else
    echo "ok 1.c"
fi

#d) check that a repository cannot be created in a directory which already is a repository
r=$(papr init 2>&1)
if [ "$r" != "You are already in a repository." ]; then
    echo "error 1.d: got $r"
    exit 1
else
    echo "ok 1.d"
fi

# =============================================================================================
# 2) Test "papr default"
# =============================================================================================

rm -rf /tmp/repo /tmp/repo2
mkdir /tmp/repo /tmp/repo2
cd /tmp/repo

#a) papr default should fail because we are not in a local repository
r=$(papr default)
if [ "$r" != "You are not in a repository." ]; then
    echo "error 2.a: got $r"
    exit 1
else
    echo "ok 2.a"
fi

papr init >/dev/null

#b) check that the default repository is /tmp/repo
r=$(cat ~/.papr/papr.cfg  | jq -r .default_repo)
if [ "$r" != "/tmp/repo" ]; then
    echo "error 2.b: got $r"
    exit 1
else
    echo "ok 2.b"
fi

cd /tmp/repo2
papr init > /dev/null

#c) check that the default repository is /tmp/repo2
r=$(cat ~/.papr/papr.cfg  | jq -r .default_repo)
if [ "$r" != "/tmp/repo2" ]; then
    echo "error 2.c: got $r"
    exit 1
else
    echo "ok 2.c"
fi

cd /tmp/repo
papr default > /dev/null

#d) check that the default repository is /tmp/repo again
r=$(cat ~/.papr/papr.cfg  | jq -r .default_repo)
if [ "$r" != "/tmp/repo" ]; then
    echo "error 2.d: got $r"
    exit 1
else
    echo "ok 2.d"
fi

# =============================================================================================
# 3) Test "papr fetch"
# =============================================================================================

#a) check that filename or URL is given as argument
r=$(papr fetch)
if [ "$r" != "You need to specify a filename or URL." ]; then
    echo "error 3.a: got $r"
    exit 1
else
    echo "ok 3.a"
fi

#b) check that a title is specified when an existing file is given
r=$(papr fetch /root/papr/data/paper1.pdf)
if [ "$r" != "For local files you need to specify the title of the paper." ]; then
    echo "error 3.b: got $r"
    exit 1
else
    echo "ok 3.b"
fi

#c) check response that paper was added
r=$(papr fetch /root/papr/data/paper1.pdf "Foo bar" | head -n 1)
if [ "$r" != "Added paper." ]; then
    echo "error 3.c: got $r"
    exit 1
else
    echo "ok 3.c"
fi

#d) check response for download via arXiv
papr fetch https://arxiv.org/abs/1901.00842 > /tmp/output.txt
r=$(cat /tmp/output.txt | grep "Added paper")
if [ "$r" != "Added paper." ]; then
    echo "error 3.d: got $r"
    exit 1
else
    echo "ok 3.d"
fi

#e) check response for download via arXiv
r=$(cat /tmp/output.txt | grep "Title")
if [ "$r" != "Title: Monte Carlo Simulations of Thermal Comptonization Process in a Two Component Advective Flow around a Neutron Star" ]; then
    echo "error 3.e: got $r"
    exit 1
else
    echo "ok 3.e"
fi

#f) check that title is given for URL which points to a PDF
r=$(papr fetch https://arxiv.org/pdf/1901.00842.pdf)
if [ "$r" != "The response is not html. You need to specify a title." ]; then
    echo "error 3.f: got $r"
    exit 1
else
    echo "ok 3.f"
fi




#./scripts/build_testrepo.sh
