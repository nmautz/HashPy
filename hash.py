# Author: Nathan M
# Desc: Hashes directory (recursivly) or file and saves results to be checked against. Depending on cli args it will do either hashing, checking hashes, or both

import hashlib
import os
import sys
import cProfile
import time

CURRENT_VERSION = "0.2"
SUPPORTED_VERSIONS = [CURRENT_VERSION, "0.1"]

def hash_file(filename):
    """This function returns the SHA-1 hash of the file passed into it"""
    # make a hash object
    h = hashlib.sha1()

    if save_load == 0:
        print(f"Hashing file of size {format_file_size(os.path.getsize(filename))}")

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
    file_size,modified_date = get_quick_file_details(filepath)
    return filehash, file_size, modified_date

def get_quick_file_details(filepath):
    file_size = os.path.getsize(filepath)
    modified_date = os.path.getmtime(filepath)
    return file_size, modified_date

def get_quick_directory_details(directory):
    """This function hashes all files in a directory and saves the results to a CSV file"""
    hashes = {}
    #check if file instead of dir
    if os.path.isfile(directory):
        file_size,modified_date = get_quick_file_details(directory)
        hashes[directory] = [file_size, modified_date]
        return hashes
    
    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_size,modified_date = get_quick_file_details(filepath)
            hashes[filepath] = [file_size, modified_date]
    return hashes

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
        elif not version_str == CURRENT_VERSION:
            print(f"Warning: Hash version {version_str} is not the current version ({CURRENT_VERSION}). Latest features unavailible")
        for line in f:
            split_line = line.strip().split('::::')
            filepath = split_line[0]
            filehash = split_line[1]
            file_size = split_line[2] if len(split_line) > 2 else None
            modified_date = split_line[3] if len(split_line) > 3 else None
            hashes[filepath] = [filehash,file_size,modified_date]
    return hashes

def format_file_size(size_in_bytes):
    size_in_bytes = float(size_in_bytes)
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    unit_index = 0
    while size_in_bytes >= 1024 and unit_index < len(units) - 1:
        size_in_bytes /= 1024
        unit_index += 1
    return "{:.2f} {}".format(size_in_bytes, units[unit_index])

def reckech_hashes(directory, original_hashes):
    """This function rechecks the hashes of files in a directory against the original hashes"""
    num_unchanged = 0
    changed_files = []
    current_hashes = hash_directory(directory)
    for filepath, file_details in current_hashes.items():
        original_file_details = original_hashes.get(filepath)
        if original_file_details is None:
            print(f"File {filepath} is new or moved.")
            changed_files.append(filepath)
        elif file_details is None:
            print(f"File {filepath} is deleted.")
            changed_files.append(filepath)
        else:
            filehash = file_details[0]
            original_filehash = original_file_details[0]

            if filehash == original_filehash:
                num_unchanged += 1
            else:
                print(f"File {filepath} has changed.")
                changed_files.append(filepath)


    print(f"{num_unchanged} files unchanged")
    return changed_files

def quick_recheck_hashes(directory, original_hashes):
    """This function rechecks the hashes of files in a directory against the original hashes"""
    num_unchanged = 0
    current_hashes = get_quick_directory_details(directory)
    changed_files = []
    for filepath, file_details in current_hashes.items():
        original_file_details = original_hashes.get(filepath)
        if original_file_details is None:
            print(f"File {filepath} is new or moved.")
            changed_files.append(filepath)
        elif file_details is None:
            print(f"File {filepath} is deleted.")
            changed_files.append(filepath)
        else:
            file_size = str(file_details[0])
            modified_date = str(file_details[1])
            original_file_size = original_file_details[1]
            original_modified_date = original_file_details[2]

            if file_size == original_file_size and modified_date == original_modified_date or (file_size != None and modified_date != None):
                file_size_human_readable = format_file_size(file_size)
                file_hash = hash_file(filepath)
                original_file_hash = original_file_details[0]
                if original_file_hash == file_hash:
                    num_unchanged += 1
                else:
                    print(f"File {filepath} has changed.")
                    changed_files.append(filepath)
            else:
                print(f"File {filepath} has changed.")
                changed_files.append(filepath)

    print(f"{num_unchanged} files unchanged")
    return changed_files


directory = sys.argv[1]

# Hash all files in the directory and save the results
cProfile.run('hashes = hash_directory(directory)')
