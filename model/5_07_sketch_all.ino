//온습도 되고 thingspeak 올리는거

#include <ESP8266WiFi.h>
#include <dht.h>
#include <WiFiClient.h>
#include <ThingSpeak.h>
#include <SoftwareSerial.h> 

#define DHT22_PIN D0

//온습도
dht DHT;
int humid =0;
int temper =0;

struct
{
    uint32_t total;
    uint32_t ok;
    uint32_t crc_error;
    uint32_t time_out;
    uint32_t connect;
    uint32_t ack_l;
    uint32_t ack_h;
    uint32_t unknown;
} stat = { 0,0,0,0,0,0,0,0};

//미세먼지
SoftwareSerial pmsSerial(D1, D3); // Arudino Uno port RX, TX  


#define START_1 0x42  
#define START_2 0x4d  
#define DATA_LENGTH_H        0  
#define DATA_LENGTH_L        1  
#define PM1_0_ATMOSPHERE_H   8  
#define PM1_0_ATMOSPHERE_L   9  
#define PM2_5_ATMOSPHERE_H   10  
#define PM2_5_ATMOSPHERE_L   11  
#define PM10_ATMOSPHERE_H    12  
#define PM10_ATMOSPHERE_L    13  
#define PM2_5_PARTICLE_H   16  
#define PM2_5_PARTICLE_L   17  
#define VERSION              26  
#define ERROR_CODE           27  
#define CHECKSUM             29  
byte bytCount1 = 0;  
byte bytCount2 = 0;  
unsigned char chrRecv;  
unsigned char chrData[30];  

int PM01;  
int PM25;  
int PM10;  

unsigned int GetPM_Data(unsigned char chrSrc[], byte bytHigh, byte bytLow)  
{  
   return (chrSrc[bytHigh] << 8) + chrSrc[bytLow];  
}

//이산화탄소
                          // Sensor Pin (ESP8266 ESP-12 D2 = GPIP4)
const int sensorPin = D2;          
const unsigned long interval = 60000*5;                // Recording interval (> 15000ms)
unsigned long logTime = 0;

int lowStart = 0;
int highStart = 0;
int lowTime = 0;
int highTime = 0;
int PPM = 0;
int nPPM = 0;
long sumPPM = 0;

// wifi
//const char* ssid = "IML-C5000W 296e";
//const char* password = "im00lgu+61";
//const char* ssid = "juhee";
//const char* password = "iptime226";
//const char* ssid = "iPhone";
//const char* password = "yeonjae1783";
//const char* password = "aaa12345";
const char* ssid = "Software 2.4G";
const char* password = "software";

WiFiClient client;

// thingSpeak 
unsigned long ChannelID = 768165;
const char* WriteAPIKey = "B2AV39Q708O57S4J";


void setup() {
  Serial.begin(115200);
  initWiFi();
  pmsSerial.begin(9600);
  pinMode(sensorPin, INPUT);
  ThingSpeak.begin(client);
}

void loop() {
  int humid_a = 0;
  int temper_a = 0;
  int ppm_a = 0;
  int pm1 = 0;
  int pm2 = 0;
  int pm3 = 0;
  int dht_ck = 0;
  int pms_ck = 0;
  int ppm_ck = 0;
  
 for(int i=0; i<20; i++)
 {
  if(UpdateDHT() == 1)
  {
   humid_a += humid;
   temper_a += temper;
  }
  else
  {
    humid_a += 0;
    temper_a += 0;
    dht_ck += 1;
  }
  delay(5000); //5000으로 바꾸기.
  if(UpdatePMS() == 1)
  {
    pm1 += PM01;
    pm2 += PM25;
    pm3 += PM10;
  }
  else
  {
    pm1 += 0;
    pm2 += 0;
    pm3 += 0;
    pms_ck += 1;
  }
  delay(5000);
  if(UpdateCO2() == 1)
    ppm_a += PPM;  
  else
    {
      ppm_a += 0;
      ppm_ck += 1;
    }
  delay(5000); //1000이 1초
 }
 humid = humid_a/(20 - dht_ck);
 temper = temper_a/(20 - dht_ck);
 PPM = ppm_a/(20 - ppm_ck);
 PM01 = pm1/(20 - pms_ck);
 PM25 = pm2/(20 - pms_ck);
 PM10 = pm3/(20 - pms_ck);

Serial.print("WriteThingspeak 1000sec  - humid : ");
Serial.print(humid);
    Serial.print(",\t temepr : ");
Serial.print(temper);
    Serial.print(",\t PPM :");
Serial.print(PPM);
    Serial.print(",\t PM01 : ");
Serial.print(PM01);
    Serial.print(",\t PM25 : ");
Serial.print(PM25);
    Serial.print(",\t PM10 : ");
Serial.print(PM10);
Serial.println();
 WriteThingspeak(temper, humid, PPM, PM01, PM25, PM10); //5분주기로 thingspeak에 씀
}

