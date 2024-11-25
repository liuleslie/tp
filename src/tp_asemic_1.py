# Leslie Liu / leslieli / Q

from cmu_graphics import *
import random, math, copy, pprint

# goals for this sprint: complete working logic of stroke (struc) generation

A = [ 'HORI', (0,0), (4,0) ]                    # 横
B = [ 'HORI', (0,0), (4,0), (-1,-1) ]           # 横钩
C = [ 'VERT', (0,0), (0,4) ]                    # 竖
D = [ 'VERT', (0,0), (0,4), (-1,-1) ]           # 竖勾
E = [ 'VERT', (0,0), (0,2), (-1,2) ]            # 竖撇      [ (0,0), (0,3), (-1,-1) ] — a less angular ver.
F = [ 'DIAG', (0,0), (-1,-1), (-2,3), (-1,0) ]  # 撇
G = [ 'DIAG', (0,0), (1,0), (2,3), (1,1) ]      # 捺
H = [ 'VERT', (0,0), (0,3), (1,1), (3,0), (0,-1) ]     # 竖弯钩
I = [ (0,0), (1,1) ]                    # 点

# AS SLOPES
# CANON = { 'HORI': [ [(0,0), (4,0)], [(0,0), (4,0), (-1,-1)] ], 
#           'VERT': [ [(0,0), (0,4)], [(0,0), (0,4), (-1,-1)], [(0,0), (0,2), (-1,2)] ],
#           'DIAG': [ [(0,0), (-1,-1), (-2,3), (-1,0)], [(0,0), (1,0), (2,3), (1,1)] ] }

# AS POINTS
CANON = { 'HORI': [ [(0,0), (4,0)], [(0,0), (4,0), (3,1)] ], 
          'VERT': [ [(0,0), (0,4)], [(0,0), (0,4), (-1,3)], [(0,0), (0,2), (-1,4)], [(0,0), (0,3), (1,4), (4,4), (4,3)] ],
          'DIAG': [ [(0,0), (-1,1), (-3,4), (-4,4)], [(0,0), (1,0), (3,3), (4,4)] ] }
# HORI: A, B
# VERT: C, D, E, H
# DIAG: F, G

#################################################
#                    TYPES   
#################################################

class Structure:    
    def __init__(self,app):
        self.cx = app.width/2   # should be drawn centered on canvas
        self.cy = app.height/2
        self.strokes=[]
        self.ix=[]
    
    def __repr__(self):
        return (f'len of strokes {len(self.strokes)}, self.strokes: {self.strokes}')

    def addStroke(self,app):     
        if len(self.strokes) == 0: # first stroke
            sCat = 'HORI'
            if random.random() < 0.5: sCat = 'VERT'
            self.strokes.append(Stroke(app,app.width/2,app.height/2,sCat,CANON[sCat][0]))
        elif len(self.strokes) == 1: 
        # else:
            # choose a random point on the stroke to make an intersection
            # check stroke cat. if vert, choose a hori or diag.
            padding = Stroke.w # not using this yet, but this'll ensure that ix at the end of the stroke are perfectly joined. sth about miter angles maybe
            # this random intersection generation will likely need to be refactored/sep'ed into a func for the else statement
            
            currPath = self.strokes[0].path
            # https://docs.python.org/3/library/random.html#random.randint — [a,b] where both are floats 
            randX = random.randint(currPath[0][0],currPath[1][0]) # get random intersection coords on curr stroke
            randY = random.randint(currPath[0][1],currPath[1][1])
            randCat, randPath = self.getNewStroke(self.strokes[0].cat) # get random stroke category
            # NB: shouldnt be using randX,randY to init Strokes bc randX,randY is where it itersects with PREVIOUS Stroke
            
            randOX, randOY, randOCoordsSegInd = self.getNewOrigCoords(randCat,randPath)
            self.ix.append((randX,randY))
            self.strokes.append(Stroke(app,randOX,randOY,randCat,randPath,randOCoordsSegInd))
            # Q: is it ok to keep representations of strokes as 0,0 unit vectors (sorta)? or should i bring the scalar in?
            # the 1 way this could be problematic is if the float <> int conversion is weird for drawing v. calculating intersections
        
