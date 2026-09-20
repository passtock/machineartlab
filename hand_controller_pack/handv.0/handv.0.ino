#include "Arduino.h"
#include "AverageValue.h"

// Number of values to calculate with. Prevents memory problems
const long MAX_VALUES_NUM = 20;

AverageValue<long> avg1G(MAX_VALUES_NUM);
AverageValue<long> avg2G(MAX_VALUES_NUM);
AverageValue<long> avg3G(MAX_VALUES_NUM);
AverageValue<long> avg4G(MAX_VALUES_NUM);
AverageValue<long> avg5G(MAX_VALUES_NUM);

AverageValue<long> avg1D(MAX_VALUES_NUM);
AverageValue<long> avg2D(MAX_VALUES_NUM);
AverageValue<long> avg3D(MAX_VALUES_NUM);
AverageValue<long> avg4D(MAX_VALUES_NUM);
AverageValue<long> avg5D(MAX_VALUES_NUM);

#include <VarSpeedServo.h>

VarSpeedServo SG1;  // sevo
VarSpeedServo SG2;
VarSpeedServo SG3;
VarSpeedServo SG4;
VarSpeedServo SG5;
VarSpeedServo SD1;
VarSpeedServo SD2;
VarSpeedServo SD3;
VarSpeedServo SD4;
VarSpeedServo SD5;


const int G1 = A0;  // capteur doigt
const int G2 = A10;
const int G3 = A11;
const int G4 = A3;
const int G5 = A4;
const int D1 = A5;
const int D2 = A6;
const int D3 = A7;
const int D4 = A8;
const int D5 = A9;

const int power_servo = 12;

int capt_G1;
int capt_G2;
int capt_G3;
int capt_G4;
int capt_G5;
int capt_D1;
int capt_D2;
int capt_D3;
int capt_D4;
int capt_D5;
int speed=300;

void setup() {


  Serial.begin(9600);

  pinMode(G1, INPUT);
  pinMode(G2, INPUT);
  pinMode(G3, INPUT);
  pinMode(G4, INPUT);
  pinMode(G5, INPUT);
  pinMode(D1, INPUT);
  pinMode(D2, INPUT);
  pinMode(D3, INPUT);
  pinMode(D4, INPUT);
  pinMode(D5, INPUT);

  pinMode(power_servo, OUTPUT);

  digitalWrite(power_servo, HIGH);  // desactive alimentation servo



  SG1.attach(2);  // attaches the servo on pin 9 to the servo object
  SG2.attach(3);
  SG3.attach(4);
  SG4.attach(5);
  SG5.attach(6);
  SD1.attach(7);
  SD2.attach(8);
  SD3.attach(9);
  SD4.attach(10);
  SD5.attach(11);

  

  
}

void loop() {

  digitalWrite(power_servo, LOW);  // active alimentation servo

  moyenne_capteur();
  limite_capteur();
  ecriture_servo();

  Serial.print("G1  ");
  Serial.print(capt_G1);
  Serial.print("   ");
  Serial.print("G2  ");
  Serial.print(capt_G2);
  Serial.print("   ");
  Serial.print("G3  ");
  Serial.print(capt_G3);
  Serial.print("   ");
  Serial.print("G4  ");
  Serial.print(capt_G4);
  Serial.print("   ");
  Serial.print("G5  ");
  Serial.print(capt_G5);

   Serial.print("   ");
   Serial.print("D1  ");
   Serial.print(capt_D1);
   Serial.print("   ");
   Serial.print("D2  ");
   Serial.print(capt_D2);
   Serial.print("   ");
   Serial.print("D3  ");
   Serial.print(capt_D3);
   Serial.print("   ");
   Serial.print("D4  ");
   Serial.print(capt_D4);
   Serial.print("   ");
   Serial.print("D5  ");
   Serial.println(capt_D5);


  ///// capteur brut
  // int CD1 =(analogRead(D1));
  // int CD2 =(analogRead(D2));
  // int CD3 =(analogRead(D3));
  // int CD4 =(analogRead(D4));
  // int CD5 =(analogRead(D5));


  ///////////////////////////////
}


