# Garden Valve

Code to control a garden valve depending on time and 
the amount of rain in a certain time range.

The garden valve used is a normally open valve, meaning the valve can spent water even if there is now power.

The garden valve is controlled by an esp32 board where e program generated with `esphome` runs. This program 
allows for controlling the valve using http.


## Controller

The script `controller.py` is used to drive the esp32 board which switches the garden valve off and on. It uses the database from `weatherstation`, see https://github.com/achkoe/weatherstation

This script is called using systemctl timers.
The service files and timer files are generated using the option `--write`.

The script uses `configuration.json` to generate the service and timer files.
The keys in `configuration.json`are:

- `on_run_times`
  - `on`: the time when to switch on
  - `for`: the duration in minutes how long the relay is on
- `calculate_rain_amount_over_hours`: the time span used to calculate rain amount
- `minimum_rain_amount_in_millimeters_for_valve_close`: the minimum rain amount for which the valve is closed
- `switchaddress`: the ip address of the esp32 board
- `weatherstation`: the path to project `weatherstation`


```
usage: controller.py [-h] [--state {enable,disable}] [-w] [--force]

Runner for garden valve.

options:
  -h, --help            show this help message and exit
  --state {enable,disable}
                        enable or disable valve
  -w, --write           write unit files for systemctl
  --force               ignore rain per day

Configuration in file configuration.json should look like this:
{
    "on_run_times": [
        {"on": "9:00", "for": 2},
        {"on": "10:55", "for": 2}
    ],
    "calculate_rain_amount_over_hours": 2000,
    "minimum_rain_amount_in_millimeters_for_valve_close": 20,
    "switchaddress": "192.168.178.46",
    "weatherstation": "/home/pi/weatherstation/"
}
```

You have to generate and install the files generated with `--write`, namely

- `gardenvalve-disable.service`
- `gardenvalve-enable.service`
- `gardenvalve-disable.timer`
- `gardenvalve-enable.timer`

The service files calls `controller.py` with option `--state enable` and `--state disable` resp.
The timer files activate the corresponding service files.


## Server

 The file `server.py` provides a tiny web server to view and set the state of the garden valve.