# NB at some point i am going to need to refactor this into the above elif... 
        else: 
            # need to select a randX, randY & randCat, randPath based on whichever stroke i am going to intersect
            # len(self.strokes)-1 is the latest
            # self.strokes[-1] is latest addition, [-2] penultimate

            # TO DO: select random stroke
            randCat, randPath = self.getNewStroke(self.strokes[-1].cat) 

            # TO DO: select random segment of existing struc to intersect with
            strokeToIx = random.choice(self.strokes[:-1])
# ?: not create a copy of Stroke obj?

            randX, randY, randIxSegInd = self.makeIntersection(app,strokeToIx)
            newOX, newOY, newOCoordsSegInd = self.getNewOrigCoords(randCat,randPath)
            print(f'new stroke to add: randCat {randCat} randPath {randPath} on original stroke: ({randX},{randY}) at new stroke: ({newOX},{newOY})')
            # ixSegStartInd = self.makeIntersection(self,app,strokeToIx)
            # ixSegEndInd = ixSegStartInd + 1 # we now have our pair of points of the segment of the ix'ing path
            
# !: ox and oy of each new stroke that's added is not intersecting with the previous stroke — 
#    they all default to (0,0) i think

            # reusing getNewOrigCoords
            
            # NB: here newOCoordsSegInd is specific to the stroke we are adding, which != strokeToIx.
            # TO DO: determine valid random intersecting point --> handled via getNewOrigCoords
        # RESUME HERE: make newn stroke again, add stuff update lists.
    # TO DO: 
            self.ix.append((randX,randY))
            self.strokes.append(Stroke(app,newOX,newOY,randCat,randPath,newOCoordsSegInd))
            
            # TO DO: append intersection coords to self.ix, create new stroke and add to strokes

            # TO DO: consider creating a new variable to store intersection relationships... more effectively

            # Stroke(app,randOX,randOY,randCat,randPath,randOCoordsSegInd)
            

    def makeIntersection(self,app,strokeToIx):
        # choose random segment in stroke to intersect
        # only use valid segment start indices
        if len(strokeToIx.path) > 2:
            randSegStartInd = random.randint(0,len(strokeToIx.path)-1)
        else:
            randSegStartInd = 0
        

# TO DO: potential refactoring; see getNewOrigCoords
        path = strokeToIx.path
        print(f'//////// strokeToIx: {strokeToIx}')
        print(f'//////// random segment starting ind: {randSegStartInd}')
        
        dx = path[randSegStartInd+1][0]-path[randSegStartInd][0]
        dy = path[randSegStartInd+1][1]-path[randSegStartInd][1]
        # if len(path) > 2:
        if dx > 0: # valid slope
            randSegX = random.randint(path[randSegStartInd][0],path[randSegStartInd+1][0])
            randSegSlope = dy/dx
            randSegY = randSegSlope * randSegX
        else:
            randSegX = 0
            randSegY = random.randint(path[randSegStartInd][1],path[randSegStartInd+1][1])
        # print(f'randSegX {randSegX}')
        return randSegX,randSegY, randSegStartInd
        
# TO DO: FINISH

    def getNewStroke(self,excludingCat):
        # make a list of all possible paths, excluding given stroke cateogry
        usable = dict()
        for key in CANON:
            if key != excludingCat:
                usable[key] = CANON[key]
        # choose random key
        # pprint.pp(usable)
        randCat = random.choice(list(usable.keys()))
        randPath = random.choice(CANON[randCat])

        return randCat, randPath
    
    def getNewOrigCoords(self,cat,path): # ? --> based on category, choose a random point to set as ox, oy
        # print(f'path to get new coords: {path}')
        randSegStartingInd = random.randrange(0,len(path)-1) # choose random segment in path for stroke-stroke intersection
        # print(f'randSegStartingInd {randSegStartingInd}')
