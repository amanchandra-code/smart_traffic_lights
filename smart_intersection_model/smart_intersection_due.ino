#include <SPI.h>
#include <nRF24L01.h>
#include <RF24Network.h>
#include <RF24.h>
#include <RF24Mesh.h>
#include <cppQueue.h>

// setting up the radio
RF24 radio(9, 10); // CE, CSN    
RF24Network network(radio);
RF24Mesh mesh(radio, network);     

uint32_t displayTimer = 0;
uint8_t combo_number = 1;
uint32_t left_signal_duration = 10000;
uint32_t straight_signal_duration = 30000;
uint32_t next_left_signal_time = left_signal_duration;
uint32_t next_straight_signal_time = 0;   
boolean button_state = 0;
uint8_t first_led_pin = 24;

uint8_t car_ids[256];

// Type of message sent from Car to Intersection
#define MSG_TYPE_ANNOUNCE 65

// Message format
struct message_t {
  uint8_t car_direction;
  uint8_t car_road;
  uint8_t light_state;
};

// Light status
uint8_t light_status[4][2];

#define	IMPLEMENTATION	FIFO
#define OVERWRITE		true
#define QUEUE_SIZE			8

// Car queues
cppQueue q_NL(sizeof(uint8_t), QUEUE_SIZE, IMPLEMENTATION, OVERWRITE);
cppQueue q_NS(sizeof(uint8_t), QUEUE_SIZE, IMPLEMENTATION, OVERWRITE);
cppQueue q_SL(sizeof(uint8_t), QUEUE_SIZE, IMPLEMENTATION, OVERWRITE);
cppQueue q_SS(sizeof(uint8_t), QUEUE_SIZE, IMPLEMENTATION, OVERWRITE);
cppQueue q_EL(sizeof(uint8_t), QUEUE_SIZE, IMPLEMENTATION, OVERWRITE);
cppQueue q_ES(sizeof(uint8_t), QUEUE_SIZE, IMPLEMENTATION, OVERWRITE);
cppQueue q_WL(sizeof(uint8_t), QUEUE_SIZE, IMPLEMENTATION, OVERWRITE);
cppQueue q_WS(sizeof(uint8_t), QUEUE_SIZE, IMPLEMENTATION, OVERWRITE);

// Car direction
#define DIRECTION_LEFT 0
#define DIRECTION_STRAIGHT 1

// Road 
#define NORTH 0
#define SOUTH 1
#define EAST 2
#define WEST 3

// Light state
#define GREEN 1
#define RED 2

#define NUM_RETRIES 4

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    // some boards need this because of native USB capability
  }

  for (uint8_t i = first_led_pin; i < first_led_pin + 24; i++) {
    pinMode(i, OUTPUT);
    // setting up the lights
  }

  for (int i = 0; i < 256; i++) {
    car_ids[i] = i;
  }

  Serial.println("Setting initial light status");
  // Set the initial light status
  light_status[0][0] = GREEN;
  light_status[0][1] = RED;
  light_status[1][0] = GREEN;
  light_status[1][1] = RED;  
  light_status[2][0] = RED;  
  light_status[2][1] = RED;
  light_status[3][0] = RED;
  light_status[3][1] = RED;
  
  // Set the nodeID to 0 for the master node
  mesh.setNodeID(0);

  Serial.println(mesh.getNodeID());
  // Connect to the mesh
  if (!mesh.begin()) {
    Serial.println(F("Radio hardware not responding or could not connect to network."));
    while (1) {
      // hold in an infinite loop
    }
  }
}

