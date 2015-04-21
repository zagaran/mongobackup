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

from boto import connect_s3
from boto.exception import S3ResponseError
from boto.s3.key import Key


def s3_connect(bucket_name, s3_access_key_id, s3_secret_key):
    """ Returns a Boto connection to the provided S3 bucket. """
    conn = connect_s3(s3_access_key_id, s3_secret_key)
    try:
        return conn.get_bucket(bucket_name)
    except S3ResponseError, e:
        if e.status == 403:
            raise Exception("Bad Amazon S3 credentials.")
        raise

def s3_key(bucket_name, s3_access_key_id, s3_secret_key):
    """ Returns an Boto S3 Key object connected to the provided bucket. """
    #this is not part of s3_connect because it makes debugging easier.
    return Key(s3_connect(bucket_name, s3_access_key_id, s3_secret_key))


def s3_list(s3_bucket, s3_access_key_id, s3_secret_key, prefix=None):
    """ Lists the contents of the S3 bucket that end in .tbz and match
        the passed prefix, if any. """
    bucket = s3_connect(s3_bucket, s3_access_key_id, s3_secret_key)
    return sorted([key.name for key in bucket.list()
                   if key.name.endswith(".tbz")
                   and (prefix is None or key.name.startswith(prefix))])


def s3_download(output_file_path, s3_bucket, s3_access_key_id, s3_secret_key,
                s3_file_key=None, prefix=None):
    """ Downloads the file matching the provided key, in the provided bucket,
        from Amazon S3.
        
        If s3_file_key is none, it downloads the last file
        from the provided bucket with the .tbz extension, filtering by
        prefix if it is provided. """
    bucket = s3_connect(s3_bucket, s3_access_key_id, s3_secret_key)
    if not s3_file_key:
        keys = s3_list(s3_bucket, s3_access_key_id, s3_secret_key, prefix)
        if not keys:
            raise Exception("Target S3 bucket is empty")
        s3_file_key = keys[-1]
    key = Key(bucket, s3_file_key)
    with open(output_file_path, "w+") as f:
        f.write(key.read())


def s3_upload(source_file_path, bucket_name, s3_access_key_id, s3_secret_key):
    """ Uploads the to Amazon S3 the contents of the provided file, keyed
        with the name of the file. """
    key = s3_key(bucket_name, s3_access_key_id, s3_secret_key)
    file_name = source_file_path.split("/")[-1]
    key.key = file_name
    if key.exists():
        raise Exception("s3 key %s already exists for current period."
                        % (file_name))
    key.set_contents_from_filename(source_file_path)
