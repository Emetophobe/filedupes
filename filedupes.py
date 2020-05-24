#!/usr/bin/env python
# Copyright (C) 2019-2020   Emetophobe (snapnaw@gmail.com)
# https://github.com/Emetophobe/filedupes/

import os
import time
import hashlib
import argparse
import textwrap
from collections import defaultdict


# Defaults
DEFAULT_ALGORITHM = 'sha256'
DEFAULT_EXCLUDE = ['RCS', 'CVS', 'tags', '.git', '.venv', '.hg', '.bzr', '_darcs', '__pycache__']


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Find duplicate files by comparing checksums.')
    parser.add_argument('directory', help='top level directory to search', type=str)
    parser.add_argument('-a', '--algorithm', help='hashing algorithm (default: %(default)s)',
                        default=DEFAULT_ALGORITHM, type=str)
    parser.add_argument('-e', '--exclude', nargs='*', help='paths to exclude', default=DEFAULT_EXCLUDE)
    args = parser.parse_args()

    # Make sure the directory is valid
    if not os.path.isdir(args.directory):
        parser.error('Invalid search directory: ' + args.directory)

    # Make sure the algorithm is valid
    algorithm = args.algorithm.lower()
    if algorithm not in hashlib.algorithms_available:
        supported = textwrap.fill(', '.join(sorted(hashlib.algorithms_available)), 70)
        parser.error('Invalid algorithm. List of supported algorithms:\n\n' + supported)

    # Create a dictionary of all file hashes
    start_time = time.time()
    hashes = defaultdict(list)
    for root, dirs, files in os.walk(os.path.abspath(args.directory), topdown=True):
        dirs[:] = [d for d in dirs if d not in args.exclude]

        for filename in files:
            filename = os.path.join(root, filename)
            try:
                digest = create_hash(filename, algorithm)
            except OSError as e:
                print('Error reading file: {} ({})'.format(filename, e.strerror))
            else:
                hashes[digest].append(filename)

    # Create a dictionary of dupes (hashes with multiple filenames)
    dupes = {k: v for k, v in hashes.items() if len(v) > 1}

    # Print the results
    print()
    for digest, files in dupes.items():
        print(digest)
        for filename in files:
            print(' ', filename)
        print()

    duration = time.time() - start_time
    print('Found {} duplicate hashes in {:.2f} seconds.'.format(len(dupes), duration))


def create_hash(filename, algorithm):
    """ Create a hash of the file using the specified algorithm. """
    hasher = hashlib.new(algorithm)
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Aborted.')
