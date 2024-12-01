# Leslie Liu / leslieli / Q

from cmu_graphics import *
import random, math, copy, pprint

# goals for this sprint: complete working logic of stroke (struc) generation
# cleaning it uppppp

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
        self.strokes=[]
        # self.ix=[]
    
    def __repr__(self):
        return (f'len of strokes {len(self.strokes)}, self.strokes: {self.strokes}')

    def addStroke(self,app):     
        if len(self.strokes) == 0: # first stroke
            sCat = 'HORI' if random.random() < 0.5 else 'VERT'
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
            prevStroke.updateIx(newStroke, prevStrokeIxSegStartInd, prevStrokeIxRandX, prevStrokeIxRandY)
            newStroke.updateIx(prevStroke, newStrokeIxSegStartInd, newStrokeIxRandX, newStrokeIxRandY)
        # TO DO: do translation

    def getRandomIxInfo(self,path):         # bug below previously
        strokeIxSegIndStart = random.randrange(0,len(path)-2) if len(path) > 2 else 0 # chose a random index of a segment in the path
        print(f'segment starting index: {strokeIxSegIndStart}')
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

# !: ox and oy of each new stroke that's added is not intersecting with the previous stroke — 
#    they all default to (0,0) i think

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
        # print(f'randSegX {randSegX}')
        return randSegX,randSegY, randSegStartingInd
    
    def draw(self,app):
        for i in range(len(self.strokes)):
            currStroke = self.strokes[i]
            currStroke.draw(app)

# individual marks that make up Structure
class Stroke:  
    w = 20 # lineWidth for stroke

    def __init__(self,app,ox,oy,cat,path):
        self.ox = ox # originating x and y; ox, oy intersects with Structure class ix list
        self.oy = oy
        self.cat = cat
        self.path = path
        self.ix = []
        self.scalar = int(app.gridStep) # scalar to scale up to fit grid
        self.col = random.choice("red blue green magenta black".split())

    def __repr__(self):
        return f'cat {self.cat}\tpath: {self.path}\n'
    
    def __eq__(self,other):
        if not isinstance(other,Stroke): return False
        return (self.cat == other.cat) and (self.path == other.path) and (self.ix == other.ix) and (self.col == other.col)

    def updateIx(self,other,ixSegStartInd,ixX,ixY):
        if isinstance(other,Stroke):
            newIx = dict()
            newIx['ixWith'] = other
            newIx['ixSelfSegStartInd'] = ixSegStartInd
            newIx['ixSelfX'] = ixX
            newIx['ixSelfY'] = ixY
            self.ix.append(newIx)
            # go ahead and add
    
    def draw(self,app,ixWithPrev=None):
        # iterate over dx,dy in path, starting at relative origin
        if self.ix != []:
            # if there are intersections, go through the stroke this stroke ix's with
            # find dx and dy / dist between self's ix and self ix'ing stroke's ix coords
            for ix in self.ix: # each ix is a dict()
                if isinstance(ix['ixWith'],Stroke):
                    otherStroke = ix['ixWith']
                    # if otherStroke.ix['ixWith']

            otherStroke = self.ix['ixWith']
            selfIxOrigX = self.ix['ixSelfX']
            selfIxOrigY = self.ix['ixSelfY']
            # loop through intersections, check if 
            otherIxOrigX = app.S.strokes[otherStroke].ix['ixSelfX']
            otherIxOrigY = app.S.strokes[otherStroke].ix['ixSelfY']
            

            pass
        # else:
            # simply draw stroke

        if ixWithPrev != None:
            dx = ixWithPrev[0]-self.ox
            dy = ixWithPrev[1]-self.oy
        else: dx, dy = 0, 0
        startingX, startingY = 0, 0
        gridOffset = app.width/3
        
        for i in range(0,len(self.path)-1): # go through 0 to second to last segment
            currPtX, currPtY = self.path[i] 
            currPtX, currPtY = startingX + currPtX, startingY + currPtY
            nextPtX, nextPtY = self.path[i+1]
            # if ox oy is in this range, translate it somehow
            nextPtX, nextPtY = int(nextPtX * self.scalar), int(nextPtY * self.scalar)
            col = 'black'
            drawLine(currPtX+gridOffset,currPtY+gridOffset,nextPtX+gridOffset,nextPtY+gridOffset,lineWidth=2,fill=self.col) 
            startingX, startingY = nextPtX + dx, nextPtY + dy
        
        print(f'\nstroke ix: {self.ix}')



#################################################
#              GAME SETUP / CONTROLS
#################################################
def onAppStart(app):
    reset(app)

def reset(app):
    print('\n')

    # canvas defaults
    # app.reset = False
    app.width = 600
    app.height = 600
    app.gridCount = 15
    app.gridStep = int(app.width/app.gridCount)

    # app controls
    app.paused = False
    app.stepsPerSecond = 12
    app.counter = 0
    app.gameOver = False    # if game over, init
    
    # initialize land, add founding stroke
    app.S = Structure(app)
    app.S.addStroke(app)

def onKeyPress(app,key):
    if key == 'space':
        app.paused = not app.paused
        # app.S.addStroke(app)
    elif key == 'r':
        # app.reset = True
        reset(app)

#################################################
#                    DRAWING                  
#################################################

def onStep(app):
    if not app.paused:
        takeStep(app)
        if app.counter % 12 == 0:
            app.S.addStroke(app)

def takeStep(app):
    app.counter += 1

def redrawAll(app): 
    drawGrid(app)
    app.S.draw(app)
    drawNoteForTA(app)

def drawGrid(app):
    drawRect(0,0,app.width,app.height,fill='gray',opacity=30)
    for x in range(0,app.width,app.gridStep):
        for y in range(0,app.height,app.gridStep):
            drawRect(x,y,app.gridStep,app.gridStep,fill=None,border='gray',borderWidth=0.5,opacity=70)

def drawCanonStrokes(app):
    drawGrid(app)


def drawNoteForTA(app):
    drawLabel('currently testing: automatic stroke generation (1 new every second)',app.width/2,app.height*0.95,size=18,bold=True)
def main():
    runApp()

main()