void loop() { 
  set_leds();

  // Call mesh.update to keep the network updated  
  mesh.update();

  // In addition, keep the 'DHCP service' running on the master node so addresses will
  // be assigned to the sensor nodes
  mesh.DHCP();

  // Check for incoming data from the cars
  if (network.available()) {
    RF24NetworkHeader header;
    network.peek(header);

    struct message_t msg;
    uint8_t car_id = 0;
    switch (header.type) {
      // Display the incoming message from the cars
      case MSG_TYPE_ANNOUNCE: 
        car_id = mesh.getNodeID(header.from_node);
        
        network.read(header, &msg, sizeof(msg));

        Serial.print("Car ID: ");
        Serial.println(car_id); 
        Serial.print("Car direction: ");
        Serial.println(msg.car_direction); 
        Serial.print("Car road: ");
        Serial.println(msg.car_road);

        msg.light_state = light_status[msg.car_road][msg.car_direction];
        
        // Add car to queue if not GREEN
        if (msg.light_state != GREEN) {
          Serial.println("Car added to queue");
          add_car_to_queue(msg.car_road, msg.car_direction, &car_ids[car_id]);
        }

        // Send response to car with color of the light
        for (int i = 0; i < mesh.addrListTop; i++) {
          for (int attempt = 0; attempt < NUM_RETRIES; attempt++) {
            if (mesh.addrList[i].nodeID == car_id) {  
              RF24NetworkHeader header(mesh.addrList[i].address, OCT); //Constructing a header
              Serial.print("Sending attempt: ");
              Serial.println(attempt);
              Serial.print("Sending light state: ");
              if (msg.light_state == GREEN) {
                Serial.println("GREEN");
              } else {
                Serial.println("RED");
              }
              // sending the message to the car
              if (network.write(header, &msg, sizeof(msg)) == 1) {
                Serial.println("Send OK");
                break;
              } else {
                Serial.println("Send Fail");
              }
            }
          }
        }
        break;
      // reading from the mesh  
      default: network.read(header, 0, 0); Serial.println(header.type); break;
    }
  }

  //timed_switch_lights();
  smart_switch_lights();
  signal_green_to_cars();
}

void add_car_to_queue(uint8_t road, uint8_t direction, uint8_t* car_id)
{
  // adding to the queue
  if (road == NORTH) {
    if (direction == DIRECTION_LEFT) {
      Serial.println("Added car to q_NL");
      q_NL.push(car_id);
    } 
    else if (direction == DIRECTION_STRAIGHT) {
      Serial.println("Added car to q_NS");
      q_NS.push(car_id);
    }
  }
  else if (road == SOUTH) {
    if (direction == DIRECTION_LEFT) {
      Serial.println("Added car to q_SL");     
      q_SL.push(car_id);
    }
    else if (direction == DIRECTION_STRAIGHT){
      Serial.println("Added car to q_SS");    
      q_SS.push(car_id);
    }
  }
  else if (road == EAST) {
    if (direction == DIRECTION_LEFT) {
      Serial.println("Added car to q_EL");    
      q_EL.push(car_id);
    }
    else if (direction == DIRECTION_STRAIGHT) {
      Serial.println("Added car to q_ES");    
      q_ES.push(car_id);
    }
  }
  else if (road == WEST) {
    if (direction == DIRECTION_LEFT) {
      Serial.println("Added car to q_WL");    
      q_WL.push(car_id);
    }
    else if (direction == DIRECTION_STRAIGHT) {
      Serial.println("Added car to q_WS");    
      q_WS.push(car_id);
    }
  }
}

