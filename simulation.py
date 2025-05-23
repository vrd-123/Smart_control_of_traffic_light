import random
import math
import time
import threading
import pygame
import sys
import os

# Default values of signal times
paused = False
defaultRed = 150
defaultYellow = 5
defaultGreen = 20
defaultMinimum = 10
defaultMaximum = 60

signals = []
noOfSignals = 4
simTime = 300
timeElapsed = 0

currentGreen = 0
nextGreen = (currentGreen+1)%noOfSignals
currentYellow = 0

# Average times for vehicles to pass the intersection
carTime = 2
bikeTime = 1
rickshawTime = 2.25 
busTime = 2.5
truckTime = 2.5

# Count of vehicles at a traffic signal
noOfCars = 0
noOfBikes = 0
noOfBuses = 0
noOfTrucks = 0
noOfRickshaws = 0
noOfLanes = 2

# Red signal time at which cars will be detected at a signal
detectionTime = 5

speeds = {'car':2.25, 'bus':1.8, 'truck':1.8, 'rickshaw':2, 'bike':2.5}

# Coordinates of start
x = {'right':[0,0,0], 'down':[755,727,697], 'left':[1400,1400,1400], 'up':[602,627,657]}    
y = {'right':[348,370,398], 'down':[0,0,0], 'left':[498,466,436], 'up':[800,800,800]}

vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 
            'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'crossed':0}}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'rickshaw', 4:'bike'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(530,230),(810,230),(810,570),(530,570)]
signalTimerCoods = [(530,210),(810,210),(810,550),(530,550)]
vehicleCountCoods = [(480,210),(880,210),(880,550),(480,550)]
vehicleCountTexts = ["0", "0", "0", "0"]

# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
stops = {'right': [580,580,580], 'down': [320,320,320], 'left': [810,810,810], 'up': [545,545,545]}

mid = {'right': {'x':705, 'y':445}, 'down': {'x':695, 'y':450}, 
       'left': {'x':695, 'y':425}, 'up': {'x':695, 'y':400}}
rotationAngle = 3

# Gap between vehicles
gap = 15    # stopping gap
gap2 = 15   # moving gap

pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, red, yellow, green, minimum, maximum):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = "30"
        self.totalGreenTime = 0
        
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.currentImage = pygame.image.load(path)

        if direction == 'right':
            if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0:
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().width - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap    
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif direction == 'left':
            if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0:
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().width + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] += temp
            stops[direction][lane] += temp
        elif direction == 'down':
            if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0:
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().height - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif direction == 'up':
            if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0:
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().height + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] += temp
            stops[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.currentImage, (self.x, self.y))

    def move(self):
        if paused:
            return
            
        if self.direction == 'right':
            if self.crossed == 0 and self.x+self.currentImage.get_rect().width > stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if self.willTurn == 1:
                if self.crossed == 0 or self.x+self.currentImage.get_rect().width < mid[self.direction]['x']:
                    if ((self.x+self.currentImage.get_rect().width <= self.stop or (currentGreen==0 and currentYellow==0) or self.crossed==1) and 
                        (self.index==0 or self.x+self.currentImage.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - gap2) or 
                         vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                        self.x += self.speed
                else:   
                    if self.turned == 0:
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 2
                        self.y += 1.8
                        if self.rotateAngle == 90:
                            self.turned = 1
                    else:
                        if (self.index==0 or self.y+self.currentImage.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - gap2) or 
                            self.x+self.currentImage.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - gap2)):
                            self.y += self.speed
            else: 
                if ((self.x+self.currentImage.get_rect().width <= self.stop or self.crossed == 1 or (currentGreen==0 and currentYellow==0)) and 
                    (self.index==0 or self.x+self.currentImage.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - gap2) or 
                     (vehicles[self.direction][self.lane][self.index-1].turned==1))):                
                    self.x += self.speed

        elif self.direction == 'down':
            if self.crossed == 0 and self.y+self.currentImage.get_rect().height > stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if self.willTurn == 1:
                if self.crossed == 0 or self.y+self.currentImage.get_rect().height < mid[self.direction]['y']:
                    if ((self.y+self.currentImage.get_rect().height <= self.stop or (currentGreen==1 and currentYellow==0) or self.crossed==1) and 
                        (self.index==0 or self.y+self.currentImage.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - gap2) or 
                         vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                        self.y += self.speed
                else:   
                    if self.turned == 0:
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 2.5
                        self.y += 2
                        if self.rotateAngle == 90:
                            self.turned = 1
                    else:
                        if (self.index==0 or self.x > (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or 
                            self.y < (vehicles[self.direction][self.lane][self.index-1].y - gap2)):
                            self.x -= self.speed
            else: 
                if ((self.y+self.currentImage.get_rect().height <= self.stop or self.crossed == 1 or (currentGreen==1 and currentYellow==0)) and 
                    (self.index==0 or self.y+self.currentImage.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - gap2) or 
                     (vehicles[self.direction][self.lane][self.index-1].turned==1))):                
                    self.y += self.speed
            
        elif self.direction == 'left':
            if self.crossed == 0 and self.x < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if self.willTurn == 1:
                if self.crossed == 0 or self.x > mid[self.direction]['x']:
                    if ((self.x >= self.stop or (currentGreen==2 and currentYellow==0) or self.crossed==1) and 
                        (self.index==0 or self.x > (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or 
                         vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                        self.x -= self.speed
                else: 
                    if self.turned == 0:
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 1.8
                        self.y -= 2.5
                        if self.rotateAngle == 90:
                            self.turned = 1
                    else:
                        if (self.index==0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height + gap2) or 
                            self.x > (vehicles[self.direction][self.lane][self.index-1].x + gap2)):
                            self.y -= self.speed
            else: 
                if ((self.x >= self.stop or self.crossed == 1 or (currentGreen==2 and currentYellow==0)) and 
                    (self.index==0 or self.x > (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or 
                     (vehicles[self.direction][self.lane][self.index-1].turned==1))):                
                    self.x -= self.speed

        elif self.direction == 'up':
            if self.crossed == 0 and self.y < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if self.willTurn == 1:
                if self.crossed == 0 or self.y > mid[self.direction]['y']:
                    if ((self.y >= self.stop or (currentGreen==3 and currentYellow==0) or self.crossed == 1) and 
                        (self.index==0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height + gap2) or 
                         vehicles[self.direction][self.lane][self.index-1].turned==1)):
                        self.y -= self.speed
                else:   
                    if self.turned == 0:
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 1
                        self.y -= 1
                        if self.rotateAngle == 90:
                            self.turned = 1
                    else:
                        if (self.index==0 or self.x < (vehicles[self.direction][self.lane][self.index-1].x - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width - gap2) or 
                            self.y > (vehicles[self.direction][self.lane][self.index-1].y + gap2)):
                            self.x += self.speed
            else: 
                if ((self.y >= self.stop or self.crossed == 1 or (currentGreen==3 and currentYellow==0)) and 
                    (self.index==0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height + gap2) or 
                     (vehicles[self.direction][self.lane][self.index-1].turned==1))):                
                    self.y -= self.speed

# Simple Button class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.Font(None, 30)
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, 0, 10)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, 10)  # Border
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)
        
    def update(self, pos):
        if self.is_hovered(pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

def initialize():
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red+ts1.yellow+ts1.green, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts4)
    repeat()

