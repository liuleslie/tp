# Leslie Liu / leslieli / Q

from cmu_graphics import *
import random, math, copy, pprint

DIAG_ON = False # diagnostics; testing/debugging 
FPS = 12 # frames (steps per second)

'''
GOAL:   working app
TO DO:  friction
        /
'''

# HORI: 横、横钩
# VERT: 竖、竖勾、竖撇、竖弯钩
# DIAG: 撇、捺
# MISC: 点

CANON = { 'HORI': [ [(0,0), (4,0)], [(0,0), (4,0), (3,1)] ], 
          'VERT': [ [(0,0), (0,4)], [(0,0), (0,4), (-1,3)], [(0,0), (0,2), (-1,4)], [(0,0), (0,3), (1,4), (4,4), (4,3)] ],
          'DIAG': [ [(0,0), (-1,1), (-3,4), (-4,4)], [(0,0), (1,0), (3,3), (4,4)] ] }

#################################################
#                    TYPES   
#################################################

class Structure:    
    def __init__(self,app):
        self.cx = app.width/2   # should be drawn centered on canvas
        self.cy = app.height/2
        self.strokes = []
        self.translated = []
    
    def __repr__(self):
        return (f'len of strokes {len(self.strokes)}, self.strokes: {self.strokes}')

    def addStroke(self,app):     
        if len(self.strokes) == 0: # first stroke
            sCat = 'HORI' # if random.random() < 0.5 else 'VERT'
            self.strokes.append(Stroke(app,app.width/2,app.height/2,sCat,CANON[sCat][0]))
        else: 
            # randomly choose a previous stroke to intersect with
            prevStroke = self.strokes[-1] if len(self.strokes) <= 2 else random.choice(self.strokes)
            # get random intersection coordinates and index for both drawn (previous) and to-be drawn (future) strokes
            prevStrokeIxSegStartInd, prevStrokeIxRandX, prevStrokeIxRandY = self.getRandomIxInfo(prevStroke.path)
            newCat, newPath = self.getNewStroke(prevStroke.cat) 
            newStrokeIxSegStartInd, newStrokeIxRandX, newStrokeIxRandY = self.getRandomIxInfo(newPath)
            # instantiate new stroke
            self.strokes.append(Stroke(app,newStrokeIxRandX,newStrokeIxRandY,newCat,newPath))
            newStroke = self.strokes[-1]
            # update intersection info for both previous and new strokes
    # THIS MAY BE PROBLEMATIC! but i am not adding the current intersection to oldStroke that newStroke is 
    # intersecting with... 
            # prevStroke.ix.append(Intersection(newStroke,prevStrokeIxRandX,prevStrokeIxRandY)) # is segInd needed?
            newStroke.ix.append(Intersection(newStrokeIxRandX,newStrokeIxRandY,prevStroke,prevStrokeIxRandX,prevStrokeIxRandY)) # is segInd needed?

    # TEMPORARILY, for gravity:
            # if newCat == 'HORI':
            #     self.platforms.append()

    def getRandomIxInfo(self,path):         # bug below previously
        strokeIxSegIndStart = random.randrange(0,len(path)-2) if len(path) > 2 else 0 # chose a random index of a segment in the path
        # get random x, y of previous stroke; choose a random int in the range between x and y
        strokeSegStart = path[strokeIxSegIndStart] # tuple representing abstract coords
        strokeSegEnd = path[strokeIxSegIndStart+1] # ^
        dx = strokeSegEnd[0] - strokeSegStart[0]
        dy = strokeSegEnd[1] - strokeSegStart[1]
        if dx > 0: # check for valid slope
            strokeSegRandX = random.randint(strokeSegStart[0],strokeSegEnd[0])
            strokeSegSlope = dy / dx
            strokeSegRandY = int(strokeSegSlope * strokeSegRandX)
        else: # infinite dy; vertical line
            strokeSegRandX = strokeSegStart[0] # need to figure out if this is reasonable
            strokeSegRandY = random.randint(strokeSegStart[1],strokeSegEnd[1])
        return strokeIxSegIndStart,strokeSegRandX,strokeSegRandY

    def getNewStroke(self,excludingCat):
        usable = dict()
        for key in CANON:
            if key != excludingCat: # new stroke cannot be same as stroke to intersect with
                usable[key] = CANON[key]
        randCat = random.choice(list(usable.keys()))
        randPath = random.choice(CANON[randCat])
        return randCat, randPath
    
    def getNewOrigCoords(self,cat,path):
        randSegStartingInd = random.randrange(0,len(path)-1) # choose random segment in path for stroke-stroke intersection
        dx = (path[randSegStartingInd+1][0]-path[randSegStartingInd][0])
        dy = path[randSegStartingInd+1][1]-path[randSegStartingInd][1]

        if dx > 0: # valid slope
            randSegX = random.randint(path[randSegStartingInd][0],path[randSegStartingInd+1][0])
            randSegSlope = dy/dx
            randSegY = int(randSegSlope * randSegX)
        else:
            randSegX = 0
            randSegY = random.randint(path[randSegStartingInd][1],path[randSegStartingInd+1][1])
        return randSegX,randSegY, randSegStartingInd
    
    def getCoordsInSitu(self,app):
        translated = []

        # translated = {'VERT':[],'HORI':[],'INCR':[],'DECR':[]}
        for i in range(len(self.strokes)):
            currStroke = self.strokes[i]
            # currStroke.draw(app)
            translated += currStroke.translate(app)
        self.translated = translated

    def draw(self,app):
        # for key in self.translated.keys():
        #     for coordPair in self.translated[key]:
        #         drawLine(coordPair,fill='black')
        for x1, y1, x2, y2 in self.translated:
            drawLine(x1,y1,x2,y2,fill='black',lineWidth=app.strucStrokeWidth)
        
        