void signal_green_to_cars() 
{
  cppQueue* q1 = NULL;
  cppQueue* q2 = NULL;
  struct message_t msg1, msg2;

  if (combo_number == 1) {
    // North and South left
    q1 = &q_NL;
    q2 = &q_SL;
    msg1.car_direction = DIRECTION_LEFT;
    msg1.car_road = NORTH;
    msg2.car_direction = DIRECTION_LEFT;
    msg2.car_road = SOUTH;
  } else if (combo_number == 2) {
    // North and South straight
    q1 = &q_NS;
    q2 = &q_SS; 
    msg1.car_direction = DIRECTION_STRAIGHT;
    msg1.car_road = NORTH;
    msg2.car_direction = DIRECTION_STRAIGHT;
    msg2.car_road = SOUTH;       
  } else if (combo_number == 3) {
    // East and West left
    q1 = &q_EL;
    q2 = &q_WL;    
    msg1.car_direction = DIRECTION_LEFT;
    msg1.car_road = EAST;
    msg2.car_direction = DIRECTION_LEFT;
    msg2.car_road = WEST;    
  } else if (combo_number == 4) {
    // East and West straight
    q1 = &q_ES;
    q2 = &q_WS; 
    msg1.car_direction = DIRECTION_STRAIGHT;
    msg1.car_road = EAST;
    msg2.car_direction = DIRECTION_STRAIGHT;
    msg2.car_road = WEST;       
  }

  // sending message to each car in each of the queues
  for (uint8_t i = 0; i < q1->getCount(); i++) {
    uint8_t car_id;

    q1->peekIdx(&car_id, i);
    msg1.light_state = GREEN;
    for (int i = 0; i < mesh.addrListTop; i++) {
      if (mesh.addrList[i].nodeID == car_id) {  
        RF24NetworkHeader header(mesh.addrList[i].address, OCT); //Constructing a header
        for (int attempt = 0; attempt < NUM_RETRIES; attempt++) {
          Serial.print("Attempt: ");
          Serial.println(attempt);
          Serial.print("Sending GREEN to car id: ");
          Serial.println(car_id);
          if (network.write(header, &msg1, sizeof(msg1)) == 1) {
            Serial.println("Send OK");
            break;
          } else {
            Serial.println("Send failed");
          }
        }
      }
    }
  }

  for (uint8_t i = 0; i < q2->getCount(); i++) {
    uint8_t car_id;

    q2->peekIdx(&car_id, i);
    msg2.light_state = GREEN;
    for (int i = 0; i < mesh.addrListTop; i++) {
      if (mesh.addrList[i].nodeID == car_id) {  
        RF24NetworkHeader header(mesh.addrList[i].address, OCT); //Constructing a header
        for (int attempt = 0; attempt < NUM_RETRIES; attempt++) {
          Serial.print("Attempt: ");
          Serial.println(attempt);
          Serial.print("Sending GREEN to car id: ");
          Serial.println(car_id);
          if (network.write(header, &msg2, sizeof(msg2)) == 1) {
            Serial.println("Send OK");
            break;
          } else {
            Serial.println("Send failed");
          }        
        }
      }
    }
  }

  // Clear the queues.
  q1->clean();
  q2->clean();
}

void timed_switch_lights()
{
  if (combo_number == 1) {
    // checking the combo number and switch the lights according to that
    if (millis()  > next_left_signal_time) {
      combo_number = 2;
      next_straight_signal_time = millis() + straight_signal_duration;
      Serial.println("North and South straight are green");
      light_status[0][0] = RED;
      light_status[0][1] = GREEN;
      light_status[1][0] = RED;
      light_status[1][1] = GREEN;  
      light_status[2][0] = RED;  
      light_status[2][1] = RED;
      light_status[3][0] = RED;
      light_status[3][1] = RED;      
    }
  } else if (combo_number == 2) {
    if (millis() > next_straight_signal_time) {
      combo_number = 3;
      next_left_signal_time = millis() + left_signal_duration;
      Serial.println("East and West left are green");
      light_status[0][0] = RED;
      light_status[0][1] = RED;
      light_status[1][0] = RED;
      light_status[1][1] = RED;  
      light_status[2][0] = GREEN;  
      light_status[2][1] = RED;
      light_status[3][0] = GREEN;
      light_status[3][1] = RED;        
    }
  } else if (combo_number == 3) {
    if (millis()  > next_left_signal_time) {
      combo_number = 4;
      next_straight_signal_time = millis() + straight_signal_duration;
      Serial.println("East and West straight are green");
      light_status[0][0] = RED;
      light_status[0][1] = RED;
      light_status[1][0] = RED;
      light_status[1][1] = RED;  
      light_status[2][0] = RED;  
      light_status[2][1] = GREEN;
      light_status[3][0] = RED;
      light_status[3][1] = GREEN;        
    }
  } else if (combo_number == 4) {
    if (millis() > next_straight_signal_time) {
      combo_number = 1;
      next_left_signal_time = millis() + left_signal_duration;
      Serial.println("North and South left are green");
      light_status[0][0] = GREEN;
      light_status[0][1] = RED;
      light_status[1][0] = GREEN;
      light_status[1][1] = RED;  
      light_status[2][0] = RED;  
      light_status[2][1] = RED;
      light_status[3][0] = RED;
      light_status[3][1] = RED;      
    }
  }
}

