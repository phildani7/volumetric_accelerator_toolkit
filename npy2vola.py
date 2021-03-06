#!/usr/bin/env python3
"""
npy2vola: Converts numpy arrays into VOLA format.

Converting numpy depth images with a fixed grid size of 256
There is no information other than voxels so the occupancy information
is only available for this format.
@author Jonathan Byrne & Anton Shmatov
@copyright 2018 Intel Ltd (see LICENSE file).
"""
from __future__ import print_function
import glob
import os
import numpy as np
import binutils as bu
from volatree import VolaTree


def main():
    """Read the file, build the tree. Write a Binary."""
    start_time = bu.timer()
    parser = bu.parser_args("*.npy")
    args = parser.parse_args()

    # Parse directories or filenames, whichever you want!
    if os.path.isdir(args.input):
        filenames = glob.glob(os.path.join(args.input, '*.npy'))
    else:
        filenames = glob.glob(args.input)

    print("processing: ", ' '.join(filenames))
    for filename in filenames:
        if args.dense:
            outfilename = bu.sub(filename, "dvol")
        else:
            outfilename = bu.sub(filename, "vol")
        if os.path.isfile(outfilename):
            print("File already exists!")
            continue

        print("converting", filename, "to", outfilename)
        bbox, points, pointsdata = parse_npy(filename)

        print("npy only has occupancy data," +
              " no additional data is being added")
        nbits = 0

        if len(points) > 0:
            volatree = VolaTree(args.depth, bbox, args.crs,
                                args.dense, nbits)
            volatree.cubify(points, pointsdata)
            volatree.writebin(outfilename)

            bu.print_ratio(filename, outfilename)
        else:
            print("The points file is empty!")
    bu.timer(start_time)


def parse_npy(filename):
    """Read xyz format point data and return header, points and points data."""
    depthmap = np.load(filename)
    points = np.argwhere(depthmap == 1).tolist()
    bbox = [[0, 0, 0], [255, 255, 255]]
    return bbox, points, None


if __name__ == '__main__':
    main()
