import time
import customtkinter as ct
import PIL.Image
import datetime
import openai
import tkinter.scrolledtext as ScrolledText
from tkinter import *
import pyttsx3
import speech_recognition as sr
import os
from requests import get
import wikipedia
import webbrowser
import threading
import librosa
import soundfile
import numpy as np
import pickle
import tempfile
from time import sleep
import mysql.connector
import sklearn.model_selection
import sklearn.neural_network
import sklearn.metrics

# setting chatgpt
openai.api_key = 'OPENAI-API-KEY'
messages = [
    {"role": "system", "content": "You are a kind helpful assistant."},
]

# setting color scheme
default_light = "#a3cfcf"
default_dark = "#3857e0"
ct.set_appearance_mode("light")
ct.set_default_color_theme("blue")

red_light = "#fca5a2"
red_dark = "#fc0e05"
blue_light = "#a3cfcf"
blue_dark = "#3857e0"
yellow_light = "#fafca4"
yellow_dark = "#d3d61e"
green_light = "#77fa73"
green_dark = "#0b7a01"
pink_light = "#fccff8"
pink_dark = "#fc03c1"
purple_light = "#dcadff"
purple_dark = "#a103fc"

# setting up voice
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.runAndWait()
r = sr.Recognizer()
r.pause_threshold = 1

# for storing emotion history
emotion_list = []

# get chatgpt response
def response(message):
    messages.append(
        {"role": "user", "content": message}
    )
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    reply = chat.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    return reply

# extracting speech features
def extract_feature(file_name, mfcc, chroma, mel):
   with soundfile.SoundFile(file_name) as sound_file:
       X = sound_file.read(dtype="float32")
       sample_rate=sound_file.samplerate
       if chroma:
           stft=np.abs(librosa.stft(X))
       result=np.array([])
       if mfcc:
           mfccs=np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)
           result=np.hstack((result, mfccs))
       if chroma:
           chroma=np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)
           result=np.hstack((result, chroma))
       if mel:
           mel=np.mean(librosa.feature.melspectrogram(y=X, sr=sample_rate).T,axis=0)
           result=np.hstack((result, mel))
   return result

# Load the trained model for speech emotion recognition
def load_emotion_model():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, 'model1.pkl')
    #model_path = "model1.pkl"  # Replace with the actual path
    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)
    return model

emotion_model = load_emotion_model()

# Function to predict emotion from user's voice input
def predict_emotion(audio_data):
   feature = extract_feature(audio_data, mfcc=True, chroma=True, mel=True)
   emotion = emotion_model.predict([feature])[0]
   return emotion

def set_text(e, text):
    e.delete(0,END)
    e.insert(0,text)
    return

def listen(mic, listening, hourglass, photo, emotion_label, entry, ChatLog, usrnme):
    global query
    with sr.Microphone() as source:
        photo.configure(image=listening)
        audio = r.listen(source, phrase_time_limit=5)
    try:
        photo.configure(image=hourglass)
        query = r.recognize_google(audio, language="en-in")
        print("log: recognized")
        #query_label.configure(text=f"User said: {query}")
        set_text(entry, query)
        enter_thread(entry, ChatLog, photo.cget("bg_color"))
        print("log: enter function done")

        # Convert audio frame_data to NumPy array of int16
        audio_data = np.frombuffer(audio.frame_data, dtype=np.int16)

        # Save the audio data as a temporary WAV file
        temp_wav_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        soundfile.write(temp_wav_path, audio_data, audio.sample_rate)
        predicted_emotion = predict_emotion(temp_wav_path)
        sleep(4)
        # Creating connection object
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="test1",
            autocommit=True
        )
        cursor = mydb.cursor()
        cursor.execute("use projectdb;")
        if predicted_emotion:
            emotion_list.append(predicted_emotion)
            print(emotion_list)
            # emo_string = ",".join(emotion_list)
            emo_string = ", " + emotion_list[-1]
            #emo_query = "select emotions from logindata ORDER BY id DESC LIMIT 1;"
            emo_query = f"select emotions from logindata where username='{usrnme}';"
            cursor.execute(emo_query)
            print("1")
            value = cursor.fetchone()
            print("2")
            full_string = value[0] + emo_string
            print(full_string)
            if len(full_string)>230:
                full_string = full_string[10:]
            update_query = f"update logindata set emotions='{full_string}' where username='{usrnme}';"
            cursor.execute(update_query)
            print("3")
            emotion_label.configure(text="Emotion: "+predicted_emotion)
            print(f"Emotion: {predicted_emotion}")


        else:
            set_text(emotion_label, "Not Recognized")
            print("Not Recognized")

        # Clean up temporary audio file
        os.remove(temp_wav_path)
        photo.configure(image=mic)

        return query
    except Exception as e:
        print("Exception.")
        photo.configure(image=mic)


