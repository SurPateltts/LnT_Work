from __future__ import print_function
import sys
import cv2; import math
from random import randint

trackerTypes = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']


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
        tracker = cv2.TrackerGOTURN_create()
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

cap = cv2.VideoCapture("test.mp4")
#cap = cv2.VideoCapture(0)

success, frame = cap.read()


# SIZE
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

size = (frame_width, frame_height)

# VIDEO WRITER
result = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'MJPG'),10, size)

if not success:
    print('Failed to read video')
    sys.exit(1)

## Select boxes
bboxes = []
colors = []
mid_points = []

while True:
    cv2.putText(frame, "Press G to select group of points", (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
    cv2.putText(frame, "Press N to select two points to measure", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
    if cv2.waitKey(0) & 0x47:  #### Group of Points
        while(cv2.waitKey(0) & 0xFF)

    bbox = cv2.selectROI('MultiTracker', frame)
    bboxes.append(bbox)
    colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))
    print("Press q to quit selecting boxes and start tracking")
    print("Press any other key to select next object")
    k = cv2.waitKey(0) & 0xFF
    
    timer = cv2.getTickCount()
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
    
    print(k)
    if k == 113:  # q is pressed
        break

trackerType = "CSRT"
createTrackerByName(trackerType)

# Create MultiTracker object
multiTracker = cv2.legacy.MultiTracker_create()

# Initialize MultiTracker
for bbox in bboxes:
    multiTracker.add(createTrackerByName(trackerType), frame, bbox)
mid_point_array =[]
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    mid_point_array.clear()
    success, boxes = multiTracker.update(frame)
    #id_no = 1
    if success:
        for i, newbox in enumerate(boxes):
            p1 = (int(newbox[0]), int(newbox[1]))
            p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
            cv2.rectangle(frame, p1, p2, colors[i], 2, 1)
            mid_point = (int((p1[0] + p2[0]) / 2), int((p1[1] + p2[1]) / 2))
            print("point ",i)
            print("midpoint: ",mid_point)
            i = int(i)
            mid_point_array.append(mid_point)
            cv2.circle(frame, mid_point, 5, (0, 0, 255), -1)
            cv2.putText(frame, "p"+str(i), (mid_point[0]+5,mid_point[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
            if len(mid_point_array)>1:
                mp1 = tuple(mid_point_array[0])
                print(mp1[0])
                mp2 = tuple(mid_point_array[1])
                print(mp2[0])
                cv2.line(frame, mp1, mp2, (0, 255, 0), thickness=3, lineType=8)
                dist = math.sqrt((mp2[0] - mp1[0])**2 + (mp2[1] - mp1[1])**2)
                dist = str(dist)
                print(str(dist))
                cv2.putText(frame, dist , (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                            (0, 0, 255), 2)

    else:
        # Tracking failure
        cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        
    cv2.putText(frame, "FPS : " + str(int(fps)), (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);

    result.write(frame)
    cv2.imshow('MultiTracker', frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Esc pressed
        break

cap.release()
result.release()

cv2.destroyAllWindows()