const int analogInPin = A0;  // Analog input pin that the potentiometer is attached to

int sensorValue = 0;        // value read from the pot
int outputValue = 1800;        // value output to the PWM (analog out) stands for around 1.5V

void setup() {
  Serial.begin(115200);
  analogWriteResolution(12);
  analogReadResolution(12);
  analogWrite(DAC1, outputValue );
}

//void serialEvent()
//{
//}


void loop() {
  // put your main code here, to run repeatedly:
  while (Serial.available() > 0) {
    float flow = 0;
    float set = 0;
    char cmd = Serial.read();
    switch (cmd) {
      case 'f':                                  // Read the flow voltage 
        sensorValue = analogRead(analogInPin);
        flow = (0.55 + float(sensorValue) / 4094 * 2.2) / 5 * 100; // convet the read voltage to sccm
        Serial.println(flow);
        break;
      case 'o':                                 // Read the current set output voltage
        set = (0.55 + float(outputValue) / 4094 * 2.2) / 5 * 100;
        Serial.println(set);
        break;
      case 's':                                 // Change the set flow speed
        outputValue = Serial.parseInt();
        if (outputValue > 4094){
          outputValue = 4094;
          };
        if (outputValue <= 0){
          outputValue = 0;
          };
        analogWrite(DAC1, outputValue );
        Serial.println(outputValue);
        break;
      case '?':
        Serial.println("Flow controller Arduino ready.");
        break;
    }
  }
}