# seperate thread for listening
def listen_thread(mic, listening, hourglass, photo, emotion_label, entry, ChatLog, usrnme):
    thread1 = threading.Thread(target=lambda:listen(mic, listening, hourglass, photo, emotion_label, entry, ChatLog, usrnme))
    thread1.start()

# bot speak
def speak(audio):
   print(audio)
   engine.say(audio)
   engine.runAndWait()

# splash screen
def intro():
    root = ct.CTk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    splash_width = 400
    splash_height = 200
    x = (screen_width - splash_width) // 2
    y = (screen_height - splash_height) // 2
    root.geometry(f"{splash_width}x{splash_height}+{x}+{y}")
    root.overrideredirect(True)
    frame = ct.CTkFrame(root, width=splash_width, height=splash_height)
    frame.pack()
    img = ct.CTkImage(PIL.Image.open("images//splash.png"), size=(splash_width, splash_height))
    label = ct.CTkLabel(master=frame, image=img, text='')
    label.pack()
    root.after(5000, lambda: main_win(root))
    root.mainloop()

# clear gui
def clear_frame(root):
   for widgets in root.winfo_children():
      widgets.destroy()

# guest, login, signup screen
def main_win(root):
    clear_frame(root)
    root.configure(bg_color=default_light)

    root.overrideredirect(False)
    root.title("Speech Emotion Recognition Software")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")
    root.wm_state("zoomed")

    root_frame = ct.CTkFrame(master=root, bg_color=default_light, fg_color=default_light)
    root_frame.pack(fill="both", expand=True)

    frame = ct.CTkFrame(master=root_frame, bg_color=default_light, fg_color=default_light)
    frame.pack(pady=140, padx=150, fill="both", expand=True)

    guest_frame = ct.CTkFrame(master=frame, bg_color=default_light, fg_color=default_light)
    guest_frame.pack(pady=5, padx=45, side=ct.LEFT)

    guest_img = ct.CTkImage(PIL.Image.open("images//guest.png"), size=(250, 250))
    guest_btn = ct.CTkButton(master=guest_frame, image=guest_img, command=lambda: guest(root), text='', bg_color=default_dark, fg_color=default_dark)
    guest_btn.pack(pady=5, side=ct.TOP)

    guest_label = ct.CTkLabel(master=guest_frame, text="Guest", font=("", 36), bg_color=default_light, fg_color=default_light)
    guest_label.pack(pady=5, side=ct.TOP)

    signin_frame = ct.CTkFrame(master=frame, bg_color=default_light, fg_color=default_light)
    signin_frame.pack(pady=5, padx=45, side=ct.LEFT)

    signin_img = ct.CTkImage(PIL.Image.open("images//login.png"), size=(250, 250))
    signin_btn = ct.CTkButton(master=signin_frame, image=signin_img, command=lambda: signin(root), text='', bg_color=default_dark, fg_color=default_dark)
    signin_btn.pack(pady=5, side=ct.TOP)

    signin_label = ct.CTkLabel(master=signin_frame, text="Sign in", font=("", 36), bg_color=default_light, fg_color=default_light)
    signin_label.pack(pady=5, side=ct.TOP)

    signup_frame = ct.CTkFrame(master=frame, bg_color=default_light, fg_color=default_light)
    signup_frame.pack(pady=5, padx=45, side=ct.LEFT)

    signup_img = ct.CTkImage(PIL.Image.open("images//signup.png"), size=(250, 250))
    signup_btn = ct.CTkButton(master=signup_frame, image=signup_img, command=lambda: signup(root), text='', bg_color=default_dark, fg_color=default_dark)
    signup_btn.pack(pady=5, side=ct.TOP)

    signup_label = ct.CTkLabel(master=signup_frame, text="Sign up", font=("", 36), bg_color=default_light, fg_color=default_light)
    signup_label.pack(pady=5, side=ct.TOP)

# chat scroller update
def scroll_to_bottom(frame):
    frame.yview(ct.END)

