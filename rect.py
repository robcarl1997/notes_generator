import cv2
# Import the necessary libraries 
from PIL import Image 
import pytesseract 
import os

def get_time(time):
    minutes = int(time/60)
    hours = int(minutes/60)
    minutes = minutes - hours*60
    seconds = time - minutes*60 - hours*3600
    return hours, minutes, seconds

def get_total_sec(hours, minutes, sec):
    hours = int(hours)
    minutes = int(minutes)
    sec = int(sec)
    return hours*3600 + minutes * 60 + sec

def remove_old_images():
    images = os.listdir()
    images = [im for im in images if "png" in im]
    for im in images:
        os.remove(im)

    images = os.listdir()
    images = [im for im in images if "jpg" in im]
    for im in images:
        os.remove(im)

    images = os.listdir("assets/")
    images = [im for im in images if "png" in im]
    for im in images:
        os.remove(os.path.join("assets",im))
    images = os.listdir("assets/")
    images = [im for im in images if "jpg" in im]
    for im in images:
        os.remove(os.path.join("assets",im))

def get_title(title_coordinates, time_sec, video_path):
    frame = get_frame_at_time(video_path, time_sec)
    x = title_coordinates["top_left"][0]
    y = title_coordinates["top_left"][1]

    width = title_coordinates["bottom_right"][0] - title_coordinates["top_left"][0]
    height = title_coordinates["bottom_right"][1] - title_coordinates["top_left"][1]

    roi = extract_roi(frame, x, y, width, height)
    title = extract_text(roi)

    return title


def get_video_length(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Check if the video file opened successfully
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return None
    
    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Get the frames per second (fps) of the video
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Calculate the duration in seconds
    if fps > 0:  # Avoid division by zero
        duration = total_frames / fps
        return duration
    else:
        print("Error: FPS is zero or invalid.")
        return None

def extract_roi(frame, x, y, width, height):
    """ Extract the region of interest (ROI) using numpy array slicing

    Args:
        frame (_type_): _description_
        x (_type_): _description_
        y (_type_): _description_
        width (_type_): _description_
        height (_type_): _description_

    Returns:
        List[List[int]]: Bild als Array
    """
    roi = frame[y:y+height, x:x+width]
    return roi

def resize_with_aspect_ratio(image, width=None, height=None):
    (h, w) = image.shape[:2]
    
    # If both width and height are None, return the original image
    if width is None and height is None:
        return image

    # If width is None, calculate the ratio based on height
    if width is None:
        ratio = height / float(h)
        dim = (int(w * ratio), height)
    
    # If height is None, calculate the ratio based on width
    elif height is None:
        ratio = width / float(w)
        dim = (width, int(h * ratio))
    
    # Resize the image with calculated dimensions
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    
    return resized

def extract_text(image):
    image_path = r"image_to_text.jpg"
    cv2.imwrite(image_path, image)
    # If you're on windows, you will need to point pytesseract to the path 
    # where you installed Tesseract 
    pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
    
    # Open the image file 
    # replace 'test.png' with your image file 
    img = Image.open(image_path)
    
    # Use pytesseract to convert the image data to text 
    text = pytesseract.image_to_string(img, lang = "deu")
    text = text.strip()
    
    # Print the text print(text)
    print(text)
    os.remove(image_path)
    return text

def get_frame_at_time(video_path:str, time_sec:int, resize = False):
    """Get frame of a video at a specific time (in seconds)

    Args:
        video_path (str): Path to video
        time_sec (int): time of the frame in seconds

    Returns:
        _type_: 
    """
    # Open the video file
    video = cv2.VideoCapture(video_path)
    
    # Set the video position to the specific time (in milliseconds)
    video.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)
    
    # Read the frame
    success, frame = video.read()
    
    if success:
        if resize == True:
            frame = resize_with_aspect_ratio(frame, width = 1500)
        return frame
    else:
        print("Could not read frame at the specified time.")
        return None

