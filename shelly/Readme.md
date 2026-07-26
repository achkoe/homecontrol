# Installation

Presuming `shellyproxy` is clonden into folder `~/homecontrol/shelly` and you are in this folder.

Create a file `.env` with `USERNAME` and `PASSWORD`
```
USERNAME=your username
PASSWORD=your password
```
Create a Python venv in folder `.venv` and activate venv
```
pushd ..
python3 -m venv .venv
source .venv/bin/activate
popd
```
Install flask and dotenv
```
pip3 install flask dotenv
```
Copy shellyproxy.service to `/etc/systemd/system`
```
sudo cp shellyproxy.service /etc/systemd/system
sudo systemctl start shellyproxy.service
sudo systemctl status shellyproxy.service 
sudo systemctl enable shellyproxy.service
```

If anything is going wrong you can check
```
journalctl -u shellyproxy.service 
```

Otherwise, open a browser, enter the IP address of the machine and look at port 5011
