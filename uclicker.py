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

'''
Called to reset all data structures for use on new multiple choice question
'''


def reset():
    map_id_answer = {}
    map_answer_total = {
        'A': 0,
        'B': 0,
        'C': 0,
        'D': 0,
        'E': 0
    }
    sender_list = []


'''
Takes in serial input from arduino
Returns: (<answer>, <iclicker_id>) or None if bad message
'''


def parse_message(serial_msg):
    string_msg = serial_msg.decode('utf-8').strip()
    if string_msg != '':
        # parse out the string message
        try:
            answer, iclicker_id = string_msg.split(':')
            return (answer, iclicker_id)
        except:
            return None
    return None


'''
if limit is not provided the function will return all available ids
Returns <limit> number of ids ordered by most recent submission
'''


def get_ids(limit=None):
    length = len(sender_list)
    if limit is None:
        limit = length
    return sender_list[length - limit:length]


'''
Takes in an iclicker_id and moves it to top of sender list
to maintain most recently active iclickers
'''


def register_sender(iclicker_id):
    try:  # try to remove if present
        sender_list.remove(iclicker_id)
    except:
        pass
    # add iclicker id to top of list
    sender_list.append(iclicker_id)


def ans():
    for k in map_answer_total:
        print(k, map_answer_total[k])


def execute_cmd(cmdstring):
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


next_cmd = None


def keyboard_listener():
    global next_cmd
    next_cmd = input('> ')
    tokens = cmdstring.split()


ser = serial.Serial('/dev/tty.usbmodem14141', 115200)  # establish connection
threading.Thread(target=keyboard_listener).start()
while True:
    # Check iClicker
    iclicker_message = parse_message(ser.readline())
    if iclicker_message is not None:
        answer, iclicker_id = iclicker_message
        if iclicker_id in map_id_answer:  # remove previous answer
            prev_answer = map_id_answer[iclicker_id]
            map_answer_total[prev_answer] -= 1
        # add to total of current answer
        map_answer_total[answer] += 1
        map_id_answer[iclicker_id] = answer

        # add the iclicker to top of sender list
        register_sender(iclicker_id)

        # prints out all the data
        print()
        print("active clickers:", get_ids())
        print("answers:", map_answer_total)

    # Check keyboard
    if next_cmd is not None:
        execute_cmd(next_cmd)
        next_cmd = None
        threading.Thread(target=keyboard_listener).start()

    sleep(.1)
