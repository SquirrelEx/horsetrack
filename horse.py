from __future__ import print_function
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import json
import cgi

HOST = "128.0.0.1"
PORT = 8000
import sys
import cv2
from random import randint
 
class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        resultlist = horserun("/Users/Gaurav/Documents/horse.mp4")
        self.wfile.write(bytes(json.dumps(resultlist), "utf-8"))
        
    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # read the message and convert it into a python dictionary
        length = int(self.headers.getheader('content-length'))
        message = json.loads(self.rfile.read(length))
        
        # add a property to the object, just to mess with data
        message['received'] = 'ok'
        
        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps(message))
        
def run(server_class=HTTPServer, handler_class=Server, port=8008):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    print('Starting httpd on port %d...' % port)
    httpd.serve_forever()
    

trackerTypes = ['BOOSTING', 'MIL', 'KCF','TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
 
def createTrackerByName(trackerType):
  # Create a tracker based on tracker name
  if trackerType == trackerTypes[0]:
    tracker = cv2.legacy.TrackerBoosting_create()
  elif trackerType == trackerTypes[1]:
    tracker = cv2.legacy.TrackerMIL_create()
  elif trackerType == trackerTypes[2]:
    tracker = cv2.legacy.TrackerKCF_create()
  elif trackerType == trackerTypes[3]:
    tracker = cv2.legacy.TrackerTLD_create()
  elif trackerType == trackerTypes[4]:
    tracker = cv2.legacy.TrackerMedianFlow_create()
  elif trackerType == trackerTypes[5]:
    tracker = cv2.legacy.TrackerGOTURN_create()
  elif trackerType == trackerTypes[6]:
    tracker = cv2.TrackerMOSSE_create()
  elif trackerType == trackerTypes[7]:
    tracker = cv2.legacy.TrackerCSRT_create()
  else:
    tracker = None
    print('Incorrect tracker name')
    print('Available trackers are:')
    for t in trackerTypes:
      print(t)
 
  return tracker
def horserun(videoparam):
# Set video to load
    videoPath = videoparam
     
    # Create a video capture object to read videos
    cap = cv2.VideoCapture(videoPath)
     
    # Read first frame
    success, frame = cap.read()
    # quit if unable to read the video file
    if not success:
      print('Failed to read video')
      sys.exit(1)
    ## Select boxes
    bboxes = []
    colors = []
     
    # OpenCV's selectROI function doesn't work for selecting multiple objects in Python
    # So we will call this function in a loop till we are done selecting all objects
    while True:
      # draw bounding boxes over objects
      # selectROI's default behaviour is to draw box starting from the center
      # when fromCenter is set to false, you can draw box starting from top left corner
      bbox = cv2.selectROI('MultiTracker', frame)
      bboxes.append(bbox)
      colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))
      print("Press q to quit selecting boxes and start tracking")
      print("Press any other key to select next object")
      k = cv2.waitKey(0) & 0xFF
      if (k == 113):  # q is pressed
        break
     
    print('Selected bounding boxes {}'.format(bboxes))

    # Specify the tracker type
    trackerType = "CSRT"
     
    # Create MultiTracker object
    multiTracker = cv2.legacy.MultiTracker_create()
    finalresult = []
    # Initialize MultiTracker
    for bbox in bboxes:
      multiTracker.add(createTrackerByName(trackerType), frame, bbox)
    frameno = 0;
    while cap.isOpened():
        success, frame = cap.read()
        frameno+=1
        if not success:
            break
        list = []
        templist = []
      # get updated location of objects in subsequent frames
        success, boxes = multiTracker.update(frame)
      # draw tracked objects
        for i, newbox in enumerate(boxes):
            p1 = (int(newbox[0]), int(newbox[1]))
            p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
            cv2.rectangle(frame, p1, p2, colors[i], 2, 1)
            cv2.putText(frame, str(i), p1, cv2.FONT_HERSHEY_SIMPLEX, 1, colors[i], 2)
            temp2 = p1[0]
            tempno = (frameno + 0.1*(600-temp2))/376
            if tempno > 1:
                tempno = 1
            list.insert(len(list), tempno)
            
        
     
            # show frame
        cv2.imshow('MultiTracker', frame)
        templist = list
        print(str(list))
        finalresult.insert(0, list)
      # quit on ESC button
        if cv2.waitKey(1) & 0xFF == 27:  # Esc pressed
            break
    return finalresult
    
if __name__ == "__main__":
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
    
