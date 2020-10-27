import curses, time
import pyfiglet, random
import requests

url = 'http://192.168.1.231/status/status.php'
auth_header = 'Basic YWRtaW46YWRtaW4='

def get_io(): # Get a random value. Tweek later with real data
    global today_kw, today_gen, ac_voltage

    try:
        data = requests.get(url, headers = {'Authorization': auth_header})
        inv_values = data.text.split(',')
#    print(inv_values[23])
        inv_current_kw = inv_values[23]
        inv_today_gen = inv_values[3]
        inv_l1_volt = str(int(inv_values[25])/10)
        inv_l2_volt = str(int(inv_values[27])/10)
        inv_l3_volt = str(int(inv_values[29])/10)
        today_kw = pyfiglet.figlet_format(str(inv_current_kw) + " W", font = "starwars" )
        today_gen = pyfiglet.figlet_format(str(int(inv_today_gen)/100) + " kWh", font = "starwars" )
        ac_voltage = pyfiglet.figlet_format("%s %s %s" % (inv_l1_volt, inv_l2_volt, inv_l3_volt), font = "helv" )
    except:
        pass

def screen_update():
# Create a string of text based on the Figlet font object

    stdscr = curses.initscr() # create a curses object
# Create a couple of color definitions
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

# Write the BIG TITLE text string
#    stdscr.addstr(0,0, "Current power to AC" ,curses.A_BOLD)

#    stdscr.addstr(8,0, "Today generated" ,curses.A_BOLD)
# Cycle getting new data, enter a 'q' to quit
    stdscr.nodelay(1)
    k = 0
    while (k != ord('q')):
        get_io() # get the data values
        stdscr.clear()
        stdscr.addstr(1,0, today_kw,curses.color_pair(1) )
        stdscr.addstr(7,0, today_gen,curses.color_pair(2) )
        stdscr.addstr(13,0, ac_voltage,curses.color_pair(3) )
        stdscr.refresh()
        time.sleep(2)

        k = stdscr.getch()

    curses.endwin()

if __name__ == "__main__":
    screen_update()

