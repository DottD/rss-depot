# Useful RSS feed repo

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

The RSS feeds will be automatically generated in the derived branches from the Python scripts in this repo. Please follow the instructions contained in the `dottD` branch to find out how to customize the feeds.

## How to contribute

Any contribution is warmly welcomed. Contribution to this branch must contain only the scripts that scrape the website and generate the feed content.

To contribute follow this simple recipe:

* write a script that reads a configuration file and generates the `.xml` of your RSS feed, check for instance my `stack-overflow.py`;
* add the information to the Github Action used to generate all the feeds; in this branch you will find the `main.yml` boilerplate that you need to edit