def setTime():
    global noOfCars, noOfBikes, noOfBuses, noOfTrucks, noOfRickshaws
    if not paused:  
        os.system("say detecting vehicles, "+directionNumbers[(currentGreen+1)%noOfSignals])
        
        noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0,0,0,0,0
        for j in range(len(vehicles[directionNumbers[nextGreen]][0])):
            vehicle = vehicles[directionNumbers[nextGreen]][0][j]
            if vehicle.crossed == 0:
                noOfBikes += 1
                
        for i in range(1,3):
            for j in range(len(vehicles[directionNumbers[nextGreen]][i])):
                vehicle = vehicles[directionNumbers[nextGreen]][i][j]
                if vehicle.crossed == 0:
                    vclass = vehicle.vehicleClass
                    if vclass == 'car':
                        noOfCars += 1
                    elif vclass == 'bus':
                        noOfBuses += 1
                    elif vclass == 'truck':
                        noOfTrucks += 1
                    elif vclass == 'rickshaw':
                        noOfRickshaws += 1

        greenTime = math.ceil(((noOfCars*carTime) + (noOfRickshaws*rickshawTime) + (noOfBuses*busTime) + 
                             (noOfTrucks*truckTime) + (noOfBikes*bikeTime))/(noOfLanes+1))
        print('Green Time: ', greenTime)
        
        if greenTime < defaultMinimum:
            greenTime = defaultMinimum
        elif greenTime > defaultMaximum:
            greenTime = defaultMaximum
            
        signals[(currentGreen+1)%(noOfSignals)].green = greenTime
   
def repeat():
    global currentGreen, currentYellow, nextGreen
    while signals[currentGreen].green > 0:
        if not paused:
            printStatus()
            updateValues()
            if signals[(currentGreen+1)%(noOfSignals)].red == detectionTime:
                thread = threading.Thread(name="detection", target=setTime, args=())
                thread.daemon = True
                thread.start()
            time.sleep(1)
        else:
            time.sleep(0.1)  
            
    if paused:
        time.sleep(0.1)
        repeat()
        return
        
    currentYellow = 1
    vehicleCountTexts[currentGreen] = "0"
    
    for i in range(0,3):
        stops[directionNumbers[currentGreen]][i] = defaultStop[directionNumbers[currentGreen]]
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
            
    while signals[currentGreen].yellow > 0:
        if not paused:
            printStatus()
            updateValues()
            time.sleep(1)
        else:
            time.sleep(0.1)  
            
    if paused:
        time.sleep(0.1)
        repeat()
        return
        
    currentYellow = 0
    signals[currentGreen].green = defaultGreen
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed
       
    currentGreen = nextGreen
    nextGreen = (currentGreen+1)%noOfSignals
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
    repeat()     

