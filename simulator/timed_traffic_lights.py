import random
import inspect

global left_percent
global num_cols
global num_rows

class Intersection:

    def __init__(self, time1, time2, int_id):
        self.combo = 4
        self.x1 = 0
        self.int_id = int_id
        self.green_lights = []
        self.combination = 'RRRRGRGR'
        self.text = 'RRRRGRGR'
        self.time1 = time1 # 30 sec
        self.time2 = time2 # 10 sec
        self.total_time = 2 * time1 + 2 * time2

        # queues for each road and direction
        self.queue_North_straight = []
        self.queue_South_straight = []
        self.queue_East_straight = []
        self.queue_West_straight = []
        self.queue_North_left = []
        self.queue_South_left = []
        self.queue_East_left = []
        self.queue_West_left = []

        # the maximum length of the queue
        self.max_queue_len_NL = 0
        self.max_queue_len_NS = 0
        self.max_queue_len_SL = 0
        self.max_queue_len_SS = 0
        self.max_queue_len_EL = 0
        self.max_queue_len_ES = 0
        self.max_queue_len_WL = 0
        self.max_queue_len_WS = 0

        # roads where cars outside the system of intersections can arrive
        self.arrival_roads = []

        # neighboring intersections
        self.N = None
        self.S = None
        self.E = None
        self.W = None
        
    def combo1(self):
        # north and south straight
        self.combo = 1
        self.combination = 'RRRRGRGR'
        self.x1 = 1
        self.green_lights = [5, 7] #lefts then forwards
    
    def combo2(self):
        #north and south left
        self.combo = 2
        self.x1 = 0
        self.combination = 'GRGRRRRR'
        self.green_lights = [1, 3]
        
    def combo3(self):
        #east and west straight
        self.combo = 3
        self.combination = 'RRRRRGRG'
        self.x1 = 1
        self.green_lights = [6, 8] #lefts then forwards
        
    def combo4(self):
        # east and west left
        self.combo = 4
        self.x1 = 0
        self.combination = 'RGRGRRRR'
        self.green_lights = [2, 4]
        
    def switchlights(self):
        if self.combo == 1:
            self.combo2()
        elif self.combo == 2:
            self.combo3()
        elif self.combo == 3:
            self.combo4()
        elif self.combo == 4:
            self.combo1()

    def print_intersection(self):
        self.text = f' <intersection {self.int_id}, combination {self.combination}>'
                            
    def enque(self, road, direction, car):
        # adding car to queue
        if road == 1:
            if direction == 'straight':
                self.queue_North_straight.append(car)
                if len(self.queue_North_straight) > self.max_queue_len_NS:
                    self.max_queue_len_NS = len(self.queue_North_straight)
            else:
                self.queue_North_left.append(car)
                if len(self.queue_North_left) > self.max_queue_len_NL:
                    self.max_queue_len_NL = len(self.queue_North_left)                
        elif road == 2:
            if direction == 'straight':
                self.queue_East_straight.append(car)
                if len(self.queue_East_straight) > self.max_queue_len_ES:
                    self.max_queue_len_ES = len(self.queue_East_straight) 
            else:
                self.queue_East_left.append(car)
                if len(self.queue_East_left) > self.max_queue_len_EL:
                    self.max_queue_len_EL = len(self.queue_East_left) 
        elif road == 3:
            if direction == "straight":
                self.queue_South_straight.append(car)
                if len(self.queue_South_straight) > self.max_queue_len_SS:
                    self.max_queue_len_SS = len(self.queue_South_straight) 
            else:
                self.queue_South_left.append(car)
                if len(self.queue_South_left) > self.max_queue_len_SL:
                    self.max_queue_len_SL = len(self.queue_South_left) 
        else:
            if direction == 'straight':
                self.queue_West_straight.append(car)
                if len(self.queue_West_straight) > self.max_queue_len_WS:
                    self.max_queue_len_WS = len(self.queue_West_straight) 
            else:
                self.queue_West_left.append(car) 
                if len(self.queue_West_left) > self.max_queue_len_WL:
                    self.max_queue_len_WL = len(self.queue_West_left) 
                            
    def deque(self, road, direction):
        # removing car from queue
        queue = None
        if road == 1:
            if direction == 'straight':
                queue = self.queue_North_straight
            else:
                queue = self.queue_North_left
        elif road == 2:
            if direction == 'straight':
                queue = self.queue_East_straight
            else:
                queue = self.queue_East_left
        elif road == 3:
            if direction == "straight":
                queue = self.queue_South_straight
            else:
                queue = self.queue_South_left
        else:
            if direction == 'straight':
                queue = self.queue_West_straight
            else:
                queue = self.queue_West_left
                
        car = queue[0]
        del queue[0]        
    
    def queue_count(self, road, direction):
        # getting length of queue
        if road == 1:
            if direction == 'straight':
                return len(self.queue_North_straight)
            else:
                return len(self.queue_North_left)
        elif road == 2:
            if direction == 'straight':
                return len (self.queue_East_straight)
            else:
                return len(self.queue_East_left)
        elif road == 3:
            if direction == "straight":
                return len(self.queue_South_straight)
            else:
                return len(self.queue_South_left)
        else:
            if direction == 'straight':
                return len(self.queue_West_straight)
            else:
                return len(self.queue_West_left)
    
    def get_next_car(self, road, direction):
        if road == 1:
            if direction == 'straight':
                return self.queue_North_straight[0]
            else:
                return self.queue_North_left[0]
        elif road == 2:
            if direction == 'straight':
                return self.queue_East_straight[0]
            else:
                return self.queue_East_left[0]
        elif road == 3:
            if direction == "straight":
                return self.queue_South_straight[0]
            else:
                return self.queue_South_left[0]
        else:
            if direction == 'straight':
                return self.queue_West_straight[0]
            else:
                return self.queue_West_left[0]
            
    def connect(self, north, east, south, west):
        # connecting the intersections together to form the queue
        self.N = north
        self.S = south
        self.E = east
        self.W = west


