
def collision(self,app):
    # app.S.translated
    moe = 3
    pLeft = app.P.cx - app.P.size/2
    pRight = pLeft + app.P.size
    pTop = app.P.cy - app.P.size/2
    pBottom = pTop + app.P.size
    # for now not using get vicinity

    for x1,y1,x2,y2 in app.S.translated: # iterate over all line segments, check for collisions
        dy, dx = y2-y1, x2-x1
        if dx == 0: # against vertical wall
            if (abs(pLeft-(x1+app.strucStrokeWidth/2)) <= moe and self.xDirection == -1) or (abs(pRight-(x1-app.strucStrokeWidth/2)) <= moe and self.xDirection == 1):
                self.xDirection = 0
        if dy == 0: # horizontal platforms
            # if (abs(pBottom-(y1-app.strucStrokeWidth/2)) <= moe and self.yDirection == -1) or (abs(pBottom-(y1-app.strucStrokeWidth/2)) <= moe and self.yDirection == 1):
            if abs(pBottom-y1) <= moe: # on top of stroke
                self.yDirection = 0
                self.isFalling = False
            else:
                self.isFalling = True

##################


self.cx += self.xDirection * self.speed * app.dt
if self.cx <= self.size: self.cx = self.size
elif self.cx > app.width-self.size/2: 
    self.cx = app.width-self.size
    self.xDirection = 0

if self.isJumping:
    self.cy -= self.jumpHeight
    self.isJumping = False
    self.isFalling = True
    
if self.isFalling: 
    self.yDirection += self.gravity * app.dt
else:
    self.yDirection = 0

self.cy += self.yDirection
if self.cy <= self.size: self.cy = self.size
elif self.cy > app.height-self.size/2: 
    self.cy = app.height-self.size/2