from time import sleep
import serial
import threading
import sys

# set up map from iclicker_id -> current_answer
map_id_answer = {}
# maps from answer string to current total
map_answer_total = {
    'A': 0,
    'B': 0,
    'C': 0,
    'D': 0,
    'E': 0
}
# queue which stores most recent iclicker ids
sender_list = []

# Global variable for saving recent keyboard input
next_cmd = None


def reset():
    '''
    Called to reset all data structures for use on new multiple choice question
    '''
    map_id_answer = {}
    map_answer_total = {
        'A': 0,
        'B': 0,
        'C': 0,
        'D': 0,
        'E': 0
    }
    sender_list = []


def parse_message(serial_msg):
    '''
    Takes in serial input from arduino
    Returns: (<answer>, <iclicker_id>) or None if bad message
    '''
    string_msg = serial_msg.decode('utf-8').strip()
    if string_msg != '':
        # parse out the string message
        try:
            answer, iclicker_id = string_msg.split(':')
            return (answer, iclicker_id)
        except:
            return None
    return None


def get_ids(limit=None):
    '''
    if limit is not provided the function will return all available ids
    Returns <limit> number of ids ordered by most recent submission
    '''
    length = len(sender_list)
    if limit is None:
        limit = length
    return sender_list[length - limit:length]


def register_sender(iclicker_id):
    '''
    Takes in an iclicker_id and moves it to top of sender list
    to maintain most recently active iclickers
    '''
    try:  # try to remove if present
        sender_list.remove(iclicker_id)
    except:
        pass
    # add iclicker id to top of list
    sender_list.append(iclicker_id)


def ans():
    '''
    Prints a summary of iClicker answers
    collected so far.
    '''
    for k in map_answer_total:
        print(k, map_answer_total[k])


def execute_cmd(cmdstring):
    '''
    Parses commands from interactive prompt
    and calls the corresponding function.
    '''
    COMMANDS = ['freq', 'ans', 'ids', 'reset',
                'send', 'startdos', 'stopdos', 'quit']
    ERR = 'Invalid command'

    tokens = cmdstring.split()
    if tokens[0] not in COMMANDS:
        print(ERR)
        return

    if tokens[0] == 'quit':
        sys.exit(0)
    elif tokens[0] == 'reset':
        reset()
    elif tokens[0] == 'ans':
        ans()
    elif tokens[0] == 'ids':
        if len(tokens) > 1:
            if tokens[1].isdigit():
                get_ids(int(tokens[1]))
            else:
                print(ERR)
        else:
            get_ids()
    elif tokens[0] == 'freq':
        pass
    elif tokens[0] == 'send':
        pass
    elif tokens[0] == 'startdos':
        pass
    elif tokens[0] == 'stopdos':
        pass


def keyboard_listener():
    '''
    Waits for keyboard input.
    Should be in its own thread.
    '''
    global next_cmd
    next_cmd = input('> ')


def check_iclicker():
    '''
    Processes incoming iClicker messages
    if they exist.
    '''
    iclicker_message = parse_message(ser.readline())
    if iclicker_message is not None:
        answer, iclicker_id = iclicker_message
        # remove previous answer
        if iclicker_id in map_id_answer:
            prev_answer = map_id_answer[iclicker_id]
            map_answer_total[prev_answer] -= 1
        # add to total of current answer
        map_answer_total[answer] += 1
        map_id_answer[iclicker_id] = answer

        # add the iclicker to top of sender list
        register_sender(iclicker_id)


def check_keyboard():
    '''
    Processes keyboard input
    if any has been captured.
    '''
    global next_cmd
    if next_cmd is not None:
        execute_cmd(next_cmd)
        next_cmd = None
        # Restart keyboard listener
        threading.Thread(target=keyboard_listener).start()


# Establish connection to Arduino transceiver
ser = serial.Serial('/dev/tty.usbmodem14141', 115200)
# Start listening to keyboard
threading.Thread(target=keyboard_listener).start()
# Main loop
while True:
    check_iclicker()
    check_keyboard()
    sleep(.1)