def draw_rectangle(video_path, time_sec, title = None):
    frame = get_frame_at_time(video_path, time_sec, resize=True)
    # Initialize global variables
    drawing = False  # True if mouse is pressed
    start_point = (-1, -1)  # Starting point of the rectangle
    end_point = (-1, -1)    # Ending point of the rectangle
    rectangle_coordinates = {}


    # Mouse callback function
    def draw_rectangle_with_mouse(event, x, y, flags, param):
        nonlocal start_point, end_point, drawing, rectangle_coordinates

        # If the left mouse button is clicked, start drawing the rectangle
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            start_point = (x, y)  # Record the start point

        # If the mouse is being moved and the button is pressed, update the end point
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                end_point = (x, y)  # Update the end point as the mouse moves

        # If the left mouse button is released, finalize the rectangle
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            end_point = (x, y)  # Set the final end point
            rectangle_coordinates = {
                "top_left": start_point,
                "bottom_right": end_point
            }
            # print(f"Rectangle drawn from {start_point} to {end_point}")

    def update_image():
        nonlocal frame, drawing, start_point, end_point, rectangle_coordinates, video_path , time_sec
        frame_at_time = get_frame_at_time(video_path, time_sec, resize = True)

        if type(frame_at_time) != None:
            frame = frame_at_time
        else:
            frame = frame

        drawing = False  # True if mouse is pressed
        start_point = (-1, -1)  # Starting point of the rectangle
        end_point = (-1, -1)    # Ending point of the rectangle
        rectangle_coordinates = {}
        clone = frame.copy()
        # print(time_sec)
        # Initialize global variables
        return frame, clone

    # Load the image
    clone = frame.copy()

    # Set up the window and mouse callback
    cv2.namedWindow(title)
    cv2.setMouseCallback(f"{title}", draw_rectangle_with_mouse)

    while True:
        # Display the image and allow drawing
        if not drawing:
            cv2.imshow(title, clone)
        else:
            temp_image = clone.copy()
            # print("drawing")
            cv2.rectangle(temp_image, start_point, end_point, (255, 0, 0), 2)
            cv2.imshow(title, temp_image)
        
        # # Break loop on 'q' key press
        key = cv2.waitKey(1)
        if key == ord('q'): 
            # print("Exit.")
            break
        elif key == ord('a') or key == 81:  # Left arrow or 'a' key
            print("Left Arrow Pressed")
            time_sec -= 15
            frame, clone = update_image()
            # cv2.imshow("Image", clone)
        elif key == ord('d') or key == 83:  # Right arrow or 'd' key
            print("Right Arrow Pressed")
            time_sec += 15
            frame, clone = update_image()
            # cv2.imshow("Image", clone)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    # Print final rectangle coordinates
    print(f"Final Rectangle Coordinates: {rectangle_coordinates}")

    height, width, channel = frame.shape
    original_frame = get_frame_at_time(video_path, time_sec)
    or_height, or_width, channel = original_frame.shape

    rectangle_coordinates = {
        "top_left": (int(rectangle_coordinates["top_left"][0]/width * or_width), int(rectangle_coordinates["top_left"][1]/height * or_height)),
        "bottom_right": (int(rectangle_coordinates["bottom_right"][0]/width * or_width), int(rectangle_coordinates["bottom_right"][1]/height * or_height))
    }
    # original_frame = get_frame_at_time(video_path, time_sec)
    # height, width, channel = original_frame.shape
    
    # Close the windows
    cv2.destroyAllWindows()

    return rectangle_coordinates


    # import sys
    # from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget
    # from PySide6.QtGui import QPixmap, QImage, QPainter, QPen
    # from PySide6.QtCore import Qt, QPoint, QRect
    # import main
    # import cv2

    # class ImageLabel(QLabel):
    #     def __init__(self, parent=None):
    #         super().__init__(parent)
    #         self.start_point = None
    #         self.end_point = None
    #         self.drawing = False
    #         self.setPixmap(QPixmap(400, 400))  # Replace with actual image
    #         self.pixmap().fill(Qt.white)

    #     def mousePressEvent(self, event):
    #         if event.button() == Qt.LeftButton:
    #             self.start_point = event.pos()
    #             self.drawing = True

    #     def mouseMoveEvent(self, event):
    #         if self.drawing:
    #             self.end_point = event.pos()
    #             self.update()  # Trigger a repaint

    #     def mouseReleaseEvent(self, event):
    #         if event.button() == Qt.LeftButton and self.drawing:
    #             self.end_point = event.pos()
    #             self.drawing = False
    #             self.update()  # Trigger a repaint
    #             print(f"Start point: {self.start_point}, End point: {self.end_point}")

    #     def paintEvent(self, event):
    #         super().paintEvent(event)
    #         if self.start_point and self.end_point:
    #             painter = QPainter(self)
    #             pen = QPen(Qt.red, 2)
    #             painter.setPen(pen)
    #             rect = QRect(self.start_point, self.end_point)
    #             painter.drawRect(rect)

    # class ImageWindow(QMainWindow):
    #     def __init__(self):
    #         super().__init__()

    #         # Create a QLabel to display the image
    #         self.label = ImageLabel(self)
    #         self.label.setAlignment(Qt.AlignCenter)

    #         # Load the initial image using QPixmap
    #         pixmap = QPixmap("path_to_your_image1.jpg")  # Replace with your image path
    #         self.label.setPixmap(pixmap)

    #         # Create a button to change the image
    #         self.change_button = QPushButton("Change Image")
    #         self.change_button.clicked.connect(self.change_image)
    #         self.cut_button = QPushButton("Cut")
    #         self.cut_button.clicked.connect(self.cut_image)

    #         # Create a layout and add the label and button to it
    #         layout = QVBoxLayout()
    #         layout.addWidget(self.label)
    #         layout.addWidget(self.change_button)
    #         layout.addWidget(self.cut_button)

    #         # Create a container widget and set the layout
    #         container = QWidget()
    #         container.setLayout(layout)

    #         # Set the container as the central widget
    #         self.setCentralWidget(container)

    #         # Set the window title and size
    #         self.setWindowTitle("Image Display")
    #         self.setGeometry(100, 100, 800, 600)

    #     def cut_image(self):
    #         self.change_image(select_roi = True)


    #     def change_image(self, select_roi = False):
    #         # Load the new image
            
    #         video_path = "/home/robin/dwhelper/Rechnergestutzte Messtechnik RMT - Vorlesungen Sommersemester 20.mp4"
    #         time_sec = 10  # Time in seconds
    #         frame = main.get_frame_at_time(video_path, time_sec)
    #         width, height = main.get_video_dimensions(video_path)

    #         if select_roi:
    #             x_start = int(self.label.start_point.x()/self.widht_scaled_pixmap*width)
    #             y_start = int(self.label.start_point.y()/self.height_scaled_pixmap*height)
    #             x_end = int(self.label.end_point.x()/self.widht_scaled_pixmap*width)
    #             y_end = int(self.label.end_point.y()/self.height_scaled_pixmap*height)
    #             print(x_start, y_start, x_end, y_end)
    #             roi = main.extract_roi(frame, x_start , y_start, x_end-x_start, y_end-y_start)
    #             cv2.imwrite("roitest.jpg", roi)
    #             qt_img = main.convert_cv_qt(frame)
    #             # qt_img = main.convert_cv_qt(roi)
    #         else:
    #             qt_img = main.convert_cv_qt(frame)
    #         # cv2.imwrite("test.jpg", frame)
    #         # Set the QPixmap of the QLabel
    #         pixmap = QPixmap.fromImage(qt_img)
            
    #         # Scale the pixmap (make it smaller)
    #         scaled_pixmap = pixmap.scaled(1200, 1200, Qt.KeepAspectRatio)  # Set desired width and height
    #         self.widht_scaled_pixmap = scaled_pixmap.width()
    #         self.height_scaled_pixmap = scaled_pixmap.height()

    #         self.label.setPixmap(scaled_pixmap)
    # if __name__ == "__main__":
    #     app = QApplication(sys.argv)

    #     window = ImageWindow()
    #     window.show()

    #     sys.exit(app.exec())
