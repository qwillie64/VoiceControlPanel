import pyaudio
import keyboard
import numpy as np
import tkinter as tk
from tkinter import ttk, font, messagebox
from playsound import playsound
from soundAdjuster import Adjuster

KEY = "f"
HINT = "Sound/hint.mp3"

PAD_X = 10
PAD_Y = 10


class Window:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Volume Controller")
        self.root.geometry("600x400")
        self.font = font.Font(family="Arial", size=10)
        self.running = False

        self.VOLUME_BOOSt = 0.0

        # 獲取音訊設備
        input_devices, output_devices = Adjuster.get_audio_devices()

        # 音訊輸入/輸出區
        devices_frame = tk.Frame(self.root)
        devices_frame.pack(padx=PAD_X, pady=PAD_Y)

        # 音訊輸入設備選單
        input_frame = tk.Frame(devices_frame)
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        input_label = tk.Label(input_frame, text="Input : ", font=self.font)
        input_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.input_box = ttk.Combobox(
            input_frame, values=input_devices, width=25, font=self.font
        )
        self.input_box.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # 音訊輸出設備選單
        output_frame = tk.Frame(devices_frame)
        output_frame.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        output_label = tk.Label(output_frame, text="Output : ", font=self.font)
        output_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.output_box = ttk.Combobox(
            output_frame, values=output_devices, width=25, font=self.font
        )
        self.output_box.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # 監聽測試
        monitor_frame = tk.LabelFrame(self.root, text="Monitor", font=self.font, pady=2)
        monitor_frame.pack(padx=PAD_X, pady=PAD_Y, fill="x")
        monitor_label = tk.Label(monitor_frame, text="Output : ", font=self.font)
        monitor_label.pack(side="left", padx=10)
        self.monitor_box = ttk.Combobox(
            monitor_frame, values=output_devices, width=40, font=self.font
        )
        self.monitor_box.pack(side="left")
        monitor_button = tk.Button(
            monitor_frame, text="Test", command=self.test, padx=10
        )
        monitor_button.pack(side="right", padx=10)

        def update_label(value):
            self.VOLUME_BOOSt = float(value)
            volume_value_label.config(text=f"{value}")

        # 音量增益滑桿
        volume_frame = tk.Frame(self.root)
        volume_frame.pack(padx=PAD_X, pady=PAD_Y)
        volume_label = tk.Label(volume_frame, text="Volume Boost : ", font=self.font)
        volume_label.pack(side="left", anchor="n")
        volume_scale = tk.Scale(
            volume_frame,
            from_=-50,
            to=50,
            orient="horizontal",
            length=300,
            tickinterval=25,
            showvalue=False,
            font=self.font,
            command=update_label,
        )
        volume_scale.pack(side="left")
        volume_value_label = tk.Label(volume_frame, text="0", width=10, font=self.font)
        volume_value_label.pack(side="left", anchor="n")
        self.check_var = tk.BooleanVar(value=True)
        volume_check = tk.Checkbutton(
            volume_frame, variable=self.check_var, font=self.font
        )
        volume_check.pack(side="left", anchor="n")

        # 開始按鈕
        start_button = tk.Button(
            self.root, text="Start", font=self.font, command=self.run, padx=10, pady=8
        )
        start_button.pack(side="bottom", anchor="se", padx=PAD_X, pady=PAD_Y)

        # 綁定按鍵事件
        self.__key_event()

        # 關閉視窗
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.running = False
            self.root.destroy()

    def show(self):
        print("Show windows...")
        self.root.mainloop()

    def run(self):
        print("Start running...")

        # 更新
        data_boost = {}
        data_boost["volume_boost"] = 1 + self.VOLUME_BOOSt / 10.0

        ad = Adjuster()
        ad.DATA_BOOST = data_boost
        ad.run(self.input_box.get(), self.output_box.get())

    def test(self):
        print("Start testing...")

        # 更新
        data_boost = {}
        data_boost["volume_boost"] = 1 + self.VOLUME_BOOSt / 10.0

        ad = Adjuster()
        ad.DATA_BOOST = data_boost
        ad.run(self.input_box.get(), self.monitor_box.get())

    def __key_event(self):

        def increase_font_size(event=None):
            new_size = self.font.cget("size") + 1
            self.font.configure(size=new_size)
            print(f"Increase font size : {new_size}")

        def decrease_font_size(event=None):
            new_size = self.font.cget("size") - 1
            if new_size >= 10:
                self.font.configure(size=new_size)
                print(f"Decrease font size : {new_size}")

        def state(event=None):
            if self.running:
                self.stop()
            else:
                self.run()

        self.root.bind_all("=", increase_font_size)
        self.root.bind_all("-", decrease_font_size)
        # self.root.bind_all("<Control-c>", state)


if __name__ == "__main__":
    window = Window()
    window.show()
