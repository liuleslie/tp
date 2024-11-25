# premise of the game: player avoids getting boxed in.
# physics works as in 2d.

from cmu_graphics import *
import random, math

'''
class Gravity, Platform
falling(yPosition,velocity,gravity,dTime)
'''


###############################################
###############################################
###############################################
###############################################
###############################################
###############################################

PLAYER, OPP = 'player', 'opp'

#################### SETUP ####################

def onAppStart(app):
    init(app)
    app.paused=False
    app.stepsPerSecond=12 
    app.stepCounter=0
    # if game over, init

def onStep(app):
    if not app.paused:
        takeStep(app)

def takeStep(app):
    # structure
    app.stepCounter+=1
    struc = app.scene['struc']
    struc.angle += struc.dAngle

    # check character states wrt structure. ensure physics.
    physics(app)

#################### INITIALIZING ####################

def initStructure(app):
    struc = SimpleNamespace()
    struc.w = app.width*0.75
    struc.h = (random.random()*struc.w*0.5) + (app.width*0.25)

# NEEDED: a func to check/generate valid dimensions so that vertices do not exceed bounds of canvas

    struc.x = app.width/2-struc.w/2
    struc.y = app.height/2-struc.h/2
    struc.color = 'black'
    struc.angle = 0
    struc.dAngle = 1
    return struc

def initChar(app,type):
    if type == PLAYER:
        player = SimpleNamespace()
        player.size = 20
# NEEDED: check bounds when init'ing so that it doesn't collide with struc
# alternatively: ensure both struc and player initializes in a fixed, 'safe' position, 
# then have a rotate func to move everything and check bounds
        player.x = random.random()*(app.width-player.size)+player.size
        player.y = random.random()*(app.height-player.size)+player.size
        player.color = 'white'
        player.v = 2
        # no acceleration for now
        return player
    
# NEEDED: define physics of this game. is it waterlike/moonlike/earth's gravity?

    elif type == OPP:
        pass
    pass

def init(app):
    app.scene, app.chars = {}, {}
# NEEDED: to confirm if this is sensible before I add substantial complexity

    # init structure
    app.scene['struc'] = initStructure(app)

    # init player
    app.chars['player'] = initChar(app,PLAYER)

    # init opps: LATER
    pass

#################### UPDATING ####################
def physics(app):
    player, struc = app.chars['player'], app.scene['struc']

# TESTING: physics
    respectPhysics(player,struc,app)

    # check collisions
    if (checkCollisions(player,struc) == PLAYER):
        respectPhysics(player,struc,app)
    # update player position if need be

def checkCollisions(player,struc):
    # how can I use / check documentation for CS3 Shape (Circle, hits(), contains()) objects?
# NEEDED: to find a good algo for now
    
    # if struc.hits(player):
    #     print('struc hits player!')
    pass

def respectPhysics(player,struc,app): # mutating func: updates player position to be pushed by struc
    margin = 1 # 10 px margin for now
    grav = 0.02
    dx=app.width/2-player.x
    dy=app.height/2-player.y
    if math.dist((player.x,player.y),(app.width/2,app.height/2)) <= margin:
        player.x,player.y=app.width/2,app.height/2
    else: # is there a theta involved??
        player.x += player.v * dx * grav
        player.y += player.v * dy * grav
    pass

#################### CONTROLLERS (input) ####################

# NEEDED: confirm what keys will be input. feeling mostly wasd or arrows.
def onKeyPress(app,key):
    if key=='space':
        app.paused = not app.paused

#################### DRAWING ####################

def redrawAll(app):
    drawBackground(app) # initializing these should be in onStep()?
    drawDiag(app)
    drawChars(app)
    pass

def drawBackground(app):
    drawRect(0,0,app.width,app.height,fill='olivedrab')
    drawStructure(app)
    # text
# what to do about unresponsive canvas (can only resize on reload/rerun)

def drawDiag(app): #purely for debugging reasons
    state = f'app is '
    state += 'paused' if app.paused else 'running'
    drawLabel(state,10,10,align='top-left')

def drawStructure(app):
    # parameterize and properly initialize later
    struc = app.scene['struc']
    drawRect(struc.x,struc.y,struc.w,struc.h,fill=struc.color,rotateAngle=struc.angle)

def drawChars(app):
    chars = app.chars
    for char in chars:
        actor = chars[char]
        drawCircle(actor.x,actor.y,actor.size,fill=actor.color)


def main():
    runApp()


main()