# individual marks that make up Structure
class Stroke:  

    def __init__(self,app,ox,oy,cat,path):
        self.ox = ox # originating x and y; ox, oy intersects with Structure class ix list
        self.oy = oy
        self.cat = cat
        self.path = path
        self.ix = []
        self.scalar = int(app.gridStep) # scalar to scale up to fit grid
        # self.col = random.choice("red blue green magenta black".split())
        self.col = 'black'

    def __repr__(self):
        return f'cat {self.cat}\tpath: {self.path}\n'
    
    def __eq__(self,other):
        if not isinstance(other,Stroke): return False
        return (self.cat == other.cat) and (self.path == other.path) and (self.ix == other.ix) and (self.col == other.col)
    
    # def draw(self,app,ixWithPrev=None):
    def translate(self,app,ixWithPrev=None):
        translated = []
        # translated = {'VERT':[],'HORI':[],'INCR':[],'DECR':[]}
        
        ixText = ''
        if self.ix != []:
            # find distance (dx) from self.ix to intersection stroke.ix, same for dy, mark as constant offset
            for i in range(len(self.ix)): # iterate over intersections. 
    # i think there'll only be one intersection, since it is randomly generated only once.
    # ^ the above only applies if i DO NOT implement two-way intersection creation.
                intersection = self.ix[i]
                ixText = f"intersection at other's {intersection.otherX},{intersection.otherY}, self's {self.ox},{self.oy}"
                # otherStroke = intersection.ixingStroke.ix[i] # guaranteed? because you add intersections, on both ends/strokes
                otherStroke = intersection.ixingStroke
                # dx = otherStroke.ox - self.ox
                # dy = otherStroke.oy - self.oy
                dx = intersection.otherX - self.ox
                dy = intersection.otherY - self.oy

        else: # no intersections, no need to offset
            dx,dy = 0,0
        
        # iterate over segments in path, add dx and dy
        prevPointEndX,prevPointEndY = 0,0
        tempGridOffset = app.width/3

        ptStartX, ptStartY = self.path[0] 
        ptStartX = ptStartX + (dx * self.scalar) # + prevPointEndX
        ptStartY = ptStartY + (dy * self.scalar) # + prevPointEndY
        for i in range(len(self.path)-1):
            ptEndX, ptEndY = self.path[i+1]
            
            ptEndX = (ptEndX + dx) * self.scalar # + (dx * self.scalar) 
            ptEndY = (ptEndY + dy) * self.scalar # + (dy * self.scalar)
            # drawLine(ptStartX + tempGridOffset,ptStartY + tempGridOffset,ptEndX + tempGridOffset,ptEndY+ tempGridOffset,fill=self.col,lineWidth=Stroke.w)
            
    # THIS IS LIKELY TEMPORARY
            # calculate slope
            
            translated.append((ptStartX+tempGridOffset, ptStartY+tempGridOffset, ptEndX+tempGridOffset, ptEndY+tempGridOffset))
            
            ptStartX = ptEndX 
            ptStartY = ptEndY 
        
        if DIAG_ON:
            drawRect(app.width/2,app.height*0.8,app.width*0.8,30,align='center',fill='white',opacity=80)
            drawLabel(f'{self.cat} {self.path} {ixText}',app.width/2,app.height*0.8)
        
        return translated
        


