#!/usr/bin/env python

"""
Lightbooth. Made for anomalyxxx by nextempire.net
Author: <erik@nextempire.net>
Run as follows: sudo python lightbooth.py
"""

import datetime
import os
import os.path
import pygame
import pygbutton
import RPi.GPIO as GPIO
import subprocess as sub
import sys
from time import sleep

hashtag = "#anomalyxxx"
show_hashtag = False
count_down_seconds = 3 # how many seconds to count down
do_count_down = False # whether there should be a count down displayed before taking a picture
upload_to_instagram = False # whether the picture should be uploaded to instagram

# gphoto settings
gphoto_aperture = 15
gphoto_iso = 2
gphoto_shutterspeed = 40
gphoto_imageformat = 1

# set up input / output pins
gpio_button = 17
gpio_LED_green = 26
gpio_relay = 4
gpio_LED_red = 19

# other globals
font = "freeserif"
bounceMillis =  2000 # wait x ms before noticing another button press
logo_size = 200
photo_dir = "/home/pi/lightbooth/images/"
continue_loop = True
last_image_taken = ""
waiting_on_download = False # if this is true, look for last_image_taken 

def clicked(channel):
    print("Button clicked")
    if waiting_on_download:
        DrawCenterMessage("Wait for it ...",250)
    else:
        TakePicture()

def ledGreenOn():
    GPIO.output(gpio_LED_green,True)
    
def ledRedOn():
    GPIO.output(gpio_LED_red,True)

def ledRedOff():
    GPIO.output(gpio_LED_red,False)
    
def lightOn():
    print "lights on"
    GPIO.remove_event_detect(gpio_button) # sw fix for Noise and erroneous readings on sensors when relay is switched on
    GPIO.output(gpio_relay,False)
    sleep(1)
    GPIO.add_event_detect(gpio_button,GPIO.RISING,callback=clicked,bouncetime=bounceMillis)
    
def lightOff():
    print "lights off"
    GPIO.output(gpio_relay,True)

def DrawLogo():
    """ Draw title """
    #logo = pygame.transform.scale(pygame.image.load("anomaly_transparent_white.png"),(logosize[0],logosize[1]))
    # image
    image = pygame.image.load("anomaly_transparent_white.png")
    
    # crop middle square and resize
    imgsize = image.get_rect().size
    image_square = pygame.Rect((imgsize[0]-imgsize[1])/2, 0, imgsize[1], imgsize[1]) # left, top, width, height
    image_surface = pygame.transform.scale(image.subsurface(image_square),(logo_size,logo_size))
    screen.blit(image_surface,(offset+width-logo_size+20,height-logo_size+20))
    
    # hashtag
    if show_hashtag:
        screen.blit(pygame.font.SysFont(font,60,bold=0).render(hashtag, 1, white),(offset+20,height-100))
    
    pygame.display.update()
    
def DrawCenterMessage(message,local_width=550):
    """displays notification messages onto the screen"""
    local_height = 70
    x = offset + width/2 - local_width/2
    y = height/2 - local_height/2

    backgroundCenterSurface = pygame.Surface((local_width,local_height)) # size
    backgroundCenterSurface.fill(black)

    screen.blit(backgroundCenterSurface,(x,y)) # position
    screen.blit(pygame.font.SysFont(font,40,bold=1).render(message, 1, white),(x+10,y+10))
    
    pygame.display.update()
    
def DrawTopMessage(message,local_width=550):
    """displays notification messages onto the screen"""
    local_height = 70
    x = offset + width/2 - local_width/2
    y = 0

    backgroundCenterSurface = pygame.Surface((local_width,local_height)) # size
    backgroundCenterSurface.fill(black)

    screen.blit(backgroundCenterSurface,(x,y)) # position
    screen.blit(pygame.font.SysFont(font,40,bold=1).render(message, 1, white),(x+10,y+10))
    
    pygame.display.update()    
    
def LoadNewImage():
    """ after new image has been downloaded from the camera
     it must be loaded and displayed on the screen"""
    global waiting_on_download

    DrawCenterMessage("Transferring picture")
    
    ledRedOff()
    lightOn()

    image = pygame.image.load(last_image_taken).convert_alpha()
    
    # crop middle square 
    imgsize = image.get_rect().size
    image_square = pygame.Rect((imgsize[0]-imgsize[1])/2, 0, imgsize[1], imgsize[1]) # left, top, width, height
    image_surface = image.subsurface(image_square)
    
    # scale to screen
    capture = pygame.transform.scale(image_surface,(width,height))
    
    # display on screen
    screen.blit(capture,(offset,0))
    pygame.display.update()
    
    print "capture added to screen"
    
    waiting_on_download = False
    
