#include <Homie.h>
#include <FastLED.h>
#include <Servo.h>

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
  changeColor(eyecolor);      // turn eyes on with defined color
  myservo.attach(PIN_SERVO);  // attaches the servo on pin 9 to the servo object
  for( float t = 0.0; t < 2000; t += 15 ) {
     float pos = midPosition + 70.0*sin( w * t ) * pow(2.714, -(w/15.0) * t);
     myservo.write((int) pos);
     delay(15);
  }
  myservo.detach();
  changeColor("");            // turn eyes off
}

void changeColor(String color) {
  Serial.print("Color: "); Serial.println(color);
  if(color == "red") {
    eyecolor = color;
    FastLED.showColor(CRGB::Red); 
  } else if (color == "green") {
    eyecolor = color;
    FastLED.showColor(CRGB::Green);
  } else if (color == "blue") {
    eyecolor = color;
    FastLED.showColor(CRGB::Blue);
  } else if (color == "yellow") {
    eyecolor = color;
    FastLED.showColor(CRGB::Yellow);
  } else if (color == "cyan") {
    eyecolor = color;
    FastLED.showColor(CRGB::Cyan);
  } else if (color == "pink") {
    eyecolor = color;
    FastLED.showColor(CRGB::Pink);
  } else {    // turn off
    Serial.println("Ignoring invalid color.");
    FastLED.showColor(CRGB::Black);
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
    } else {
      // insert input validation here
      eyecolor = inputString;
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
  Homie.setFirmware("felixthecat", "1.0.0");
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
