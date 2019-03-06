// stretchy = pneumograph

#define USE_ARDUINO_INTERRUPTS true    // Set-up low-level interrupts for most acurate BPM math.
#include <PulseSensorPlayground.h>     

const int stretchyPin = A0;
const int heartRatePin = A1;
const int heartRateThreshold = 550;

int stretchyVal = 0;
int bpm = 0;
PulseSensorPlayground pulseSensor;

void setup() {
  // set up serial
  Serial.begin(9600);  

  // set up heart rate monitor
  pulseSensor.analogInput(heartRatePin);   
  pulseSensor.setThreshold(heartRateThreshold);   

  // start heart rate monitor
  if (!pulseSensor.begin()) { Serial.println("Heart rate monitor could not start"); }
}

void loop() {
  
  stretchyVal = analogRead(stretchyPin);

  //Serial.println("Stretchy");
  Serial.println(stretchyVal);

  bpm = pulseSensor.getBeatsPerMinute();
  //Serial.println("Heart rate");
  Serial.println(bpm);
  
  delay(20);
}