def uploadToInstagram():
    rect = pygame.Rect((width-height)/2, 0, height, height)
    rect_surface = screen.subsurface(rect)
    pygame.image.save(rect_surface, photo_dir + "instagram.jpg")
    print "square screenshot saved"
    p = sub.Popen("php instagram.php",stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
    DrawTopMessage("Uploaded to instagram")
    sleep(5)
    DrawLogo()

def GetDateTimeString():
    """format the datetime for the time-stamped filename"""
    dt = str(datetime.datetime.now()).split(".")[0]
    clean = dt.replace(" ","_").replace(":","_")
    return clean

def TakePicture():
    """ executes the gphoto2 command to take a photo and download it from the camera """
    global last_image_taken, waiting_on_download
    
    print "taking picture"
    ledRedOn()

    # count down 
    if do_count_down:
        for x in range(count_down_seconds, 0, -1):
            DrawCenterMessage(str(x),200)
            pygame.display.update()
            sleep(1)
    
    lightOff()
    
    # dim screen
    screen.fill(black)
    DrawCenterMessage("SMILE :)",200)
    DrawLogo()
    pygame.display.update()
    
    # @todo start counting until camera is done
    
    # @todo add camera settings
    
    # take picture
    last_image_taken = photo_dir + "lightbooth" + GetDateTimeString() + ".jpg"
    take_pic_command = "gphoto2 --capture-image-and-download --filename " + last_image_taken + " --force-overwrite"
    print "command given " + take_pic_command
    p = sub.Popen(take_pic_command,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)

    # starts looking for the saved downloading image name
    waiting_on_download = True
    

# drop other possible connections to the camera on every restart, just to be safe
os.system("sudo pkill gvfs")
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"

print hashtag + " started"

# set GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_button,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(gpio_button,GPIO.RISING,callback=clicked,bouncetime=bounceMillis)
GPIO.setup(gpio_LED_green, GPIO.OUT, False) 
GPIO.setup(gpio_LED_red, GPIO.OUT, False) 
GPIO.setup(gpio_relay, GPIO.OUT)

# camera settings
print "fixing camera settings"
gphoto_iso_command = "gphoto2 --set-config /main/imgsettings/iso=" + str(gphoto_iso)
print gphoto_iso_command
p = sub.Popen(gphoto_iso_command,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
gphoto_shutterspeed_command = "gphoto2 --set-config /main/capturesettings/shutterspeed=" + str(gphoto_shutterspeed)
print gphoto_shutterspeed_command
p = sub.Popen(gphoto_shutterspeed_command,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
gphoto_aperture_command = "gphoto2 --set-config gphoto2 /main/capturesettings/aperture=" + str(gphoto_aperture)
print gphoto_aperture_command
p = sub.Popen(gphoto_aperture_command,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
gphoto_imageformat_command = "gphoto2 --set-config /main/imgsettings/imageformat=" + str(gphoto_imageformat)
print gphoto_imageformat_command
p = sub.Popen(gphoto_imageformat_command,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)

# set up pygame display
"Ininitializes a new pygame screen using the framebuffer"
# Based on "Python GUI in Linux frame buffer"
# http://www.karoltomala.com/blog/?p=679
disp_no = os.getenv("DISPLAY")
if disp_no:
    print "I'm running under X display = {0}".format(disp_no)

# Check which frame buffer drivers are available
# Start with fbcon since directfb hangs with composite output
drivers = ['fbcon', 'directfb', 'svgalib']
found = False
for driver in drivers:
    # Make sure that SDL_VIDEODRIVER is set
    if not os.getenv('SDL_VIDEODRIVER'):
        os.putenv('SDL_VIDEODRIVER', driver)
    try:
        pygame.display.init()
    except pygame.error:
        print 'Driver: {0} failed.'.format(driver)
        continue
    found = True
    break

if not found:
    raise Exception('No suitable video driver found!')

size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
height = size[1]
width = height # we want square pictures
offset = size[0]/2 - (width/2)
print "Framebuffer size: %d x %d" % (size[0], size[1])
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
# Clear the screen to start
screen.fill((0, 0, 0))        
# Initialise font support
pygame.font.init()
# Render the screen
pygame.display.update()

# define colours
white = pygame.Color(255,255,255)
black = pygame.Color(0,0,0)

# draw logo
DrawLogo()

print "Ready for action"
ledGreenOn()
ledRedOff()

try:
    while(continue_loop):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print "quiting..."
                continue_loop = False

        if waiting_on_download and os.path.isfile(last_image_taken):
            print "found file: " + last_image_taken
            LoadNewImage()
            DrawLogo()
            pygame.display.update()
            if upload_to_instagram:
                uploadToInstagram()

except:
    GPIO.cleanup()
    print "Unexpected error:", sys.exc_info()[0]

print "process complete"
pygame.quit()
exit(2)