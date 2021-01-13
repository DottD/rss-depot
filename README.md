# Useful RSS feed repo

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Python scripts](https://github.com/DottD/rss-depot/workflows/Python%20scripts/badge.svg)

The RSS feeds that you find in `rss-gen` are automatically generated from the Python scripts in this repo. Feel free to PR the feeds you feel useful for others.

## Complete list of feeds

* [EPSO - Concorsi](https://github.com/DottD/rss-depot/blob/master/rss-gen/epso-rss.xml?raw=true)
* [Stack Overflow](https://github.com/DottD/rss-depot/blob/master/rss-gen/stack-overflow-rss.xml?raw=true)

## How to contribute

Any contribution is warmly welcomed. In order to host your auto-generated feed on this repo you must follow these steps:

* write a script that actually generates the `.xml` of your RSS feed, check for instance my `epso.py`;
* add the information to the Github Action used to generate all the feeds; as for my case, look for steps `Creating EPSO RSS` and `Upload EPSO artifact` in `.github/workflows/main.yml` file;
* [optional but highly preferable] add the link to your RSS feed to this file in the upmost part.
