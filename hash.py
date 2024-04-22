# Author: Nathan M
# Desc: Generated by chatgpt on 4/22/24 at 2:30pm and modified to have seperate save/load

import hashlib
import os
import sys

def hash_file(filename):
    """This function returns the SHA-1 hash of the file passed into it"""
    # make a hash object
    h = hashlib.sha1()

    # open file for reading in binary mode
    with open(filename, 'rb') as file:
        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            # read only 1024 bytes at a time
            chunk = file.read(1024)
            h.update(chunk)

    # return the hex representation of digest
    return h.hexdigest()

def hash_directory(directory):
    """This function hashes all files in a directory and saves the results to a CSV file"""
    hashes = {}
    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            filehash = hash_file(filepath)
            hashes[filepath] = filehash
    return hashes

def save_hashes(hashes, filename):
    """This function saves the hashes to a CSV file"""
    with open(filename, 'w') as f:
        for filepath, filehash in hashes.items():
            f.write(f"{filepath}::::{filehash}\n")

def load_hashes(filename):
    """This function loads hashes from a CSV file"""
    hashes = {}
    with open(filename, 'r') as f:
        for line in f:
            filepath, filehash = line.strip().split('::::')
            hashes[filepath] = filehash
    return hashes

def recheck_hashes(directory, original_hashes):
    """This function rechecks the hashes of files in a directory against the original hashes"""
    num_unchanged = 0
    current_hashes = hash_directory(directory)
    for filepath, filehash in current_hashes.items():
        original_hash = original_hashes.get(filepath)
        if original_hash is None:
            print(f"File {filepath} is new or moved.")
        elif filehash != original_hash:
            print(f"File {filepath} has been modified.")
        else:
            num_unchanged +=1
    print(f"{num_unchanged} files unchanged")

save_load = int(sys.argv[1])
directory = sys.argv[2]
hashes_file = sys.argv[3]
if save_load == 0:

    # Hash all files in the directory and save the results
    hashes = hash_directory(directory)
    save_hashes(hashes, hashes_file)
else:

    # Load the original hashes and recheck
    original_hashes = load_hashes(hashes_file)
    recheck_hashes(directory, original_hashes)