class Car:
    def __init__(self, road, direction, time, car_id, intersection):
        self.car_id = car_id
        self.road = road
        self.direction = direction
        self.intersection = intersection
        self.combo = None
        self.arrival_time = time
        self.departure_time = 0
        self.intersection_arrival_time = time
        self.intersection_departure_time = 0
        self.total_wait_time = 0
        
    def print_car(self):
        if self.road == 1:
            self.combo = f' car {self.car_id}, North, {self.direction}, time {self.arrival_time}, intersection {self.intersection.int_id} '
        elif self.road == 2:
            self.combo = f' car {self.car_id}, East, {self.direction}, time {self.arrival_time}, intersection {self.intersection.int_id} '
        elif self.road == 3:
            self.combo = f' car {self.car_id}, South, {self.direction}, time {self.arrival_time}, intersection {self.intersection.int_id} '
        else:
            self.combo = f' car {self.car_id}, West, {self.direction}, time {self.arrival_time}, intersection {self.intersection.int_id} '

SWITCH_LIGHT = 0
CAR_ARRIVAL = 1
CAR_DEPARTURE = 2
class Event:
    def __init__(self, ev_time, ev_type, ev_intersection, ev_car):
        self.ev_time = ev_time
        self.ev_type = ev_type
        self.ev_intersection = ev_intersection
        self.ev_car = ev_car
        
def useEventTime(event):
    return (event.ev_time)


