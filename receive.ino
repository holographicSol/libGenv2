// Precision Geiger Counter written by Benjamin Jack Cullen

#include "SSD1306Wire.h" // legacy include: `#include "SSD1306.h"`
#include <SPI.h>
#include "printf.h"
#include "RF24.h"
#include "OLEDDisplayUi.h"

#define max_count 100
#define CE_PIN 25 // radio can use tx
#define CSN_PIN 26 // radio can use rx
#define warning_level_0 99 // warn at this cpm 

SSD1306Wire display(0x3c, SDA, SCL);
OLEDDisplayUi ui ( &display );
RF24 radio(CE_PIN, CSN_PIN);

int led_red = 32; // led 32 RED 2 BLUE 4 GREEN
int speaker_0 = 33; // geiger counter sound

uint64_t address[6] = { 0x7878787878LL,
                        0xB3B4B5B6F1LL,
                        0xB3B4B5B6CDLL,
                        0xB3B4B5B6A3LL,
                        0xB3B4B5B60FLL,
                        0xB3B4B5B605LL };

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
  unsigned long counts = 0; // stores counts and resets to zero every minute
  unsigned long precisionCounts = 0; // stores how many elements are in counts array
  unsigned long CPM = 0;
  char CPM_str[12];
  float uSvh = 0; // stores the micro-Sievert/hour for units of radiation dosing
  unsigned long maxPeriod = 60000000; //Maximum logging period in microseconds
  unsigned long currentMicrosMain; // stores current
  unsigned long previousMicrosMain; // stores previous
  unsigned long precisionMicros; // stores main loop time
  char precisionMicros_str[12]; // stores main loop time
};
GCStruct geigerCounter;

// frame to be displayed on ssd1306 182x64
void GC_Measurements(OLEDDisplay* display, OLEDDisplayUiState* state, int16_t x, int16_t y) {
  display->setTextAlignment(TEXT_ALIGN_CENTER);
  if (geigerCounter.CPM >= warning_level_0) { display->drawString(display->getWidth()/2, 0, "WARNING");}
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
  while (!Serial) {
  }

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

  // geiger counter
  pinMode(led_red, OUTPUT);
  pinMode(speaker_0, OUTPUT);
  digitalWrite(speaker_0, LOW);
  digitalWrite(led_red, LOW); 

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
  radio.openWritingPipe(address[0]); // always uses pipe 0
  radio.openReadingPipe(1, address[1]); // using pipe 1
  radio.stopListening();
  radio.startListening(); // put radio in RX mode
  
} 

void loop() {

  // refresh ssd1306 128x64 display
  ui.update();

  // get payload
  uint8_t pipe;
  if (radio.available(&pipe)) { // is there a payload? get the pipe number that recieved it
    uint8_t bytes = radio.getPayloadSize(); // get the size of the payload
    radio.read(&payload, bytes); // fetch payload from FIFO
    // Serial.println(String("[ID ") + String(payload.payloadID) + "] " + payload.message);

    // counts
    if (payload.payloadID == 1000){
      digitalWrite(speaker_0, HIGH);
      digitalWrite(led_red, HIGH); // turn the LED on (HIGH is the voltage level)
      delay(3); // wait for a second
      digitalWrite(led_red, LOW);  // turn the LED off by making the voltage LOW
      digitalWrite(speaker_0, LOW);
    }

    // cpm
    else if (payload.payloadID == 1111){
      memset(geigerCounter.CPM_str, 0, 12);
      memcpy(geigerCounter.CPM_str, payload.message, 12);
      geigerCounter.CPM = atoi(geigerCounter.CPM_str);
      geigerCounter.uSvh = geigerCounter.CPM * 0.00332;
    }
  }
}
