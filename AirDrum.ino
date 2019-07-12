#include "MIDIUSB.h"

byte input;

void noteOn(byte channel, byte pitch, byte velocity) {
  midiEventPacket_t noteOn = {0x09, 0x90 | channel, pitch, velocity};
  MidiUSB.sendMIDI(noteOn);
}

void noteOff(byte channel, byte pitch, byte velocity) {
  midiEventPacket_t noteOff = {0x08, 0x80 | channel, pitch, velocity};
  MidiUSB.sendMIDI(noteOff);
}

void setup() {
  Serial.begin(115200);
}

void controlChange(byte channel, byte control, byte value) {
  midiEventPacket_t event = {0x0B, 0xB0 | channel, control, value};
  MidiUSB.sendMIDI(event);
}

void loop() {
  if(Serial.available()){
    input = Serial.read();
    if (input == '1'){
      noteOn(0, 62, 255);
      MidiUSB.flush();
      input = 0;
    }
    else if (input == '2'){
      noteOn(0, 66, 255);
      MidiUSB.flush();
      input = 0;
    }
    else if (input == '3'){
      noteOn(0, 55, 255);
      MidiUSB.flush();
      input = 0;
    }
  }
}