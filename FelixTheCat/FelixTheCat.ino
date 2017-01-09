#include <Homie.h>
#include <FastLED.h>
#include <Servo.h>

#define FW_NAME "felixthecat"
#define FW_VERSION "1.0.2"

/* Magic sequence for Autodetectable Binary Upload */
const char *__FLAGGED_FW_NAME = "\xbf\x84\xe4\x13\x54" FW_NAME "\x93\x44\x6b\xa7\x75";
const char *__FLAGGED_FW_VERSION = "\x6a\x3f\x3e\x0e\xe1" FW_VERSION "\xb0\x30\x48\xd4\x1a";
/* End of magic sequence for Autodetectable Binary Upload */

#define NUM_LEDS 2
#define PIN_LEDS 14
#define PIN_SERVO 4

Servo myservo;  // create servo object to control a servo

HomieNode commandNode("command", "command");
HomieNode eyecolorNode("eyecolor", "color");

CRGB leds[NUM_LEDS];

int pos = 0;    // variable to store the servo position
const int midPosition = 100;
const float pi = 3.14;
const float w = 2*pi/800;
String eyecolor = "red";

const int NUMBER_OF_COLORS = 6;
const int SIZE_OF_COLORS = 7;

char colors[NUMBER_OF_COLORS][SIZE_OF_COLORS] = {
 { "red" },
 { "green" },
 { "blue" },
 { "yellow" },
 { "cyan" },
 { "pink" },
};

bool isValidColor(String color) {
  for(int i = 0; i < NUMBER_OF_COLORS; i++) {
    if(String(colors[i]) == color) return true;
  }
  return false;
}

bool commandHandler(String value) {
  value.toLowerCase();
  Serial.print("command: "); Serial.println(value);
  if(value == "wink") {
    wink();
  } else {
    return false;
  }
  return true;
}

bool eyecolorHandler(String value) {
  value.toLowerCase();
  Serial.print("eyecolor: "); Serial.println(value);
  if(value != "") {
    changeColor(value);
  } else {
    return false;
  }
  return true;
}

void wink() {
  Serial.println("o/");
  if(Homie.isReadyToOperate()) {
      Homie.setNodeProperty(commandNode, "status", "fishing", false);
  }
  showEyeColor(eyecolor);             // turn eyes on with defined color
  myservo.attach(PIN_SERVO);          // attaches the servo on pin 9 to the servo object
  for( float t = 0.0; t < 2000; t += 15 ) {
     float pos = midPosition + 70.0*sin( w * t ) * pow(2.714, -(w/15.0) * t);
     myservo.write((int) pos);
     delay(15);
  }
  myservo.detach();
  showEyeColor("");                   // turn eyes off
}

void showEyeColor(String color) {
  if(color == "red") {
    FastLED.showColor(CRGB::Red); 
  } else if (color == "green") {
    FastLED.showColor(CRGB::Green);
  } else if (color == "blue") {
    FastLED.showColor(CRGB::Blue);
  } else if (color == "yellow") {
    FastLED.showColor(CRGB::Yellow);
  } else if (color == "cyan") {
    FastLED.showColor(CRGB::Cyan);
  } else if (color == "pink") {
    FastLED.showColor(CRGB::Pink);
  } else {
    FastLED.showColor(CRGB::Black);   // turn eyes off
  }
}

void changeColor(String color) {
  if(isValidColor(color)) {
    Serial.print("Color: "); Serial.println(color);
    if(Homie.isReadyToOperate()) {
      Homie.setNodeProperty(eyecolorNode, "eyecolor", color); 
    }
    eyecolor = color;
  } else {
    Serial.println("Ignoring invalid color.");
  }
}

void serialComm() {
  // enable Serial communication
  while (Serial.available()) {
    String inputString = Serial.readString();
    inputString.trim();
    inputString.toLowerCase();
    if(inputString == "wink") {
      wink();
    } else if(isValidColor(inputString)) {
      changeColor(inputString);
    } else {
      Serial.print("Ignoring: "); Serial.println(inputString);
    }
  }
}

void loopHandler() {
  // pass
}

void setup() {
  FastLED.addLeds<WS2811, PIN_LEDS, RGB>(leds, NUM_LEDS);
  wink();
  Homie.enableBuiltInLedIndicator(false);
  Homie.setFirmware(FW_NAME, FW_VERSION);
  commandNode.subscribe("wink", commandHandler);
  eyecolorNode.subscribe("eyecolor", eyecolorHandler);
  Homie.registerNode(commandNode);
  Homie.registerNode(eyecolorNode);
  Homie.setLoopFunction(loopHandler);
  Homie.setup();
}

void loop() {
  serialComm();
  Homie.loop();
}