class Intersection:
    # def __init__(self,ixingStroke,selfIxX,selfIxY):
    def __init__(self,selfIxX,selfIxY,other,otherX,otherY):
        if isinstance(other,Stroke):
            self.ixingStroke = other
            self.ix = selfIxX
            self.iy = selfIxY
            self.otherX = otherX
            self.otherY = otherY

class Player:
    def __init__(self,cx,cy):
        # basics: location, size, color
        self.cx = cx
        self.cy = cy
        self.size = 20
        self.col = 'red'

        # gravity and motion
        self.jumping = False
        self.falling = True
        self.fallCount = 0
        # self.supported = False

        self.speed = self
        self.xSpeed = self.size
        self.xDir = 0
        
        self.grav = 0.5
        self.jumpHeight = self.size
        self.vy = self.jumpHeight


    
    def draw(self):
        drawRect(self.cx-self.size/2,self.cy-self.size/2,self.size,self.size,fill=self.col)
    
    def update(self,app):
        # collision(app,'HORI')
        # collision(app,'VERT')

        # if not (self.cy <= self.size or self.cy >= app.height-self.size/2):
        #     self.vy += self.grav
        # else:
        #     self.vy = 0
        #     self.falling = False
        
        # below 3 lines from easy mario jump tutorial: https://www.youtube.com/watch?v=ST-Qq3WBZBE
        # sorta understand it but not using bc its messing up my program
        # if self.jumping: # need to jump to certain height only; would this be smoother if cy changed based on hold, like left/right?
        #     self.cy -= self.jumpHeight
        #     self.falling = True
        
        self.vy += self.grav

        if self.falling: 
            self.cy += self.vy 
        else:
            self.vy = 0
        self.cx += self.xSpeed * self.xDir # xSpeed * xDir = x velocity
        if DIAG_ON: print(f'vy is {self.vy}')

        if self.cx <= self.size: self.cx = self.size
        elif self.cx > app.width-self.size/2: self.cx = app.width-self.size
        if self.cy <= self.size: self.cy = self.size
        elif self.cy > app.height-self.size/2: self.cy = app.height-self.size/2
        
        


#################################################
#              GAME SETUP / CONTROLS
#################################################
def onAppStart(app):
    reset(app)

def reset(app):
    print('\n')

    # canvas defaults
    app.width = 600
    app.height = 600
    app.gridCount = 15
    app.gridStep = int(app.width/app.gridCount)

    # app controls
    app.paused = False
    app.stepsPerSecond = FPS
    app.counter = 0
    app.gameOver = False    # if game over, init
    
    # initialize land, add founding stroke
    app.S = Structure(app)
    app.S.addStroke(app)
    app.strucStrokeWidth = 3

    # initializer player
    app.P = Player(app.width/2,50)

def onKeyPress(app,key):
    # game controls
    if key == 'space':
        app.paused = not app.paused
    elif key == 'r':
        reset(app)
    
    # player movement
    if key == 'up' and not app.P.falling: app.P.jumping = True
    if key == 'left': app.P.xDir = -1 # app.P.vx = -1 
    if key == 'right': app.P.xDir = 1 # app.P.vx = 1 

