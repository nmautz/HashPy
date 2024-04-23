# Author: Nathan M
# Desc: Generated by chatgpt on 4/22/24 at 2:30pm and moderately modified

import hashlib
import os
import sys

CURRENT_VERSION = "0.2"
SUPPORTED_VERSIONS = [CURRENT_VERSION]

def hash_file(filename):
    """This function returns the SHA-1 hash of the file passed into it"""
    # make a hash object
    h = hashlib.sha1()

    # open file for reading in binary mode
    with open(filename, 'rb') as file:
        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            # https://stackoverflow.com/questions/17731660/hashlib-optimal-size-of-chunks-to-be-used-in-md5-update
            chunk = file.read(65536)
            h.update(chunk)

    # return the hex representation of digest
    return h.hexdigest()


def get_file_details(filepath):
    filehash = hash_file(filepath)
    file_size,modified_date = get_shallow_file_details(filepath)
    return filehash, file_size, modified_date

def get_shallow_file_details(filepath):
    file_size = os.path.getsize(filepath)
    modified_date = os.path.getmtime(filepath)
    return file_size, modified_date

def hash_directory(directory):
    """This function hashes all files in a directory and saves the results to a CSV file"""
    hashes = {}
    #check if file instead of dir
    if os.path.isfile(directory):
        filehash,file_size,modified_date = get_file_details(directory)
        hashes[directory] = [filehash, file_size, modified_date]
        return hashes
    
    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            filehash,file_size,modified_date = get_file_details(filepath)
            hashes[filepath] = [filehash, file_size, modified_date]
    return hashes

def save_hashes(hashes, filename):
    """This function saves the hashes to a CSV file"""
    with open(filename, 'w') as f:
        # Write the version number to the file
        f.write(f"{CURRENT_VERSION}\n")

        for filepath, file_details in hashes.items():
            filehash = file_details[0]
            file_size = file_details[1]
            modified_date = file_details[2]
            f.write(f"{filepath}::::{filehash}::::{file_size}::::{modified_date}\n")

def load_hashes(filename):
    """This function loads hashes from a CSV file"""
    hashes = {}
    with open(filename, 'r') as f:
        # read first line to get version number
        version_str = f.readline()
        version_str = version_str.strip()
        if not version_str in SUPPORTED_VERSIONS:
            print(f"Unsupported version: {version_str}")
            print(f"Supported versions: {SUPPORTED_VERSIONS}")
            exit(1)
        for line in f:
            filepath, filehash,file_size,modified_date = line.strip().split('::::')
            hashes[filepath] = [filehash,file_size,modified_date]
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
