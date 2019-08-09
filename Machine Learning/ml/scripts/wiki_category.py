
# -*- coding: utf-8 -*-

#Install these libraries
from optparse import OptionParser
import sys
from ml.sunflower.categorize import multiprocessConceptCategories

# parse commandline arguments
op = OptionParser()
op.add_option("--multiprocess",
              action="store_true", dest="parallel_mp",
              help="Use multiprocess for processing job. Cannot use with multithread option.")
op.add_option("--dataset", type='str', dest="dataset", 
              help="CS: Computer Science.")
op.add_option("--width", type='int', dest="width", default=2, 
              help="Width of graph tree of categories for a concept.")
op.add_option("--depth", type='str', dest="depth", default=2, 
              help="Depth of graph tree of categories for a concept.")

hoho = ["--dataset","--multiprocess"]
(opts, args) = op.parse_args(hoho)

if len(args) > 0:
    op.error("this script takes no arguments.")
    sys.exit(1)

if __doc__:
    print(__doc__)
op.print_help()

#depth and width of categories
if __name__ == "__main__":
    if opts.parallel_mp:
        multiprocessConceptCategories(opts.dataset, opts.width, opts.depth)
