#!/usr/bin/env python3
"""
Converts ply triangle meshes into VOLA format.

PLY is an industry standard mesh format. This parser only looks at the points
and their colors, not the triangles.

TODO: Need to cleverly remove duplicate points and add subdivide function.
"""
from __future__ import print_function
import glob
import re
import os
import plyfile
import numpy as np
from stl import mesh
import binutils as bu
from volatree import VolaTree


def main():
    """Read the file, build the tree. Write a Binary."""
    start_time = bu.timer()
    parser = bu.parser_args("*.ply")
    args = parser.parse_args()

    # Parse directories or filenames, whichever you want!
    if os.path.isdir(args.input):
        filenames = glob.glob(os.path.join(args.input, '*.ply'))
    else:
        filenames = glob.glob(args.input)

    print("processing: ", ' '.join(filenames))
    for filename in filenames:
        if args.dense:
            outfilename = re.sub("(?i)ply", "dvol", filename)
        else:
            outfilename = re.sub("(?i)ply", "vol", filename)
        if os.path.isfile(outfilename):
            print("File already exists!")
            continue

        print("converting", filename, "to", outfilename)
        bbox, points, pointsdata = parse_ply(filename, args.nbits)

        # work out how many chunks are required for the data
        if args.nbits:
            div, mod = divmod(len(pointsdata[0]), 8)
            if mod > 0:
                nbits = div + 1
            else:
                nbits = div
        else:
            nbits = 0

        volatree = VolaTree(args.depth, bbox, args.crs, args.dense, nbits)
        volatree.cubify(points)
        volatree.countlevels()
        volatree.writebin(outfilename)

    bu.timer(start_time)


def parse_ply(filename, nbits):
    """Read ply format mesh and return header and points."""
    ply_file = plyfile.PlyData.read(filename)
    vertices = ply_file.elements[0].data
    coords = np.zeros((len(vertices), 3), dtype=np.float)
    # data = np.zeros(len(vertices))

    for idx, vert in enumerate(vertices):
        coords[idx] = list(vert)[:3]
    #    data[idx] = list(vert)[3:]

    minvals = coords.min(axis=0).tolist()
    maxvals = coords.max(axis=0).tolist()
    bbox = [minvals, maxvals]

    # if nbits > 0:
#        return bbox, coords, data
#    else:
    return bbox, coords, None


if __name__ == '__main__':
    main()