class Simulator:
    def __init__(self):
        self.event_list = []
        self.car_id = 0
        self.car_times = []
        self.check = 0
        # length of the queues
        self.NS = 0
        self.SS = 0
        self.NL = 0
        self.SL = 0
        self.ES = 0
        self.WS = 0
        self.EL = 0
        self.WL = 0
        #the last time in the queues
        self.NS_last = 0
        self.SS_last = 0
        self.NL_last = 0
        self.SL_last = 0
        self.ES_last = 0
        self.WS_last = 0
        self.EL_last = 0
        self.WL_last = 0
        self.car_ids = []
    
    def add_event(self, event):      
        #print("ADDED")
        #self.print_event(event)
        self.event_list.append(event)    
        self.event_list.sort(key=useEventTime)
    
    def delete_event(self):
        del self.event_list[0]
        
    def initialize(self, straight_time, left_time):
        self.event_time = 0
        
        num_intersections = num_rows * num_cols
        
        # Create intersections
        self.intersections = []
        for i in range (num_intersections):
            self.intersections.append(Intersection(straight_time, left_time, i))
        
        # Create intersections
        self.car_id = 0
        
        # Connect intersections
        for i in self.intersections:
            indx = self.intersections.index(i)
            if indx > num_cols-1:
                i.N = self.intersections[indx - num_cols]
                #print(indx, ".N = ", indx - num_cols)
            if indx < num_cols:
                i.S = self.intersections[indx + num_cols]
                #print(indx, ".S = ", indx + num_cols)
            if indx % num_cols != num_cols - 1:
                i.E = self.intersections[indx + 1]
                #print(indx, ".E = ", indx + 1)
            if indx % num_cols != 0:
                i.W = self.intersections[indx - 1]
                #print(indx, ".W = ", indx - 1)       
        
        # Initialize car arrival roads for each intersection.
        for i in self.intersections:
            indx = self.intersections.index(i)
            if indx % num_cols != 0 and indx%num_cols != num_cols - 1:
                if i.N == None:
                    i.arrival_roads = [1]
                    #print(indx, i.arrival_roads)
                elif i.S == None:
                    i.arrival_roads = [3]
                    #print(indx, i.arrival_roads)                    
            elif i.E == None:
                if i.N == None:
                    i.arrival_roads = [1, 2]
                    #print(indx, i.arrival_roads)                    
                else:
                    i.arrival_roads = [2, 3]
                    #print(indx, i.arrival_roads)                    
            elif i.W == None:
                if i.N == None:
                    i.arrival_roads = [1, 4]
                    #print(indx, i.arrival_roads)                    
                else:
                    i.arrival_roads = [3, 4]
                    #print(indx, i.arrival_roads)
        
                    
        
        for i in self.intersections:
            switch_event = Event(0, SWITCH_LIGHT, i, None)
            self.add_event(switch_event)
        

        # Schedule a car arrival on all arrival_roads
        for i in self.intersections:
            car = Car(random.choice(i.arrival_roads), random.choice(['straight', 'left']), random.randint(1, 10), self.car_id, i)
            car_event = Event(car.arrival_time, CAR_ARRIVAL, car.intersection, car)
            self.add_event(car_event)
            self.car_id += 1  
                      
    def run(self, time, time_var):
        while 1:
            ev = self.event_list[0]
            self.event_time = ev.ev_time
            if self.event_time >= time:
                break
            self.execute_event(ev, time_var)
            self.delete_event()

    def print_event(self, event):
        if event.ev_type == 0:
            bob = 'switchlights'
        elif event.ev_type == 1:
            bob = 'car arrival'
        else:
            bob = 'car departure'
            
        event.ev_intersection.print_intersection()
        if event.ev_car != None:
            event.ev_car.print_car()
            print(f'{self.event_time}, {event.ev_time}, {bob}', event.ev_car.combo, event.ev_intersection.text)
        else:
            print(f'{event.ev_time} , {bob}', event.ev_intersection.text)
            
        print()
        
    def execute_switch_light_event(self, event, time_var):
        intersection = event.ev_intersection
        car = event.ev_car
                
        self.NS = len(intersection.queue_North_straight)
        self.NL = len(intersection.queue_North_left)
        self.SL = len(intersection.queue_South_left)
        self.SS = len(intersection.queue_South_straight)
        self.EL = len(intersection.queue_East_left)
        self.ES = len(intersection.queue_East_straight)
        self.WL = len(intersection.queue_West_left)
        self.WS = len(intersection.queue_West_straight)
        
        # Switch lights
        intersection.switchlights()
        
        # Schedule CAR_DEPARTURE events for cars in the queue corresponding to Green lights
        direction = None
        queue1 = None
        queue2 = None
        q1_num = 0
        q2_num = 0
        if intersection.green_lights == [5, 7]:
            queue1 = intersection.queue_North_straight
            queue2 = intersection.queue_South_straight
            q1_num = 1
            q2_num = 3
            direction = 'straight'
            duration = intersection.time1
        elif intersection.green_lights == [1, 3]:
            queue1 = intersection.queue_North_left
            queue2 = intersection.queue_South_left
            q1_num = 1
            q2_num = 3            
            direction = 'left'    
            duration = intersection.time2    
        elif intersection.green_lights == [6, 8]:
            queue1 = intersection.queue_East_straight
            queue2 = intersection.queue_West_straight
            q1_num = 2
            q2_num = 4            
            direction = 'straight'
            duration = intersection.time1
        elif intersection.green_lights == [2, 4]:
            queue1 = intersection.queue_East_left
            queue2 = intersection.queue_West_left
            q1_num = 2
            q2_num = 4             
            direction = 'left'
            duration = intersection.time2
            
        last_time1 = 0
        last_time2 = 0
        move_time = 3
        num_cars = duration / 3
        car_count = 0
        for i in queue1:
            car = i
            car_event = Event(event.ev_time + move_time, CAR_DEPARTURE, intersection, car)
            self.add_event(car_event)
            last_time1 = event.ev_time + move_time
            move_time += 3
            car_count += 1
            #intersection.deque(q1_num, direction)
            if car_count >= num_cars:
                break
            
        for i in range(car_count):
            intersection.deque(q1_num, direction)

                 
        move_time = 3
        car_count = 0
        for i in queue2:
            car = i
            car_event = Event(event.ev_time + move_time, CAR_DEPARTURE, intersection, car)
            self.add_event(car_event)
            last_time2 = event.ev_time + move_time
            move_time += 3
            car_count += 1
            #intersection.deque(q2_num, direction) 
            if car_count >= num_cars:
                break

        for i in range(car_count):
            intersection.deque(q2_num, direction)
                       
        if intersection.green_lights == [5, 7]:
            self.NS_last = last_time1
            self.SS_last = last_time2
        elif intersection.green_lights == [1, 3]:
            self.NL_last = last_time1
            self.SL_last = last_time2   
        elif intersection.green_lights == [6, 8]:
            self.ES_last = last_time1
            self.WS_last = last_time2
        elif intersection.green_lights == [2, 4]:
            self.EL_last = last_time1
            self.WL_last = last_time2
                                    
                        
        # Schedule next SWITCH_LIGHT event
        if intersection.green_lights in [[5, 7], [6, 8]]:
            self.add_event(Event(event.ev_time + intersection.time1, SWITCH_LIGHT, intersection, None))
        else:
            self.add_event(Event(event.ev_time + intersection.time2, SWITCH_LIGHT, intersection, None))        
        

    def execute_car_arrival_event(self, event, time_var):
        intersection = event.ev_intersection
        car = event.ev_car

        # If the light is red or the queue is non zero, add car to queue
        # If the light is green and queue is empty, schedule car departure event        
        if car.direction == 'left':
            lights = intersection.combination[0:4]
        else:
            lights = intersection.combination[4:8]
            
        if lights[car.road - 1] == 'G' and intersection.queue_count(car.road, car.direction) == 0:
            # Schedule car departure
            car_event = Event(event.ev_time + 3, CAR_DEPARTURE, intersection, car)
            self.add_event(car_event)
        else:
            # Add to the queue
            intersection.enque(car.road, car.direction, car)
            
        # Schedule next car arrival event
        if car.total_wait_time == 0:
            #print("New car arrived with id:", self.car_id)
            rand_value = random.randint(1, 100)
            car_direction = 'straight'
            if (rand_value <= left_percent):
                car_direction = 'left'
            next_car = Car(random.choice(intersection.arrival_roads), car_direction, event.ev_time + random.randint(0, time_var), self.car_id, intersection)
            next_car_event = Event(next_car.arrival_time, CAR_ARRIVAL, intersection, next_car)
            self.add_event(next_car_event)
            self.car_id += 1
        
    
    def execute_car_departure_event(self, event, time_var):
      
        car = event.ev_car
        intersection = event.ev_intersection
        
        car.intersection_departure_time = event.ev_time
        #print(car.intersection_departure_time - car.intersection_arrival_time, 'was the wait time at this intersection')
        car.total_wait_time += car.intersection_departure_time - car.intersection_arrival_time
        
        # Schedule a CAR_ARRIVAL event if car is going to another intersection
        next_intersection = None
        if car.direction == 'left':
            # Is there another intersection to the left the current intersection?
            if car.road == 1: # North
                next_intersection = intersection.E
            elif car.road == 2: # East
                next_intersection = intersection.S
            elif car.road == 3: # South
                next_intersection = intersection.W
            else: # West
                next_intersection = intersection.N
        else:
            # Is there another intersection straight ahead?
            if car.road == 1: # North
                next_intersection = intersection.S
            elif car.road == 2: # East
                next_intersection = intersection.W
            elif car.road == 3: # South
                next_intersection = intersection.N
            else: # West
                next_intersection = intersection.E
                
        if next_intersection != None:
            if car.direction == 'left':
                if car.road == 1:
                    car.road = 4
                elif car.road == 2:
                    car.road = 1
                elif car.road == 3:
                    car.road = 2
                else:
                    car.road = 3
            
            rand_value = random.randint(1, 100)
            car.direction = 'straight'
            if (rand_value <= left_percent):
                car.direction = 'left'
                
            car.intersection_arrival_time = event.ev_time + 15
            car.intersection = next_intersection
            ev = Event(event.ev_time + 15, CAR_ARRIVAL, next_intersection, car)
            self.add_event(ev)
        else:
            #print (car.total_wait_time, 'was the total wait time')
            self.car_times.append(car.total_wait_time)
            self.car_ids.append(car.car_id)
        
                        
    def execute_event(self, event, time_var): # event is and Event
        #print("EXECUTED")
        #self.print_event(event)
        if event.ev_type == SWITCH_LIGHT:
            self.execute_switch_light_event(event, time_var)
        elif event.ev_type == CAR_ARRIVAL:
            self.execute_car_arrival_event(event, time_var)
        else:
            self.execute_car_departure_event(event, time_var)
                          
    def average_time(self):
        #print (self.car_times)
        total = 0
        for x in self.car_times:
            total += x
        #print (round(total/len(self.car_times), 2), 'was the average wait time')
        return total/len(self.car_times)

    def print_queue(self, queue):
        # print car_ids in queue
        car_ids = [ ]
        for car in queue:
            car_ids.append(car.car_id)
        return (car_ids)



