from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
import numpy as np
import os
import json
import time
import math

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'
allowed_extensions = {'mp4', 'avi', 'mov'}

# Constants for conversion and timing
PIXEL_TO_CM = 0.1      # 1 pixel equals 0.1 cm (adjust as needed)
FRAME_RATE = 30.0      # Video FPS (adjust based on your video)
dt = 1.0 / FRAME_RATE  # Time step in seconds

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Global variables for video processing and tracking
video_uploaded = False
cap = None
frame_count = 0
velocity = 0.0
acceleration = 0.0
total_frames = 0
previous_velocity = 0.0  # For acceleration calculation
direction = "N/A"  # Global variable to store the current direction
mass = 1.0  # Default mass in kg

# Optical flow tracking globals
prev_gray = None
prev_points = None

@app.route('/upload', methods=['POST'])
def upload_video():
    global cap, video_uploaded, frame_count, total_frames, previous_velocity, prev_gray, prev_points, direction, mass
    if 'video_file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['video_file']
    mass = 0.1  # Fixed mass value in kg
    
    if file.filename == '' or not allowed_file(file.filename):
        return redirect(url_for('index'))
    
    # Save the uploaded video file in the static folder
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(video_path)
    
    # Release any previous capture and open the new video
    if cap is not None:
        cap.release()
    cap = cv2.VideoCapture(video_path)
    
    # Reset counters and variables
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    previous_velocity = 0.0
    direction = "N/A"
    
    # Read the first frame to initialize optical flow tracking
    ret, first_frame = cap.read()
    if not ret:
        return redirect(url_for('index'))
    prev_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
    prev_points = cv2.goodFeaturesToTrack(prev_gray, maxCorners=1, qualityLevel=0.3, minDistance=7)
    
    # Reset video position to start
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    video_uploaded = True
    return redirect(url_for('index'))

def process_video():
    global frame_count, velocity, acceleration, cap, total_frames, previous_velocity, dt, prev_gray, prev_points, direction, mass

    while cap is not None and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break  # End of video
        
        frame_count += 1
        current_time = frame_count / FRAME_RATE  # seconds
        
        # Convert current frame to grayscale for optical flow calculation
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Optical flow: track the feature point from the previous frame
        next_points, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_points, None)
        if next_points is not None and status is not None and status[0][0] == 1:
            # Calculate displacement between the previous and current feature positions
            prev_pt = prev_points[0][0]
            curr_pt = next_points[0][0]
            dx = curr_pt[0] - prev_pt[0]
            dy = curr_pt[1] - prev_pt[1]
            displacement_pixels = np.linalg.norm([dx, dy])
            real_distance = displacement_pixels * PIXEL_TO_CM  # in cm
            
            # Compute velocity (cm/s) and acceleration (cm/s²)
            velocity = real_distance * FRAME_RATE
            acceleration = (velocity - previous_velocity) / dt
            previous_velocity = velocity
            
            # Compute direction based on the displacement vector
            angle = math.degrees(math.atan2(dy, dx))
            if -45 <= angle < 45:
                direction = "East"
            elif 45 <= angle < 135:
                direction = "South"
            elif -135 <= angle < -45:
                direction = "North"
            else:
                direction = "West"
            
            # Compute force (in Newtons)
            acceleration_mps2 = acceleration / 100  # Convert cm/s² to m/s²
            force = mass * acceleration_mps2  # Force = mass * acceleration
            
            # Update previous frame and feature points for the next iteration
            prev_gray = gray.copy()
            prev_points = next_points
        else:
            # If tracking fails, reinitialize feature detection on the current frame
            prev_points = cv2.goodFeaturesToTrack(gray, maxCorners=1, qualityLevel=0.3, minDistance=7)
            velocity = 0.0
            acceleration = 0.0
            direction = "N/A"
            force = 0.0
        
        # Overlay the computed data on the frame
        cv2.putText(frame, f"Frame: {frame_count}/{total_frames}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Velocity: {velocity:.2f} cm/s", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Acc: {acceleration:.2f} cm/s²", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Direction: {direction}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        #cv2.putText(frame, f"Force: {force:.2f} N", (10, 150),
                    #cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Encode the frame as JPEG for streaming
        ret2, buffer = cv2.imencode('.jpg', frame)
        if not ret2:
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(dt)
        if frame_count >= total_frames:
            break

def generate_data():
    global frame_count, velocity, acceleration, cap, total_frames, dt, direction, mass
    # Send frame data until the video ends
    while cap is not None and cap.isOpened() and frame_count < total_frames:
        acceleration_mps2 = acceleration / 100  # Convert cm/s² to m/s²
        force = mass * acceleration_mps2  # Force = mass * acceleration
        data = {
            'frame': frame_count,
            'velocity': velocity,
            'acceleration': acceleration,
            'direction': direction,
            'force': force
        }
        json_data = json.dumps(data)
        yield f"data: {json_data}\n\n"
        time.sleep(dt)
    
    # Send a final message when the video ends
    yield "data: {\"message\": \"Video Ended\"}\n\n"
@app.route("/")
def index():
    return render_template("index.html", video_uploaded=video_uploaded)

@app.route("/video_feed")
def video_feed():
    return Response(process_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/data_feed")
def data_feed():
    return Response(generate_data(), mimetype="text/event-stream")
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
