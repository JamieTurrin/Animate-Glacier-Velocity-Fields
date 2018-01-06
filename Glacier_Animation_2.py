# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 11:29:00 2015

@author: James Turrin
"""

#####################################################################################
# Program to animate a glacier using displacement measurements
# from multiple velocity fields.

# Required inputs:
# Glacier mask (tif)
# Text file with paths to x_velocity, y_velocity, and glacier image
# for each velocity field (all in tiff format). Paths must not have quotes!!

# Output: frames (.png images) of the glacier, with BVs moved according to the
# displacements prescribed by the x_velocity and y_velocity data.



from read_tiff_file import read_tiff_file    #import function to read TIFF files    
from write_png_file import write_png_file    #import function to write data array to PNG file
import math,numpy,os
from contrast_stretch import contrast_stretch

# Choose a good image of glacier, free of clouds, scanline stripes, excess snow, etc.
background_image = read_tiff_file('C:/users/James/satellite_data/logan_path63_row17/1999_aug5/logan_1999.tif')

#read glacier mask and get columns, rows, bands....
mask,cols,rows,bands=read_tiff_file('C:/users/James/satellite_data/logan_path63_row17/logan_glacier_mask.tif',dims=1)

#output=glacier_image.copy()  #create copy of input image, this will receive displaced BVs
output=numpy.zeros((rows,cols),dtype='float') #create array to recieve displaced BVs


print '# columns =',cols, '# rows =',rows, '# bands =',bands


time_span = 1.0  # time between satellite images
num_frames = 10.0   # number of frames per velocity field to create
res = 30.0       # spatial resolution of satellite images
frame = 0        # frame number

infile = open("c:/users/james/vectors/logan/logan_animation_inputs.txt","r")
#input file contains path to x_vel, y_vel, and glacier image on each line, without quotation marks!!

all_lines=infile.readlines() #read whole infile list
list_length = len(all_lines) #get length of list
all_lines = None
counter = int(list_length*num_frames)  #total # frames to be produced
#cannot re-read infile, must close it and then open it a 2nd time
# to read each line individually in FOR loop below.
infile.close()   #close input text file


infile =  open("c:/users/james/vectors/logan/logan_animation_inputs.txt","r")
#input file contains path to x_vel, y_vel, and glacier image on each line, without quotation marks!!

for line in infile:  #read input text file to get paths to velocity fields

    words = line.split() #split each line of text into separate words (strings)
    x_vel = read_tiff_file(words[0]) #read x vel tiff file, path is given in words[0]
    y_vel = read_tiff_file(words[1]) #read y vel tiff file, path is given in words[1]
    glacier_image = read_tiff_file(words[2]) #read glacier image file, path is in words[2]

    k = 1.0  # set/reset iterator for WHILE loop:
    while k <= num_frames:  # each iteration of WHILE loop creates a separate frame

        frame = frame + 1 #iterate frame number
        # FOR loops to mask copy of glacier image, placing values of 0.0 into glacier, but leaving
        # surrounding terrain, which is filled in using original glacier image.
        print ''
        print 'Begin masking frame',frame,'out of',counter
        print ''
        for i in range(0,rows-1):
            for j in range(0,cols-1):
                if mask[i,j] > 0:  #where mask is > 0
                    output[i,j]=0.0
                else:
                    output[i,j]=float(background_image[i,j])
        print 'Finished masking frame',frame,'out of',counter
        print ''
    
        x_disp = x_vel*time_span*(k/num_frames)/res  #x displacement in pixels
        y_disp = -y_vel*time_span*(k/num_frames)/res  #y displacement in pixels (negative to orient correctly)

        # FOR loops go through each pixel of image and move BVs according to displacements
        # prescribed by x_disp and y_disp.

        for i in range(0,rows-1):
            for j in range(0,cols-1):
                if math.sqrt(x_disp[i,j]**2+y_disp[i,j]**2) > 0.0:
            
                
                    if x_disp[i,j] < 0.0:  #if x disp. is neg., then reverse floor and ceiling
                        xfloor = math.ceil(x_disp[i,j])
                        xceil = math.floor(x_disp[i,j])
                        x_dec = math.fabs(x_disp[i,j]) - math.fabs(xfloor) #calc. decimal portion of x disp
                    else:                   # if x disp. is pos., then calc floor and ceiling
                        xfloor = math.floor(x_disp[i,j])
                        xceil = math.ceil(x_disp[i,j])
                        x_dec = x_disp[i,j] - xfloor  #calc. decimal portion of x disp.
                
            
                    if y_disp[i,j] < 0.0:  #if y disp. is neg. then reverse floor and ceiling
                        yfloor = math.ceil(y_disp[i,j])
                        yceil = math.floor(y_disp[i,j])
                        y_dec = math.fabs(y_disp[i,j]) - math.fabs(yfloor) #calc. decimal portion of y disp
                    else:                   # if y disp, is pos., then calc. floor and ceiling
                        yfloor = math.floor(y_disp[i,j])
                        yceil = math.ceil(y_disp[i,j])
                        y_dec = y_disp[i,j] - yfloor   #calc. decimal portion of y disp.
            
            
                        
                    output[i+yfloor,j+xfloor] = output[i+yfloor,j+xfloor] + (1.0-y_dec)*(1-x_dec)*glacier_image[i,j]
                    output[i+yfloor,j+xceil] = output[i+yfloor,j+xceil] + (1.0-y_dec)*(x_dec)*glacier_image[i,j]
                    output[i+yceil,j+xfloor] = output[i+yceil,j+xfloor] + (y_dec)*(1-x_dec)*glacier_image[i,j]
                    output[i+yceil,j+xceil] = output[i+yceil,j+xceil] + (y_dec)*(x_dec)*glacier_image[i,j]   
            
            if i%100 == 0:
                percent_complete = math.floor(100*float(i)/float(rows-1))
                print 'Frame ',frame,' out of ',counter,' is ',percent_complete, '% complete'
                
        # FOR LOOPS THAT MOVE BVS FINISH HERE....
    
        x_disp = None  #clear x_disp for next interation of WHILE loop
        y_disp = None  #clear y_disp for next interation of WHILE loop

        # FOR loops to check each pixel of output and replace any empty pixels with a BV
        # from the original image
        print ''
        print 'Filling empty pixels in frame',frame
        for i in range(0,rows-1):
            for j in range(0, cols-1):
                if output[i,j] == 0.0:
                    output[i,j] = float(glacier_image[i,j])
    
        print ''
        print 'Finished filling empty pixels in frame',frame
    

        output=contrast_stretch(output,10) #stretch contrast of output image by 10%          
    
        #supply name of output file
        destination_filename='C:/users/James/vectors/logan/animation/frame_' + str(frame) +'.png' 

        #write data array to file, save to disk    
        write_png_file(destination_filename, cols, rows, output)
        
        #supply name of .tmp file that is automatically created so it can be deleted
        tmp_filename='C:/users/James/vectors/logan/animation/frame_' + str(frame) + '.tmp'
        os.remove(tmp_filename)  #remove .tmp file
            
        k=k+1 # iterate WHILE loop index
        
    # WHILE LOOP THAT CREATES FRAMES FINISHES HERE....
        
    x_vel = None #del x vel, new x vel will be reloaded when next line of input text file is read
    y_vel = None
    glacier_image = None #del glacier image, new image will be reloaded with next line of input text.
    words = None #del paths to previous velocity field files
    
# FOR LOOP THAT READS INPUT TEXT FILE FINISHES HERE....
    
infile.close()   #close input text file
del output  #delete variables to free memory space
del mask
del background_image
del x_vel
del y_vel
del glacier_image

print ''
print 'PROGRAM FINISHED'


















