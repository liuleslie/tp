# Leslie Liu / leslieli / Q

from cmu_graphics import *
import random, math, copy, pprint

DIAG_ON = False # diagnostics; testing/debugging 
FPS = 24 # frames (steps per second)

'''
GOAL:           working app:
                    --> sliding down slopes
                    --> check if boxed in: win/loss condition

GOOD TO HAVE:   friction
                player doublejump bug
                /
'''

# HORI: 横、横钩        VERT: 竖、竖勾、竖撇、竖弯钩        DIAG: 撇、捺

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
        self.translated = {'READY':[],'NOT READY':[]} # []
    
    def __repr__(self):
        return (f'len of strokes {len(self.strokes)}, self.strokes: {self.strokes}')

    def addStroke(self,app):     
        if len(self.strokes) == 0: # first stroke
            sCat = 'HORI' # if random.random() < 0.5 else 'VERT'
            self.strokes.append(Stroke(app,app.width/2,app.height/2,sCat,CANON[sCat][0],app.counter))
        else: 
            # randomly choose a previous stroke to intersect with
            prevStroke = self.strokes[-1] if len(self.strokes) <= 2 else random.choice(self.strokes)
            # get random intersection coordinates and index for both drawn (previous) and to-be drawn (future) strokes
            prevStrokeIxSegStartInd, prevStrokeIxRandX, prevStrokeIxRandY = self.getRandomIxInfo(prevStroke.path)
            newCat, newPath = self.getNewStroke(prevStroke.cat) 
            newStrokeIxSegStartInd, newStrokeIxRandX, newStrokeIxRandY = self.getRandomIxInfo(newPath)
            # instantiate new stroke
            self.strokes.append(Stroke(app,newStrokeIxRandX,newStrokeIxRandY,newCat,newPath,app.counter))
            newStroke = self.strokes[-1]
            # add current intersection info to new stroke: attach previous (drawn) stroke coord info
            newStroke.ix.append(Intersection(newStrokeIxRandX,newStrokeIxRandY,prevStroke,prevStrokeIxRandX,prevStrokeIxRandY)) # is segInd needed?

    def getRandomIxInfo(self,path):
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
        translated = {'READY':[],'NOT READY':[]}
        for i in range(len(self.strokes)):
            currStroke = self.strokes[i]
            # check if stroke is permanent or cue
            ind = 'READY' if currStroke.isReady else 'NOT READY'
            translated[ind] += currStroke.translate(app)
        self.translated = translated
    
    def checkReadyStrokes(self,app):
        print(self.strokes)
        for currStroke in self.strokes[1:]:
            if (app.counter - currStroke.initTime) >= app.strokeReadyThreshold:
                currStroke.isReady = True

    def draw(self,app):
        for strokeType in ['NOT READY','READY']:
            strokeCol = 'black' if strokeType == 'READY' else 'gray'
            for x1, y1, x2, y2 in self.translated[strokeType]:
                drawLine(x1,y1,x2,y2,lineWidth=app.strucStrokeWidth,fill=strokeCol)

