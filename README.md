# STORM

STORM (Smart Tracking & Optimization for Room Monitoring) is a React-Django web-app for real time smartroom monitoring.

## Warning

Please understand that the application contained in this project does not contain any form of user authentication. It should be executed in a local environment, or extended as needed for production.

A public demo of this app can be found at https://teaching-dgp24-digitaltwin-team5.onrender.com/rooms.

## How to Install

### Back-end
To install and run the back-end this application, first clone the main branch of the repository.

Then, install virtualenv and create an environment:
```bash
apt install python3-virtualenv
virtualenv venv
```

Then activate the environment and install the required packages:
```bash
source venv/bin/activate
pip3 install -r requirements.txt
```

Then fill out the credentials required for the application database, copying the template from `storm/storm/.env.template` using 'postgres' as the `ENGINE`. Finally, apply migrations and run the server from `storm/`:
```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

### Front-end
Navigate to `storm-ui/`, and install all packages:
```
pnpm i
```

To run the web-app in developer mode, use:
```
pnpm dev
```

To run STORM as in production, compile the app and run it:
```
pnpm build
pnpm start
```

## Testing the Application
A simple, random metric-generation script can be found at `storm-datagen/`. To run it, use:
```
python3 metrics.py
```
The script accepts various inputs that change the values sent to the backend:
- "dt": Injects a temperature of 70C in a random room.
- "dc": Injects a co2 value of 1001ppm in a random room.
- "wt": Injects a temperature of 40C in a random room.
- "wc": Injects a co2 value of 801ppm in a random room.
- "ip": Removes all people from a random room.
- "restart": Sets the temperature/co2/people of all rooms to 23C/500ppm/5.