# guest mode
def guest(root, usrnme="rehmah"):
    clear_frame(root)
    root.configure(background=default_light)

    # Calculate the desired heights based on the 30:50:20 ratio
    total_width = root.winfo_screenwidth()
    total_height = root.winfo_screenheight()
    profile_width = (20 / 100) * total_width
    main_width = (60 / 100) * total_width
    ins_width = (20 / 100) * total_width

    global profile_frame
    global photo_frame
    global photo_label
    global name_label
    global data_frame
    global ins_frame

    profile_frame = ct.CTkFrame(master=root, width=profile_width, bg_color=default_light, fg_color=default_light)
    profile_frame.pack(fill="y", expand=False, side=ct.LEFT)

    photo_frame = ct.CTkFrame(master=profile_frame, width=profile_width-6, height=(40 / 100) * total_height, bg_color=default_light, fg_color=default_light)
    photo_frame.pack(pady=2, expand=False, side=ct.TOP)

    img = ct.CTkImage(PIL.Image.open("images//guest.png"), size=(250, 250))
    photo_label = ct.CTkLabel(master=photo_frame, image=img, text='')
    photo_label.pack(pady=5, side=ct.TOP)
    name_label = ct.CTkLabel(master=photo_frame, text="Mr Guest", font=('', 36))
    name_label.pack(side=ct.TOP)

    data_frame = ct.CTkFrame(master=profile_frame, width=profile_width-6, height=(35 / 100) * total_height, bg_color=default_light, fg_color=default_light)
    data_frame.pack(pady=2, expand=False, side=ct.TOP)

    text1 = "\nTo get emotion history\nand average mood\n"
    text1_label = ct.CTkLabel(master=data_frame, text=text1, font=('', 20))
    text1_label.pack()

    #signin_link = Label(master=data_frame, text="Sign In", font=('', 20), fg=default_dark, bg=default_light, cursor="hand2", underline=True)
    #signin_link.pack()
    #signin_link.bind("<Button-1>", lambda e:
    #signin(root))

    signin_link = ct.CTkButton(master=data_frame, text="Sign In", font=('', 20), fg_color=default_dark, bg_color=default_light, command=lambda:signin(root))
    signin_link.pack()

    text2_label = ct.CTkLabel(master=data_frame, text="\nor\n", font=('', 20))
    text2_label.pack()

    #signup_link = Label(master=data_frame, text="Sign Up", font=('', 20), fg=default_dark, bg=default_light, cursor="hand2", underline=True)
    #signup_link.pack()
    #signup_link.bind("<Button-1>", lambda e:
    #signup(root))

    signin_link = ct.CTkButton(master=data_frame, text="Sign Up", font=('', 20), fg_color=default_dark, bg_color=default_light,
                               command=lambda: signup(root))
    signin_link.pack()

    info_frame = ct.CTkFrame(master=profile_frame, width=profile_width-6, height=(20 / 100) * total_height, bg_color=default_light, fg_color=default_light)
    info_frame.pack(pady=2, expand=False, side=ct.BOTTOM)

    dt = datetime.datetime.now()
    date_label = ct.CTkLabel(master=info_frame, text=dt.strftime("%d / %m / %Y %a"), font=('', 20), bg_color=default_light)
    date_label.pack(pady=5, side=ct.BOTTOM)

    time_label = ct.CTkLabel(master=info_frame, text=dt.strftime("%I:%M %p"), font=('', 20), bg_color=default_light)
    time_label.pack(pady=5, side=ct.BOTTOM)

    def time():
        dt = datetime.datetime.now()
        time_str = dt.strftime('%H:%M:%S %p')
        #date_str = dt.strftime("%d / %m / %Y %a")
        time_label.configure(text=time_str)
        #date_label.configure(text=date_str)
        time_label.after(1000, time)
        #date_label.after(1000, time)

    time_thread = threading.Thread(target=time)
    time_thread.start()

    main_frame = ct.CTkFrame(master=root, width=main_width, bg_color=default_light, fg_color=default_light)
    main_frame.pack(fill="both", expand=True, side=ct.LEFT)

    btn_frame = ct.CTkFrame(master=main_frame, bg_color=default_light, fg_color=default_light)
    btn_frame.pack(pady=5, fill="x", expand=False, side=ct.TOP)

    speak_btn = ct.CTkButton(master=btn_frame, command=lambda: listen_thread(mic, listening, hourglass, m_label, emotion_label, entry, ChatLog, usrnme), text='Speak', font=('', 40), width=(25/100)*main_width, height=140, bg_color=default_dark, fg_color=default_dark)
    speak_btn.pack(pady=5, padx=5, side=ct.LEFT)

    state_frame = ct.CTkFrame(master=btn_frame, width=(20/100)*main_width, height=140, bg_color=default_light, fg_color=default_light)
    state_frame.pack(pady=5, side=ct.LEFT)

    mic = ct.CTkImage(PIL.Image.open("images//mic.png"), size=((20/100)*main_width, 140))
    listening = ct.CTkImage(PIL.Image.open("images//listening.png"), size=((20 / 100) * main_width, 140))
    hourglass = ct.CTkImage(PIL.Image.open("images//hourglass.png"), size=((20 / 100) * main_width, 140))
    m_label = ct.CTkLabel(master=state_frame, image=mic, text='')
    m_label.pack()

    query_frame = ct.CTkFrame(master=btn_frame, width=(55/100)*main_width, height=140)
    query_frame.pack(pady=5, padx=2, side=ct.LEFT)

    emotion_label = ct.CTkLabel(master=query_frame, width=(55/100)*main_width-10, height=140, text="Emotion: ", font=('Terminal', 36), bg_color=default_light)
    emotion_label.pack()

    chat_frame = ct.CTkFrame(master=main_frame, height=450, bg_color=default_light, fg_color=default_light)
    chat_frame.pack(pady=5, fill="x", expand=True)

    ChatLog = ScrolledText.ScrolledText(chat_frame, bd=0, bg="white", height="8", width="50", font="Arial")
    ChatLog.config(state=DISABLED)
    ChatLog.place(height=450, width=main_width)

    type_frame = ct.CTkFrame(master=main_frame, height=100, bg_color=default_light, fg_color=default_light)
    type_frame.pack(pady=5, fill="x", expand=False, side=ct.BOTTOM)

    entry = ct.CTkEntry(master=type_frame, width=(80/100)*main_width, height=90, font=('', 18))
    entry.pack(pady=5, padx=2, side=ct.LEFT)

    def event_handle(event):
        if event.keysym == "Return":
            enter_thread(entry, ChatLog, chat_frame.cget("bg_color"))
    root.bind('<KeyRelease>', event_handle)

    enter_btn = ct.CTkButton(master=type_frame, command=lambda: enter_thread(entry, ChatLog, chat_frame.cget("bg_color")), text='Enter', font=('', 22), width=(20/100)*main_width, height=90, bg_color=default_dark, fg_color=default_dark)
    enter_btn.pack(pady=5, side=ct.LEFT)

    ins_frame = ct.CTkFrame(master=root, width=ins_width, bg_color=default_light, fg_color=default_light)
    ins_frame.pack(fill="y", expand=False, side=ct.LEFT)
    #ins_frame.pack(pady=10, side=ct.TOP)

    #logout = ct.CTkButton(master=ins_frame, text="Log Out", bg_color=default_dark, command=lambda:main_win(root))
    #logout.pack(pady=10, side=ct.TOP)

    color_frame = ct.CTkFrame(master=ins_frame, width=ins_width, bg_color=default_light, fg_color=default_light)
    color_frame.pack(pady=10, side=ct.BOTTOM)

    instructions = "Hey There!\n\n\nChat via voice or text.\nAsk anything!\n\nVoice chat introduces you to\nSpeech Emotion Recognition\n(SER)\n\nCheck out what emotion you\nsound like to AI.\n\nEmotion history tracks your\nhistory of detected emotions\n& evaluates your average mood.\n\n\n\nNote: The emotions detected\nare not always accurate.\nAccuracy may vary due to\nbackground noise, mic\nquality or perception error."
    ins_label = ct.CTkLabel(master=ins_frame, text=instructions, font=('', 20), width=ins_width)
    ins_label.pack(fill="y", expand=True, side=ct.BOTTOM)

    c_width = (15 / 100) * ins_width

    def all_children(root, finList=None, indent=0):
        finList = finList or []
        #print(f"{'   ' * indent}{root=}")
        children = root.winfo_children()
        for item in children:
            finList.append(item)
            all_children(item, finList, indent + 1)
        return finList

    #print(finList)
    def color_set(light, dark):
        finList = all_children(root)
        for child in finList:
            if type(child) is ct.CTkLabel:
                child.configure(bg_color=light, fg_color=light, text_color="black")
            elif type(child) is ct.CTkFrame:
                child.configure(bg_color=light, fg_color=light)
            elif type(child) is ct.CTkButton:
                if len(child.cget("text"))!=0:
                    child.configure(bg_color=dark, fg_color=dark, hover_color=dark)
            elif type(child) is ScrolledText.ScrolledText:
                if child != ChatLog:
                    child.config(bg=light)
                    scroll=False
        return light, dark
    red = ct.CTkButton(master=color_frame, width=c_width, height=c_width, bg_color=red_dark, fg_color=red_dark, hover_color=red_dark, text="", command=lambda: color_set(red_light, red_dark))
    red.pack(side=ct.LEFT)

    blue = ct.CTkButton(master=color_frame, width=c_width, height=c_width, bg_color=blue_dark, fg_color=blue_dark, text="", hover_color=blue_dark,  command=lambda: color_set(blue_light, blue_dark))
    blue.pack(side=ct.LEFT)

    yellow = ct.CTkButton(master=color_frame, width=c_width, height=c_width, bg_color=yellow_dark, fg_color=yellow_dark, text="", hover_color=yellow_dark,  command=lambda: color_set(yellow_light, yellow_dark))
    yellow.pack(side=ct.LEFT)

    green = ct.CTkButton(master=color_frame, width=c_width, height=c_width, bg_color=green_dark, fg_color=green_dark, text="", hover_color=green_dark,  command=lambda: color_set(green_light, green_dark))
    green.pack(side=ct.LEFT)

    pink = ct.CTkButton(master=color_frame, width=c_width, height=c_width, bg_color=pink_dark, fg_color=pink_dark, text="", hover_color=pink_dark,  command=lambda: color_set(pink_light, pink_dark))
    pink.pack(side=ct.LEFT)

    purple = ct.CTkButton(master=color_frame, width=c_width, height=c_width, bg_color=purple_dark, fg_color=purple_dark, text="", hover_color=purple_dark,  command=lambda: color_set(purple_light, purple_dark))
    purple.pack(side=ct.LEFT)