def printStatus():                                                                                           
    for i in range(0, noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                print(" GREEN TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
            else:
                print("YELLOW TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
        else:
            print("   RED TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
    print()

def updateValues():
    if paused:
        return
        
    for i in range(0, noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                signals[i].green -= 1
                signals[i].totalGreenTime += 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1

def generateVehicles():
    while True:
        if paused:
            time.sleep(0.1)
            continue
            
        vehicle_type = random.randint(0,4)
        if vehicle_type == 4:
            lane_number = 0
        else:
            lane_number = random.randint(0,1) + 1
            
        will_turn = 0
        if lane_number == 2:
            temp = random.randint(0,4)
            will_turn = 1 if temp <= 2 else 0
            
        temp = random.randint(0,999)
        direction_number = 0
        a = [400,800,900,1000]
        if temp < a[0]:
            direction_number = 0
        elif temp < a[1]:
            direction_number = 1
        elif temp < a[2]:
            direction_number = 2
        elif temp < a[3]:
            direction_number = 3
            
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
        time.sleep(0.75)

def simulationTime():
    global timeElapsed, simTime
    while True:
        if not paused:
            timeElapsed += 1
            if timeElapsed == simTime:
                totalVehicles = 0
                print('Lane-wise Vehicle Counts')
                for i in range(noOfSignals):
                    print('Lane',i+1,':',vehicles[directionNumbers[i]]['crossed'])
                    totalVehicles += vehicles[directionNumbers[i]]['crossed']
                print('Total vehicles passed: ',totalVehicles)
                print('Total time passed: ',timeElapsed)
                print('No. of vehicles passed per unit time: ',(float(totalVehicles)/float(timeElapsed)))
                os._exit(1)
        time.sleep(1)

class Main:
    def __init__(self):
        self.initialize_threads()
        self.setup_pygame()
        self.main_loop()

    def initialize_threads(self):
        self.thread4 = threading.Thread(name="simulationTime", target=simulationTime)
        self.thread4.daemon = True
        self.thread4.start()
        self.thread2 = threading.Thread(name="initialization", target=initialize)
        self.thread2.daemon = True
        self.thread2.start()
        self.thread3 = threading.Thread(name="generateVehicles", target=generateVehicles)
        self.thread3.daemon = True
        self.thread3.start()

    def setup_pygame(self):
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.screenWidth = 1400
        self.screenHeight = 800
        self.screenSize = (self.screenWidth, self.screenHeight)
        self.background = pygame.image.load('images/mod_int.png')
        self.screen = pygame.display.set_mode(self.screenSize)
        pygame.display.set_caption("SIMULATION")
        self.redSignal = pygame.image.load('images/signals/red.png')
        self.yellowSignal = pygame.image.load('images/signals/yellow.png')
        self.greenSignal = pygame.image.load('images/signals/green.png')
        self.font = pygame.font.Font(None, 30)
        self.large_font = pygame.font.Font(None, 50)
        pause_btn_color = (150, 200, 150)  # Green-ish
        pause_btn_hover = (120, 170, 120)  # Darker green
        play_btn_color = (200, 150, 150)   # Red-ish
        play_btn_hover = (170, 120, 120)   # Darker red
        
        self.pause_button = Button(1200, 100, 150, 50, "PAUSE", pause_btn_color, pause_btn_hover)
        self.play_button = Button(1200, 100, 150, 50, "PLAY", play_btn_color, play_btn_hover)

    def main_loop(self):
        global paused
        
        while True:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = not paused
                        print("Simulation paused:", paused)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if paused and self.play_button.is_hovered(mouse_pos):
                        paused = False
                        print("Simulation resumed")
                    elif not paused and self.pause_button.is_hovered(mouse_pos):
                        paused = True
                        print("Simulation paused")

            self.screen.blit(self.background, (0,0))
            if paused:
                self.play_button.update(mouse_pos)
                self.play_button.draw(self.screen)
            else:
                self.pause_button.update(mouse_pos)
                self.pause_button.draw(self.screen)
            
            for i in range(0, noOfSignals):
                if i == currentGreen:
                    if currentYellow == 1:
                        if signals[i].yellow == 0:
                            signals[i].signalText = "STOP"
                        else:
                            signals[i].signalText = signals[i].yellow
                        self.screen.blit(self.yellowSignal, signalCoods[i])
                    else:
                        if signals[i].green == 0:
                            signals[i].signalText = "SLOW"
                        else:
                            signals[i].signalText = signals[i].green
                        self.screen.blit(self.greenSignal, signalCoods[i])
                else:
                    if signals[i].red <= 10:
                        if signals[i].red == 0:
                            signals[i].signalText = "GO"
                        else:
                            signals[i].signalText = signals[i].red
                    else:
                        signals[i].signalText = "---"
                    self.screen.blit(self.redSignal, signalCoods[i])

            if paused:
                pause_text = self.large_font.render("SIMULATION PAUSED", True, (255, 0, 0), self.white)
                text_rect = pause_text.get_rect(center=(self.screenWidth/2, 50))
                self.screen.blit(pause_text, text_rect)
            
            signalTexts = ["", "", "", ""]
            for i in range(0, noOfSignals):  
                signalTexts[i] = self.font.render(str(signals[i].signalText), True, self.white, self.black)
                self.screen.blit(signalTexts[i], signalTimerCoods[i]) 
                displayText = vehicles[directionNumbers[i]]['crossed']
                vehicleCountTexts[i] = self.font.render(str(displayText), True, self.black, self.white)
                self.screen.blit(vehicleCountTexts[i], vehicleCountCoods[i])

            timeElapsedText = self.font.render(("Time Elapsed: "+str(timeElapsed)), True, self.black, self.white)
            self.screen.blit(timeElapsedText, (1100, 50))

            for vehicle in simulation:  
                self.screen.blit(vehicle.currentImage, [vehicle.x, vehicle.y])
                if not paused:
                    vehicle.move()

            pygame.display.update()

if __name__ == "__main__":
    Main()
