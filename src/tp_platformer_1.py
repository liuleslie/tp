# more meaningfully serious draft 1, november 9

from cmu_graphics import *
import random, math

# define classes
# onappstart: initialize objects
# onstep: apply gravity; can break up into x and y. 
#   here you can let dTime be something like 0.01
#   collision detection
#       "closest point on rect to player's center"
#       "then calculate from balls center to this closest point"
#       "if dist either way is < player size, apply velocity accordingly"
#   checking for bounds of canvas: separate if statements from trbl
#       constrain player to very edge of the canvas if at/beyond edge
#       consider friction
# have a reset function

class Land:
    def __init__(self):
        self.cx=app.width/2
        self.cy=app.height/2
        self.w=app.width*0.75
        self.h=(random.random()*self.w*0.5) + (app.width*0.25)

class Pers:
    def __init__(self):
        self.cx=10
        self.cy=10
        self.sz=20

'''
euler? integration
verlet integration: more precise — uses prev x post
g, planet density ,velocity norm, fps, dt
--> use numpy to access vectors, since ordinary numbers can be problematic
rope/cloth physics?? https://www.cs.cmu.edu/afs/cs/academic/class/15462-s13/www/lec_slides/Jakobsen.pdf ?

ask Vishant about advanced physics math
other TA: Gabriel

'''