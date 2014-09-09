import util

mov = util.MovableNewtonObject()
mov.vel.x = 10
mov.vel.y = 20
mov.accel.x = 5
mov.friction = 0.2
for i in range(20):
    mov.turn(1)
    print(mov)