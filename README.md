# emacsclient sudo

Act as a proxy between emacsclient and the emacs server only allowing certain eval commands.
Can be useful when you are using jails to reduce privileges, which still allowing emacs.
(For example docker, subuser, firejail, selinux or apparmor)

This was developed with [firejail](https://l3net.wordpress.com/projects/firejail/) in mind.

# Requirements

* `python3`
* `sexpdata`
* `emacs`

# Motivation

In the past privilege separation on a machine was achieved through multiple distinct users. However, this can be problematic in a general setting where you don't know ahead of time what privileges different activities should have. 

We are starting to see forms of privilege separation that tease apart the notion of a single user. Rather you have a restricted subuser for different activities. This is often used through dropping privileges for a process within the linux kernel. Android is in many ways a poster-child for this approach.

Useful as many of these kernel-based approaches are, the architecture behind
the linux desktop (`dbus`, `X`, `emacs`, `tmux`) have the assumption of the *monolithic user* baked-in via various means of remote procedure call.

This is a small attempt to retrofit part of this architecture (`emacs`) with additional security.

# Usage

* Install: `pip3 install git+https://github.com/talwrii/emacsclientsudo#egg=emacsclientsudo`
* Set up some sort of reduced privileged execution environment.
* Run emacs --daemon in a more privileged environment
* Ensure that your less privileged environment does not have access to the emacs server socket (/tmp/emacs$(id -u)/socket).
* In the more privileged environment run `emacsclientsudo --allow-function list /tmp/proxy-socket /tmp/emacs$(id -u)/socket).
* Run `emacsclient -s /tmp/proxy-socket` in the less privileged environment.

# Prior work

* [Subuser](http://subuser.org) is a grand scheme to run reduced privilege applications for linux based upon docker.
In particular, the author of subuser has written an X11 proxy for privilege reduction.

* This firejail issue discusses similar issues related to dbus <https://github.com/netblue30/firejail/issues/796>.

# Default warnings

As a rule open source software licenses attempt to minimise legal liability to the maximum extent possible (often to
comic effect). This is equally true for this project, it is licensed under GPLv3 which includes such clauses.

Nevertheless, for any piece of software that deals with security in any way it behoves the author to make some limitations clear.

* The most important thing you can do for security is keeping your software up-to-date, and being aware of phishing attacks.
* Many forms of sandboxing in linux are susceptible to escape through kernel bugs. Virtual machines, or even separate hardware are suggested by many.
* There are a variety of sandbox escapes. Good practice involves minimising your attack surface by running as little as possible, and where possible using approaches that are broadly used and audited.
* It can be advisable to have a risk model in mind whenever working on security, one can waste a lot of time making niche elements of your system very secure.
* As an entry point to the world of software security I would recommend the risky business security podcast (no affiliation).


