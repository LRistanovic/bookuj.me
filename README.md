# Bookuj.me

Add something about the project here

## Project set up

> NOTE: Most of the following commands require root privileges

1. Install basic dependencies
```
apt install python3 python3.8-venv python3-pip sqlite3/postgresql
```
2. Clone the project into /var/www/ folder and cd into it
```
cd /var/www/
git clone https://github.com/LRistanovic/bookuj.me/
cd bookuj.me/
```
3. Set up a virtual environment and install the dependecies
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
4. Create the environment file, and fill it with data like in .env.dist
```
vim .env
...
```
5. Make django migrations
```
python3 manage.py migrate
```
6. Collect static files for browsable API and admin page
```
python3 manage.py collectstatic
```
7. Create the uwsgi socket file
```
mkdir .venv/var/
mkdir .venv/var/run/
touch .venv/var/run/uwsgi.sock
```
8. Create the uwsgi service for the project
```
cp server/bookujme.service /etc/systemd/system/
systemctl daemon-reload
systemctl start/restart/enable bookujme.service | sudo service bookujme.service start/restart/enable
```
9. If nginx is not installed, install it
```
apt install nginx
```
10. Add nginx configuration file and start nginx service
```
cp server/nginx-bookujme.conf /etc/nginx/sites-enabled/
systemctl start/restart/enable nginx | sudo service nginx start/restart/enable
```

The server should now be up and responding to requests.
