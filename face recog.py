import cv2

# Function to check camera availability
def check_camera(index):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"Camera index {index} not available.")
        return False
    return cap

# Test different camera indexes
camera_found = False
for i in range(3):  # Try first three indexes
    cap = check_camera(i)
    if cap:
        camera_found = True
        break

if not camera_found:
    print("No camera found. Exiting...")
    exit()

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # Draw rectangles around the detected faces and show coordinates
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # Show coordinates on the frame
        coordinates = f"X: {x}, Y: {y}"
        cv2.putText(frame, coordinates, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Print coordinates to console
        print(f"Detected face at: X: {x}, Y: {y}")

    # Display the resulting frame
    cv2.imshow('Face Detection', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
