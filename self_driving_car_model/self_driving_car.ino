#include <SPI.h>
#include <RF24Network.h>
#include <RF24.h>
#include <RF24Mesh.h>

// setting up the NRF24L01+ wireless RF tranciever
RF24 radio(9, 10); // CE, CSN
RF24Network network(radio);
RF24Mesh mesh(radio, network);     

uint8_t nodeID = 255;

boolean green_straight = 0;
uint8_t button_pin = 2;
boolean button_state = 0;
uint8_t red_light_pin= 8;
uint8_t green_light_pin = 7;
uint8_t blue_light_pin = 6;

// Car ID pins
uint8_t car_id_pin0 = 3;
uint8_t car_id_pin1 = 4;
uint8_t car_id_pin2 = 5;

// Car direction
#define DIRECTION_LEFT 0
#define DIRECTION_STRAIGHT 1

// Road 



#define NORTH 0
#define SOUTH 1
#define EAST 2
#define WEST 3

uint8_t my_direction = DIRECTION_STRAIGHT;
uint8_t my_road = NORTH;
// Type of message sent from Car to Intersection
#define MSG_TYPE_ANNOUNCE 65

// Light state
#define GREEN 1
#define RED 2

// Message format
struct message_t {
  uint8_t car_direction;
  uint8_t car_road;
  uint8_t light_state;
};

#define NUM_RETRIES 4

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    // some boards need this because of native USB capability
  }

  pinMode(red_light_pin, OUTPUT);
  pinMode(green_light_pin, OUTPUT);
  pinMode(blue_light_pin, OUTPUT);
  pinMode(button_pin, INPUT);

  pinMode(car_id_pin0, INPUT);
  pinMode(car_id_pin1, INPUT);
  pinMode(car_id_pin2, INPUT);

  // Read my car_id
  uint8_t bit0 = digitalRead(car_id_pin0);
  uint8_t bit1 = digitalRead(car_id_pin1);
  uint8_t bit2 = digitalRead(car_id_pin2);

  nodeID = (bit2 << 2) | (bit1 << 1) | bit0;
  Serial.print("My car id is: ");
  Serial.println(nodeID);

  my_road = nodeID % 4;
  Serial.print("My road is: ");
  Serial.println(my_road);
  
  // Set the nodeID manually
  mesh.setNodeID(nodeID);
  
  // Connect to the mesh
  Serial.println(F("Connecting to the mesh..."));
  for (int i = 0; i < NUM_RETRIES; i++) {
    if (!mesh.begin()) {
      Serial.print("Attempt: ");
      Serial.println(i);
      Serial.println(F("Radio hardware not responding or could not connect to network."));
    } else {
      Serial.println("Successfully connected to mesh!");
      break;
    }
  }
  
  // Initialize LED to off
  RGB_color(0, 0, 0); // Off
}

void loop()
{
  mesh.update();
  // Read the button state
  button_state = digitalRead(button_pin);

  // Send to the master node if button pressed
  if (button_state == HIGH) {
    // sending the message if the button is pressed
    Serial.println("The button is pressed");

    // Create a message
    struct message_t msg;
    msg.car_direction = my_direction;
    msg.car_road = my_road;

    for (int i = 0; i < NUM_RETRIES; i++) {
      // retrying if the car does not connect to the mesh first try
      if (!mesh.write(&msg, MSG_TYPE_ANNOUNCE, sizeof(msg))) {
  
        // If a write fails, check connectivity to the mesh network
        if ( ! mesh.checkConnection() ) {
          //refresh the network address
          Serial.print("Send attempt: ");
          Serial.println(i);
          Serial.println("Renewing Address");
          if (!mesh.renewAddress()) {
            //If address renewal fails, reconfigure the radio and restart the mesh
            //This allows recovery from most if not all radio errors
            mesh.begin();
          }
        } else {
          Serial.print("Send attempt: ");
          Serial.println(i);
          Serial.println("Send fail, Test OK");
        }
      } else {
        Serial.println("Send OK"); 
        // the car was successfully able to send the message to the intersection
        break;
      }
    }
  }

  while (network.available()) {
    RF24NetworkHeader header;
    message_t response;
    // Getting the message and reading it
    network.read(header, &response, sizeof(response));
    Serial.print("Received message from intersection.  Light state: ");
    if (response.light_state == GREEN) {
      Serial.println("GREEN");
      RGB_color(0, 255, 0);
      // setting light color to green
    }
    else {
      Serial.println("RED");
      RGB_color(255, 0, 0);
      // setting light color red
    }
  } 

  delay(1000);
}

void RGB_color(int red_light_value, int green_light_value, int blue_light_value)
// setting the value of the rgb led
 {
  analogWrite(red_light_pin, red_light_value);
  analogWrite(green_light_pin, green_light_value);
  analogWrite(blue_light_pin, blue_light_value);
}
