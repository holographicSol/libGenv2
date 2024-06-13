// Precision Geiger Counter written by Benjamin Jack Cullen

// Include the correct display library
// For a connection via I2C using Wire include
#include <Wire.h> // Only needed for Arduino 1.6.5 and earlier
#include <SSD1306Wire.h> // legacy include: `#include "SSD1306.h"`
#include <math.h>
#include <stdio.h>
#include <Arduino.h>
#include <SPI.h>
#include <HardwareSerial.h>
#include <printf.h>
#include <RF24.h>
#include <OLEDDisplayUi.h>
#include <stdlib.h>

// memory limitations require counts log max.
// on esp32 a maxcount of 100 should mean main loop time will be half the time of main loop time with max count 10240.
// it may be preferrable to have a max count <=100 (cpm 100 considered unsafe to humans) if all you are interested in
// is reacting to a precise cpm reading within the shortest time you can. if instead you are actually trying to get as
// precise (arduino is not medical/military grade) a reading as you can at any level of activity then you may increase
// max count from 10240 providing you beleive there is the memory and performance available on the MCU your building for.
#define max_count       100
#define warning_level_0 99 // warn at this cpm 

#define CE_PIN     25 // radio can use tx
#define CSN_PIN    26 // radio can use rx
#define GEIGER_PIN 27

// on esp32 if broadcast false then precision is to approximately 40 microseconds at around 35 cpm with max_count 100.
// on esp32 if broadcast true then precision is to approximately 700 microseconds at around 35 cpm with max_count 100.
volatile bool broadcast = true;

RF24 radio(CE_PIN, CSN_PIN);
SSD1306Wire display(0x3c, SDA, SCL);
OLEDDisplayUi ui(&display);

// Radio Addresses
uint64_t address[6] = { 0x7878787878LL,
                        0xB3B4B5B6F1LL,
                        0xB3B4B5B6CDLL,
                        0xB3B4B5B6A3LL,
                        0xB3B4B5B60FLL,
                        0xB3B4B5B605LL };

// Transmission Payload
struct PayloadStruct {
  unsigned long nodeID;
  unsigned long payloadID;
  char message[10];
};
PayloadStruct payload;


// Geiger Counter
struct GCStruct {
  double countsArray[max_count]; // stores each impulse as timestamps
  double countsArrayTemp[max_count]; // temporarily stores timestamps
  bool impulse = false; // sets true each interrupt on geiger counter pin
  bool warmup = true; // sets false after first 60 seconds have passed
  unsigned long counts; // stores counts and resets to zero every minute
  unsigned long precisionCounts = 0; // stores how many elements are in counts array
  unsigned long CPM = 0;
  char CPM_str[12];
  float uSvh = 0; // stores the micro-Sievert/hour for units of radiation dosing
  unsigned long maxPeriod = 60; // maximum logging period in seconds.
  unsigned long countsIter;
};
GCStruct geigerCounter;

struct TimeStruct {
  double previousTimestamp; // a placeholder for a previous time
  unsigned long mainLoopTimeTaken; // necessary to count time less than a second
  unsigned long mainLoopTimeStart; // necessary for loop time taken
  double subTime;
  double subTimeDivided;
  double interTimeDivided;
  unsigned long currentMilliSecond;
  double timestamp;
  double interTime;
  unsigned long currentSecond;
};
TimeStruct timeData;

// create a timestamp
double currentTime() {
  if (timeData.subTime >= 1000) {
      timeData.subTime = 0;
      timeData.currentMilliSecond++;
      if (timeData.currentMilliSecond >= 1000) {
          timeData.currentMilliSecond = 0;
          timeData.currentSecond++;
      }
  }
  timeData.subTime += (timeData.mainLoopTimeTaken);
  timeData.subTimeDivided = timeData.subTime / 1000000;
  return timeData.currentSecond+timeData.subTimeDivided;
}

// create an intermediary timestamp
double interCurrentTime() {
  timeData.interTime = (micros() - timeData.mainLoopTimeStart);
  timeData.interTimeDivided = timeData.interTime / 1000000;
  return timeData.timestamp+timeData.interTimeDivided;
}

// subprocedure for capturing events from Geiger Kit
void tubeImpulseISR() {
  geigerCounter.impulse = true;
  if (geigerCounter.countsIter < max_count) {geigerCounter.countsIter++;}
  else {geigerCounter.countsIter=0;}

  // add current timestamp (per loop) to timestamps in array
  geigerCounter.countsArray[geigerCounter.countsIter] = timeData.timestamp;

  // compare current (unique) timestamp to timestamps in array
  // geigerCounter.countsArray[geigerCounter.countsIter] = interCurrentTime();
}

void BGTubeImpulseISR() {
  geigerCounter.counts++;
  geigerCounter.impulse = true;
}

// frame to be displayed on ssd1306 182x64
void GC_Measurements(OLEDDisplay* display, OLEDDisplayUiState* state, int16_t x, int16_t y) {
    display->setTextAlignment(TEXT_ALIGN_CENTER);
    if (geigerCounter.CPM >= warning_level_0) { display->drawString(display->getWidth()/2, 0, "WARNING");}
    else {display->drawString(display->getWidth()/2, 0, String(timeData.mainLoopTimeTaken));}
    display->drawString(display->getWidth()/2, 25, "cpm");
    display->drawString(display->getWidth()/2, 13, String(geigerCounter.CPM));
    display->drawString(display->getWidth()/2, display->getHeight()-10, "uSv/h");
    display->drawString(display->getWidth()/2, display->getHeight()-22, String(geigerCounter.uSvh));
}

