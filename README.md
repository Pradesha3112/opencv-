# 🎥 Object Motion Analysis

Object Motion Analysis is a web application that allows users to upload a video and analyze the motion of objects within the frames. It calculates velocity, acceleration, direction, and force using fundamental physics formulas, making it ideal for educational and experimental motion-tracking use cases.

---

## 📌 Key Features

- 📤 Upload and process video files
- 🎞️ Live video stream playback with frame tracking
- 📊 Real-time analysis of:
  - Velocity
  - Acceleration
  - Direction
  - Force
- 📚 Scrollable frame-by-frame data log
- 🧠 Physics formulas displayed for clarity
- 💅 Stylish animated UI with Bootstrap, Font Awesome, and Animate.css

---

## 🛠️ Technologies Used

- **Frontend:** HTML5, CSS3, JavaScript
- **Styling Frameworks:** Bootstrap 5, Google Fonts, Animate.css
- **Icons:** Font Awesome
- **Live Data Streaming:** JavaScript EventSource (SSE)
- **Backend (assumed):** Python Flask (for handling `/upload`, `/video_feed`, and `/data_feed` routes)

---

## 📂 Project Structure

```

📁 object-motion-analysis/
├── index.html            # Main frontend logic and structure
├── static/               # Static assets like CSS or JS (if any)
├── templates/            # (If using Flask) HTML templates
├── app.py                # Backend logic (uploading, processing, streaming)
├── uploads/              # Uploaded video storage

````

---

## 🧪 Core Formulas Used

- **Velocity:**  
  `Velocity = (displacement in pixels × PIXEL_TO_CM) × FRAME_RATE`

- **Acceleration:**  
  `Acceleration = (Velocity_current - Velocity_previous) / dt`

- **Force:**  
  `Force = Mass × Acceleration`

- **Direction:**  
  `Calculated based on displacement vector angle`

---

## 🚀 How to Run Locally

1. Clone this repository:

```bash
git clone https://github.com/your-username/object-motion-analysis.git
cd object-motion-analysis
````

2. Make sure your backend (like Flask) is running with proper routes:

   * `/upload` – to receive video
   * `/video_feed` – to stream processed video
   * `/data_feed` – to push frame-wise data using SSE

3. Open `index.html` in your browser (or serve it via Flask templates).

---


## 📧 Contact

**Author:** Pradesha Senthilkumaran
📧 Email: [pradesha3112@gmail.com](mailto:pradesha3112@gmail.com)
🔗 [LinkedIn](https://www.linkedin.com/in/your-profile)

---

## ⭐ Show Your Support

If you found this helpful, please ⭐ star the repository and share it with others!