# this could be reused in makeIntersection too
        dx = (path[randSegStartingInd+1][0]-path[randSegStartingInd][0])
        dy = path[randSegStartingInd+1][1]-path[randSegStartingInd][1]

        if dx > 0: # valid slope
            randSegX = random.randint(path[randSegStartingInd][0],path[randSegStartingInd+1][0])
            randSegSlope = dy/dx
            randSegY = randSegSlope * randSegX
        else:
            randSegX = 0
            randSegY = random.randint(path[randSegStartingInd][1],path[randSegStartingInd+1][1])
        # print(f'randSegX {randSegX}')
        return randSegX,randSegY, randSegStartingInd
    
    
    def draw(self,app):
        # print(f'INTERSECTIONS: {self.ix} \n')
        # something
        # for stroke in self.strokes:
        for i in range(len(self.strokes)):
        #     print(app.S)
        #     prevStroke, currStroke = None, self.strokes[i]
        #     self.strokes[i].draw(app,self.ix[i])
            currStroke = self.strokes[i]
            if len(self.ix) > 0:
                currStroke.draw(app,self.ix[i-1])
            else: currStroke.draw(app)

# individual marks that make up Structure
class Stroke:  
    w = 20 # lineWidth for stroke

    def __init__(self,app,ox,oy,cat,path,ix=[],oInd=None):
        self.ox = ox # originating x and y; ox, oy intersects with Structure class ix list
        self.oy = oy
        self.cat = cat
        self.path = path
        self.oInd = oInd # which line segment the intersection is on
        # self.ix = ix # intersection list; info with other strokes  --> using this in Structure class instead
        self.scalar = app.gridStep # scalar to scale up to fit grid
        self.intersections = [] 

    def __repr__(self):
        return f'\tcat {self.cat}\tpath: {self.path}\n'
    
    def draw(self,app,ixWithPrev=None):
        # iterate over dx,dy in path, starting at relative origin


        if ixWithPrev != None:
            # print(f'ixWithPrev {ixWithPrev}')
            # print(f'self ox {self.ox} self.oy {self.oy}')
            dx = ixWithPrev[0]-self.ox
            dy = ixWithPrev[1]-self.oy
            # print(f'dx {dx} dy {dy}')
        else: dx, dy = 0, 0

        # if prev is none: drawing only one stroke
        # else: prev is Stroke and need to draw based on ix offset
        startingX, startingY = 0, 0
        gridOffset = app.width/3
        for i in range(0,len(self.path)-1): # go through 0 to second to last segment
            # line from each segment

            currPtX, currPtY = self.path[i]
            currPtX, currPtY = startingX + currPtX, startingY + currPtY
            nextPtX, nextPtY = self.path[i+1]
            nextPtX, nextPtY = nextPtX * self.scalar, nextPtY * self.scalar
            col = 'black'
            # drawLine(currPtX+gridOffset,currPtY+gridOffset,nextPtX+gridOffset,nextPtY+gridOffset,lineWidth=Stroke.w,fill=col) 
            drawLine(currPtX+gridOffset,currPtY+gridOffset,nextPtX+gridOffset,nextPtY+gridOffset,lineWidth=2,fill='black') 
            
            # drawLabel(i,currPtX+gridOffset,currPtY+gridOffset,fill='red',size=30)

            startingX, startingY = nextPtX + dx, nextPtY + dy



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
        app.S.addStroke(app)
    elif key == 'r':
        # app.reset = True
        reset(app)

#################################################
#                    DRAWING                  
#################################################

def onStep(app):
    if not app.paused:
        takeStep(app)

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
    drawLabel('diagnostics: press space to add strokes, r to reset',app.width/2,app.height*0.95,size=20,bold=True)
def main():
    runApp()

main()