def enter_thread(typespace, chatspace, light_color):
    thread3 = threading.Thread(target=lambda: enter(typespace, chatspace, light_color))
    thread3.start()
# chat message update
def enter(typespace, chatspace, light_color):
    user_msg = typespace.get()
    typespace.delete(0, ct.END)
    bot_response = exec_query(user_msg.lower())
    speak_thread = threading.Thread(target=lambda: speak(bot_response))
    speak_thread.start()
    i = 0
    for letter in range(0, len(bot_response)):
        i += 80
        bot_response = "".join((bot_response[:i], "\n", bot_response[i:]))
    bot_response = bot_response.strip()

    for letter in range(0, len(user_msg)):
        i += 80
        user_msg = "".join((user_msg[:i], "\n", user_msg[i:]))
    user_msg = user_msg.strip()

    chatspace.tag_configure('tag-right', justify='right')
    chatspace.tag_configure('tag-left', justify='left')

    chatspace.config(state=ct.NORMAL)

    frame1 = ct.CTkFrame(chatspace, bg_color=light_color, fg_color=light_color)
    ct.CTkLabel(frame1, text=user_msg,
          font=("Arial", 18),
          bg_color=light_color).grid(row=0, column=0, sticky="e", padx=5, pady=5)
    ct.CTkLabel(frame1, text=datetime.datetime.now().strftime("%H:%M"),
          font=("Arial", 10),
          bg_color=light_color).grid(row=1, column=0, sticky="e")

    frame2 = ct.CTkFrame(chatspace, bg_color=light_color, fg_color=light_color)
    ct.CTkLabel(
        frame2,
        text=bot_response,
        font=("Arial", 18),
        bg_color=light_color).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    ct.CTkLabel(
        frame2,
        text=datetime.datetime.now().strftime("%H:%M"),
        font=("Arial", 10),
        bg_color=light_color).grid(row=1, column=0, sticky="w")

    chatspace.insert('end', '\n ', 'tag-right')
    chatspace.window_create('end', window=frame1)

    chatspace.insert('end', '\n', 'tag-left')
    chatspace.window_create('end', window=frame2)

    chatspace.config(state=ct.DISABLED)
    scroll_to_bottom(chatspace)  # Scroll to the bottom after adding a message

