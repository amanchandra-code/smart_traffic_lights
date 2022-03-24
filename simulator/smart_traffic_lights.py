import random

global left_percent
global pref_road_percent
global pref_road
global simulation_time
global i2i_arrival_window
global i2i_travel_time
global num_rows
global num_cols

simulation_time = 0

class Intersection2:

    def __init__(self, int_id, min_time, max_time, enable_i2i):
        self.combo = 1
        self.x1 = 0
        self.int_id = int_id
        self.green_lights = [1, 3]
        self.combination = 'GRGRRRRR'
        self.text = 'GRGRRRRR'
        self.duration_straight = 0 
        self.duration_left = 0
        self.queue_North_straight = []
        self.queue_South_straight = []
        self.queue_East_straight = []
        self.queue_West_straight = []
        self.queue_North_left = []
        self.queue_South_left = []
        self.queue_East_left = []
        self.queue_West_left = []
        
        self.N_neighbor_count = 0
        self.S_neighbor_count = 0
        self.E_neighbor_count = 0
        self.W_neighbor_count = 0
        
        self.max_queue_len_NL = 0
        self.max_queue_len_NS = 0
        self.max_queue_len_SL = 0
        self.max_queue_len_SS = 0
        self.max_queue_len_EL = 0
        self.max_queue_len_ES = 0
        self.max_queue_len_WL = 0
        self.max_queue_len_WS = 0
        self.enable_i2i = enable_i2i

        # the roads which cars from the outside can arrive at
        self.arrival_roads = []
        
        # the time of the last departure in each queue
        self.last_dep_NS = 0
        self.last_dep_NL = 0
        self.last_dep_SS = 0
        self.last_dep_SL = 0
        self.last_dep_ES = 0
        self.last_dep_EL = 0
        self.last_dep_WS = 0
        self.last_dep_WL = 0
        
        # the neighboring intersections
        self.N = None
        self.S = None
        self.E = None
        self.W = None
        
        # the times of cars from the neighboring intersections
        self.times_N = []
        self.times_S = []
        self.times_E = []
        self.times_W = []
        
        self.previous_switch_time = 0
        self.next_switch_time_left = 0
        self.next_switch_time_straight = 0
        self.min_time = min_time
        self.max_time= max_time
        self.start_time = 0

        # the average time it takes for the cars to arrive at each direction
        self.avg_inter_arrival_E = 0
        self.avg_inter_arrival_W = 0
        self.avg_inter_arrival_S = 0
        self.avg_inter_arrival_N = 0
        
    def combo1(self):
        # North and South Straight
        self.combo = 1
        self.combination = 'RRRRGRGR'
        self.x1 = 1
        self.green_lights = [5, 7] #lefts then forwards
    
    def combo2(self):
        # North and South Left
        self.combo = 2
        self.x1 = 0
        self.combination = 'GRGRRRRR'
        self.green_lights = [1, 3]
        
    def combo3(self):
        # East and West Straight
        self.combo = 3
        self.combination = 'RRRRRGRG'
        self.x1 = 1
        self.green_lights = [6, 8] #lefts then forwards
        
    def combo4(self):
        # East and West Left
        self.combo = 4
        self.x1 = 0
        self.combination = 'RGRGRRRR'
        self.green_lights = [2, 4]

    # Combos 5-7 are not used for now
    def combo5(self):
        self.combo = 5
        self.combination = 'GRRRGRRR'
        self.green_lights = [1, 5]

    def combo6(self):
        self.combo = 6
        self.combination = 'RGRRRGRR'
        self.green_lights = [2, 6]

    def combo7(self):
        self.combo = 6
        self.combination = 'RRGRRRGR'
        self.green_lights = [3, 7]

    def combo8(self):
        self.combo = 6
        self.combination = 'RRRGRRRG'
        self.green_lights = [4, 8]
    
    def increment_neighbor_count(self, neighbor, count):
        #print("Increment:", self.int_id, neighbor.int_id, count)
        if neighbor == self.N:
            self.N_neighbor_count += count
            #print("N count:", self.N_neighbor_count)
        elif neighbor == self.S:
            self.S_neighbor_count += count
            #print("S count:", self.S_neighbor_count)
        elif neighbor == self.E:
            self.E_neighbor_count += count
            #print("E count:", self.E_neighbor_count)
        elif neighbor == self.W:
            self.W_neighbor_count += count
            #print("W count:", self.W_neighbor_count)

    def decrement_neighbor_count(self, neighbor, count):
        #print("Decrement:", self.int_id, neighbor.int_id, count)        
        if neighbor == self.N:
            self.N_neighbor_count -= count
            #print("N count:", self.N_neighbor_count)            
        elif neighbor == self.S:
            self.S_neighbor_count -= count
            #print("S count:", self.S_neighbor_count)            
        elif neighbor == self.E:
            self.E_neighbor_count -= count
            #print("E count:", self.E_neighbor_count)            
        elif neighbor == self.W:
            self.W_neighbor_count -= count
            #print("W count:", self.W_neighbor_count)
                        
    def switchlights(self):
        # the purpose of this function is to switch the light phases based on the queues
        
        # If we are still in left green don't do anything
        if simulation_time <= self.next_switch_time_left:
            return False

        # If we are done with green, switch to straight in same direction
        elif simulation_time <= self.next_switch_time_straight:
            if self.combo == 2:
                self.combo1()
                self.last_dep_NS = min(self.max_time, len(self.queue_North_straight)*3) + simulation_time
                self.last_dep_SS = min(self.max_time, len(self.queue_South_straight)*3) + simulation_time
            elif self.combo == 4:
                self.combo3()
                self.last_dep_ES = min(self.max_time, len(self.queue_East_straight)*3) + simulation_time
                self.last_dep_WS = min(self.max_time, len(self.queue_West_straight)*3) + simulation_time 

             
        # Done with previous direction.  Re-evaluate and determine which direction has the most number of cars queued
        count_ns = len(self.queue_North_left) + len(self.queue_North_straight) + len(self.queue_South_left) + len(self.queue_South_straight)
        count_ew = len(self.queue_East_left) + len(self.queue_East_straight) + len(self.queue_West_left) + len(self.queue_West_straight)
        
        if count_ns == 0 and count_ew == 0:
            # Nothing to schedule
            return False
        
        if count_ns == 0 and count_ew != 0:
            # Schedule East-West direction
            self.duration_left = max(len(self.queue_East_left), len(self.queue_West_left)) * 3
            self.duration_straight = max(len(self.queue_East_straight), len(self.queue_West_straight)) * 3

            if self.duration_left != 0:
                self.combo4()
                self.last_dep_EL = min(self.max_time, len(self.queue_East_left) * 3) + simulation_time
                self.last_dep_WL = min(self.max_time, len(self.queue_West_left) * 3) + simulation_time
            elif self.duration_straight != 0:
                self.combo3()
                self.last_dep_ES = min(self.max_time, len(self.queue_East_straight)*3) + simulation_time
                self.last_dep_WS = min(self.max_time, len(self.queue_West_straight)*3) + simulation_time  
                            
        if count_ew == 0 and count_ns != 0:
            # Schedule North-South direction            
            self.duration_left = max(len(self.queue_North_left), len(self.queue_South_left)) * 3
            self.duration_straight = max(len(self.queue_North_straight), len(self.queue_South_straight)) * 3

            if self.duration_left != 0:
                self.combo2()
                self.last_dep_NL = min(self.max_time, len(self.queue_North_left) * 3) + simulation_time
                self.last_dep_SL = min(self.max_time, len(self.queue_South_left) * 3) + simulation_time
            elif self.duration_straight != 0:
                self.combo1()
                self.last_dep_NS = min(self.max_time, len(self.queue_North_straight)*3) + simulation_time
                self.last_dep_SS = min(self.max_time, len(self.queue_South_straight)*3) + simulation_time
        
        if count_ew != 0 and count_ns != 0:
            if self.combo in [1, 2]:
                # Current direction is North-South, switch to East-West direction
                self.duration_left = max(len(self.queue_East_left), len(self.queue_West_left)) * 3
                self.duration_straight = max(len(self.queue_East_straight), len(self.queue_West_straight)) * 3
    
                if self.duration_left != 0:
                    self.combo4()
                    self.last_dep_EL = min(self.max_time, len(self.queue_East_left) * 3) + simulation_time
                    self.last_dep_WL = min(self.max_time, len(self.queue_West_left) * 3) + simulation_time
                elif self.duration_straight != 0:
                    self.combo3()
                    self.last_dep_ES = min(self.max_time, len(self.queue_East_straight)*3) + simulation_time
                    self.last_dep_WS = min(self.max_time, len(self.queue_West_straight)*3) + simulation_time
            else:
                # Current direction in East-West, switch to North-South direction            
                self.duration_left = max(len(self.queue_North_left), len(self.queue_South_left)) * 3
                self.duration_straight = max(len(self.queue_North_straight), len(self.queue_South_straight)) * 3
    
                if self.duration_left != 0:
                    self.combo2()
                    self.last_dep_NL = min(self.max_time, len(self.queue_North_left) * 3) + simulation_time
                    self.last_dep_SL = min(self.max_time, len(self.queue_South_left) * 3) + simulation_time
                elif self.duration_straight != 0:
                    self.combo1()
                    self.last_dep_NS = min(self.max_time, len(self.queue_North_straight)*3) + simulation_time
                    self.last_dep_SS = min(self.max_time, len(self.queue_South_straight)*3) + simulation_time                                

        if self.enable_i2i:
            last_dep_time = self.duration_left + self.duration_straight + simulation_time
            i2i_last_dep_time = last_dep_time + i2i_arrival_window
            count_neighbor_cars = 0
            if self.combo in [1, 2]:
                # North-South was selected
                count_N = 0
                for neighbor_car_time in self.times_N:
                    if last_dep_time < neighbor_car_time <= i2i_last_dep_time:
                        count_N += 1
                
                #print("count N:", count_N)
                
                for i in range(count_N):
                    del self.times_N[0]
                    
                count_S = 0
                for neighbor_car_time in self.times_S:
                    if last_dep_time < neighbor_car_time <= i2i_last_dep_time:
                        count_S += 1
                
                #print("count S:", count_S)
        
                for i in range(count_S):
                    del self.times_S[0]
                
                count_neighbor_cars = max(count_N, count_S)
                #count_neighbor_cars = 0
                #print("Neighbor cars NS:", count_neighbor_cars)
            else:
                # East-West was selected
                count_E = 0
                for neighbor_car_time in self.times_E:
                    if last_dep_time < neighbor_car_time <= i2i_last_dep_time:
                        count_E += 1
                
                #print("count E:", count_E)
                
                for i in range(count_E):
                    del self.times_E[0]
                    
                count_W = 0
                for neighbor_car_time in self.times_W:
                    if last_dep_time < neighbor_car_time <= i2i_last_dep_time:
                        count_W += 1
                
                #print("count W:", count_W)

                for i in range(count_W):
                    del self.times_W[0]
                    
                count_neighbor_cars = max(count_E, count_W)                
                #print("Neighbor cars EW:", count_neighbor_cars)

            self.duration_left += round(left_percent * count_neighbor_cars / 100) * 3 
            self.duration_straight += round((100 - left_percent) * count_neighbor_cars / 100) * 3 

        # calculating the durations of the times of the lights
        self.duration_left = min(self.duration_left, self.max_time)
        self.duration_straight= min(self.duration_straight, self.max_time)
        self.duration_left = max(self.duration_left, min_time)
        self.duration_straight = max(self.duration_straight, min_time)
        self.next_switch_time_left = simulation_time + self.duration_left
        self.next_switch_time_straight = simulation_time + self.duration_straight
        
        return True

    def add_dep_from_neighbor(self, neighbor, arrival_time):
        # adding a departure from the neighbor
        if neighbor == self.N:
            self.times_N.append(arrival_time)
        elif neighbor == self.S:
            self.times_S.append(arrival_time)
        elif neighbor == self.E:
            self.times_E.append(arrival_time)
        elif neighbor == self.W:
            self.times_W.append(arrival_time)

    def print_intersection(self):
        self.text = f' <intersection {self.int_id}, combination {self.combination}>'
                            
    def enque(self, road, direction, car):
        # adding the car to the queue
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
        # removing the car from the queue
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
        # getting the length of the queue
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
        # connecting the intersections in their systems
        self.N = north
        self.S = south
        self.E = east
        self.W = west


    def get_last_dep(self, road, d):
        # getting the last departure time from each queue
        if road == 1 and d == 'straight':
            return self.last_dep_NS
        if road == 1 and d == 'left':
            return self.last_dep_NL
        if road == 2 and d == 'straight':
            return self.last_dep_ES
        if road == 2 and d == 'left':
            return self.last_dep_EL
        if road == 3 and d == 'straight':
            return self.last_dep_SS
        if road == 3 and d == 'left':
            return self.last_dep_SL
        if road == 4 and d == 'straight':
            return self.last_dep_WS
        if road == 4 and d == 'left':
            return self.last_dep_WL
        
