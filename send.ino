// Precision Geiger Counter written by Benjamin Jack Cullen

// Include the correct display library
// For a connection via I2C using Wire include
#include <Wire.h>         // Only needed for Arduino 1.6.5 and earlier
#include "SSD1306Wire.h"  // legacy include: `#include "SSD1306.h"`
#include <math.h>
#include <stdio.h>
#include <Arduino.h>
#include <SPI.h>
#include <HardwareSerial.h>
#include "printf.h"
#include "RF24.h"
#include "OLEDDisplayUi.h"
#include "RTClib.h"
#include <stdlib.h>

#define max_count 10240  // memory limitations require counts log max (todo: increase max) HAS TO BE THE SAME VALUE AS GCTIME AND GCTTIME!
#define CE_PIN 25        // radio can use tx
#define CSN_PIN 26       // radio can use rx
#define GEIGER_PIN 27

volatile bool state = LOW;

RTC_DS1307 rtc;
RF24 radio(CE_PIN, CSN_PIN);
SSD1306Wire display(0x3c, SDA, SCL);
OLEDDisplayUi ui(&display);

char serialBuffer[16];

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
  int countsArray[10240];             // stores each impulse as micros
  int countsArrayTemp[10240];         // temporarily stores micros from countsArray that have not yet expired
  bool impulse = false;               // sets true each interrupt on geiger counter pin
  bool warmup = true;                 // sets false after first 60 seconds have passed
  unsigned long counts;               // stores counts and resets to zero every minute
  unsigned long precisionCounts = 0;  // stores how many elements are in counts array
  unsigned long precisionCPM = 0;     // stores cpm value according to precisionCounts (should always be equal to precisionCounts because we are not estimating)
  char precisionCPM_str[12];
  float precisioncUSVH = 0;           // stores the micro-Sievert/hour for units of radiation dosing
  unsigned long maxPeriod = 60;       // maximum logging period in seconds (microseconds). Should always be 60 (60,000,000 for one minute)
  unsigned long CPM_BURST_GUAGE_LOG_PERIOD = 15000; //Logging period in milliseconds, recommended value 15000-60000.
  unsigned long CPM_BURST_GUAGE_MAX_PERIOD = 60000; //Maximum logging period without modifying this sketch. default 60000.
  unsigned long cpm_high;
  unsigned long cpm_low;
  unsigned long previousMillis; //variable for time measurement
  unsigned long currentMillis;
  unsigned int multiplier;      //variable for calculation CPM in this sketch
  unsigned int cpm_arr_max = 3;
  unsigned int cpm_arr_itter = 0;
  int cpms[6]={0,0,0,0,0,0};
  float cpm_average;
  int GCMODE = 2;
  signed long previousCounts;
};
GCStruct geigerCounter;

struct TimeStruct {
  double UNIX_MICRO_TIME_I;
  double PREVIOUS_UNIX_MICRO_TIME_I;
  char UNIX_MICRO_TIME[100];
  char PREVIOUS_UNIX_MICRO_TIME[100];
  double microsI;
  double microsF;
  char microsStr[54];
  char microsStrTmp[54];
  char unixtStr[54];
  double currentTime;                          // a placeholder for a current time (optionally used)
  double previousTime;                         // a placeholder for a previous time (optionally used)
  unsigned long microLoopTimeTaken;                   // necessary to count time less than a second (must be updated every loop of main)
  unsigned long microLoopTimeStart;                   // necessary for loop time taken (must be recorded every loop of main)
  unsigned long microAccumulator;                     // accumulates loop time take and resets at threshold (must accumulate every loop of main)
  unsigned long microAccumulatorThreshold = 1000000;  // micro accumulator resets to zero when the threshold is reached (10^6 or any other number say if you dont need current time)
  double microseconds = 0;
  unsigned long microMultiplier = 0;
  int previousSecond = 0;
  char microsStrTag[4] = ".";
};
TimeStruct timeData;