def exec_query(query):
    if "open notepad" in query:
        npath = "C:\\Windows\\system32\\notepad"
        os.startfile(npath)
        result = "anything else?"
        return result
    elif "open command prompt" in query:
        os.system("start cmd")
        result = "anything else?"
        return result
    elif "ip address" in query:
        ip = get("http://api.ipify.org").text
        result = f"your IP address is {ip}\nanything else?"
        return result
    elif "wikipedia" in query:
        query = query.replace("wikipedia", "")
        result = wikipedia.summary(query, sentences=2)
        result = f"according to wikipedia...{result}\nanything else?"
        return result
    elif "open youtube" in query:
        webbrowser.open("www.youtube.com")
        result = "anything else?"
        return result
    elif "no thanks" in query:
        result = "thanks for using me, have a good day"
        return result
    else:
        result = response(query)
        return result
def signin(root):
    clear_frame(root)
    root.configure(bg_color=default_light, fg_color=default_light)

    main_frame = ct.CTkFrame(master=root, bg_color="white", fg_color="white")
    main_frame.pack(pady=80, padx=150, fill="both", expand=True, side=ct.TOP)

    button_frame = ct.CTkFrame(master=main_frame, bg_color="white", fg_color="white")
    button_frame.pack(pady=12, padx=10, fill="x", side=ct.TOP)

    back_button = ct.CTkButton(master=button_frame, text="<-", font=("", 48), width=20, bg_color="white", fg_color="white", text_color="black", hover_color=default_light, command=lambda: main_win(root))
    back_button.pack(side=ct.LEFT)

    heading_label = ct.CTkLabel(master=main_frame, text="Sign In", font=("", 64))
    heading_label.pack(pady=12, padx=10, side=ct.TOP)

    username = ct.CTkEntry(master=main_frame, placeholder_text="Username", width=300, height=50, font=("", 26))
    username.pack(pady=12, padx=10, side=ct.TOP)

    password = ct.CTkEntry(master=main_frame, placeholder_text="Password", width=300, height=50, font=("", 26),
                           show="*")
    password.pack(pady=12, padx=10, side=ct.TOP)

    def toggle_password():
        if password.cget('show') == '':
            password.configure(show='*')
        else:
            password.configure(show='')

    show_hide = Label(master=main_frame, text="Show/Hide password", font=('', 12), fg="blue", bg="white",
                      cursor="hand2", underline=True)
    show_hide.pack(side=ct.TOP)
    show_hide.bind("<Button-1>", lambda e:
    toggle_password())

    def validation():
        usrnme = username.get()
        pswd = password.get()
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="test1",
            autocommit=True
        )
        cursor = mydb.cursor()
        cursor.execute("use projectdb;")

        check_user = f"select username from logindata where binary username='{usrnme}';"
        cursor.execute(check_user)
        u = cursor.fetchone()
        if u:
            u = u[0]
            check_pass = f"select password from logindata where binary username='{u}';"
            cursor.execute(check_pass)
            p = cursor.fetchone()
            p = p[0]
            if p==pswd:
                get_pic = f"select picture from logindata where binary username='{u}';"
                cursor.execute(get_pic)
                picture = cursor.fetchone()
                picture = picture[0]
                picture = picture
                profile_program(root, usrnme, picture)
            else:
                message.configure(text="Incorrect password")
        else:
            message.configure(text="Invalid User")

    signin_button = ct.CTkButton(master=main_frame, text="Sign in", command=validation, width=200, height=50, font=("", 26), bg_color=default_dark, fg_color=default_dark)
    signin_button.pack(pady=12, padx=10, side=ct.TOP)

    message = ct.CTkLabel(master=main_frame, text="", font=('', 12), fg_color="white", bg_color="white", text_color="red")
    message.pack(pady=12, padx=10, side=ct.TOP)

