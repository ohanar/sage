# -*- coding: utf-8 -*-
#
# PREP Tutorials documentation build configuration file, created by
# sphinx-quickstart on Tue Jul  3 10:54:56 2012.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys, os
sys.path.append(os.environ['SAGE_DOC'])
from common.conf import *


# General information about the project.
project = u'PREP Tutorials'
copyright = u'2012, Rob Beezer, Karl-Dieter Crisman, and Jason Grout'
name = 'prep_tutorials'

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = project + " v"+release

# Output file base name for HTML help builder.
htmlhelp_basename = name

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = [
  ('index', name+'.tex', u'PREP Tutorials',
   u'Rob Beezer, Karl-Dieter Crisman, and Jason Grout', 'manual'),
]