import cv2
from PySide6.QtGui import QPixmap, QImage
from skimage.metrics import structural_similarity as ssim
from typing import List
from rect import draw_rectangle, get_frame_at_time, extract_text, resize_with_aspect_ratio, extract_roi, get_video_length, get_title, remove_old_images, get_time
from extraction import find_next_slide, save_img, ext
from datetime import datetime
import os
import sys



def get_video_dimensions(video_path):
    # Open the video file
    video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        print("Error: Could not open video.")
        return None, None

    # Get the width and height of the video
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    return width, height


if __name__ == "__main__":
    remove_old_images()

    # Example usage
    video_path = r"/home/robin/dwhelper/Robot mechanisms and user interfaces.mp4"
    time_sec = 20  # Time in seconds

    # Example usage
    # x, y = 1500, 700  # Top-left corner coordinates of the ROI
    # width, height = 400, 400  # Width and height of the ROI
    # print(get_video_dimensions(video_path))

    frame = get_frame_at_time(video_path, time_sec)
    # cv2.imwrite("test.jpg",frame)
    times = []
    times.append(time_sec)
    times_dict = []
    
    rectangle_coordinates = draw_rectangle(video_path,time_sec, title = "Page number")
    title_coordinates = draw_rectangle(video_path,time_sec, title = "Title coordinates")
    content_coordinates = draw_rectangle(video_path,time_sec, title = "Content coordinates")

    time = time_sec
    title = get_title(title_coordinates, time, video_path)
    hours, minutes, seconds = get_time(time)
    # minutes = int(time/60)
    # hours = int(minutes/60)
    # minutes = minutes - hours*60
    # seconds = time - minutes*60 - hours*3600
    # Aktuelle Uhrzeit abrufen
    current_time = datetime.now().strftime("%d_%m_%Y_H-%M-%S-%f")[:-3]
    img_name = f"img_{current_time}.jpg"
    times_dict.append({"total_seconds":time,
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds,
                "img":img_name,
                "title": title})


    video_length = int(get_video_length(video_path))

    while True:
        time = find_next_slide(time, video_path, rectangle_coordinates)
        title = get_title(title_coordinates, time, video_path)
        print(title)

        if time == video_length:
            break
        elif time - times[-1] > 15:
            times.append(time)
            hours, minutes, seconds = get_time(time)
            # Aktuelle Uhrzeit abrufen
            print(f"H: {hours}; m: {minutes}; sec: {seconds}")
            current_time = datetime.now().strftime("%d_%m_%Y_H-%M-%S-%f")[:-3]
            img_name = f"img_{current_time}.png"
            times_dict.append({"total_seconds":time,
                        "hours": hours,
                        "minutes": minutes,
                        "seconds": seconds,
                        "img":img_name,
                        "title": title})

# for file in os.listfiles("assets/")
markdown = ""
for i, item in enumerate(times_dict):
    if i < len(times_dict)-1:
        save_img(video_path, times_dict[i+1]["total_seconds"]-5, times_dict[i]["img"], content_coordinates)
    else:
        save_img(video_path, item["total_seconds"], item["img"], content_coordinates)
    title_img = f'2_{item["img"]}'
    save_img(video_path, times_dict[i+1]['total_seconds']-5, title_img, title_coordinates)
    markdown = markdown + f'\n---\n'
    markdown = markdown + f'\n### {item["title"]}\n'
    markdown = markdown + f'\n---\n'
    markdown = markdown + f'\n![[{title_img}]]\n'
    markdown = markdown + f'\n![[{item["img"]}]]\n'
    markdown = markdown + f'\ntimestamp:{ext(item["hours"])}:{ext(item["minutes"])}:{ext(item["seconds"])}\n'
    # if i < len(times_dict)-1:
    #     next_item = times_dict[i+1]
    #     markdown = markdown + f'\end:{next_item(item["hours"])}:{next_item(item["minutes"])}:{next_item(item["seconds"])}\n'
    # else:
    #     markdown = markdown + f'\end:{next_item(item["hours"])}:{next_item(item["minutes"])}:{next_item(item["seconds"])}\n'


with open("summary.md", "w") as f:
    f.write(markdown)

    
    # x = rectangle_coordinates["top_left"][0]
    # y = rectangle_coordinates["top_left"][1]

    # width = rectangle_coordinates["bottom_right"][0] - rectangle_coordinates["top_left"][0]
    # height = rectangle_coordinates["bottom_right"][1] - rectangle_coordinates["top_left"][1]

    # roi = extract_roi(frame, x, y, width, height)
    # extract_text(roi)

    # cv2.imshow("frame", roi)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
#     roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) 

#     time_sec2 = 1000
#     frame2 = get_frame_at_time(video_path, time_sec2)
#     roi2 = extract_roi(frame2, x, y, width, height)
#     roi2 = cv2.cvtColor(roi2, cv2.COLOR_BGR2GRAY) 

#     cv2.imwrite("roitest.jpg",roi)
#     cv2.imwrite("roitest2.jpg",roi2)
    
#     img = cv2.imread("roitest.jpg")
#     print("test")
#     sim, diff = ssim(roi, roi2, full = True)
#     print(sim)


# # If the frame was successfully captured, display it
# # if frame is not None:
# #     # Extract ROI from the frame
# #     roi = extract_roi(frame, x, y, width, height)
# #     cv2.imshow('Frame at 10 seconds', roi)
# #     cv2.waitKey(0)
# #     cv2.destroyAllWindows()