// concatinates unix time and micros to make timestamps. requires loop time taken and accuracy and resolution is predicated upon loop time.
// time resolution greater than main loop time is not currently required so make the most of those seconds from the RTC by dividing them instead of using micros() which will overflow.
// any reference to microseconds in this function is temporary and will be refactored as these fractions of seconds are not microseconds, nor are they milliseconds, but they are divisions
// of time smaller than milliseconds and greater than nano seconds. there are other ways like using the frequencies from other clocks but it will still be imprecise and then ultimately
// you wont update CPM any faster than your main loop time anyway. 
double current_SUBSECOND_UNIXTIME() {
  DateTime time = rtc.now();
  dtostrf((unsigned long)time.unixtime(), 0, 0, timeData.unixtStr);
  if (timeData.previousSecond != time.second()) {
    timeData.previousSecond = time.second();
    timeData.microMultiplier = 1;
    timeData.microseconds = 0;
  }
  else {
    timeData.microseconds+=(double)((1.0*timeData.microMultiplier) / 1000000.0);
    timeData.microMultiplier++;
  }
  strcpy(timeData.UNIX_MICRO_TIME, timeData.unixtStr);
  timeData.microsI = timeData.microseconds;
  memset(timeData.microsStr, 0, sizeof(timeData.microsStr));
  memset(timeData.microsStrTmp, 0, sizeof(timeData.microsStrTmp));
  sprintf(timeData.microsStrTmp,"%.10f", timeData.microsI);
  memmove(timeData.microsStrTmp, timeData.microsStrTmp+2, strlen(timeData.microsStrTmp));
  timeData.microsStr[0] = timeData.microsStrTag[0]; // put a period at the beginning of our new string
  strcat(timeData.microsStr, timeData.microsStrTmp); // copy micros into new string after the period
  strcat(timeData.UNIX_MICRO_TIME, timeData.microsStr); // concatinate unix time with new string that looks suspiciously like a double
  // timeData.UNIX_MICRO_TIME_I = atof(timeData.UNIX_MICRO_TIME); // make the string an actual double
  // Serial.print("SUBSECOND_UNIXTIME: "); Serial.println(timeData.UNIX_MICRO_TIME_I, 12);
  return timeData.UNIX_MICRO_TIME_I;
}

// subprocedure for capturing events from Geiger Kit
void tube_impulse() {
  geigerCounter.counts++;
  geigerCounter.impulse = true;
}

// frame to be displayed on ssd1306 182x64
void GC_Measurements(OLEDDisplay* display, OLEDDisplayUiState* state, int16_t x, int16_t y) {
  if (geigerCounter.GCMODE == 2) {
    display->drawString(0, 0, "Precision: " + String(timeData.microLoopTimeTaken));
    display->drawString(0, 15, "CPM:   " + String(geigerCounter.precisionCPM));
    display->drawString(0, 25, "uSv/h:  " + String(geigerCounter.precisioncUSVH));
    display->drawString(0, 35, "Epoch: " + String(geigerCounter.maxPeriod - (timeData.currentTime - timeData.previousTime)));
  }
  else if (geigerCounter.GCMODE == 3) {
    display->drawString(0, 0, "Burst Guage: " + String(timeData.microLoopTimeTaken));
    display->drawString(0, 15, "CPM:   " + String(geigerCounter.precisionCPM));
    display->drawString(0, 25, "uSv/h:  " + String(geigerCounter.precisioncUSVH));
    display->drawString(0, 35, "Epoch: " + String(geigerCounter.CPM_BURST_GUAGE_LOG_PERIOD - (geigerCounter.currentMillis - geigerCounter.previousMillis)));
  }
}

// this array keeps function pointers to all frames are the single views that slide in
FrameCallback frames[] = { GC_Measurements };
int frameCount = 1;