class Car:
    # car object
    def __init__(self, road, direction, time, car_id, intersection):
        self.car_id = car_id
        self.road = road
        self.direction = direction
        self.intersection = intersection
        self.combo = None # for displaying purposes
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
        self.car_ids = []
        self.NScars = 0
        self.EWcars = 0
    
    def add_event(self, event):
        # adding an event to the event list
        #print("ADDED")
        #self.print_event(event)
        self.event_list.append(event)    
        self.event_list.sort(key=useEventTime)
    
    def delete_event(self):
        # deleting the first event from the list
        del self.event_list[0]
        
    def initialize(self, min_time, max_time, enable_i2i):
        # initializing all of the intersections based on the number of rows and columns
        # connecting the intersections
        
        #random.seed(10)
    
        num_intersections = num_rows * num_cols
        
        # Create intersections
        self.intersections = []
        for i in range (num_intersections):
            self.intersections.append(Intersection2(i, min_time, max_time, enable_i2i))
        
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
                elif i.S == None:
                    i.arrival_roads = [3]
            elif i.E == None:
                if i.N == None:
                    i.arrival_roads = [1, 2]
                else:
                    i.arrival_roads = [2, 3]
            elif i.W == None:
                if i.N == None:
                    i.arrival_roads = [1, 4]
                else:
                    i.arrival_roads = [3, 4]
                    
        
        north_south = 0
        east_west = 0
        for i in self.intersections:
            for j in i.arrival_roads:
                if j in [1, 3]:
                    north_south += 1
                else:
                    east_west += 1
        
                    
            
        #print(north_south, east_west)
        for i in self.intersections:
            for j in i.arrival_roads:
                if j == 1:
                    i.avg_inter_arrival_N = round((100*car_arrival_interval/(100-pref_road_percent))*north_south)
                    #print(i.avg_inter_arrival_N)
                if j == 2:
                    i.avg_inter_arrival_E = round(100*car_arrival_interval/pref_road_percent*east_west)
                    #print(i.avg_inter_arrival_E)
                if j == 3:
                    i.avg_inter_arrival_S = round((100*car_arrival_interval/(100-pref_road_percent))*north_south)
                    #print(i.avg_inter_arrival_S)
                if j == 4:
                    i.avg_inter_arrival_W = round((100*car_arrival_interval/pref_road_percent)*east_west)
                    #print(i.avg_inter_arrival_W)
        
        for i in self.intersections:
            switch_event = Event(0, SWITCH_LIGHT, i, None)
            self.add_event(switch_event)
        

        # Schedule a car arrival on all arrival_roads
        for i in self.intersections:
            for j in i.arrival_roads:
                car = Car(j, random.choice(['straight', 'left']), random.randint(1, 10), self.car_id, i)
                car_event = Event(car.arrival_time, CAR_ARRIVAL, car.intersection, car)
                self.add_event(car_event)
                self.car_id += 1
        
    def run(self, time, time_var):
        # running the simulation
        global simulation_time
        while 1:
            ev = self.event_list[0]
            simulation_time = ev.ev_time
            if simulation_time >= time:
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
            print(simulation_time, bob, event.ev_car.combo, event.ev_intersection.text)
        else:
            print(f'{simulation_time} , {bob}', event.ev_intersection.text)
            
        print()

    def execute_switch_light_event(self, event, time_var):
        intersection = event.ev_intersection
        car = event.ev_car
        
        # Switch lights
        x = intersection.switchlights()
        if x == False:
            # Schedule next SWITCH_LIGHT
            next_switchlights = Event(event.ev_time + 1, SWITCH_LIGHT, intersection, None)
            self.add_event(next_switchlights)
            return
        
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
            duration = intersection.duration_straight
        elif intersection.green_lights == [1, 3]:
            queue1 = intersection.queue_North_left
            queue2 = intersection.queue_South_left
            q1_num = 1
            q2_num = 3            
            direction = 'left'    
            duration = intersection.duration_left    
        elif intersection.green_lights == [6, 8]:
            queue1 = intersection.queue_East_straight
            queue2 = intersection.queue_West_straight
            q1_num = 2
            q2_num = 4            
            direction = 'straight'
            duration = intersection.duration_straight
        elif intersection.green_lights == [2, 4]:
            queue1 = intersection.queue_East_left
            queue2 = intersection.queue_West_left
            q1_num = 2
            q2_num = 4             
            direction = 'left'
            duration = intersection.duration_left
        move_time = 3
        num_cars = duration / 3
        car_count = 0
        for i in queue1:
            car = i
            car_event = Event(event.ev_time + move_time, CAR_DEPARTURE, intersection, car)
            self.add_event(car_event)
            move_time += 3
            car_count += 1
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
            move_time += 3
            car_count += 1
            if car_count >= num_cars:
                break

        for i in range(car_count):
            intersection.deque(q2_num, direction)
                        
        # Schedule next SWITCH_LIGHT
        next_switchlights = Event(event.ev_time + 1, SWITCH_LIGHT, intersection, None)
        self.add_event(next_switchlights)

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
            dep_time = max(intersection.get_last_dep(car.road, car.direction), event.ev_time)
            car_event = Event(dep_time + 3, CAR_DEPARTURE, intersection, car)
            #car_event = Event(event.ev_time + 3, CAR_DEPARTURE, intersection, car)
            self.add_event(car_event)
        else:
            # Add to the queue
            intersection.enque(car.road, car.direction, car)
            
        # Schedule next car arrival event
        # Check if the road car arrived on does not have a neighbor
        if car.road in intersection.arrival_roads:
            rand_value = random.randint(1, 100)
            car_direction = 'straight'
            if (rand_value <= left_percent):
                car_direction = 'left'   
            
            # Calculate the following using the formula
            #avg_inter_arrival_EW = round(100*self.time_var/pref_road_percent_EW)
            #avg_inter_arrival_NS = round(100*self.time_var/(100-pref_road_percent_EW))
            #print(avg_inter_arrival_EW, avg_inter_arrival_NS)
            
            if car.road == 1:
                next_car = Car(car.road, car_direction, event.ev_time + random.randint(0, intersection.avg_inter_arrival_N), self.car_id, intersection)
                self.NScars += 1            
            elif car.road == 2:
                next_car = Car(car.road, car_direction, event.ev_time + random.randint(0, intersection.avg_inter_arrival_E), self.car_id, intersection)            
                self.EWcars += 1
            elif car.road == 3:
                next_car = Car(car.road, car_direction, event.ev_time + random.randint(0, intersection.avg_inter_arrival_S), self.car_id, intersection)
                self.NScars += 1            
            elif car.road == 4:
                next_car = Car(car.road, car_direction, event.ev_time + random.randint(0, intersection.avg_inter_arrival_W), self.car_id, intersection)            
                self.EWcars += 1
                
            #next_car = Car(random.choice(intersection.arrival_roads), car_direction, event.ev_time + random.randint(0, time_var), self.car_id, intersection)
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
        
        if intersection.enable_i2i:
            
            prev_intersection = None
            if car.road == 1: # North
                prev_intersection = intersection.N
            elif car.road == 2: # East
                prev_intersection = intersection.E
            elif car.road == 3: # South
                prev_intersection = intersection.S
            else: # West
                prev_intersection = intersection.W
            
            if prev_intersection != None:
                intersection.decrement_neighbor_count(prev_intersection, 1)
                        
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

            car.intersection_arrival_time = event.ev_time + i2i_travel_time
            car.intersection = next_intersection
            ev = Event(event.ev_time + i2i_travel_time, CAR_ARRIVAL, next_intersection, car)
            self.add_event(ev)
            
            # Tell neighbor car is coming their way
            if intersection.enable_i2i:
                next_intersection.increment_neighbor_count(intersection, 1)
                next_intersection.add_dep_from_neighbor(intersection, car.intersection_arrival_time)
        else:
            #print (car.total_wait_time, 'was the total wait time')
            self.car_times.append(car.total_wait_time)
            self.car_ids.append(car.car_id)
        
                        
    def execute_event(self, event, time_var): # event is and Event
        # executing the event based on the event type
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