void moyenne_capteur() {

  avg1G.push(analogRead(G1));               // fonction avera lie le capteur
  capt_G1 = avg1G.average();                // moyenne capteur
  capt_G1 = map(capt_G1, 14, 140, 180, 0);  // mapp capteur

  avg2G.push(analogRead(G2));              // fonction avera lie le capteur
  capt_G2 = avg2G.average();               // moyenne capteur
  capt_G2 = map(capt_G2, 0, 160, 180, 0);  // mapp capteur


  avg3G.push(analogRead(G3));              // fonction avera lie le capteur
  capt_G3 = avg3G.average();               // moyenne capteur
  capt_G3 = map(capt_G3, 4, 230, 180, 0);  // mapp capteur


  avg4G.push(analogRead(G4));              // fonction avera lie le capteur
  capt_G4 = avg4G.average();               // moyenne capteur
  capt_G4 = map(capt_G4, 0, 160, 180, 0);  // mapp capteur

  avg5G.push(analogRead(G5));              // fonction avera lie le capteur
  capt_G5 = avg5G.average();               // moyenne capteur
  capt_G5 = map(capt_G5, 0, 180, 180, 0);  // mapp capteur


  avg1D.push(analogRead(D1));               // fonction avera lie le capteur
  capt_D1 = avg1D.average();                // moyenne capteur
  capt_D1 = map(capt_D1, 87, 132, 0, 100);  // mapp capteur

  avg2D.push(analogRead(D2));              // fonction avera lie le capteur
  capt_D2 = avg2D.average();               // moyenne capteur
  capt_D2 = map(capt_D2, 0, 150, 0, 180);  // mapp capteur

  avg3D.push(analogRead(D3));              // fonction avera lie le capteur
  capt_D3 = avg3D.average();               // moyenne capteur
  capt_D3 = map(capt_D3, 0, 150, 0, 120);  // mapp capteur

  avg4D.push(analogRead(D4));               // fonction avera lie le capteur
  capt_D4 = avg4D.average();                // moyenne capteur
  capt_D4 = map(capt_D4, 10, 120, 0, 100);  // mapp capteur

  avg5D.push(analogRead(D5));              // fonction avera lie le capteur
  capt_D5 = avg5D.average();               // moyenne capteur
  capt_D5 = map(capt_D5, 0, 120, 0, 120);  // mapp capteur
}

void limite_capteur() {


  if (capt_G1 >= 180) {
    capt_G1 = 150;
  }
  if (capt_G1 <= 0) {
    capt_G1 = 0;
  }

  if (capt_G2 >= 90) {
    capt_G2 = 150;
  }
  if (capt_G2 <= 0) {
    capt_G2 = 0;
  }

  if (capt_G3 >= 180) {
    capt_G3 = 150;
  }
  if (capt_G3 <= 0) {
    capt_G3 = 0;
  }

  if (capt_G4 >= 180) {
    capt_G4 = 150;
  }
  if (capt_G4 <= 0) {
    capt_G4 = 0;
  }

  if (capt_G5 >= 180) {
    capt_G5 = 180;
  }
  if (capt_G5 <= 0) {
    capt_G5 = 0;
  }

  if (capt_D1 >= 100) {
    capt_D1 = 100;
  }
  if (capt_D1 <= 0) {
    capt_D1 = 0;
  }

  if (capt_D2 >= 100) {
    capt_D2 = 100;
  }
  if (capt_D2 <= 0) {
    capt_D2 = 0;
  }

  if (capt_D3 >= 120) {
    capt_D3 = 120;
  }
  if (capt_D3 <= 0) {
    capt_D3 = 0;
  }

  if (capt_D4 >= 100) {
    capt_D4 = 100;
  }
  if (capt_D4 <= 0) {
    capt_D4 = 0;
  }

  if (capt_D5 >= 120) {
    capt_D5 = 120;
  }
  if (capt_D5 <= 0) {
    capt_D5 = 0;
  }
}

void ecriture_servo() {

  SG1.write(capt_G1);
  SG2.write(capt_G2);
  SG3.write(capt_G3);
  SG4.write(capt_G4);
  SG5.write(capt_G5);
  SD1.write(capt_D1);
  SD2.write(capt_D2);
  SD3.write(capt_D3);
  SD4.write(capt_D4);
  SD5.write(capt_D5);
  delay(15);
  
}