void setup() {

  // serial
  Serial.begin(115200);

  // rtc
  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    Serial.flush();
    while (1) delay(10);
  }
  if (! rtc.isrunning()) {
    Serial.println("RTC is NOT running, let's set the time!");
  }
  // rtc.adjust(DateTime(2024, 6, 9, 16, 15, 0)); // Y M D H MS. uncomment this thine during compile time only if the clock is not already set

  // display
  display.init();
  display.flipScreenVertically();
  ui.setTargetFPS(60);
  ui.setFrames(frames, frameCount);
  display.setContrast(255);
  display.setFont(ArialMT_Plain_10);
  display.cls();
  display.println("starting..");

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
  radio.setPALevel(RF24_PA_LOW);          // RF24_PA_MAX is default.
  radio.setPayloadSize(sizeof(payload));  // 2x int datatype occupy 8 bytes
  Serial.println("Channel:  " + String(radio.getChannel()));
  Serial.println("Data Rate:" + String(radio.getDataRate()));
  Serial.println("PA Level: " + String(radio.getPALevel()));
  radio.openWritingPipe(address[1]);     // always uses pipe 0
  radio.openReadingPipe(1, address[0]);  // using pipe 1
  radio.stopListening();

  // attach geiger counter pin to interrupts last
  attachInterrupt(GEIGER_PIN, tube_impulse, FALLING);  //define external interrupts
}