// this array keeps function pointers to all frames are the single views that slide in
FrameCallback frames[] = { GC_Measurements };
int frameCount = 1;

void setup() {

  // serial
  Serial.begin(115200);

  // display
  display.init();
  display.flipScreenVertically();
  ui.setTargetFPS(60);
  ui.setFrames(frames, frameCount);
  display.setContrast(255);
  display.setFont(ArialMT_Plain_10);
  display.cls();
  display.println("starting..");
  ui.disableAllIndicators();

  // system
  Serial.print("XTAL Crystal Frequency: ");
  Serial.print(getXtalFrequencyMhz());
  Serial.println(" MHz");
  Serial.print("CPU Frequency: ");
  Serial.print(getCpuFrequencyMhz());
  Serial.println(" MHz");
  Serial.print("APB Bus Frequency: ");
  Serial.print(getApbFrequency());
  Serial.println(" Hz");

  // radio
  if (!radio.begin()) {
    Serial.println(F("radio hardware is not responding!!"));
    while (1) {}
  }
  radio.flush_rx();
  radio.flush_tx();
  radio.setPALevel(RF24_PA_LOW); // RF24_PA_MAX is default.
  radio.setPayloadSize(sizeof(payload)); // 2x int datatype occupy 8 bytes
  Serial.println("Channel:  " + String(radio.getChannel()));
  Serial.println("Data Rate:" + String(radio.getDataRate()));
  Serial.println("PA Level: " + String(radio.getPALevel()));
  radio.openWritingPipe(address[1]); // always uses pipe 0
  radio.openReadingPipe(1, address[0]); // using pipe 1
  radio.stopListening();

  attachInterrupt(GEIGER_PIN, tubeImpulseISR, FALLING); // define external interrupts
}


void loop() {
  // measure this loop time so we know how quickly items are added/removed from arrays
  timeData.mainLoopTimeStart = micros();

  // set current timestamp to be used this loop same millisecond+- depending on loop speed.
  timeData.timestamp = currentTime();

  // Serial.print("currentTime: "); Serial.println(timeData.currentTime, 12);

  // check if impulse
  if (geigerCounter.impulse == true) {
    geigerCounter.impulse = false;

    if (broadcast == true) {
      // transmit counts seperately from CPM, so that the receiver(s) can react to counts as they occur
      memset(payload.message, 0, 12);
      memcpy(payload.message, "X", 1);
      payload.payloadID = 1000;
      radio.write(&payload, sizeof(payload));
    }
  }

  // set previous time each minute
  if ((timeData.timestamp - timeData.previousTimestamp) > geigerCounter.maxPeriod) {
    Serial.print("cycle expired: "); Serial.println(timeData.timestamp, sizeof(timeData.timestamp));
    timeData.previousTimestamp = timeData.timestamp;
    geigerCounter.warmup = false; // completed 60 second warmup required for precision
  }
  // step through the array and remove expired impulses by exluding them from our new array.
  geigerCounter.precisionCounts = 0;
  memset(geigerCounter.countsArrayTemp, 0, sizeof(geigerCounter.countsArrayTemp));
  for (int i = 0; i < max_count; i++) {
    if (geigerCounter.countsArray[i] >= 1) { // only entertain non zero elements
      // compare current timestamp (per loop) to timestamps in array
      if (((timeData.timestamp - (geigerCounter.countsArray[i])) > geigerCounter.maxPeriod)) {
      // compare current (unique) timestamp to timestamps in array
      // if (((interCurrentTime() - (geigerCounter.countsArray[i])) > geigerCounter.maxPeriod)) {
        geigerCounter.countsArray[i] = 0;
        }
      else {
        geigerCounter.precisionCounts++; // non expired counters increment the precision counter
        geigerCounter.countsArrayTemp[i] = geigerCounter.countsArray[i]; // store non expired
      }
    }
  }
  memset(geigerCounter.countsArray, 0, sizeof(geigerCounter.countsArray));
  memcpy(geigerCounter.countsArray, geigerCounter.countsArrayTemp, sizeof(geigerCounter.countsArray));

  // then calculate usv/h
  geigerCounter.CPM = geigerCounter.precisionCounts;
  geigerCounter.uSvh = geigerCounter.CPM * 0.00332;

  // refresh ssd1306 128x64 display
  ui.update();

  // transmit the results
  if (broadcast == true) {
    memset(payload.message, 0, 12);
    memset(geigerCounter.CPM_str, 0, 12);
    dtostrf(geigerCounter.CPM, 0, 4, geigerCounter.CPM_str);
    memcpy(payload.message, geigerCounter.CPM_str, sizeof(geigerCounter.CPM_str));
    payload.payloadID = 1111;
    radio.write(&payload, sizeof(payload));
  }

  // store time taken to complete
  timeData.mainLoopTimeTaken = micros() - timeData.mainLoopTimeStart;
  // Serial.println("timeData.mainLoopTimeTaken:" + String(timeData.mainLoopTimeTaken));
}

