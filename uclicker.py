from time import sleep
import serial
import threading
import sys
import argparse
import random


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
        for k in sorted(self.map_answer_total):
            print(k, self.map_answer_total[k])


class Session():
    '''
    Runs a uClicker session
    with interactive prompt
    '''
    ERR = 'Invalid command'

    def __init__(self, port):
        '''
        Initializes the session and
        connects to the transceiver if port is given.
        '''

        # Information captured for each iClicker question
        self.questions = [Question()]
        # Recently captured keyboard input
        self.next_cmd = None
        # Recently captured iClicker message
        self.next_msg = None

        # Start listening to keyboard
        threading.Thread(target=self.keyboard_listener).start()

        # Establish connection to Arduino transceiver
        self.ser = serial.Serial(port, 115200) if port else None
        if self.ser is not None:
            threading.Thread(target=self.iclicker_listener).start()

    def loop(self):
        '''
        Main loop
        '''
        while True:
            self.check_keyboard()
            self.check_iclicker()
            sleep(.1)

    def check_iclicker(self):
        '''
        Checks for an incoming iClicker message
        and passes it to the current Question
        '''
        if self.next_msg is not None:
            iclicker_message = self.next_msg
            self.questions[-1].save_message(iclicker_message)
            # Restart iClicker listener
            self.next_msg = None
            threading.Thread(target=self.iclicker_listener).start()

    def check_keyboard(self):
        '''
        Processes keyboard input
        if any has been captured.
        '''
        if self.next_cmd is not None:
            self.execute_cmd(self.next_cmd)
            # Restart keyboard listener
            self.next_cmd = None
            threading.Thread(target=self.keyboard_listener).start()

    def execute_cmd(self, cmdstring):
        '''
        Parses commands from interactive prompt
        and calls the corresponding function.
        '''
        tokens = cmdstring.split()

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
        elif tokens[0] == 'gen':
            print(self.generate_id())
        else:
            print(self.ERR)

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
        self.next_cmd = input('(uclicker)> ')

    def iclicker_listener(self):
        '''
        Waits for iClicker messages.
        Should be in its own thread.
        '''
        self.next_msg = self.parse_message(self.ser.readline())

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

    @staticmethod
    def generate_id():
        '''
        Generates a random iClicker ID.
        iClicker IDs are 4 bytes in hexadecimal,
        where the last byte is an XOR checksum of the first three.
        '''
        def x(i):
            return (hex(i)[2:]).upper().zfill(2)

        b1 = random.randint(0, 255)
        b2 = random.randint(0, 255)
        b3 = random.randint(0, 255)
        b4 = b1 ^ b2 ^ b3
        return ' '.join([x(i) for i in [b1, b2, b3, b4]])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port')
    args = parser.parse_args()

    session = Session(args.port)
    session.loop()