int UpdateDHT(){
    // READ DATA
    int retck = 0;
    uint32_t start = micros();
    int chk = DHT.read22(DHT22_PIN);
    uint32_t stop = micros();
    static boolean data_state = false;

    stat.total++;
    switch (chk)
    {
    case DHTLIB_OK:
        stat.ok++;
        Serial.print("OK,\t");
        retck = 1;
        break;
    case DHTLIB_ERROR_CHECKSUM:
        stat.crc_error++;
        Serial.print("Checksum error,\t");
        break;
    case DHTLIB_ERROR_TIMEOUT:
        stat.time_out++;
        Serial.print("Time out error,\t");
        break;
    default:
        stat.unknown++;
        Serial.print("Unknown error,\t");
        break;
    }
    // DISPLAY DATA
    Serial.print(DHT.humidity, 1);
    Serial.print(",\t");
    Serial.print(DHT.temperature, 1);
    Serial.print(",\t");
    Serial.println();
    humid = DHT.humidity;
    temper = DHT.temperature;

    if (stat.total % 20 == 0)
    {
        Serial.println("\nTOT\tOK\tCRC\tTO\tUNK");
        Serial.print(stat.total);
        Serial.print("\t");
        Serial.print(stat.ok);
        Serial.print("\t");
        Serial.print(stat.crc_error);
        Serial.print("\t");
        Serial.print(stat.time_out);
        Serial.print("\t");
        Serial.print(stat.connect);
        Serial.print("\t");
        Serial.print(stat.ack_l);
        Serial.print("\t");
        Serial.print(stat.ack_h);
        Serial.print("\t");
        Serial.print(stat.unknown);
        Serial.println("\n");
    }
    delay(1000);
     Serial.print(retck);
   Serial.println();
    if(retck)
      return 1;
     else
     return -1;
}

int UpdateCO2(){
   int retck = 0;  
  while(digitalRead(sensorPin) == LOW) {yield();}      // Read Starting Value
  highStart = millis();
  logTime = millis(); 

  delay(5);
  while(digitalRead(sensorPin) == HIGH) {yield();}     // Check for High State
  lowStart = millis();
  highTime = lowStart - highStart;
  delay(5);
  
  while(digitalRead(sensorPin) == LOW) {yield();}      // Check for Low State
  highStart = millis();
  lowTime = highStart - lowStart;

  PPM = 2000 * (highTime - 2) / (highTime + lowTime - 4);

  delay(5);

  if(lowTime + highTime > 990) {                       // Validity Checking

    retck = 1;
    Serial.print("  H: ");
    Serial.print(highTime, DEC);
    Serial.print(",  L: ");
    Serial.println(lowTime, DEC);
    Serial.print("* CO2 Concentration [PPM] = ");
    Serial.println(PPM, DEC);

    nPPM = nPPM + 1;
    sumPPM = sumPPM + PPM;
  } 

  else {
    Serial.print("** NG ** : ");
    Serial.println(lowTime + highTime, DEC);
  }
  delay(5);
  if(millis() - logTime >= interval) {
    yield();
    logTime = millis();
  }
   Serial.print(retck);
   Serial.println();
  if(retck)
  return 1;
  else
  return -1;
}


int UpdatePMS(){
  int retck = 0;
  pmsSerial.listen();
    if (pmsSerial.available())   {  
       for(int i = 0; i < 32; i++)     {  
           chrRecv = pmsSerial.read();  
           if (chrRecv == START_2 ) {   
              bytCount1 = 2;  
              break;  
            }  
       }   
      if (bytCount1 == 2)  
     {  
        bytCount1 = 0;  
        for(int i = 0; i < 30; i++){  
           chrData[i] = pmsSerial.read();  
         }   
  
         if ( (unsigned int) chrData[ERROR_CODE] == 0 ) {  
            retck = 1;
            PM01  = GetPM_Data(chrData, PM1_0_ATMOSPHERE_H, PM1_0_ATMOSPHERE_L);  
            PM25  = GetPM_Data(chrData, PM2_5_ATMOSPHERE_H, PM2_5_ATMOSPHERE_L);  
            PM10  = GetPM_Data(chrData, PM10_ATMOSPHERE_H, PM10_ATMOSPHERE_L);  
            Serial.print("PM1.0=");  
            Serial.print(PM01);  
            Serial.print(",PM2.5=");  
            Serial.print(PM25);  
            Serial.print(",PM10=");  
            Serial.println(PM10);  
            }  
         else{  
            retck = 0;
            Serial.println("PMS7003  ERROR");  
         }  
      }   
   }  
   else{  
      retck = 0;
      Serial.println("PMS7003 NOT available");  
   }  
   delay(1000);
   Serial.print(retck);
   Serial.println();
   if(retck)
    return 1;
    else
    return -1;
}


void WriteThingspeak(int temper, int humid, int PPM, int PM01, int PM25, int PM10){
  
      ThingSpeak.setField(1, temper);
      ThingSpeak.setField(2, humid);
      ThingSpeak.setField(3, PPM);
      ThingSpeak.setField(4, PM01);
      ThingSpeak.setField(5, PM25);
      ThingSpeak.setField(6, PM10);
      ThingSpeak.writeFields(ChannelID, WriteAPIKey);
}
  

void initWiFi(){
  Serial.println();
  Serial.println();
  Serial.println("Connectiong to ssid ...");
  // attempt to connect to WiFi network
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.println(".");
  }
  // 접속성공!
  Serial.println();
  Serial.println("Connected WiFi");
  //사용하는 ip출력
  Serial.println(WiFi.localIP());
  Serial.println();
}
