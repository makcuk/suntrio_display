import pygame
import pygame.freetype  # Import the freetype module.
import time
import requests

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

    try:
        data = requests.get(url, headers = {'Authorization': auth_header})
        inv_values = data.text.split(',')
        inv_data['current_power'] = str(inv_values[23])+" W"
        inv_data['daily_generation'] = str(int(inv_values[3])/100)+" kWh"
        inv_data['l1_volts'] = str(int(inv_values[25])/10)+"V"
        inv_data['l2_volts'] = str(int(inv_values[27])/10)+"V"
        inv_data['l3_volts'] = str(int(inv_values[29])/10)+"V"
        inv_data['inv_temp'] = str(int(inv_values[32])/10)+" C"
        inv_data['ac_freq'] = str(float(inv_values[24])/100)+" Hz"

    except:
        print("Failed request")
        inv_data['current_power'] = "N/A"
        inv_data['daily_generation'] = "NO DATA"
        inv_data['l1_volts'] = "N/A"
        inv_data['l2_volts'] = "N/A"
        inv_data['l3_volts'] = "N/A"
        inv_data['inv_temp'] = "N/A"
        inv_data['ac_freq'] = "N/A"
    return dotdict(inv_data)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    CURRENT_FONT = pygame.freetype.Font("freesansbold.ttf", grid(16))
    DAILY_FONT = pygame.freetype.Font("freesansbold.ttf", grid(10))
    AC_FONT = pygame.freetype.Font("freesansbold.ttf", grid(4))
    BAR_FONT = pygame.freetype.Font("freesansbold.ttf", grid(3))
    running =  True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        screen.fill((40,40,40))
        pygame.draw.rect(screen, PH1_GREEN,[2,2,S_WIDTH,S_HEIGHT])
        pygame.draw.rect(screen, (40,40,40),[4,4,S_WIDTH-7,S_HEIGHT-7])
        inv_data = update_inv_data()
        text_surface, rect = CURRENT_FONT.render(inv_data.current_power, PH1_GREEN)
        center(text_surface)
        screen.blit(text_surface, (center(text_surface), grid(3)))

        text_surface, rect = DAILY_FONT.render(inv_data.daily_generation, (255, 255, 255))
        screen.blit(text_surface, (center(text_surface), grid(20)))
        text_surface, rect = AC_FONT.render("L1: %s L2: %s L3: %s" % (inv_data.l1_volts,inv_data.l2_volts,inv_data.l3_volts), (250, 51, 10))
        screen.blit(text_surface, (center(text_surface), grid(33)))
        text_surface, rect = BAR_FONT.render("%s  %s" % (inv_data.inv_temp,inv_data.ac_freq), PH1_GREEN)
        screen.blit(text_surface, (center(text_surface), grid(45)))


        pygame.display.flip()
        time.sleep(5)

    pygame.quit()

