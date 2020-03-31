#!/usr/bin/env python3

    



import glob
import os
import sys
# import pygame
import matplotlib.pyplot as plt
try:
    sys.path.append(glob.glob('/opt/carla/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (sys.version_info.major, sys.version_info.minor, 'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
except IndexError:
    pass
import carla

import random
import time
import numpy as np
from numpy import savetxt
import cv2

IM_WIDTH = 800
IM_HEIGHT = 600


def show_img(image):
    raw = np.array(image.raw_data).astype('uint8')
    bgra = np.reshape(raw, (IM_HEIGHT, IM_WIDTH, 4))
    bgr = bgra[:IM_HEIGHT,:IM_WIDTH, :3]
    cv2.imshow("", bgr)
    cv2.waitKey(1)
    # plt.figure()
    # plt.imshow(bgr[:,:,::-1]/255.0)
    # plt.show(0.1)

def show_img_pygame(image):
    array = np.frombuffer(image.raw_data, dtype=np.dtype('uint8'))
    array = np.reshape(array, (image.height, image.width, 4))
    array = array[:,:,:3]
    array = array[:,:,::-1]
    pygame.surfarray.make_surface(array.swapaxes(0,1)) 

actor_list = []
try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)

    world = client.get_world()
    print(client.get_available_maps())

    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter('model3')[0]
    # print(bp)

    spawn_point = random.choice(world.get_map().get_spawn_points())
    vehicle = world.spawn_actor(bp, spawn_point)
    # transform = carla.Transform(carla.Location(x=200, y=200, z=1), 
        # carla.Rotation(yaw=180))
    # vehicle = world.spawn_actor(bp, transform)

    vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))
    # vehicle.set_autopilot(True)  # if you just wanted some NPCs to drive.
    location = vehicle.get_location()
    print(vehicle.get_location())
    actor_list.append(vehicle)

    # https://carla.readthedocs.io/en/latest/cameras_and_sensors
    # get the blueprint for this sensor
    blueprint = blueprint_library.find('sensor.camera.rgb')
    # change the dimensions of the image
    blueprint.set_attribute('image_size_x', '{0}'.format(IM_WIDTH))
    blueprint.set_attribute('image_size_y', '{0}'.format(IM_HEIGHT))
    blueprint.set_attribute('fov', '110')
    blueprint.set_attribute('sensor_tick', '1.0')

    # Adjust sensor relative to vehicle
    spawn_point = carla.Transform(carla.Location(x=0.8, z=1.7))

    # spawn the sensor and attach to vehicle.
    sensor = world.spawn_actor(blueprint, spawn_point, attach_to=vehicle)

    # add sensor to list of actors
    actor_list.append(sensor)

    # do something with this sensor
    # sensor.listen(lambda data: data.save_to_disk('_out/%06d.png' % data.frame))
    sensor.listen(lambda data: show_img(data))

    time.sleep(6)

finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')
