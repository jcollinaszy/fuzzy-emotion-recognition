def emotion(IP, PORT):

    import time
    import math
    import fuzzy.storage.fcl.Reader

    # read fuzzy control language file
    system = fuzzy.storage.fcl.Reader.Reader().load_from_file("fuzzy.fcl")

    # make space for fuzzy inputs and outputs
    fuzzyInput = {
            "smileLeft" : 0.0,
            "smileRight" : 0.0,
            "mouth": 0.0,
            "nose": 0.0
            }
    fuzzyOutput = {
            "Emotion" : 0.0
            }

    # function to calculate euclidean distances of feature points on face multiplied by 100 for use in fuzzy system
    def normEuDist(x1, y1, x2, y2, fx, fy):
        return math.sqrt(((x1/fx-x2/fx)**2)+((y1/fy-y2/fy)**2))*100

    from naoqi import ALProxy

    # used for output announcement
    tts = ALProxy("ALTextToSpeech", IP, PORT)

    # create a proxy to ALFaceDetection
    try:
      faceProxy = ALProxy("ALFaceDetection", IP, PORT)
    except Exception, e:
      print "Error when creating face detection proxy:"
      print str(e)
      exit(1)

    # subscribe to the ALFaceDetection proxy with <period> frequency
    period = 0.5
    faceProxy.subscribe("faceDetection", period*100, 0.0 )

    # create a proxy to ALMemory
    try:
      memoryProxy = ALProxy("ALMemory", IP, PORT)
    except Exception, e:
      print "Error when creating memory proxy:"
      print str(e)
      exit(1)

    # a simple loop that reads "FaceDetected" and checks whether faces are detected
    for i in range(0, 20):
      time.sleep(period)
      val = memoryProxy.getData("FaceDetected")

      # check whether we got a valid output
      if(val and isinstance(val, list) and len(val) >= 2):

        try:
            # get info about first detected face
            faceShapeInfo = val[1][0][0]
            faceExtraInfo = val[1][0][1]

            # calculate euclidean distances for facial features
            #leftEye = normEuDist(faceExtraInfo[3][2], faceExtraInfo[3][3], faceExtraInfo[3][4], faceExtraInfo[3][5], faceShapeInfo[3], faceShapeInfo[4])
            #rightEye = normEuDist(faceExtraInfo[4][2], faceExtraInfo[4][3], faceExtraInfo[4][4], faceExtraInfo[4][5], faceShapeInfo[3], faceShapeInfo[4])
            mouth = normEuDist(faceExtraInfo[8][0], faceExtraInfo[8][1], faceExtraInfo[8][2], faceExtraInfo[8][3], faceShapeInfo[3], faceShapeInfo[4])
            #nose = normEuDist(faceExtraInfo[7][2], faceExtraInfo[7][3], faceExtraInfo[7][4], faceExtraInfo[7][5], faceShapeInfo[3], faceShapeInfo[4])
            smileLeft = normEuDist(faceExtraInfo[3][4], faceExtraInfo[3][5], faceExtraInfo[8][0], faceExtraInfo[8][1], faceShapeInfo[3], faceShapeInfo[4])
            smileRight = normEuDist(faceExtraInfo[4][4], faceExtraInfo[4][5], faceExtraInfo[8][2], faceExtraInfo[8][3], faceShapeInfo[3], faceShapeInfo[4])
            noseMouth = normEuDist(faceExtraInfo[7][0], faceExtraInfo[7][1], faceExtraInfo[8][4], faceExtraInfo[8][5], faceShapeInfo[3], faceShapeInfo[4])

            # feed distances to fuzzy system
            fuzzyInput["smileLeft"] = smileLeft
            fuzzyInput["smileRight"] = smileRight
            fuzzyInput["mouth"] = mouth
            fuzzyInput["nose"] = noseMouth

            # run fuzzy system
            system.calculate(fuzzyInput, fuzzyOutput)

            # get outputs from fuzzy system
            if (fuzzyOutput["Emotion"]<1.5):
                tts.say("happy")
            elif (fuzzyOutput["Emotion"]>2.5):
                tts.say("surprised")
            elif (fuzzyOutput["Emotion"]>1.5):
                tts.say("neutral")

        except Exception, e:
          print "faces detected, but getData is invalid. ALValue ="
          print val
          print "Error msg %s" % (str(e))

    # unsubscribe the module
    faceProxy.unsubscribe("faceDetection")

# run
emotion("IP", "PORT")