left_percent = 20
left_time = 10
straight_time = 30

num_rows = 2
num_cols = 2
#car_arrival_interval = 20
#s = Simulator()
#s.initialize(straight_time, left_time)
#s.run(10000, car_arrival_interval)
#s.car_ids.sort()

#print("Number of car arrivals:", s.car_id)
#print("Average car arrival time:", num_rows * num_cols * round(s.event_time/s.car_id, 2))
#print(round(s.average_time(), 2))
    

for i in range(1, 7):
    car_arrival_interval = 4*i
    s = Simulator()
    s.initialize(straight_time, left_time)
    s.run(10000, car_arrival_interval)
    s.car_ids.sort()

#    print("Number of car arrivals:", s.car_id)
#    print("Average car arrival time:", num_rows * num_cols * round(s.event_time/s.car_id, 2))
    print(round(s.average_time(), 2))


'''print("Number of car arrivals:", s.car_id)
print("Number of car departures:", len(s.car_ids))
print("Cars departed:", s.car_ids)

print()
print("Pending events")
for ev in s.event_list:
    s.print_event(ev)

# print queues at intersections
print("Intersection queues")
intersections = [s.intersection0, s.intersection1, s.intersection2, s.intersection3]
for i in intersections:
    print("Intersection:", i.int_id, "NL:", i.max_queue_len_NL, s.print_queue(i.queue_North_left))
    print("Intersection:", i.int_id, "NS:", i.max_queue_len_NS, s.print_queue(i.queue_North_straight))
    print("Intersection:", i.int_id, "EL:", i.max_queue_len_EL, s.print_queue(i.queue_East_left))
    print("Intersection:", i.int_id, "ES:", i.max_queue_len_ES, s.print_queue(i.queue_East_straight))
    print("Intersection:", i.int_id, "SL:", i.max_queue_len_SL, s.print_queue(i.queue_South_left))
    print("Intersection:", i.int_id, "SS:", i.max_queue_len_SS, s.print_queue(i.queue_South_straight))
    print("Intersection:", i.int_id, "WL:", i.max_queue_len_WL, s.print_queue(i.queue_West_left))
    print("Intersection:", i.int_id, "WS:", i.max_queue_len_WS, s.print_queue(i.queue_West_straight))
    '''