# input parameters
num_rows = 2
num_cols = 4
car_arrival_interval = 1
min_time = 6
max_time = 30


left_percent = 20
pref_road_percent = 80
pref_road = 2 # East
i2i_arrival_window = 10
i2i_travel_time = 15

# for loop to run multiple times with different car arrival intervals
for i in range(1, 7):
    car_arrival_interval = i
    s = Simulator()
    s.initialize(min_time, max_time, True)
    s.run(10000, car_arrival_interval)
    s.car_ids.sort()
    print(round(s.average_time(), 2))


#s = Simulator()
#s.initialize(min_time, max_time, True)
#s.run(10000, car_arrival_interval)
#s.car_ids.sort()
#print("Average car arrival time:", num_rows * num_cols * round(10000/s.car_id, 2))
#print(round(s.average_time(), 2))

    
#for i in range(10):
#    s = Simulator()
#    s.initialize(min_time, max_time, True)
#    s.run(10000, car_arrival_interval)
#    s.car_ids.sort()
#    print("Average car arrival time:", round(s.event_time/s.car_id, 2))
#    print("Average wait time:", round(s.average_time(), 2), "seconds")

'''print()
print("Number of car arrivals:", s.car_id)
print("Number of car departures:", len(s.car_ids))
print("Cars departed:", s.car_ids)'''


