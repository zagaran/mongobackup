Mongo Backup
========
Mongo backup is designed to handle backing up and restoring a mongo database locally and on s3.

It can be installed by pip:

```
pip install mongobackup
```

Example usage follows.

```
# To do a local backup
from mongobackup import backup
backup("mongo_user", "mongo_password", "/var/backups/mongo/")

```
```
# To do a local backup of only one specific database, not every database on
# the server (some MongoDB auth/security configurations require this)
from mongobackup import backup
backup("mongo_user", "mongo_password", "/var/backups/mongo/",
       database="my_database_name")

```

```
# To do a local backup and a local backup on attached storage
from mongobackup import backup
backup("mongo_user", "mongo_password", "/var/backups/mongo/",
       attached_directory_path='/mnt/backups/')
```

```
# To do a local backup, backup on attached storage, and backup on S3
from mongobackup import backup
backup("mongo_user", "mongo_password", "/var/backups/mongo/",
       attached_directory_path='/mnt/backups/',
       s3_bucket="mongo-backup-bucket", s3_access_key_id="ASDF424242ASDF4242",
       s3_secret_key="lksLKDkakka983jk1DKJa3lkadkjq3askllkad")
```

```
# To do a local backup, backup on attached storage, and backup on S3,
# deleting all local and attached storage backups older than 30 days
from mongobackup import backup
backup("mongo_user", "mongo_password", "/var/backups/mongo/",
       attached_directory_path='/mnt/backups/',
       s3_bucket="mongo-backup-bucket", s3_access_key_id="ASDF424242ASDF4242",
       s3_secret_key="lksLKDkakka983jk1DKJa3lkadkjq3askllkad",
       purge_local=30, purge_attached=30)
```

```
# To download the latest S3 backup
from mongobackup import s3_download
s3_download("latest.tbz", s3_bucket="mongo-backup-bucket",
            s3_access_key_id="ASDF424242ASDF4242",
            s3_secret_key="lksLKDkakka983jk1DKJa3lkadkjq3askllkad")
```

```
# To see all s3 backups and download a particular one
from mongobackup import s3_list, s3_download
s3_list(s3_bucket="mongo-backup-bucket",
        s3_access_key_id="ASDF424242ASDF4242",
        s3_secret_key="lksLKDkakka983jk1DKJa3lkadkjq3askllkad")

s3_download("latest.tbz", s3_bucket="mongo-backup-bucket",
            s3_access_key_id="ASDF424242ASDF4242",
            s3_secret_key="lksLKDkakka983jk1DKJa3lkadkjq3askllkad",
            s3_file_key="backup_2015-03-05_21-40.tbz")
```

```
# To restore a backup
from mongobackup import restore
restore("mongo_user", "mongo_password", "latest.tbz")
```

```
# If you are having difficulties with restoring a backup from an older version
# of Mongo due to changes in their user permissions system, you can include the
# skip_system_and_user_files flag.
restore("mongo_user", "mongo_password", "latest.tbz", skip_system_and_user_files=True)
```