void smart_switch_lights() {
  // getting the total queue counts
   int count_ns = q_NL.getCount() + q_NS.getCount() + q_SL.getCount() + q_SS.getCount();
   int count_ew = q_EL.getCount() + q_ES.getCount() + q_WL.getCount() + q_WS.getCount();
   int left_signal_duration = 0;
   int straight_signal_duration = 0;

   if (millis()  <= next_left_signal_time) {
     // Still in left green don't do anything
     return;
   }
   else if (millis() <= next_straight_signal_time) {
     // Switch to straight in same direction
     if (combo_number == 1) {
        combo_number = 2;
        //Serial.println("North and South straight are green");
        light_status[0][0] = RED;
        light_status[0][1] = GREEN;
        light_status[1][0] = RED;
        light_status[1][1] = GREEN;  
        light_status[2][0] = RED;  
        light_status[2][1] = RED;
        light_status[3][0] = RED;
        light_status[3][1] = RED;  
     }
     else if (combo_number == 3) {
        combo_number = 4;
        //Serial.println("East and West straight are green");
        light_status[0][0] = RED;
        light_status[0][1] = RED;
        light_status[1][0] = RED;
        light_status[1][1] = RED;  
        light_status[2][0] = RED;  
        light_status[2][1] = GREEN;
        light_status[3][0] = RED;
        light_status[3][1] = GREEN;  
     }
     return;
   }

   if ((count_ns == 0) && (count_ew == 0)) {
     // Nothing to schedule
     return;
   }
   else if ((count_ns == 0) && (count_ew != 0)) {
     // Schedule East-West
     left_signal_duration = max(q_EL.getCount(), q_WL.getCount()) * 3;
     straight_signal_duration = max(q_ES.getCount(), q_WS.getCount()) * 3;

     if (left_signal_duration != 0) {
        combo_number = 3;
        next_left_signal_time = millis() + left_signal_duration;
        //Serial.println("East and West left are green");
        light_status[0][0] = RED;
        light_status[0][1] = RED;
        light_status[1][0] = RED;
        light_status[1][1] = RED;  
        light_status[2][0] = GREEN;  
        light_status[2][1] = RED;
        light_status[3][0] = GREEN;
        light_status[3][1] = RED;  
     }
     else if (straight_signal_duration != 0) {
        combo_number = 4;
        next_straight_signal_time = millis() + straight_signal_duration;
        //Serial.println("East and West straight are green");
        light_status[0][0] = RED;
        light_status[0][1] = RED;
        light_status[1][0] = RED;
        light_status[1][1] = RED;  
        light_status[2][0] = RED;  
        light_status[2][1] = GREEN;
        light_status[3][0] = RED;
        light_status[3][1] = GREEN;         
     }
   }
   else if ((count_ns != 0) && (count_ew == 0)) {
     // Schedule North-South
     left_signal_duration = max(q_NL.getCount(), q_SL.getCount()) * 3;
     straight_signal_duration = max(q_NS.getCount(), q_SS.getCount()) * 3;

     if (left_signal_duration != 0) {
        combo_number = 1;
        next_left_signal_time = millis() + left_signal_duration; // North and South left
        //Serial.println("North and South left are green");
        light_status[0][0] = GREEN;
        light_status[0][1] = RED;
        light_status[1][0] = GREEN;
        light_status[1][1] = RED;  
        light_status[2][0] = RED;  
        light_status[2][1] = RED;
        light_status[3][0] = RED;
        light_status[3][1] = RED;  
     }
     else if (straight_signal_duration != 0) {
        combo_number = 2;
        next_straight_signal_time = millis() + straight_signal_duration; // North and south straight
        //Serial.println("North and South straight are green");
        light_status[0][0] = RED;
        light_status[0][1] = GREEN;
        light_status[1][0] = RED;
        light_status[1][1] = GREEN;  
        light_status[2][0] = RED;  
        light_status[2][1] = RED;
        light_status[3][0] = RED;
        light_status[3][1] = RED;         
     }     
   }
   else {
     if ((combo_number == 1) || (combo_number == 2)) {
       // Current direction is North-South, switch to East-West direction
        left_signal_duration = max(q_EL.getCount(), q_WL.getCount()) * 3;
        straight_signal_duration = max(q_ES.getCount(), q_WS.getCount()) * 3;

        if (left_signal_duration != 0) {
            combo_number = 3;
            next_left_signal_time = millis() + left_signal_duration; // East west left
            //Serial.println("East and West straight are green");
            light_status[0][0] = RED;
            light_status[0][1] = RED;
            light_status[1][0] = RED;
            light_status[1][1] = RED;  
            light_status[2][0] = GREEN;  
            light_status[2][1] = RED;
            light_status[3][0] = GREEN;
            light_status[3][1] = RED;  
        }
        else if (straight_signal_duration != 0) {
            combo_number = 4;
            next_straight_signal_time = millis() + straight_signal_duration; // east west straight
            //Serial.println("East and West straight are green");
            light_status[0][0] = RED;
            light_status[0][1] = RED;
            light_status[1][0] = RED;
            light_status[1][1] = RED;  
            light_status[2][0] = RED;  
            light_status[2][1] = GREEN;
            light_status[3][0] = RED;
            light_status[3][1] = GREEN;         
        }
     } 
     else {
        // Current direction is East-West, switch to North-South direction
        left_signal_duration = max(q_NL.getCount(), q_SL.getCount()) * 3;
        straight_signal_duration = max(q_NS.getCount(), q_SS.getCount()) * 3;

        if (left_signal_duration != 0) {
            combo_number = 1;
            next_left_signal_time = millis() + left_signal_duration;
            //Serial.println("North and South left are green");
            light_status[0][0] = GREEN;
            light_status[0][1] = RED;
            light_status[1][0] = GREEN;
            light_status[1][1] = RED;  
            light_status[2][0] = RED;  
            light_status[2][1] = RED;
            light_status[3][0] = RED;
            light_status[3][1] = RED;  
        }
        else if (straight_signal_duration != 0) {
            combo_number = 2;
            next_straight_signal_time = millis() + straight_signal_duration;
            //Serial.println("North and South straight are green");
            light_status[0][0] = RED;
            light_status[0][1] = GREEN;
            light_status[1][0] = RED;
            light_status[1][1] = GREEN;  
            light_status[2][0] = RED;  
            light_status[2][1] = RED;
            light_status[3][0] = RED;
            light_status[3][1] = RED;         
        }  
     }
   }
}

void set_leds() {
  for (uint8_t i = 0; i < 8; i++) {
    uint8_t road = i / 2;
    uint8_t direction = i % 2;
    set_led_color(i, light_status[road][direction]);
  }
}

void set_led_color(uint8_t led_num, uint8_t led_color) {
  // setting the rgb led colors
  int first_pin = first_led_pin + led_num * 3;
  if (led_color == GREEN) {
    digitalWrite(first_pin, LOW);
    digitalWrite(first_pin+1, HIGH);
    digitalWrite(first_pin+2, LOW);
  }
  else {
    digitalWrite(first_pin, HIGH);
    digitalWrite(first_pin+1, LOW);
    digitalWrite(first_pin+2, LOW);
  }
}
