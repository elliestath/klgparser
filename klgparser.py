#!/usr/bin/python

'''
    File name: klgparser.py
    Based on code by Neil Ibrahimli
'''
__author__     = "Carlos Beltran-Gonzalez"
__copyright__  = "Copyright 2017, Carlos Beltran-Gonzalez"
__credits__    = "Neil Ibrahimli"
__licence__    = "GPL"
__version__    = "3.0"
__maintainer__ = "Carlos Beltran-Gonzalez"
__email__      = "carlos.beltran@iit.it"

import numpy as np
import cv2
import zlib
import Image
import filecmp
import unittest
import os
import shutil
import sys, getopt

class TestKLGParser(unittest.TestCase):
    def __init__(self, testName, outputfolder, testfolder, framesrange):
            super(TestKLGParser, self).__init__(testName) 
            self.outputfolder = outputfolder
            self.testfolder   = testfolder
            self.framesrange  = framesrange
    def testDepthOutput(self):
        _outputfolder = self.outputfolder
        _testfolder   = self.testfolder
        testindx = 0 #Test index always starts at 0
        for indx in self.framesrange:
            filename     = "depth_aug" + str(indx) +".png"
            filenametest = "depth_aug" + str(testindx) +".png"
            testindx+=1;
            file1 = _outputfolder + filename
            file2 = _testfolder   + filenametest
            self.assertTrue(filecmp.cmp(file1,file2,shallow=False))
    def testRGBOutput(self):
        _outputfolder = self.outputfolder
        _testfolder   = self.testfolder
        testindx = 0 #Test index always starts at 0
        for indx in self.framesrange:
            filename     = "rgb_aug" + str(indx) + ".png"
            filenametest = "rgb_aug" + str(testindx) + ".png"
            testindx+=1;
            file1 = _outputfolder + filename
            file2 = _testfolder   + filenametest
            self.assertTrue(filecmp.cmp(file1,file2,shallow=False))

def checkCreateOutputFolder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def removeFolder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)

def klg2png(inputfile,firstframe,lastframe, outputfolder):
    
    f = open(inputfile, "rb")

    # extract number of frames (32 bits)
    byte = f.read(4)
    a=map(ord,byte)
    numberofframes= a[3]*256*256*256+a[2]*256*256+a[1]*256+a[0]

    count=0

    # initialize images matrices
    depth = np.ones( (480,640),   dtype=np.uint16)
    rgb   = np.ones( (480,640,3), dtype=np.uint8)

    #numberofframes = 10 #TOFIX: hack for testing

    while count < lastframe:

        print count

        #reading timestamp
        byte = f.read(8)
        a=map(ord,byte)

        #reading depthsize
        byte = f.read(4)
        a=map(ord,byte)
        depthsize = a[3]*256*256*256+a[2]*256*256+a[1]*256+a[0]

        #reading imagesize
        byte = f.read(4)
        a=map(ord,byte)
        imagesize = a[3]*256*256*256+a[2]*256*256+a[1]*256+a[0]

        #extracting depth image
        byte = f.read(depthsize)
        if count >= firstframe and count < lastframe: 
            dimage=zlib.decompress(byte)
            a=map(ord,dimage)
            for i in range(len(a)-1):
                depth[(i/1280)][(i%1280)/2]=a[i+1]*256+a[i]
            dname= outputfolder + "depth_aug"+str(count)+".png"
            cv2.imwrite(dname,depth)

            #extracting rgb image
        byte = f.read(imagesize)
        if count >= firstframe and count < lastframe: 
            timage = np.fromstring(byte, dtype=np.uint8)
            rgb=cv2.imdecode(timage,1)
            cname= outputfolder + "rgb_aug"+str(count)+".png"
            cv2.imwrite(cname,cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB))

        count+=1

    f.close()