def onKeyRelease(app,key):
    # player movement
    if key == 'up': 
        app.P.jumping = False
        app.P.falling = True
    if key == 'left': app.P.xDir = 0 # vx = 0
    if key == 'right': app.P.xDir = 0 # vx = 0
    

#################################################
#                    DRAWING                  
#################################################

def onStep(app):
    if not app.paused:
        takeStep(app)
        if app.counter % (12 * 3) == 0: # automatic stroke addition every however many seconds
            app.S.addStroke(app)
        # collision checks
        # go through Structure.translated, check if colliding with Player
        checkCollisions(app)
        # update player location
        app.P.update(app)

# split axis: check horizontal coll
# then check vert coll
# overlap check
# update position

def collision(self,app,axis):
    pass

def checkCollisions(app):
    playerLeft = app.P.cx - app.P.size/2
    playerRight = playerLeft + app.P.size
    playerTop = app.P.cy - app.P.size/2
    playerBottom = playerTop + app.P.size
    collisionMargin = 3
    vertCollisionMargin = 30
    # print(app.S.translated)

    # slopes = {'VERT':[],'HORI':[],'INCR':[],'DECR':[]}

    for x1,y1,x2,y2 in app.S.translated:
        # these are all rogue line segments
        
        dy = y2-y1
        dx = x2-x1

        slopeCat = ''
        if dx == 0: 
            slopeCat = 'VERT'
            if (y1 < playerTop and playerBottom <= y2):
                if playerLeft - x1 <= collisionMargin and app.P.xDir == -1:
                    app.P.xDir = 0
                elif x1 - playerRight <= collisionMargin and app.P.xDir == 1:
                    app.P.xDir = 0

        elif dy == 0: 
            slopeCat = 'HORI'
            if (x1 < playerLeft and playerRight <= x2) and (y1 - playerBottom <= collisionMargin):
                app.P.falling = False
                app.P.vy = 0
                # app.P.cy = y1-(app.strucStrokeWidth/2)-app.P.size/2
                print(f'should not be falling, vy {app.P.vy}')
            else:
                app.P.falling = True
        elif dy/dx > 0: 
            slopeCat = 'INCR'
        else: 
            slopeCat = 'DECR'



        # could move collision detection here directly?

        # slopes[slopeCat].append([(x1,y1,x2,y2)])
    
    # for slopeCat in slopes:
    #     slopes[slopeCat] = sorted(slopes[slopeCat])

    # # find nearest 
    # for horiPlatforms in slopes['HORI']:
    #     for horiPlatform in horiPlatforms:
    #         x1,y1,x2,y2 = horiPlatform
    #         platformTop = y1-app.strucStrokeWidth/2
    #         platformBottom = platformTop+app.strucStrokeWidth

    #         if abs(platformTop-playerBottom) < collisionMargin:
    #             if x1 <= playerLeft and playerRight <= x2:
    #                 app.P.falling=False
    #                 app.P.cy = platformTop-app.strucStrokeWidth
    #         # print(f'hori platform as list: {horiPlatform}')


    # if not app.paused: pprint.pp(slopes)
    
    
        

def takeStep(app):
    app.counter += 1

def redrawAll(app): 
    drawGrid(app)       # for testing, draw grid
    app.S.getCoordsInSitu(app)     
    app.S.draw(app)     # draw structure (which draws its strokes) — not specific to Stroke object rn though
    app.P.draw()        # draw player

    # print(f'player x,y {app.P.cx},{app.P.cy} player velocity {app.P.vy}')
    drawNoteForTA(app)

def drawGrid(app):
    drawRect(0,0,app.width,app.height,fill='gray',opacity=30)
    for x in range(0,app.width,app.gridStep):
        for y in range(0,app.height,app.gridStep):
            drawRect(x,y,app.gridStep,app.gridStep,fill=None,border='gray',borderWidth=0.5,opacity=70)

def drawCanonStrokes(app):
    drawGrid(app)


def drawNoteForTA(app):
    pastTest = f'automatic stroke generation (1 new every second)'
    currTest = f'gravity on player + player interactions with structure'
    drawLabel(f'currently testing: {currTest}',app.width/2,app.height*0.95,size=18,bold=True)
def main():
    runApp()

main()
