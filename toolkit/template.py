#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# <author-github>/<repository>/<filepath/name>
"""
<Short description one-liner: - New Python module template>

<Multiline description of the module:>
<A template file designed for new and returning members of the lab.>
<Replace all <> tags with the actual info BEFORE starting to program stuff.>
<It is always a good idea to first think WHAT and WHY are you going to code?>
<Thoughtfully design you module/script/command-line-tool/GUI first!>
<Then it becomes much easier to implement desired cleanly and efficiently.>

**Copyright:** <Year>, <Author> (<URL or mail>)

**License:** [MIT](../LICENSE)

**Core dependencies:**
* <Python version> (standard lib packages)
E.g.: Python 3.4+ (`pathlib`), ObsPy 1.4.0
"""
################################## IMPORTS ####################################
# Python standard library imports
from pathlib import Path

# Necessary packages (not in standard lib)
import obspy

# Local application/library specific imports
#from misc import get_code, is_pow_of_two, nearest_pow_of_two


############################## GLOBAL CONSTANTS ###############################
# Paths to directories/files - may/should evolve to command line arguments
ROOT_DIR = Path(__file__).parent

# Some hardcoded processing parameters - easier to keep track of
NFFT: int = nearest_pow_of_two(64)


############################# AUXILIARY FUNCTIONS #############################
# Low-level or support function what are mostly needed inside the module.
# It is a good way to keep things organized and clean.
# Prepend function name with _ to identify that it is (should be) private.
# E.g. _is_valid() or _unpack()


################################# DECORATORS ##################################
# Wrapper functions to add more functionality to other functions and classes.


################################### CLASSES ###################################
# Core object-oriented concept - order of definition matters!
# Importing in other modules will look like so:
# from template import Foo


############################### CORE FUNCTIONS ################################
# Key functions of the module living in a global namespace.
# This means you can import them in other module as: 
# from template import foobar


################################### TESTING ###################################
# It is never a bad idea to test your code. Just saying.


############################## SCRIPT BEHAIVIOR ###############################
# Python idiom to check if the module is not imported (i.e. script behaivior)
# Also a good place to call testing routines for the module
if __name__ == '__main__':
    # Your script code goes here - delete 'pass' statement.
    pass
    # Return error code 0 back to shell if everything works ok.
    exit(0)
###############################################################################