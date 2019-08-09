
# -*- coding: utf-8 -*-

#Install these libraries
from optparse import OptionParser
import sys
from ml.wikify.annotate import wikiAnnotation, multithreadAnnotation,\
     multiProcessAnnotation, singleThreadAnnotation

# parse commandline arguments
op = OptionParser()
op.add_option("--illinois-wikifier",
              action="store_true", dest="illinois_miner",
              help="Annotate using Illinois Wikifier.")
op.add_option("--multithread",
              action="store_true", dest="parallel_mt",
              help="Use multithreading for processing job.")
op.add_option("--multiprocess",
              action="store_true", dest="parallel_mp",
              help="Use multiprocess for processing job. Cannot use with multithread option.")
op.add_option("--dataset", type='str', dest="dataset", 
              help="CS: Computer Science.")

yoyo = ["--dataset","cs_test","--multithread","--illinois-wikifier"]
(opts, args) = op.parse_args(yoyo)
if len(args) > 0:
    op.error("this script takes no arguments.")
    sys.exit(1)

if __doc__:
    print(__doc__)
op.print_help()

if __name__ == "__main__":
    if opts.illinois_miner:
        if opts.parallel_mt:
            multithreadAnnotation(opts.dataset,annotator=wikiAnnotation)
        elif opts.parallel_mp:
            multiProcessAnnotation(opts.dataset,target = wikiAnnotation)
        else:
            singleThreadAnnotation(opts.dataset, target=wikiAnnotation)