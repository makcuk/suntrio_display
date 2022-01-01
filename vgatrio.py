import pygame
import pygame.freetype  # Import the freetype module.
import time
import requests
from datetime import datetime
import os
import paho.mqtt.client as paho
import logging
import logging.handlers
from sermatec_logger import Sermatec

my_logger = logging.getLogger('vgatrio')
my_logger.setLevel(logging.DEBUG)

handler = logging.handlers.SysLogHandler(address = '/dev/log')

my_logger.addHandler(handler)

broker = os.getenv('MQTT_BROKER')
port = 1883
broker_user = os.getenv('MQTT_USER')
broker_password = os.getenv('MQTT_PASSWORD')
mqtt_root = os.getenv('MQTT_ROOT')

my_sm = Sermatec()
client1 = paho.Client("suntrio")
client1.username_pw_set(broker_user, broker_password)
tries = 10
while True:
    try:
        client1.connect(broker, port)
#        my_sm.connect("pvdisplay.local")
        break
    except Exception as e:
        print(str(e))
        time.sleep(5)
        if tries == 0: os._exit(3)
        tries -= 1

ret = client1.publish(mqtt_root+"/status", "on")




def publish_mqtt(parameter, value):
    try:
        ret = client1.publish(mqtt_root+"/"+parameter, value)
    except Exception as e:
        my_logger.debug("Failed publishing "+str(e))

url = 'http://192.168.1.231/status/status.php' #set your ip address of SAJ Wi-FI module
auth_header = 'Basic YWRtaW46YWRtaW4=' # basic auth token, here is default admin/admin
S_WIDTH = 1024
S_HEIGHT = 768
GRID_STEP = 16
PH1_GREEN = (51, 255, 0) #old-school green display color 

def grid(pos):
    return pos*GRID_STEP

def center(text_obj):
    return (S_WIDTH  /2) - (text_obj.get_rect().width/2)

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def update_inv_data():
    inv_data = {}

    now = datetime.now()

    sm_data = my_sm.get_data()
    inv_data['sm_current_power'] = sm_data[0]
    inv_data['sm_daily_power'] = sm_data[1]
    try:
        data = requests.get(url, headers = {'Authorization': auth_header})
        inv_values = data.text.split(',')
        inv_data['current_power'] = str(int(inv_values[23]))
        inv_data['daily_generation'] = str(int(inv_values[3])/100)
        inv_data['l1_volts'] = str(int(inv_values[25])/10)
        inv_data['l2_volts'] = str(int(inv_values[27])/10)
        inv_data['l3_volts'] = str(int(inv_values[29])/10)
        inv_data['inv_temp'] = str(int(inv_values[32])/10)+" C"
        inv_data['ac_freq'] = str(float(inv_values[24])/100)

    except:
        print("Failed request")
        inv_data['current_power'] = "0"
        inv_data['daily_generation'] = "-1"
        inv_data['l1_volts'] = "N/A"
        inv_data['l2_volts'] = "N/A"
        inv_data['l3_volts'] = "N/A"
        inv_data['inv_temp'] = "N/A"
        inv_data['ac_freq'] = "N/A"
    inv_data['current_time'] = now.strftime("%H:%M:%S")
    return dotdict(inv_data)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    CURRENT_FONT = pygame.freetype.Font("freesansbold.ttf", grid(16))
    DAILY_FONT = pygame.freetype.Font("freesansbold.ttf", grid(10))
    AC_FONT = pygame.freetype.Font("freesansbold.ttf", grid(4))
    BAR_FONT = pygame.freetype.Font("freesansbold.ttf", grid(3))
    running =  True
    daily_gen = "00.0 kWh"
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        screen.fill((40,40,40))
        pygame.draw.rect(screen, PH1_GREEN,[2,2,S_WIDTH,S_HEIGHT])
        pygame.draw.rect(screen, (40,40,40),[4,4,S_WIDTH-7,S_HEIGHT-7])
        inv_data = update_inv_data()
        text_surface, rect = CURRENT_FONT.render(inv_data.current_power+" W", PH1_GREEN)
        center(text_surface)
        screen.blit(text_surface, (center(text_surface), grid(3)))

        text_surface, rect = BAR_FONT.render(str(inv_data.sm_current_power)+" W", PH1_GREEN)
        center(text_surface)
        screen.blit(text_surface, (center(text_surface), grid(16)))
        

        if inv_data.daily_generation != "NO DATA":
            daily_gen = inv_data.daily_generation
        text_surface, rect = DAILY_FONT.render(daily_gen+" kWh", (255, 255, 255))
        screen.blit(text_surface, (center(text_surface), grid(20)))


        text_surface, rect = BAR_FONT.render(str(inv_data.sm_daily_power)+" kWh", (255, 255, 255))
        screen.blit(text_surface, (center(text_surface), grid(29)))

        text_surface, rect = AC_FONT.render("L1: %sV L2: %sV L3: %sV" % (inv_data.l1_volts,inv_data.l2_volts,inv_data.l3_volts), (250, 51, 10))
        screen.blit(text_surface, (center(text_surface), grid(33)))
        text_surface, rect = BAR_FONT.render("%s  %sHz  %s" % (inv_data.inv_temp,inv_data.ac_freq, inv_data.current_time), PH1_GREEN)
        screen.blit(text_surface, (center(text_surface), grid(45)))

        publish_mqtt('current_power', inv_data.current_power)
        publish_mqtt('current_power_sm', inv_data.sm_current_power)
        publish_mqtt('daily_power', inv_data.daily_generation)
        publish_mqtt('daily_power_sm', inv_data.sm_daily_power)
        publish_mqtt('ac_frequency', inv_data.ac_freq)
        publish_mqtt('phase1', inv_data.l1_volts)
        publish_mqtt('phase2', inv_data.l2_volts)
        publish_mqtt('phase3', inv_data.l3_volts)
        pygame.display.flip()
        time.sleep(5)

    pygame.quit()