# individual marks that make up Structure
class Stroke:  

    def __init__(self,app,ox,oy,cat,path,count):
        self.ox = ox # originating x and y; ox, oy intersects with Structure class ix list
        self.oy = oy
        self.cat = cat
        self.path = path
        self.ix = []
        self.scalar = int(app.gridStep) # scalar to scale up to fit grid
        self.initTime = count
        self.isReady = False
        # self.col = random.choice("red blue green magenta black".split())
        self.col = 'black'

    def __repr__(self):
        return f'cat {self.cat}\tpath: {self.path}\n'
    
    def __eq__(self,other):
        if not isinstance(other,Stroke): return False
        return (self.cat == other.cat) and (self.path == other.path) and (self.ix == other.ix) and (self.col == other.col)
    
    def translate(self,app,ixWithPrev=None):
        translated = []
        
        ixText = ''
        if self.ix != []:
            # find distance (dx) from self.ix to intersection stroke.ix, same for dy, mark as constant offset
            for i in range(len(self.ix)): # iterate over intersections. 
                intersection = self.ix[i]
                ixText = f"intersection at other's {intersection.otherX},{intersection.otherY}, self's {self.ox},{self.oy}"
                otherStroke = intersection.ixingStroke
                dx = intersection.otherX - self.ox
                dy = intersection.otherY - self.oy
        else: # no intersections, no need to offset
            dx,dy = 0,0
        # iterate over segments in path, add dx and dy
        tempGridOffset = app.width/3

        ptStartX, ptStartY = self.path[0] 
        ptStartX = ptStartX + (dx * self.scalar) # + prevPointEndX
        ptStartY = ptStartY + (dy * self.scalar) # + prevPointEndY
        for i in range(len(self.path)-1):
            ptEndX, ptEndY = self.path[i+1]
            ptEndX = (ptEndX + dx) * self.scalar # + (dx * self.scalar) 
            ptEndY = (ptEndY + dy) * self.scalar # + (dy * self.scalar)
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
        
        # movement
        self.xDirection = 0
        self.yDirection = 0 # basically y velocity
        self.speed = self.size * 20
        self.gravity = 20
        self.isJumping = False
        self.isFalling = True
        self.jumpHeight = self.size * 2
    
    def draw(self):
        # print(f'xdir {self.xDirection} ydir {self.yDirection} isjumping {self.isJumping}')
        drawRect(self.cx-self.size/2,self.cy-self.size/2,self.size,self.size,fill=self.col)

    def update(self,app):
        # check if colliding with anything left/right
        self.colliding('VERT',app)

        # check if colliding with anything below
        self.colliding('HORI',app)

        # check if on ground / canvas
        self.move(app)

    def move(self,app):
        if self.size < self.cx < app.width-self.size:
            self.cx += self.xDirection * self.speed * app.dt

        if self.isJumping:
            self.cy -= self.jumpHeight
            self.isJumping = False
            self.isFalling = True
            
        if self.isFalling:
            self.yDirection += self.gravity * app.dt
            if self.cy > app.height-self.size/2:
                self.isFalling = False
                self.yDirection = 0
                self.cy = app.height-self.size/2

        if self.isFalling: self.cy += self.yDirection

    def colliding(self,dir,app):
        moe = 3 # margin of error. this gets problematic quick.
        pLeft = app.P.cx - app.P.size/2
        pRight = pLeft + app.P.size
        pTop = app.P.cy - app.P.size/2
        pBottom = pTop + app.P.size
        slopes = getSlopes(app,dir)

        # go through slopes, check if colliding
        for x1,y1,x2,y2 in slopes: 
            if dir == 'VERT': # x axis: left/right collision
                if (((abs(pLeft-(x1+app.strucStrokeWidth/2)) <= moe and self.xDirection == -1) or 
                    (abs(pRight-(x1-app.strucStrokeWidth/2)) <= moe and self.xDirection == 1)) and 
                    (y1 <= pTop <= pBottom <= y2)):
                    self.xDirection = 0
                    print('should not be able to move left/right; since against wall')
            
            if dir == 'HORI': # y axis: horizontal platforms
                # if (abs(pBottom-(y1-app.strucStrokeWidth/2)) <= moe and self.yDirection == -1) or (abs(pBottom-(y1-app.strucStrokeWidth/2)) <= moe and self.yDirection == 1):
                if (abs(pBottom-y1) <= moe) and (x1 <= pLeft <= x2): # on top of stroke and within stroke length
                    self.yDirection = 0
                    self.cy = y2-(app.strucStrokeWidth/2)-(self.size/2) # snap to platform/stroke top 
                    self.isFalling = False # on ground
                else:
                    self.isFalling = True


