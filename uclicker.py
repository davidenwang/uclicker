from time import sleep
import serial
import threading
import sys


class Question():
    '''
    Holds all captured information
    for a single iClicker question
    '''

    def __init__(self):
        # set up map from iclicker_id -> current_answer
        self.map_id_answer = {}
        # maps from answer string to current total
        self.map_answer_total = {
            'A': 0,
            'B': 0,
            'C': 0,
            'D': 0,
            'E': 0
        }
        # queue which stores most recent iclicker ids
        self.sender_list = []

    def register_sender(self, iclicker_id):
        '''
        Takes in an iclicker_id and moves it to top of sender list
        to maintain most recently active iclickers
        '''
        # try to remove if present
        try:
            self.sender_list.remove(iclicker_id)
        except:
            pass
        # add iclicker id to top of list
        self.sender_list.append(iclicker_id)

    def save_message(self, iclicker_message):
        '''
        Processes an incoming iClicker message
        if it exists.
        '''
        if iclicker_message is not None:
            answer, iclicker_id = iclicker_message
            # remove previous answer
            if iclicker_id in self.map_id_answer:
                prev_answer = self.map_id_answer[iclicker_id]
                self.map_answer_total[prev_answer] -= 1
            # add to total of current answer
            self.map_answer_total[answer] += 1
            self.map_id_answer[iclicker_id] = answer

            # add the iclicker to top of sender list
            self.register_sender(iclicker_id)

    def get_ids(self, limit=None):
        '''
        if limit is not provided the function will return all available ids
        Returns <limit> number of ids ordered by most recent submission
        '''
        length = len(self.sender_list)
        if limit is None:
            limit = length
        return self.sender_list[length - limit:length]

    def ans(self):
        '''
        Prints a summary of iClicker answers
        collected so far.
        '''
        for k in self.map_answer_total:
            print(k, self.map_answer_total[k])


class Session():
    '''
    Runs a uClicker session
    with interactive prompt
    '''
    COMMANDS = ['freq', 'ans', 'ids', 'reset',
                'send', 'startdos', 'stopdos', 'quit']
    ERR = 'Invalid command'

    def __init__(self):
        # Information captured for each iClicker question
        self.questions = [Question()]
        # Recently captured keyboard input
        self.next_cmd = None
        # Establish connection to Arduino transceiver
        self.ser = serial.Serial('/dev/tty.usbmodem14141', 115200)
        # Start listening to keyboard
        threading.Thread(target=self.keyboard_listener).start()

    def loop(self):
        '''
        Main loop
        '''
        while True:
            self.check_iclicker()
            self.check_keyboard()
            sleep(.1)

    def check_iclicker(self):
        '''
        Checks for an incoming iClicker message
        and passes it to the current Question
        '''
        iclicker_message = self.parse_message(self.ser.readline())
        self.questions[-1].save_message(iclicker_message)

    def check_keyboard(self):
        '''
        Processes keyboard input
        if any has been captured.
        '''
        if self.next_cmd is not None:
            self.execute_cmd(self.next_cmd)
            self.next_cmd = None
            # Restart keyboard listener
            threading.Thread(target=self.keyboard_listener).start()

    def execute_cmd(self, cmdstring):
        '''
        Parses commands from interactive prompt
        and calls the corresponding function.
        '''
        tokens = cmdstring.split()
        if tokens[0] not in self.COMMANDS:
            print(self.ERR)
            return

        if tokens[0] == 'quit':
            sys.exit(0)
        elif tokens[0] == 'reset':
            self.reset()
        elif tokens[0] == 'ans':
            self.ans()
        elif tokens[0] == 'ids':
            if len(tokens) > 1:
                if tokens[1].isdigit():
                    self.ids(int(tokens[1]))
                else:
                    print(self.ERR)
            else:
                self.ids()
        elif tokens[0] == 'freq':
            pass
        elif tokens[0] == 'send':
            pass
        elif tokens[0] == 'startdos':
            pass
        elif tokens[0] == 'stopdos':
            pass

    def reset(self):
        '''
        Move on to a new Question
        '''
        self.questions.append(Question())

    def ans(self):
        '''
        Prints the captured answers for the current question
        '''
        self.questions[-1].ans()

    def ids(self, limit=None):
        '''
        Prints the captured iClicker IDs for the current question
        '''
        ids = self.questions[-1].get_ids(limit)
        for id in ids:
            print(id)

    def keyboard_listener(self):
        '''
        Waits for keyboard input.
        Should be in its own thread.
        '''
        self.next_cmd = input('> ')

    @staticmethod
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
