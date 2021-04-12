import logging
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
logging.basicConfig(level=config['DEFAULT'].get('logging_level'),
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='cris_error.log',
                    filemode='a')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
logging.info("Started")

import pygsheets as ps
from time import sleep
from datetime import datetime
from pytz import timezone
import random
import emailer


tz = timezone('EST5EDT')  # this sets the time to be our time zone with daylight savings time

# I put this import in a try statement so you can run this on your local PC without the Raspberry Pi.

try:
    import piplates.THERMOplate as THERMO

    piplate = True
    # THERMO.setSCALE('f')
    # THERMO.setSCALE('k')
    # THERMO.setSCALE('c') <<--- Default Value
    logging.info("Loaded piplates")
except:
    logging.critical("Failed to load piplates")
    piplate = False
    pass

# googlesheet info
url = config['DEFAULT'].get('sheets_url')
gc = ps.authorize(service_file='google_key.json')
sh = gc.open_by_url(url)
wks = sh[0]

# this is a dictionary of all your thermoplate sensors.
# you can name these descriptively.  to help you keep track.
LOOP_TIMER =int(config['DEFAULT'].get('loop_timer')) #seconds
SENSORS = {
    'ReactionTemp': True,
    'CoolingWater': True,
    'Analog-3': False,
    'Analog-4': False,
    'Analog-5': False,
    'Analog-6': False,
    'Analog-7': False,
    'Analog-8': False,
    'Digital-9': False,
    'Digital-10': False,
    'Digital-11': False,
    'Digital-12': False,
}

# this gets all the sensors you have turned on.

sensor_list = []
for sensors, inuse in enumerate(SENSORS.values(), start=1):
    if inuse == True:
        sensor_list.append(sensors)


def email(temperature, sensor):
    if temperature >70 and sensor=='reaction':
        logging.critical('HIGH TEMP'+ str(temperature))
        emailer.subject =sensor + ": " +str(temperature)
        emailer.body = "ALERT HIGH TEMP"
    if temperature >15 and sensor=='cooling_water':
        logging.critical('HIGH TEMP'+ str(temperature))
        emailer.subject =sensor + ": " +str(temperature)
        emailer.body = "ALERT HIGH TEMP"


def get_temperature(sensor=None):

    if sensor == None:
        time_stamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S.%f")
        record_name = 'ERROR'

        return [time_stamp, record_name, -999]

    elif sensor == 'reaction':
        time_stamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S.%f")
        record_name = 'ReactionTemp'

        if piplate == True:
            temperature = THERMO.getTEMP(0, sensor)
        else:
            temperature = -999.99

        return [time_stamp, record_name, temperature]

    elif sensor == 'cooling_water':
        time_stamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S.%f")
        record_name = 'CoolingWater'

        if piplate == True:
            temperature = THERMO.getTEMP(0, sensor)
        else:
            temperature = -999.99

        return [time_stamp, record_name, temperature]


# while true loops forever we can turn this on and off if we wanted from another google sheet by getting a value.
while (True):
    n = 1
    try:
        reaction = get_temperature(sensor='reaction')
        if reaction:
            wks.append_table(reaction, start='A2', end=None, dimension='ROWS', overwrite=False)
        cooling_water = get_temperature(sensor='cooling_water')
        if reaction:
            wks.append_table(cooling_water, start='A2', end=None, dimension='ROWS', overwrite=False)
    except Exception as e:
        logging.critical("ERROR DATA NOT IN SHEET : " + str(e))
        sleep((10 ** n) + (random.randint(0, 1000) / 1000.0))
        n = n + 1
        continue
    sleep(LOOP_TIMER)
