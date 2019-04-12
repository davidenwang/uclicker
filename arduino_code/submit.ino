#include "iClickerEmulator.h"
#include <string.h>

/* UPDATE THESE FOR YOUR PARTICULAR BOARD */
#define IS_RFM69HW false //make true if using w version
#define IRQ_PIN 3 // This is 3 on adafruit feather
#define CSN 8 // This is 8 on adafruit feather
/* END THINGS YOU MUST UPDATE */

iClickerEmulator clicker(CSN, IRQ_PIN, digitalPinToInterrupt(IRQ_PIN), IS_RFM69HW);


// This will flood base station with random answers under random ids
// Use at your own risk...

void setup()
{
    Serial.begin(115200);
    clicker.begin(iClickerChannels::AA); //set channel to AA
    //clicker.dumpRegisters();
}


void loop()
{
  char hexstr[4];
  uint8_t id[4];
  for (int i = 0; i < 4; i++){
    hexstr[i] = Serial.read();
    id[i] = (uint8_t)hexstr[i];
  }
  //iClickerEmulator::randomId(id);
  ans_num = Serial.read();
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
  clicker.submitAnswer(id, ans, false, 100);

  //delay(1000);

}