void loop() {
  if (state) {
      Serial.println("mode: " + String(geigerCounter.GCMODE));
      state = false;//reset interrupt flag
  }
  // set current timestamp to be used this loop as UNIXTIME+MICROSECONDTIME. this is not actual time like a clock.
  timeData.currentTime = current_SUBSECOND_UNIXTIME();
  
  // store current time in micros to measure this loop time so we know how quickly items are added/removed from counts arrays
  timeData.microLoopTimeStart = micros();
  
  // use precision cpm counter (measures actual cpm to as higher resolution as it can per minute)
  geigerCounter.precisionCounts = 20000;
  // if (geigerCounter.precisionCounts < 10240-1) {
  if (geigerCounter.GCMODE == 2) {

    // reset counts every minute
    if ((timeData.currentTime - timeData.previousTime) > geigerCounter.maxPeriod) {
      Serial.print("cycle expired: "); Serial.println(timeData.currentTime, 12);
      timeData.previousTime = timeData.currentTime;
      geigerCounter.counts = 0;      // resets every 60 seconds
      geigerCounter.warmup = false;  // completed 60 second warmup required for precision
    }
    // check if impulse
    if (geigerCounter.impulse == true) {
      geigerCounter.impulse = false;

      // add the impulse as a timestamp to array
      geigerCounter.countsArray[geigerCounter.counts] = timeData.currentTime;  // add count to array as micros    TOD: replace counts with another method of indexing

      // transmit counts seperately from CPM, so that the receiver(s) can react to counts (with leds and sound) as they happen, as you would expect from a 'local' geiger counter.
      memset(payload.message, 0, 12);
      memcpy(payload.message, "X", 1);
      payload.payloadID = 1000;
      radio.write(&payload, sizeof(payload));
    }
    // step through the array and remove expired impulses by exluding them from our new array.
    geigerCounter.precisionCounts = 0;
    memset(geigerCounter.countsArrayTemp, 0, sizeof(geigerCounter.countsArrayTemp));
    for (int i = 0; i < max_count; i++) {
      if (geigerCounter.countsArray[i] >= 1) { // only entertain non zero elements
        if (((timeData.currentTime - (geigerCounter.countsArray[i])) > geigerCounter.maxPeriod)) {
          geigerCounter.countsArray[i] = 0;
          }
        else {
          geigerCounter.precisionCounts++; // non expired counters increment the precision counter
          geigerCounter.countsArrayTemp[i] = geigerCounter.countsArray[i];  // non expired counters go into the new temporary array
        }
      }
    }
    memset(geigerCounter.countsArray, 0, sizeof(geigerCounter.countsArray));
    memcpy(geigerCounter.countsArray, geigerCounter.countsArrayTemp, sizeof(geigerCounter.countsArray));

    // then calculate usv/h
    geigerCounter.precisionCPM = geigerCounter.precisionCounts;
    geigerCounter.precisioncUSVH = geigerCounter.precisionCPM * 0.00332;
  }
  
  // cpm burst guage (estimates cpm reactively)
  else if (geigerCounter.GCMODE == 3) {
    // cpm burst guage
    geigerCounter.CPM_BURST_GUAGE_LOG_PERIOD = 15000;
    geigerCounter.CPM_BURST_GUAGE_MAX_PERIOD = 60000;
    if (geigerCounter.counts >= 1) {
      geigerCounter.CPM_BURST_GUAGE_LOG_PERIOD = 15000 / geigerCounter.counts;
      geigerCounter.CPM_BURST_GUAGE_MAX_PERIOD = 60000 / geigerCounter.counts;
      geigerCounter.CPM_BURST_GUAGE_LOG_PERIOD = (unsigned long)(geigerCounter.CPM_BURST_GUAGE_LOG_PERIOD);
      geigerCounter.CPM_BURST_GUAGE_MAX_PERIOD = (unsigned long)(geigerCounter.CPM_BURST_GUAGE_MAX_PERIOD);
    }
    // store highs and lows
    if (geigerCounter.precisionCPM > geigerCounter.cpm_high) {geigerCounter.cpm_high = geigerCounter.precisionCPM;};
    if ((geigerCounter.precisionCPM < geigerCounter.cpm_low) && (geigerCounter.precisionCPM >= 1)) {geigerCounter.cpm_low = geigerCounter.precisionCPM;};
    // check the variable time window
    geigerCounter.currentMillis = millis();
    if(geigerCounter.currentMillis - geigerCounter.previousMillis > geigerCounter.CPM_BURST_GUAGE_LOG_PERIOD){
      geigerCounter.previousMillis = geigerCounter.currentMillis;
      geigerCounter.multiplier = geigerCounter.CPM_BURST_GUAGE_MAX_PERIOD / geigerCounter.CPM_BURST_GUAGE_LOG_PERIOD; // calculating multiplier, depend on your log period
      geigerCounter.multiplier = (unsigned int)(geigerCounter.multiplier);
      geigerCounter.precisionCPM = geigerCounter.counts * geigerCounter.multiplier; /// multiply cpm by 0.003321969697 for geiger muller tube J305
      geigerCounter.precisioncUSVH = geigerCounter.precisionCPM * 0.00332;
      int i;
      float sum = 0;
      if (geigerCounter.cpm_arr_itter <= geigerCounter.cpm_arr_max) {geigerCounter.cpms[geigerCounter.cpm_arr_itter]=geigerCounter.cpm_high; Serial.println("[" + String(geigerCounter.cpm_arr_itter) + "] " + String(geigerCounter.cpms[geigerCounter.cpm_arr_itter])); geigerCounter.cpm_arr_itter++;}
      if (geigerCounter.cpm_arr_itter == geigerCounter.cpm_arr_max) {
        // average between lowest high and highest high (so far the more prefferable)
        for(i = 0; i < 3; i++) {sum = sum + geigerCounter.cpms[i];}
        geigerCounter.cpm_average = sum/3.0;
        geigerCounter.cpm_average = (long int)geigerCounter.cpm_average;
        Serial.println("cpm_average: " + String(geigerCounter.cpm_average));
        geigerCounter.precisioncUSVH = geigerCounter.cpm_average * 0.00332;
        geigerCounter.cpm_high=0; geigerCounter.cpm_low=0; geigerCounter.cpm_arr_itter = 0;
      }
    geigerCounter.counts = 0;
    }
  }

  // refresh ssd1306 128x64 display
  ui.update();

  // store time taken to complete
  timeData.microLoopTimeTaken = micros() - timeData.microLoopTimeStart;
}

