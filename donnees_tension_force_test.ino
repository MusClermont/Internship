const int     sensor=A0;
float         force_value=0;
float         sensor_value_volt=0;


void setup() {
  Serial.begin(57600);
}

void loop() {
  float sensor_value = analogRead(sensor);
  float sensor_value_volt = sensor_value * (5.0 / 1023.0);

  int force_value = random(0, 20);

  Serial.print("Voltage : ");
  Serial.print(sensor_value_volt);
  Serial.print(" V; ");
  
  Serial.print("Force : ");
  Serial.print(force_value);
  Serial.println(" N");
  delay(9);
}
