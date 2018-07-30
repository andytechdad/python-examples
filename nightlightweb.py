from flask import Flask
from blinkt import set_pixel, set_brightness, show, clear
import colorsys
import time

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/rainbow")
def rainbow():
    spacing = 360.0 / 16.0
    hue = 0

    set_brightness(0.1)

    while True:
        hue = int(time.time() * 100) % 360
        for x in range(8):
            offset = x * spacing
            h = ((hue + offset) % 360) / 360.0
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
            set_pixel(x, r, g, b)
        show()
        time.sleep(0.001)
    return "Rainbow mode on"

@app.route("/off")
def off():
    clear()
    show()
    return "Turning light off"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
