#include <SimpleTimer.h>
#include <SoftwareSerial.h>
#include <EEPROM.h>
#define AT_FLAG 0
#define AT_ID 1
#define AT_LAT 20
#define AT_LNG 25
#define AT_ST 30
#define AT_INITIAL_SET 41
#define AT_BAUD_SET 42
#define AT_WIFI_SET 43
#define AT_BASIC_SET 44
#define AT_SSID 50
#define AT_PW 80
#define AT_IP 110
#define AT_PORT 140
#define AT_START 200
#define AT_END 210
//0 >> Flag (Used = 1)
//1 >> ID
//20 >> Lat
//25 >> Lng
//30 >> ST
//41 >> initialSet
//42 >> baudSet
//43 >> wifiset
//50 >> ssid
//80 >> pw
//110 >> ip
//140 >> port
//200 >> start
//210 >> end

SoftwareSerial mySerial(2, 3); // RX, TX
char strbuf[256];
int intBuf;
String stringBuf;
float floatBuf;

int WIFIdisconnected = 1;
int IPdisconnected = 0;
int IPchecking = 0;
int CURsending = 0;
int CURcounter = 0; // coount 10min, 30times.
SimpleTimer aliveTimer;
SimpleTimer IPCheckTimer;
SimpleTimer IPTimer;
SimpleTimer WIFITimer;
SimpleTimer CURsendTimer;







void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(9600);

  aliveTimer.setInterval(20000); //wifi check timer setting
  IPCheckTimer.setInterval(2000);
  WIFITimer.setInterval(3000);
  IPTimer.setInterval(8000);
  CURsendTimer.setInterval(2000);
  for(int i=0;i<220;i++)  // for test
    EEPROM.write(i,0);

  EEPInitializing();

  // set the data rate for the SoftwareSerial port
  if(EEPROM.read(AT_BAUD_SET) == 0){
      mySerial.begin(115200);
      mySerial.write("AT+UART_DEF=9600,8,1,0,0\r\n");
      mySerial.write("AT+RST\r\n");
      mySerial.begin(9600);
      EEPROM.write(AT_BAUD_SET, 1);
      //EEPROM.commit();
  }
  if(EEPROM.read(AT_INITIAL_SET) == 0){
      mySerial.write("AT+CWMODE=3\r\n");
      mySerial.write("AT+CIPMUX=0\r\n");
      EEPROM.write(AT_INITIAL_SET, 1);
      //EEPROM.commit();
  }
  if(EEPROM.read(AT_WIFI_SET) == 0){ // for wifi test >> appliacation's job
    write_String(AT_SSID,"SeungWoo");
    write_String(AT_PW,"123456789a");
    EEPROM.write(AT_WIFI_SET, 1);
    //EEPROM.commit();
  }
  if(EEPROM.read(AT_BASIC_SET) == 0){ //for test >> appliacation's job
    EEPROM.put(AT_LAT,(float)127.2341);
    EEPROM.put(AT_LNG,(float)40.22114);
    EEPROM.put(AT_ST,(float)0.3);
    write_String(AT_ID,"10000001");
    EEPROM.write(AT_BASIC_SET, 1);
  }
}









void loop() { // run over and over
  if(EEPROM.read(AT_BASIC_SET)&&EEPROM.read(AT_WIFI_SET)){
    if(aliveTimer.isReady()){
      WIFIcheckAlive();
      aliveTimer.reset();
    }
    if(IPchecking && IPCheckTimer.isReady()){
      IPchecking = 0;
      IPcheck();
    }

    if(WIFIdisconnected && WIFITimer.isReady()){
      WIFIdisconnected = 0;
      aliveTimer.reset();
      reconnectWifi();
      IPTimer.reset();
      IPdisconnected = 1;
    }
    if(IPdisconnected && IPTimer.isReady()){
      IPdisconnected = 0;
      aliveTimer.reset();
      reconnectIP();
    }
    if(CURsending && CURsendTimer.isReady()){
      CURsending = 0;
      aliveTimer.reset();
      sendCUR();
    }
  }

  if (Serial.available()) {
    mySerial.write(Serial.read());
  }
  if (mySerial.available()) {
    Serial.write(mySerial.read());
  }
}