'''for i in range(2, 13):
    s = Simulator()
    s.initialize(30, 10)
    s.run(10000, i*10)
    s.car_ids.sort()
    
    print("Average car arrival time:", round(s.event_time/s.car_id, 2))
    print("Average wait time:", round(s.average_time(), 2), "seconds")
    print()

print('OOGABOOGA')

for i in range(2, 13):
    s = Simulator()
    s.initialize(60, 20)
    s.run(10000, i*10)
    s.car_ids.sort()
    
    print("Average car arrival time:", round(s.event_time/s.car_id, 2))
    print("Average wait time:", round(s.average_time(), 2), "seconds")
    print()
print("Number of car arrivals:", s.car_id)
print("Number of car departures:", len(s.car_ids))
print("Cars departed:", s.car_ids)
'''
'''print()
print("Pending events")
for ev in s.event_list:
    s.print_event(ev)
'''
        
# print queues at intersections
'''print("Intersection queues")
for i in s.intersections:
    print("Intersection:", i.int_id, "NL:", i.max_queue_len_NL, s.print_queue(i.queue_North_left))
    print("Intersection:", i.int_id, "NS:", i.max_queue_len_NS, s.print_queue(i.queue_North_straight))
    print("Intersection:", i.int_id, "EL:", i.max_queue_len_EL, s.print_queue(i.queue_East_left))
    print("Intersection:", i.int_id, "ES:", i.max_queue_len_ES, s.print_queue(i.queue_East_straight))
    print("Intersection:", i.int_id, "SL:", i.max_queue_len_SL, s.print_queue(i.queue_South_left))
    print("Intersection:", i.int_id, "SS:", i.max_queue_len_SS, s.print_queue(i.queue_South_straight))
    print("Intersection:", i.int_id, "WL:", i.max_queue_len_WL, s.print_queue(i.queue_West_left))
    print("Intersection:", i.int_id, "WS:", i.max_queue_len_WS, s.print_queue(i.queue_West_straight))

print(s.NScars, s.EWcars)'''