def getSlopes(app,dir):
    slopes = {'VERT':[],'HORI':[],'INCR':[],'DECR':[]}
    for x1,y1,x2,y2 in app.S.translated['READY']: # iterate over all line segments, check for collisions
        dy, dx = y2-y1, x2-x1
        if dx == 0: slopeCat = 'VERT'
        elif dy == 0: slopeCat = 'HORI'
        elif dy/dx > 0: slopeCat = 'INCR'
        else: slopeCat = 'DECR'
        slopes[slopeCat].append((x1,y1,x2,y2))
    return slopes[dir]

def getVicinity(app):   
    vicinity = []
    pLeft = app.P.cx - app.P.size/2
    pRight = pLeft + app.P.size
    pTop = app.P.cy - app.P.size/2
    pBottom = pTop + app.P.size
    vic = app.P.size * 2
    rangeX = range(int(app.P.cx-app.width/3),int(app.P.cx+app.width/3))
    rangeY = range(int(app.P.cy-app.height/3),int(app.P.cy+app.height/3))   
    vicinity.append(app.S.translated[0])
    for x1,y1,x2,y2 in app.S.translated:
        if ((x1 in rangeX) or (x2 in rangeX)) and ((y1 in rangeY) or (y2 in rangeY)):
            vicinity.append((x1,y1,x2,y2))
    return vicinity


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
    app.dt = 0.01

    # app controls
    app.paused = False
    app.stepsPerSecond = FPS
    app.counter = 0
    app.strokeReadyThreshold = FPS * 2 # stroke ready after this many seconds
    app.gameOver = False    # if game over, init
    
    # initialize land, add founding stroke
    app.S = Structure(app)
    app.S.addStroke(app)
    app.S.strokes[0].isReady = True
    app.strucStrokeWidth = 3

    # initializer player
    app.P = Player(app.width/2,50)

    # collision checks
    app.relevantSegments = []

def onKeyPress(app,key):
    # game controls
    if key == 'space': app.paused = not app.paused
    elif key == 'r': reset(app)
    
    # player movement
    if key == 'up': # and not app.P.isFalling: 
        app.P.isJumping = True
        print(f'pressed up and can jump, player coords {app.P.cx},{app.P.cy}')
    if key == 'left': app.P.xDirection = -1
    if key == 'right': app.P.xDirection = 1

def onKeyRelease(app,key):
    # player movement
    # if key == 'up': app.P.isJumping = False # app.P.isFalling = True
    if key == 'left': app.P.xDirection = 0
    if key == 'right': app.P.xDirection = 0
    

#################################################
#                    DRAWING                  
#################################################

def onStep(app):
    if not app.paused:
        takeStep(app)
        if app.counter % (FPS * 3) == 0: # automatic stroke addition every however many seconds
            app.S.addStroke(app)
        # app.S.checkReadyStrokes(app)
        app.P.update(app) 

def takeStep(app):
    app.counter += 1

def redrawAll(app): 
    drawGrid(app)       # for testing, draw grid
    app.S.checkReadyStrokes(app)
    app.S.getCoordsInSitu(app)     
    app.S.draw(app)     # draw structure (which draws its strokes) — not specific to Stroke object rn though
    app.P.draw()        # draw player
    drawNoteForTA(app)
    print(f'allSlopes:')
    pprint.pp(app.S.translated)

    # collision checking
    for seg in app.relevantSegments:
        drawLine(*seg,fill='red')

def drawGrid(app):
    drawRect(0,0,app.width,app.height,fill='gray',opacity=30)
    for x in range(0,app.width,app.gridStep):
        for y in range(0,app.height,app.gridStep):
            drawRect(x,y,app.gridStep,app.gridStep,fill=None,border='gray',borderWidth=0.5,opacity=70)

def drawCanonStrokes(app):
    drawGrid(app)

def drawNoteForTA(app):
    currTest = f'gravity on player + player interactions with structure'
    drawLabel(f'currently testing: {currTest}',app.width/2,app.height*0.95,size=18,bold=True)
def main():
    runApp()

main()