void EEPInitializing(){
    if(EEPROM.read(AT_FLAG) != 1){
    Serial.println("initializing EEPROM...");
    EEPROM.write(AT_FLAG,1);
    EEPROM.write(AT_ID,0);
    EEPROM.write(AT_LAT,0);
    EEPROM.write(AT_LNG,0);
    EEPROM.write(AT_ST,0);
    EEPROM.write(AT_INITIAL_SET,0);
    EEPROM.write(AT_BAUD_SET,0);
    EEPROM.write(AT_WIFI_SET,0);
    EEPROM.write(AT_BASIC_SET,0);

    EEPROM.write(AT_SSID,0);
    EEPROM.write(AT_PW,0);

    write_String(AT_IP,"54.221.152.48");
    EEPROM.put(AT_PORT,(int)4000);

    EEPROM.write(AT_START,0);
    EEPROM.write(AT_END,0);

    //EEPROM.commit();
    read_String(AT_IP,strbuf);
    Serial.println(strbuf);
    EEPROM.get(AT_PORT,intBuf);
    Serial.println(String(intBuf));
    Serial.println("result : 0 0 ==>> initializing EEPROM complete!");
    Serial.flush();
  }
}

void write_String(char address,const char data[])
{
  int _size = strlen(data);
  int i;
  for(i=0;i<_size;i++)
  {
    EEPROM.write(address+i,data[i]);
  }
  EEPROM.write(address+_size,'\0');
}

void read_String(char address, char* data)
{
  int i;
  int len=0;
  unsigned char k;
  k=EEPROM.read(address);
  while(k != '\0' && len<500)   //Read until null character
  {
    k=EEPROM.read(address+len);
    data[len]=k;
    len++;
  }
  data[len]='\0';
}

void WIFIcheckAlive(){
  Serial.println("WIFIchecking...");
  Serial.flush();
  mySerial.write("AT+CIFSR\r\n");

  if(mySerial.find("0.0.0.0")){
    WIFITimer.reset();
    WIFIdisconnected = 1;
    Serial.println("wifiDisconnected while checking WIFI STATUS");
    Serial.flush();
  }
  else{
    IPCheckTimer.reset();
    IPchecking = 1;
    Serial.println("wifi Stable");
    Serial.flush();
  }
}
void IPcheck(){
  Serial.println("IPchecking...");
  Serial.flush();



  if(CURcounter == 0){
    CURsendTimer.reset();
    CURsending = 1;
  }
  CURcounter = (CURcounter+1)%30;
}
void reconnectWifi(){
    Serial.println("WIFIconnecting...");
    Serial.flush();
    mySerial.write("AT+CWJAP=\"");
    read_String(AT_SSID,strbuf);
    mySerial.write(strbuf);
    mySerial.write("\",\"");
    read_String(AT_PW,strbuf);
    mySerial.write(strbuf);
    mySerial.write("\"\r\n");
}
void reconnectIP(){
    Serial.println("IPconnecting...");
    Serial.flush();
    mySerial.write("AT+CIPSTART=\"TCP\",\"");
    read_String(AT_IP,strbuf);
    mySerial.write(strbuf);
    mySerial.write("\",");
    EEPROM.get(AT_PORT,intBuf);
    stringBuf = String(intBuf);
    stringBuf.toCharArray(strbuf,stringBuf.length());
    mySerial.write(strbuf);
    mySerial.write("\r\n");
    CURcounter = 0;
}

void sendCUR(){
    String message = "HW ID ";
    Serial.println("sending CURRENT STATUS...");
    Serial.flush();
    mySerial.write("AT+CIPSEND=");
    read_String(AT_ID,strbuf);
    message += String(strbuf) + " ST ";
    EEPROM.get(AT_ST, floatBuf);
    message += String(floatBuf);
    stringBuf = String(message.length());
    stringBuf.toCharArray(strbuf,stringBuf.length());
    mySerial.write(strbuf);
    mySerial.write("\r\n");
    message.toCharArray(strbuf,message.length());
    mySerial.write(strbuf);
    mySerial.write("\r\n");


}