def klg2klg(inputfile,outputfile,firstframe,lastframe):

    f    = open(inputfile, "rb")
    fout = open(outputfile, "wb")

    # extract number of frames (32 bits)
    byte = f.read(4)
    a=map(ord,byte)
    numberofframes= a[3]*256*256*256+a[2]*256*256+a[1]*256+a[0]

    dstnumofframes = lastframe - firstframe;
    dstnumofframes = np.uint32(dstnumofframes);
    
    # save to output file
    fout.write(dstnumofframes);

    count=0

    # initialize images matrices
    depth = np.ones( (480,640),   dtype=np.uint16)
    rgb   = np.ones( (480,640,3), dtype=np.uint8)

    #numberofframes = 10 #TOFIX: hack for testing

    while count < lastframe:

        #print count

        #reading timestamp
        byte = f.read(8)
        a=map(ord,byte)
        if count >= firstframe and count < lastframe: 
            fout.write(byte)

        #reading depthsize
        byte = f.read(4)
        if count >= firstframe and count < lastframe: 
            fout.write(byte)
        a=map(ord,byte)
        depthsize = a[3]*256*256*256+a[2]*256*256+a[1]*256+a[0]

        #reading imagesize
        byte = f.read(4)
        if count >= firstframe and count < lastframe: 
            fout.write(byte)
        a=map(ord,byte)
        imagesize = a[3]*256*256*256+a[2]*256*256+a[1]*256+a[0]

        #extracting depth image
        byte = f.read(depthsize)
        if count >= firstframe and count < lastframe: 
            fout.write(byte)

        #extracting rgb image
        byte = f.read(imagesize)
        if count >= firstframe and count < lastframe: 
            fout.write(byte)

        count+=1

    f.close()

def Test():

    klg2png_output      = "klg2png_output/"
    klg2png_output_test = "output_test/"

    dynfolder     = "dyn_output/"
    dyntestfolder = "dyn_test/"

    # Preparing the environment
    removeFolder(klg2png_output);
    checkCreateOutputFolder(klg2png_output)
    removeFolder(dyntestfolder);
    checkCreateOutputFolder(dyntestfolder)
    removeFolder(dynfolder);
    checkCreateOutputFolder(dynfolder)

    # Actuating algorihtms for first 10 frames
    klg2klg("2017-08-01.00.klg","outklg.klg",0,10)
    klg2png("outklg.klg",0,10,klg2png_output)

    # Actuating algorihtms for frame interval
    klg2png("2017-08-01.00.klg",50,60,dynfolder)
    klg2klg("2017-08-01.00.klg","outklg.klg",50,60)
    klg2png("outklg.klg",0,10,dyntestfolder)

    # calling tests
    suite = unittest.TestSuite()
    suite.addTest(TestKLGParser('testDepthOutput', klg2png_output, klg2png_output_test, range(10)))
    suite.addTest(TestKLGParser('testRGBOutput',   klg2png_output, klg2png_output_test, range(10)))
    suite.addTest(TestKLGParser('testDepthOutput', dynfolder, dyntestfolder, range(50,60)))
    suite.addTest(TestKLGParser('testRGBOutput',   dynfolder, dyntestfolder, range(50,60)))

    unittest.TextTestRunner(verbosity=2).run(suite)

def printUse():
    print 'klgparser.py -i <inputfile> -o <outputfile> -s <startframe> -e <endframe>'
    print 'klgparser.py --ifile <inputfile> --ofile <outputfile> --fstar <startframe --fend <endframe>'

def main(argv):

    inputfile  = ''
    outputfile = ''
    fstart     = ''
    fend       = ''

    try:
       opts, args = getopt.getopt(argv,"hti:o:s:e:",["ifile=","ofile=","fstart=","fend="])
    except getopt.GetoptError:
       printUse()
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          printUse()
          sys.exit()
       elif opt == '-t':
          print 'Testing'
          Test()
          sys.exit()
       elif opt in ("-i", "--ifile"):
          inputfile = arg
       elif opt in ("-o", "--ofile"):
          outputfile = arg
       elif opt in ("-s", "--fstart"):
          fstart = arg
       elif opt in ("-e", "--fend"):
          fend = arg
    
    if not inputfile  or \
       not outputfile or \
       not fstart      or \
       not fend:
        printUse()
        sys.exit()

    print "Converting file"
    klg2klg(inputfile,outputfile,int(fstart),int(fend))
    print "Done"
    #removeFolder("finaltest");
    #checkCreateOutputFolder("finaltest")
    #klg2png(outputfile,0,int(fend)-int(fstart),"finaltest/")

if __name__ == "__main__":
   main(sys.argv[1:])   

