# Bookuj.me

Add something about the project here

## Project set up

> NOTE: Most of the following commands require root privileges

1. Install basic dependencies
```
apt install python3 python3.8-venv python3-pip postgresql
```
2. Set up postgresql
```
sudo su postgres
initdb -D /var/lib/postgres/data
systemctl enable postgresql.service
createdb bookuj
psql
	CREATE USER django WITH PASSWORD <password> (the same one as in .env)
	ALTER ROLE django SET client_encoding TO 'utf8';
	ALTER ROLE django SET default_transaction_isolation TO 'read committed';
	ALTER ROLE django SET timezone TO 'UTC';
	GRANT ALL PRIVILEGES ON DATABASE bookuj TO django;
```
3. Clone the project into /var/www/ folder and cd into it
```
cd /var/www/
git clone https://github.com/LRistanovic/bookuj.me/
cd bookuj.me/
```
4. Set up a virtual environment and install the dependecies
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
5. Create the environment file, and fill it with data like in .env.dist
```
vim .env
...
```
6. Make django migrations
```
python3 manage.py migrate
```
7. Collect static files for browsable API and admin page
```
python3 manage.py collectstatic
```
8. Create the uwsgi socket file
```
mkdir .venv/var/
mkdir .venv/var/run/
touch .venv/var/run/uwsgi.sock
```
9. Create the uwsgi service for the project
```
cp server/bookujme.service /etc/systemd/system/
systemctl daemon-reload
systemctl start/restart/enable bookujme.service | sudo service bookujme.service start/restart/enable
```
10. If nginx is not installed, install it
```
apt install nginx
```
11. Add nginx configuration file and start nginx service
```
cp server/nginx-bookujme.conf /etc/nginx/sites-enabled/
systemctl start/restart/enable nginx | sudo service nginx start/restart/enable
```

The server should now be up and responding to requests.
