# Backup and Restore Database from Admin’s Local Machine to Server

## Steps

### 1. Backup and clear the server database
Before wiping the server database, make a backup:

~~~bash
cd postgres_container
sudo docker exec -t postgres_container-db-1 pg_dump -U user -d app_db > server_backup.sql
~~~

After confirming the backup is safe, you can clear or drop the existing data.

---

### 2. Create a `.sql` backup file from local machine
~~~bash
cd postgres_container
docker exec -t postgres_container_db_1 pg_dump -U user -d app_db > backup.sql
~~~

---

### 3. Copy backup to the server
~~~bash
scp backup.sql username@x.x.x.x:/path/postgres_container/backup.sql
~~~

---

### 4. Load the backup file on the server
~~~bash
cd postgres_container
cat ./backup.sql | sudo docker exec -i postgres_container-db-1 psql -U user -d app_db
~~~
