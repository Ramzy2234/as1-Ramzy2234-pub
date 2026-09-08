from turtle import *
import colorsys

tracer(30)
bgcolor("black")
width(1)
hideturtle()

for i in range(460):
    hue = i / 460
    rgb = colorsys.hsv_to_rgb(hue, 1, 1)
    color(rgb)

    forward(i * 0.5)

    left(90)
    circle(i * 0.1)
    right(90)

    backward(i * 0.5)
    right(91)

done()