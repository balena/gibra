Gibra
=====

Gibra (Git Binary Repository Assistant) is a static binary repository manager
that uses Git as file storage for a single project.


# Overview

`gibra` provides a simple way to store static binary files in Git. `gibra` just
pushes static files into a `dist` folder in a Git repository, and annotates the
changelog in Git tag comments.

The Assistant depends on Python 3.


# Usage


## Preparation

Before running it, install the required dependencies with:

    $ ./gibra reqs > requirements.txt
    $ pip3 install --user -r requirements.txt

Then add `gibra` script somewhere in your PATH.


## Configure

1) Create a Git repository to host your binaries.

2) Put a `.gibrarc` file to the root of this repository, following the template
below:

    {
      # Gibra will attempt to extract ZIP files with the following extensions:
      'allowed_extensions': ['zip'],

      # In changelog comments, transform the following pattern in links to your
      # bugtracking system:
      'issue_key_pattern': r'#([0-9]{2,})',

      # Bugtracking links will have the following prefix:
      'bugtracking_url': 'https://github.com/balena/artifacts/issues/',
    }


## Running

Just move to your root repository folder and do:

    $ gibra

Point your browser to http://127.0.0.1:5757/ and enjoy!


# Why an Assistant?

The idea is to ease using Git as a (small) binary artifacts repository.
Experienced users may not be interested in this interface, as the command line
may be more than enough. On the other hand, those who aren't used to Git may
want to use it to ease performing the several steps involved in maintaining a
tiny artifacts (binary) repository.

Those willing to adopt the idea for automating their publishing process may
extend/change this code in order to add their own processes.


# Working with branches

Just synchronize remote branches locally, like so:

    $ git checkout --track origin/branch_name

Then it will show in a selector in the top of `gibra` interface.

When handling multiple branches, don't forget to replicate the `.gibrarc`
config file.


# Modifying the changelog

Well, you cannot easily change git comments, but you can add `git notes`.
`gibra` will consider whatever you write on the tag notes as updates to the
changelog entry.