def signup(root):
    clear_frame(root)
    root.configure(bg_color=default_light, fg_color=default_light)

    def photo():

        usrnme = username.get()
        pswd = password.get()

        if len(usrnme) == 0 or len(pswd) == 0:
            message.configure(text="Username and Password cannot be blank!")
        else:
            clear_frame(root)
            root.configure(bg_color=default_light, fg_color=default_light)

            # Create StringVar to store the selected image path
            p_selected = StringVar(root, "1")

            main_frame = ct.CTkFrame(master=root, bg_color="white", fg_color="white")
            main_frame.pack(pady=80, padx=150, fill="both", expand=True)

            male_frame = ct.CTkFrame(master=main_frame, bg_color="white", fg_color="white")
            male_frame.pack(pady=10, side="top")

            female_frame = ct.CTkFrame(master=main_frame, bg_color="white", fg_color="white")
            female_frame.pack(pady=10, side="top")

            # Create radio buttons with images
            pf1 = ct.CTkFrame(master=male_frame, width=100, height=200, bg_color="white", fg_color="white")
            pf1.pack(side=ct.LEFT)
            p1 = ct.CTkImage(PIL.Image.open("images//m1.png"), size=(150, 150))
            p1_label = ct.CTkLabel(master=pf1, image=p1, text="")
            p1_label.pack(side=ct.TOP)
            photo_1 = ct.CTkRadioButton(master=pf1, variable=p_selected, text="", value="images//m1.png")
            photo_1.pack(side=ct.TOP)

            pf2 = ct.CTkFrame(master=male_frame, width=100, height=200, bg_color="white", fg_color="white")
            pf2.pack(side=ct.LEFT)
            p2 = ct.CTkImage(PIL.Image.open("images//m2.png"), size=(150, 150))
            p2_label = ct.CTkLabel(master=pf2, image=p2, text="")
            p2_label.pack(side=ct.TOP)
            photo_2 = ct.CTkRadioButton(master=pf2, variable=p_selected, text="", value="images//m2.png")
            photo_2.pack(side=ct.TOP)

            pf3 = ct.CTkFrame(master=male_frame, width=100, height=200, bg_color="white", fg_color="white")
            pf3.pack(side=ct.LEFT)
            p3 = ct.CTkImage(PIL.Image.open("images//m3.png"), size=(150, 150))
            p3_label = ct.CTkLabel(master=pf3, image=p3, text="")
            p3_label.pack(side=ct.TOP)
            photo_3 = ct.CTkRadioButton(master=pf3, variable=p_selected, text="", value="images//m3.png")
            photo_3.pack(side=ct.TOP)

            pf4 = ct.CTkFrame(master=male_frame, width=100, height=200, bg_color="white", fg_color="white")
            pf4.pack(side=ct.LEFT)
            p4 = ct.CTkImage(PIL.Image.open("images//m4.png"), size=(150, 150))
            p4_label = ct.CTkLabel(master=pf4, image=p4, text="")
            p4_label.pack(side=ct.TOP)
            photo_4 = ct.CTkRadioButton(master=pf4, variable=p_selected, text="", value="images//m4.png")
            photo_4.pack(side=ct.TOP)

            pf5 = ct.CTkFrame(master=female_frame, width=100, height=200, bg_color="white", fg_color="white")
            pf5.pack(side=ct.LEFT)
            p5 = ct.CTkImage(PIL.Image.open("images//f1.png"), size=(150, 150))
            p5_label = ct.CTkLabel(master=pf5, image=p5, text="")
            p5_label.pack(side=ct.TOP)
            photo_5 = ct.CTkRadioButton(master=pf5, variable=p_selected, text="", value="images//f1.png")
            photo_5.pack(side=ct.TOP)

            pf6 = ct.CTkFrame(master=female_frame, width=100, height=200, bg_color="white", fg_color="white")
            pf6.pack(side=ct.LEFT)
            p6 = ct.CTkImage(PIL.Image.open("images//f2.png"), size=(150, 150))
            p6_label = ct.CTkLabel(master=pf6, image=p6, text="")
            p6_label.pack(side=ct.TOP)
            photo_6 = ct.CTkRadioButton(master=pf6, variable=p_selected, text="", value="images//f2.png")
            photo_6.pack(side=ct.TOP)

            pf7 = ct.CTkFrame(master=female_frame, width=100, height=200, bg_color="white", fg_color="white")
            pf7.pack(side=ct.LEFT)
            p7 = ct.CTkImage(PIL.Image.open("images//f3.png"), size=(150, 150))
            p7_label = ct.CTkLabel(master=pf7, image=p7, text="")
            p7_label.pack(side=ct.TOP)
            photo_7 = ct.CTkRadioButton(master=pf7, variable=p_selected, text="", value="images//f3.png")
            photo_7.pack(side=ct.TOP)

            pf8 = ct.CTkFrame(master=female_frame, width=100, height=200, bg_color="white", fg_color="white")
            pf8.pack(side=ct.LEFT)
            p8 = ct.CTkImage(PIL.Image.open("images//f4.png"), size=(150, 150))
            p8_label = ct.CTkLabel(master=pf8, image=p8, text="")
            p8_label.pack(side=ct.TOP)
            photo_8 = ct.CTkRadioButton(master=pf8, variable=p_selected, text="", value="images//f4.png")
            photo_8.pack(side=ct.TOP)

            proceed_frame = ct.CTkFrame(master=main_frame, bg_color="white", fg_color="white")
            proceed_frame.pack(pady=10, side="top")

            proceed_button = ct.CTkButton(master=proceed_frame, text="Proceed", font=("", 30), height=80, bg_color=default_dark, fg_color=default_dark,
                                          command=lambda: make_profile(root, usrnme, pswd, p_selected.get()))
            proceed_button.pack()

    main_frame = ct.CTkFrame(master=root, bg_color="white", fg_color="white")
    main_frame.pack(pady=80, padx=150, fill="both", expand=True, side=ct.TOP)

    button_frame = ct.CTkFrame(master=main_frame, bg_color="white", fg_color="white")
    button_frame.pack(pady=12, padx=10, fill="x", side=ct.TOP)

    back_button = ct.CTkButton(master=button_frame, text="<-", font=("", 48), width=20, bg_color="white",
                               fg_color="white", text_color="black", hover_color=default_light,
                               command=lambda: main_win(root))
    back_button.pack(side=ct.LEFT)

    heading_label = ct.CTkLabel(master=main_frame, text="Sign Up", font=("", 64))
    heading_label.pack(pady=12, padx=10)

    username = ct.CTkEntry(master=main_frame, placeholder_text="Username", width=300, height=50, font=("", 26))
    username.pack(pady=12, padx=10)

    password = ct.CTkEntry(master=main_frame, placeholder_text="Password", width=300, height=50, font=("", 26), show="*")
    password.pack(pady=12, padx=10)

    def toggle_password():
        if password.cget('show') == '':
            password.configure(show='*')
        else:
            password.configure(show='')

    show_hide = Label(master=main_frame, text="Show/Hide password", font=('', 12), fg=default_dark, bg="white", cursor="hand2", underline=True)
    show_hide.pack()
    show_hide.bind("<Button-1>", lambda e:
    toggle_password())

    signup_button = ct.CTkButton(master=main_frame, text="Sign up", command=photo, width=200, height=50, font=("", 26), bg_color=default_dark, fg_color=default_dark)
    signup_button.pack(pady=12, padx=10)

    message = ct.CTkLabel(master=main_frame, text="", font=('', 12), fg_color="white", bg_color="white",
                          text_color="red")
    message.pack(pady=12, padx=10, side=ct.TOP)

    #remember_state = ct.CTkCheckBox(master=main_frame, text="Remember me", width=200, height=50, font=("", 26))
    #remember_state.pack(pady=12, padx=10)

