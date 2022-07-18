#include <TimerOne.h>
#include <HX711_ADC.h>
#if defined(ESP8266)|| defined(ESP32) || defined(AVR)
#include <EEPROM.h>
#endif


const int     spring_element = A0;
float         spring_element_value = 0;
float         spring_element_value_volt = 0;
long          strt;
long          MS;

const int     SPS           = 50;                                                 // Samples per second
const int     forceTareTime = 10;                                                 // [s]
const int     cell_serial   = 0;                                                  // true if using classic Loadcell
const int     force_serial  = 1;                                                  // Output for logging

const int     HX711_dout = 10;                                                    // mcu > HX711 dout pin, must be external interrupt capable!
const int     HX711_sck = 11;                                                     // mcu > HX711 sck pin

//ProtReadings 
const double  zero_signal = 0.0323;                                               // [mv/V]
const double  maxN_delta = 0.483562;                                              // [mv/V]
const double  maxN = 50;                                                          // [N]
const double  AVdd = 4.24;                                                        // [V]
const double  GAIN =  128;
const double  maxRead = 0xFFFFFF;

const double  meas_t_interval = 30.0;                                              // [s]
int           meas_idx  = 0;                                                       // Index of current measuring
int           meas_stbs = 0;                                                       // stbs = samples to be send

double        forceTareValSum = 0;                                                 // Sum of force measuments to calc tare
int           forceTareFlag = 0;                                                   // Flag to show if ForceTare is colleceting values
int           forceTareCnt =  0;                                                   // Counter how many values have been collected for Force Tare
double        forceTareOffset = 0;                                                 // Offset to be deducted from the force measurment


//HX711 constructor:
HX711_ADC LoadCell(HX711_dout, HX711_sck);

const int calVal_eepromAdress = 0;
unsigned long t = 0;
volatile boolean newDataReady;


void setup() {
  Serial.begin(57600); delay(10);
  Serial.println();
  
  // Initialize Timer1 to run every 0.1 seconds
  Timer1.initialize(12500);
  // Execute for each interruption the function read_U()
  Timer1.attachInterrupt(dataReadyISR);
  
  float calibrationValue = 1; // calibration value
#if defined(ESP8266) || defined(ESP32)
#endif
  if (cell_serial)  EEPROM.get(calVal_eepromAdress, calibrationValue);            // Uncomment this if you want to fetch the value from eeprom
  
  LoadCell.begin();
  unsigned long stabilizingtime = 1000;                                           // Tare preciscion can be improved by adding a few seconds of stabilizing time
  boolean _tare = 0;                                                              // Set this to false if you don't want tare to be performed in the next step
  LoadCell.start(stabilizingtime, _tare);
  if (LoadCell.getTareTimeoutFlag()) {
    Serial.println("Timeout, check MCU > HX711 wiring and pin designations");
    while (1);
  }
  else {
    LoadCell.setCalFactor(calibrationValue);                                      // Set calibration value (float)
    strt = millis();
    Serial.println("-1, Startup is complete, begin tare:");
  }
  if (!cell_serial) LoadCell.setTareOffset(0);                                    // Making sure Tare Offset is 0
  LoadCell.setGain(GAIN);
  delay(1000);
  if (!cell_serial) forceTareFlag = 1;
}


//interrupt routine:
void dataReadyISR() {
  if (LoadCell.update()) {
    newDataReady = 1;
  }
}

//get Force in Newton
double getForce(long rawDat) {
  double tempF3 = (((rawDat - maxRead/2) * ((AVdd / GAIN * 1000) / maxRead)) - (zero_signal * AVdd)) * (maxN / ((maxN_delta - zero_signal) * AVdd));
  if (!forceTareFlag) {
    tempF3 -= forceTareOffset;
  }
  return tempF3;
}


void loop() {
  long t_cnt = micros();  
  const int serialPrintInterval = 0;                                              // Increase value to slow down serial print activity

  // get smoothed value from the dataset:
  if (newDataReady) {
    double raw = LoadCell.getData();
    newDataReady = 0;
    double force = getForce(raw);
    spring_element_value = analogRead(spring_element);
    spring_element_value_volt = spring_element_value * (5.0 / 1023.0);
    
    
    //BEGIN ForceTareBlock//
    if (forceTareFlag) {
      forceTareValSum += force;
      ++forceTareCnt;
      if (forceTareCnt >= SPS*forceTareTime) {
        forceTareOffset = forceTareValSum / (SPS*forceTareTime);
        forceTareFlag = 0;
        forceTareCnt = 0;
        forceTareValSum = 0;       
      }
    }   //END ForceTareBlock// 

    
    if (force_serial) {
      if (meas_stbs > 0 && !forceTareFlag) {
        Serial.print(meas_idx);
      } else if (forceTareFlag) {
        Serial.print(-1);
      } else {
        Serial.print(0);
      }
      Serial.print(" ; ");
      Serial.print((-1) * force,8);
      Serial.print(" N");
      --meas_stbs;
      Serial.print(" ; Voltage : ");
      Serial.print(spring_element_value_volt);
      Serial.println(" V; ");
    }
  }
  
  MS = millis()- strt;

  if ( ( (MS / 1000) % 60) >= 13 ) {
    meas_stbs = (double)SPS * meas_t_interval;
    meas_idx = 1;
  }

  //check if last tare operation is complete
  if (LoadCell.getTareStatus() == true) {
    Serial.println("Tare complete");
  }

  delay(20);
}
