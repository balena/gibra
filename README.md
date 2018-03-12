# Git Binary Repository Assistant

This is a pocket app that maintains a binary artifacts repository using a
`dist` folder, and annotating the changelog in Git tag comments.

The Assistant depends on Python 3.

Before running it, install the required dependencies with:

    $ ./assistant.py reqs > requirements.txt
    $ pip3 install --user -r requirements.txt

Add the `assistant.py` script to an empty Git repository to start, then run:

    $ ./assistant.py

You may want to configure the `BUGTRACKING_URL` in the `assistant.py` script,
such as the URL of your bugtracking system, so it will add links to it whenever
you write `#NNNN` in the changelog.

Finally, point your browser to http://127.0.0.1:5757/ and enjoy!


## Why an Assistant?

The idea is to ease using Git as a (small) binary artifacts repository.
Experienced users may not be interested in this interface, as the command line
may be more than enough. On the other hand, those who aren't used to Git may
want to use it to ease performing the several steps involved in maintaining a
tiny artifacts (binary) repository.

Those willing to adopt the idea for automating their publishing process may
extend/change this code in order to add their own processes.


## Working with branches

Just synchronize remote branches locally, like so:

    $ git checkout --track origin/branch_name

Then it will show in a selector in the top of the assistant.

When handling multiple branches, don't forget to replicate the same
`assistant.py` script on them.


## Modifying the changelog

Well, you cannot easily change git comments, but you can add `git notes`. The
`assistant.py` will consider whatever you write on the tag notes as updates to
the changelog entry.

