# Bookuj.me

Add something about the project here

## Project set up

1. Clone the project into /var/www/ folder and cd into it
```
cd /var/www/
git clone https://github.com/LRistanovic/bookuj.me/
cd bookuj.me/
```
2. Set up a virtual environment and install the dependecies
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
3. Create the uwsgi socket file
```
mkdir .venv/var/
mkdir .venv/var/run/
touch .venv/var/run/uwsgi.sock
```
4. Create the uwsgi service for the project
```
sudo cp server/bookujme.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start/restart/enable bookujme.service | sudo service bookujme.service start/restart/enable
```
5. If nginx is not installed, install it
```
sudo apt install nginx | sudo pacman -S nginx
```
6. Add nginx configuration file and start nginx service
```
sudo cp server/nginx-bookujme.conf /etc/nginx/sites-enabled/
sudo systemctl start/restart/enable nginx | sudo service nginx start/restart/enable
```

The server should now be up and responding to requests.