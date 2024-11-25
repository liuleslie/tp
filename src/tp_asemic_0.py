# very rough start — can dismiss

# more meaningfully serious draft 1, november 9

from cmu_graphics import *
import random, math, copy

# cats, i.e. categories
VERT = 'VERT'
HORI = 'HORI'
DIAG = 'DIAG'

# dx, dy where (0,0) is relative origin, drawing from global origin (0,0) left top to bottom right.
A = [ (0,0), (4,0) ]                    # 横
B = [ (0,0), (4,0), (-1,-1) ]           # 横钩
C = [ (0,0), (0,4) ]                    # 竖
D = [ (0,0), (0,4), (-1,-1) ]           # 竖勾
E = [ (0,0), (0,2), (-1,2) ]            # 竖撇      [ (0,0), (0,3), (-1,-1) ] — a less angular ver.
F = [ (0,0), (-1,-1), (-2,3), (-1,0) ]  # 撇
G = [ (0,0), (1,0), (2,3), (1,1) ]      # 捺
I = [ (0,0), (1,1) ]                    # 点

ALL_STROKES = {
    'HORI': [copy.copy(A),copy.copy(B)],
    'VERT': [copy.copy(C),copy.copy(D),copy.copy(E)],
    'DIAG': [copy.copy(E)],
    'INIT': [copy.copy(A),copy.copy(C)]
}

# lol is this problematic? using existing static global variable names?


#################################################
#                    TYPES                  
#################################################

# central structure, land mass, terrain — the word, collection of strokes.
class Structure:
    def __init__(self,app): 
        self.ix = app.width/2 # ix
        self.iy = app.height/2 # iy
        self.strokes = []
        # should self.strokes include additional data.... what data type should it be?
    
# TO DO: intiialize each Stroke object using static global var info above.
#        then: draw it... 




        if random.random()<0.5: # vert
            self.strokes += [A]
        else: # hori
            self.strokes += [C]

        print(f'strokes: {self.strokes}') 

    
    def addStroke(self,s):
        if isinstance(s,Stroke):
            self.strokes += [s]
    
    def draw(self,app):
        for stroke in self.strokes:
            print(type(stroke))
            stroke.draw(app)
        # iterate over strokes, draw them one by one

### Q: can i group strokes somehow? define this in polar, navigate to point, draw relative to point ,then apply transformations?
###    Or i suppose the natural rotation will be handled by rotateAngle param?

# a single stroke, procedurally made/determined.
class Stroke:
    def __init__(self,ix,iy,cat):
        self.ix = ix
        self.iy = iy
        self.cat = cat
    
    def draw(self,app):
        drawRect(0,0,app.width,app.height,fill='blue')
        drawLabel('testing',app.width/2,app.height/2,size=30)
 

#################################################
#                    GAME SETUP                  
#################################################

def onAppStart(app):
    # app controls
    app.paused = False
    app.stepsPerSecond = 12
    app.counter = 0
    app.gameOver = False    # if game over, init

    # game design constants
    app.canonStrokes = []

    # initialize land
    cat = HORI if random.random() < 0.5 else VERT
    s = Stroke(app.width/2,app.height/2,cat)
    app.S = Structure(app)
    app.S.addStroke(s)




#################################################
#                    DRAWING                  
#################################################

def onStep(app):
    if not app.paused:
        takeStep(app)

def takeStep(app):
    app.counter += 1

def redrawAll(app):
    app.S.draw(app)

def main(app):
    runApp()

main(app)



#################################################
#                    QUESTIONS                  
#################################################

# 