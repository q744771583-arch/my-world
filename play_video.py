# -*- coding: utf-8 -*-
"""
PyCharm 弹窗播放视频脚本
用法：直接在 PyCharm 里右键 Run 即可，会弹出一个窗口自动播放视频（带声音）。

依赖安装（PyCharm 终端执行一次）：
    pip install opencv-python pillow
"""

import os
import sys
import threading
import tkinter as tk
import wave

import cv2
import winsound  # Python 自带，Windows 播放 wav

# ========== 配置 ==========
# 默认播放与本脚本同目录下的视频；也可以改成你自己的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_PATH = os.path.join(BASE_DIR, "video/去水印视频.mp4")
AUDIO_PATH = os.path.join(BASE_DIR, "video/去水印视频音频.wav")

WINDOW_TITLE = "视频播放器"
LOOP_PLAY = True   # True = 循环播放；False = 播完一遍自动关闭
WINDOW_SCALE = 1.0  # 窗口缩放，视频是 720x720，如觉得大可改成 0.8


def play_audio_loop():
    """在子线程里循环播放音频"""
    while True:
        try:
            # SND_FILENAME + SND_ASYNC：异步播放 wav 文件
            winsound.PlaySound(AUDIO_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC)
            # 阻塞等这段音频播完再循环（读出 wav 时长）
            with wave.open(AUDIO_PATH, "rb") as w:
                duration = w.getnframes() / w.getframerate()
            import time
            time.sleep(duration)
        except Exception as e:
            print("音频播放出错：", e)
            break
        if not LOOP_PLAY:
            break


def main():
    if not os.path.exists(VIDEO_PATH):
        print("找不到视频文件：", VIDEO_PATH)
        sys.exit(1)

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print("无法打开视频文件")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    delay = int(1000 / fps)  # 每帧间隔（毫秒）

    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.resizable(False, False)
    root.attributes("-topmost", True)  # 置顶显示，方便观察
    root.attributes("-topmost", False)

    label = tk.Label(root, bg="black")
    label.pack()

    playing = {"stopped": False}

    def show_frame():
        if playing["stopped"]:
            return
        ret, frame = cap.read()
        if not ret:
            if LOOP_PLAY:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 回到开头，循环
                root.after(delay, show_frame)
            else:
                playing["stopped"] = True
                cap.release()
                root.destroy()
            return
        # BGR -> RGB，交给 tkinter 显示
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if WINDOW_SCALE != 1.0:
            h, w = frame.shape[:2]
            frame = cv2.resize(frame, (int(w * WINDOW_SCALE), int(h * WINDOW_SCALE)))
        from PIL import Image, ImageTk
        img = ImageTk.PhotoImage(image=Image.fromarray(frame))
        label.configure(image=img)
        label.image = img  # 防止被垃圾回收
        root.after(delay, show_frame)

    # 启动音频线程
    if os.path.exists(AUDIO_PATH):
        threading.Thread(target=play_audio_loop, daemon=True).start()
    else:
        print("提示：未找到音频文件，将静音播放")

    show_frame()
    root.mainloop()

    if not LOOP_PLAY:
        cap.release()


if __name__ == "__main__":
    main()
