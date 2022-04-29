import cv2
import numpy as np
import time
from flask import Flask,render_template,Response,request
app=Flask(__name__)
algo=cv2.createBackgroundSubtractorMOG2()
def center_handle(x,y,w,h):
    x1=int(w/2)
    y1=int(h/2)
    cx=x+x1
    cy=y+y1
    return cx,cy


@app.route('/')
def index():
     return  render_template('index.html')
def gen():
    min_width = 80
    min_height = 80
    count_line_pos = 550
    detect = []
    offset = 6
    count1 = 0
    count2 = 0
    count_prev = 999999
    k = 0
    j = 0
    cap=cv2.VideoCapture('video.mp4')
    while (cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            frame = cv2.VideoCapture('video.mp4')
            continue
        if ret:
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(grey, (13, 13), 5)
            img_sub = algo.apply(blur)
            dilat = cv2.dilate(img_sub, np.ones((5, 5)))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            dilatada = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)
            dilatada = cv2.morphologyEx(dilatada, cv2.MORPH_CLOSE, kernel)
            countershape, h = cv2.findContours(dilatada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cv2.line(frame, (25, count_line_pos), (1200, count_line_pos), (255, 127, 0), 3)

            for (i, c) in enumerate(countershape):
                (x, y, w, h) = cv2.boundingRect(c)
                validate_counter = (w >= min_width) and (h >= min_height)
                if not validate_counter:
                    continue
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                center = center_handle(x, y, w, h)
                detect.append(center)
                cv2.circle(frame, center, 4, (0, 0, 255), -1)
                for (x, y) in detect:
                    # if y < 556 and  y <=544:
                    if y < (count_line_pos + offset) and y > (count_line_pos - offset):
                        if x > 25 and x < 660:
                            count1 += 1
                        if x > 680 and x < 1200:
                            count2 += 1
                    cv2.line(frame, (25, count_line_pos), (1200, count_line_pos), (0, 127, 255), 3)
                    detect.remove((x, y))
                    if (count_prev != count1):
                        # print("vihcle count:"+str(count1))
                        count_prev = count1
            c1 = count1
            c2 = count2
            cv2.putText(frame, "c1:" + str(count1), (200, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
            cv2.putText(frame, "c2:" + str(count2), (800, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
            cv2.circle(frame, (100, 80), 30, (5, 252, 240), -1)
            cv2.circle(frame, (1200, 80), 30, (5, 252, 240), -1)
            if (count1 - count2 >= 5):
                cv2.circle(frame, (100, 80), 30, (0, 255, 0), -1)
                cv2.circle(frame, (1200, 80), 30, (0, 0, 255), -1)
                # t.sleep(3)
                if (count2 >= 10):
                    cv2.circle(frame, (100, 80), 30, (0, 0, 255), -1)
                    cv2.circle(frame, (1200, 80), 30, (0, 255, 0), -1)
                    if (count1 >= 2 * count2):
                        cv2.circle(frame, (100, 80), 30, (0, 255, 0), -1)
                        cv2.circle(frame, (1200, 80), 30, (0, 0, 255), -1)
            if (count2 - count1 >= 5):
                cv2.circle(frame, (1200, 80), 30, (0, 255, 0), -1)
                cv2.circle(frame, (100, 80), 30, (0, 0, 255), -1)
        frmae = cv2.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frmae + b'\r\n')
        #time.sleep(0.1)
        if cv2.waitKey(1) == 13:
                break
@app.route('/res',methods = ['POST','GET'])
def res():
	global result
	if request.method == 'POST':
		result = request.form.to_dict()
		return render_template("results.html",result = result)

@app.route('/results')
def video_feed():
    global result
    params= result
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
app.run(debug=True)