def make_profile(root, username, password, picture):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="test1",
        autocommit=True
    )
    cursor = db.cursor()
    query1 = "use projectdb;"
    cursor.execute(query1)
    query2 = f"insert into logindata(username, password, picture, emotions) values('{username}', '{password}', '{picture}', '');"
    #query2 = f"insert into logindata values('{username}', '{password}', '{picture}');"
    cursor.execute(query2)

    profile_program(root, username, picture)
def profile_program(root, username, picture):
    guest(root, username)
    logout = ct.CTkButton(master=ins_frame, text="Log Out", font=("", 24), bg_color=default_dark, command=lambda: main_win(root))
    logout.pack(pady=10, side=ct.TOP)
    p = ct.CTkImage(PIL.Image.open(picture), size=(150, 150))
    photo_label.configure(image=p)
    name_label.configure(text=username)
    clear_frame(data_frame)
    hist_label = ct.CTkLabel(master=data_frame, width=250, text="History", font=('', 24))
    hist_label.pack(pady=5, side=ct.TOP)
    hist_frame = ct.CTkFrame(master=data_frame, width=250, height=300, bg_color="white", fg_color="white")
    hist_frame.pack(pady=5, side=ct.TOP)
    emo_Log = ScrolledText.ScrolledText(hist_frame, bd=0, bg=default_light, height="8", width="50", font="Arial")
    #emo_Log.config(state=DISABLED)
    emo_Log.place(height=300, width=250)
    #emo_Log.pack(pady=5, side=ct.TOP)
    #emo_Log.tag_configure('tag-right', justify='right')
    log_frame = ct.CTkFrame(master=emo_Log, width=250, height=300, bg_color=default_light, fg_color=default_light)
    log_frame.pack()
    emo_hist = ct.CTkLabel(master=log_frame, width=250, height=300, text="", font=('Terminal', 16), bg_color=default_light, fg_color=default_light)
    emo_hist.pack(pady=5, side=ct.TOP)
    last_frame = ct.CTkFrame(master=emo_Log, width=250, height=10, bg_color=default_light, fg_color=default_light)
    last_frame.pack()
    emo_Log.insert('end', '\n ', 'tag-right')
    emo_Log.see(ct.END)
    emo_Log.window_create('end', window=log_frame)
    emo_Log.window_create('end', window=last_frame)
    scroll_to_bottom(emo_Log)
    emo_avg = ct.CTkLabel(master=data_frame, width=250, text="Average Mood: ", font=('', 22))
    emo_avg.pack(pady=5, side=ct.TOP)
    print(emo_Log.winfo_parent())

    def update_emo():
        while True:
            time.sleep(5)
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="test1",
                autocommit=True
            )
            cursor = mydb.cursor()
            cursor.execute("use projectdb;")
            emo_query = f"select emotions from logindata where username='{username}';"
            cursor.execute(emo_query)
            emo_tuple = cursor.fetchone()
            emo_str = emo_tuple[0]
            emo_list = emo_str.split(", ")
            average = avg_mood(emo_list)
            emo_avg.configure(text="Average Mood: "+average)
            #def avg(emo_list) returns avg mood
            emotions = emo_str.replace(", ", "\n\n")
            #emo_Log.config(state=ct.NORMAL)
            emo_hist.configure(text=emotions)
            mydb.close()
            #emo_Log.config(state=DISABLED)
            scroll_to_bottom(emo_Log)
    update_thread = threading.Thread(target=update_emo)
    update_thread.start()
    def avg_mood(emo_list):
        happy = emo_list.count("happy")
        sad = emo_list.count("sad")
        neutral = emo_list.count("neutral")
        angry = emo_list.count("angry")
        moods = {"Happy":happy, "Neutral":neutral, "Sad":sad, "Angry":angry}
        avg = max(zip(moods.values(), moods.keys()))[1]
        return avg
def main():
    intro()

main()
