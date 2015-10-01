"""
The MIT License (MIT)

Copyright (c) 2015 Zagaran, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@author: Zags (Benjamin Zagorsky)
@author: Eli Jones
"""

from os import path, listdir, makedirs
from shlex import split as command_to_array
from subprocess import CalledProcessError, check_call

def call(command):
    """ Runs a bash command safely, with shell=false, catches any non-zero
        return codes.  Raises slightly modified CalledProcessError exceptions
        on failures.
        Note: command is a string and cannot include pipes."""
    try:  # Using the defaults, shell=False, no i/o redirection.
        return check_call(command_to_array(command))
    except CalledProcessError as e:
        # We are modifying the error itself for 2 reasons.  1) it WILL contain
        # login credentials when run_mongodump is run, 2) CalledProcessError is
        # slightly not-to-spec (the message variable is blank), which means
        # cronutils.ErrorHandler would report unlabeled stack traces.
        e.message = "%s failed with error code %s" % (e.cmd[0], e.returncode)
        e.cmd = e.cmd[0] + " [arguments stripped for security]"
        raise e

def create_folders(absolute_path):
    """ Creates the nested directory structure to satisfy a given absolute path,
        does nothing to existing directory structure.
        Any path passed in will be treated as an absolute path. """
    if not path.exists(absolute_path):
        makedirs(absolute_path)  # FIRST MAKE SURE YOU HAVE WRITE PERMISSIONS!


def tarbz(source_directory_path, output_file_full_path):
    """ Tars and bzips a directory, preserving as much metadata as possible.
        Adds '.tbz' to the provided output file name. """
    output_directory_path = output_file_full_path.rsplit("/", 1)[0]
    create_folders(output_directory_path)
    # Note: default compression for bzip is supposed to be -9, highest compression.
    full_tar_file_path = output_file_full_path + ".tbz"
    if path.exists(full_tar_file_path):
        raise Exception("%s already exists, aborting." % (full_tar_file_path))
    
    # preserve permissions, create file, use files (not tape devices), preserve
    # access time.  tar is the only program in the universe to use (dstn, src).
    tar_command = ("tar jpcfvC %s %s %s" %
                   (full_tar_file_path, source_directory_path, "./"))
    call(tar_command)
    return full_tar_file_path


def untarbz(source_file_path, output_directory_path):
    """ Restores your mongo database backup from a .tbz created using this library.
    This function will ensure that a directory is created at the file path
    if one does not exist already.
    
    If used in conjunction with this library's mongodump operation, the backup
    data will be extracted directly into the provided directory path.
    
    This command will fail if the output directory is not empty as existing files
    with identical names are not overwritten by tar. """
    
    if not path.exists(source_file_path):
        raise Exception("the provided tar file %s does not exist." % (source_file_path))
    
    if output_directory_path[0:1] == "./":
        output_directory_path = path.abspath(output_directory_path)
    if output_directory_path[0] != "/":
        raise Exception("your output directory path must start with '/' or './'; you used: %s"
                        % (output_directory_path))
    create_folders(output_directory_path)
    if listdir(output_directory_path):
        raise Exception("Your output directory isn't empty.  Aborting as "
                        + "exiting files are not overwritten by tar.")
    
    untar_command = ("tar jxfvkCp %s %s --atime-preserve " %
                     (source_file_path, output_directory_path))
    call(untar_command)
