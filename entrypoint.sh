# Start postgres database server, create role & DB
su -c 'pg_ctl -D /var/lib/postgresql/data start' postgres
su -c "psql -h 0.0.0.0 -p 5432 -c \"CREATE USER test WITH ENCRYPTED PASSWORD 'test';\" || true" postgres
su -c "psql -h 0.0.0.0 -p 5432 -c \"CREATE DATABASE storm OWNER test;\" || true" postgres

# Database migrations
cd /app/storm
python manage.py makemigrations
python manage.py migrate

# Start backend server
daphne -b 0.0.0.0 -p 8000 storm.asgi:application
