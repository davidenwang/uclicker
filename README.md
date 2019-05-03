# uClicker
CS 460 Security Lab Final Project by Eric Lee (ericdl2), Ray Sun (raysun2), Allen Tang (allenjt2), and David Wang (davidew2).

Emulates an iClicker or many iClickers, and sniffs all iClicker answers sent in the room.

## Description

We created a single binary that implements the functionality of both a fake iClicker and a fake base station. When the binary is launched, it will provide an interactive prompt. While running, the binary will listen to and save any iClicker messages sent through the air (using an attached Adafruit Feather M0 radio running our Arduino sketch), on a given iClicker frequency.

As an alternative to the interactive prompt, the user can launch a simple GUI interface that resembles an iClicker.

## Commands
The interactive prompt will accept the following commands:
- freq [ID]: Sets the iClicker frequency for listening and sending. This should always be the first command used.
  - ID: String of 2 characters from A-D (e.g. "AB")
- ans: Display a summary of all real answers sent (a count for each choice, A-E)
- ids [LIMIT]: List all iClicker IDs that have sent messages
  - LIMIT: Optional argument, an integer. If given, will only display the LIMIT most recent IDs
- reset: Clear the stored iClicker messages (e.g. for a new multiple choice question)
- gen: Generate a random valid iClicker ID
- send [ID] [CHOICE]: Send an iClicker message with iClicker id ID and multiple choice answer CHOICE
  - ID: String of 8 characters from A-F, 0-9
  - CHOICE: A character from A-E
- startdos: Start spamming the base station with iClicker messages
- stopdos: Stop spamming
- quit: Quits the binary and stops listening to iClicker messages (and stops DOSing if active).

## Acknowledgements
- Used the iSkipper repo as a library - https://github.com/wizard97/iSkipper/  
- Used an Adafruit Feather M0 Radio with RFM69 Packet Radio - https://learn.adafruit.com/adafruit-feather-m0-radio-with-rfm69-packet-radio/overview