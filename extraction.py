from skimage.metrics import structural_similarity as ssim
from rect import get_frame_at_time, extract_roi, get_video_length
import cv2
import os
import sys
open_ai_dir = r"/home/robin/pCloud_loc/skripte/openai"

sys.path.append(open_ai_dir)
import test_open_ai
import gpt



lang = input("Bitte Sprache eingeben (deu/eng): ")
if lang == "deu":
    header = """Erstelle stichpunktartige Karteikarten mit den gegebenen Informationen.
                Überschriften sollen fett gemacht werden (markdown).
                Du kannst wichtige Aspekte hervorheben durch unterschreichen oder Farbe (HTML)!
                Setze (Latex) Formeln zwischen zwei $. Mehrere Formeln hintereindander sollen wie folgt dargestellt werden: $$ Formeln $$.
                """
else:
    header = """Create flashcards in form of bullet points with the given informations.
                Make the headlines (content of the front of the cards) in Bold (markdown).
                You can emphasize important information with underscoring or color (HTML)!
                Set (Latex) formulas between two $. In case of several formulas place them like this: $$ formulas $$.
                """

messages = [
            {"role": "system", "content": header} # {"role": "user", "content": prompt}
]

def ext(input):
    """Extend input number to two digits for function of chat gpt

    Args:
        input (_type_): number
    """
    if len(str(input)) < 2:
        return f"0{input}"
    else:
        return f"{input}"

def get_lines():
    with open("summary.md", "r") as f:
        data = f.read()
        # lines = f.read()
    lines = data.split("\n")
    lines = [line.replace("\n","") for line in lines if "timestamp" in line]
    return lines


def save_img(video_path, time, img_name, content_coordinates):
    x = content_coordinates["top_left"][0]
    y = content_coordinates["top_left"][1]
    width = content_coordinates["bottom_right"][0] - content_coordinates["top_left"][0]
    height = content_coordinates["bottom_right"][1] - content_coordinates["top_left"][1]

    frame = get_frame_at_time(video_path, time)
    roi = extract_roi(frame, x, y, width, height)
    cv2.imwrite(os.path.join("assets",img_name), roi)

def find_next_slide(start_time, video_path, rectangle_coordinates):
    x = rectangle_coordinates["top_left"][0]
    y = rectangle_coordinates["top_left"][1]
    width = rectangle_coordinates["bottom_right"][0] - rectangle_coordinates["top_left"][0]
    height = rectangle_coordinates["bottom_right"][1] - rectangle_coordinates["top_left"][1]
    video_length = int(get_video_length(video_path))
    # print(video_length)

    # Get start frame
    start_frame = get_frame_at_time(video_path, start_time)
    start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY) 
    start_roi = extract_roi(start_frame, x, y, width, height)
    time = start_time + 2

    while True:
        if time >= video_length:
            time = video_length
            # print(time)
            # print("-----------------")
            break
        else:
            end_frame = get_frame_at_time(video_path, time)
            end_frame = cv2.cvtColor(end_frame, cv2.COLOR_BGR2GRAY) 
            end_roi = extract_roi(end_frame, x, y, width, height)
            sim, diff = ssim(start_roi, end_roi, full = True)
            # print(sim)
            if (1-sim)*100 > 3:
                # print(time)
                # print("-----------------")
                break

            time = time + 2

    return time

def main():
    global messages
    # copy_lines = [line.replace("timestamp:","") for line in lines if "timestamp" in line]
    lines = get_lines()
    for i, line in enumerate(lines):        
        copy_line = line.replace("timestamp:","")
        start_hour, start_minute, start_sec = copy_line.split(":")

        # TODO: Start und Endzeiten anpassen!
        if int(start_sec) > 5:
            start_sec = f"{ext(int(start_sec)-5)}"
        else:
            start_sec = str(50)
            if int(start_hour) == 1 and int(start_minute) == 0:
                start_hour = "00"
                start_minute = f"59"
            else:
                start_minute = f"{ext(int(start_minute)-1)}"

        if i == len(lines)-1:
            prompt, prompt_ls = test_open_ai.load_lecture_part(start_hour, start_minute, start_sec)
        else:
            end_line = lines[i+1].replace("timestamp:","")
            end_hour, end_minute, end_sec = end_line.split(":")

            if int(end_sec) < 50:
                end_sec = f"{int(end_sec)+2}"
            else:
                end_sec = "00"
                if int(end_minute) == 59:
                    end_minute = "00"
                    end_hour = "01"
                else:
                    end_minute = f"{int(end_minute)+1}"

            prompt, prompt_ls = test_open_ai.load_lecture_part(start_hour, start_minute, start_sec, end_hour = end_hour, end_minute = end_minute, end_sec= end_sec)

        if prompt_ls != None:
            response_ls = []
            for prmpt in prompt_ls:
                # print("--------- Prompt -------------")
                # print(prmpt)
                messages = gpt.update_chat(messages,"user", prmpt)
                response = gpt.ask_gpt(messages)
                response_ls.append(response)
                messages = gpt.update_chat(messages,"system",response)
            response = "\n".join(response_ls)
            # print("--------- Responce -------------")
            # print(response)
            
            with open("summary.md", "r") as f:
                data = f.read()
            # data = data.replace(line, f"{line}\nTest\n")
            data = data.replace(line, f"{line}\n\n{response}\n")
            with open("summary.md", "w") as f:
                f.write(data)

    # hour, minute, sec = lines[1].split(":")
    # hour2, minute2, sec2 = lines[2].split(":")
    # print(lines[1].split(":"))
    # print(lines[2].split(":"))

    # lecture_part = test_open_ai.load_lecture_part(hour, minute, sec, end_hour = hour2, end_minute = minute2, end_sec= sec2)
    # print(lecture_part)


    #     elif end_hour != "":
    #         prompt, prompt_ls = load_lecture_part(hour,minute,sec, end_hour=end_hour, end_minute= end_minute, end_sec= end_sec)
    #     else:
    #         prompt, prompt_ls = load_lecture_part(hour,minute,sec)

    #     if end_hour != "q":
    #         if prompt_ls == None:
    #             messages = update_chat(messages,"user", prompt)
    #             response = ask_gpt(messages)
    #             messages = update_chat(messages,"system",response)
    #             # Kopiere den String in die Clipboard
    #         else:
    #             response_ls = []
    #             for prmpt in prompt_ls:
    #                 print(prmpt)
    #                 messages = update_chat(messages,"user", prmpt)
    #                 response = ask_gpt(messages)
    #                 response_ls.append(response)
    #                 messages = update_chat(messages,"system",response)
    #             response = "\n".join(response_ls)


if __name__ == "__main__":
    # start_hour = "00"
    # start_minute = "07" 
    # start_sec = "46"

    # end_hour = "00"
    # end_minute = "08"
    # end_sec = "02"
    # prompt, prompt_ls = test_open_ai.load_lecture_part(start_hour, start_minute, start_sec, end_hour = end_hour, end_minute = end_minute, end_sec= end_sec)
    main()
