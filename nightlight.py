#!/usr/bin/python

# python nightlight.py on colour

import sys
import logging as log
import blinkt

light_state = sys.argv[1]

def get_colour(light_colour):
    rgb_colour = ();
    if light_colour == 'yellow':
        rgb_colour = (255, 255, 5,)
    elif light_colour == 'blue':
        rgb_colour = (0, 0, 255,)
    elif light_colour == 'green':
        rgb_colour = (0, 200, 0,)
    return rgb_colour

def main():
    FORMAT = '%(asctime)-15s %(message)s'
    log.basicConfig(stream=sys.stdout, level=log.DEBUG)
    log.info("Light is " + light_state)
    blinkt.set_clear_on_exit(value=False)
    if light_state == 'off':
        blinkt.clear()
        blinkt.show()
        sys.exit(0)
    elif light_state == 'on':
        light_colour = sys.argv[2]
        log.info("Colour is " + light_colour)
        rgb_colour = get_colour(light_colour)
        log.info(rgb_colour)
        blinkt.set_brightness(1)
        blinkt.set_all(rgb_colour[0], rgb_colour[1], rgb_colour[2])
        log.info(rgb_colour[0])
        log.info(rgb_colour[1])
        log.info(rgb_colour[2])
        blinkt.show()
main()
