import threading
import time
import tkinter as tk
from tkinter import ttk, font
from soundAdjuster import Adjuster, DataPack

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
        self.AD = None

        # 獲取音訊設備
        input_devices, output_devices = Adjuster.get_audio_devices()

        default_input = None
        for i in range(0, len(input_devices)):
            if "Microphone" in input_devices[i]:
                default_input = i
                break

        default_output = None
        for i in range(0, len(output_devices)):
            if "Speaker" in output_devices[i]:
                default_output = i
                break

        # 音訊輸入/輸出區
        master_frame = tk.LabelFrame(self.root, text="Master", font=self.font)
        master_frame.pack(padx=PAD_X, pady=PAD_Y, fill="x")
        device_frame = tk.Frame(master_frame)
        device_frame.pack(side="left")

        # 音訊輸入設備選單
        input_frame = tk.Frame(device_frame)
        input_frame.pack(side='top', anchor="w")
        input_label = tk.Label(input_frame, text="Input : ", font=self.font)
        input_label.pack(side="left", padx=5, pady=5)
        self.input_box = ttk.Combobox(
            input_frame, values=input_devices, width=30, font=self.font
        )
        self.input_box.current(default_input)
        self.input_box.pack(side="left", padx=5, pady=5)

        # 音訊輸出設備選單
        output_frame = tk.Frame(device_frame)
        output_frame.pack(side="top", anchor="w")
        output_label = tk.Label(output_frame, text="Output : ", font=self.font)
        output_label.pack(side="left", padx=5, pady=5)
        self.output_box = ttk.Combobox(
            output_frame, values=output_devices, width=30, font=self.font
        )
        self.output_box.pack(anchor="n", padx=5, pady=5)

        # 音訊設備刷新
        refresh_button = tk.Button(
            master_frame, text="Refresh", font=self.font, padx=10
        )
        refresh_button.pack(side="right", anchor="sw", padx=5, pady=5)

        # 監聽測試
        monitor_frame = tk.LabelFrame(self.root, text="Monitor", font=self.font)
        monitor_frame.pack(padx=PAD_X, pady=PAD_Y, fill="x")
        monitor_label = tk.Label(monitor_frame, text="Output : ", font=self.font)
        monitor_label.pack(side="left", padx=5, pady=5)
        self.monitor_box = ttk.Combobox(
            monitor_frame, values=output_devices, width=30, font=self.font
        )
        self.monitor_box.current(default_output)
        self.monitor_box.pack(side="left", padx=5, pady=5)
        monitor_button = tk.Button(
            monitor_frame, text="Test", command=self.test, padx=10
        )
        monitor_button.pack(side="right", anchor="sw", padx=5, pady=5)

        # 音量增益滑桿
        volume_frame = tk.Frame(self.root)
        volume_frame.pack(padx=PAD_X, pady=PAD_Y)
        volume_label = tk.Label(volume_frame, text="Volume Boost : ", font=self.font)
        volume_label.pack(side="left", anchor="n")
        self.volume_scale = tk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient="horizontal",
            length=300,
            tickinterval=20,
            showvalue=False,
            font=self.font,
            command=lambda val: volume_value_label.config(text=f"{val}"),
        )
        self.volume_scale.pack(side="left")
        volume_value_label = tk.Label(volume_frame, text="0", width=10, font=self.font)
        volume_value_label.pack(side="left", anchor="n")
        volume_check = tk.Checkbutton(volume_frame, font=self.font)
        volume_check.select()
        volume_check.pack(side="left", anchor="n")

        # 失真強度滑桿
        clip_frame = tk.Frame(self.root)
        clip_frame.pack(padx=PAD_X, pady=PAD_Y)
        clip_label = tk.Label(clip_frame, text="Clip : ", font=self.font)
        clip_label.pack(side="left", anchor="n")
        self.clip_scale = tk.Scale(
            clip_frame,
            from_=0,
            to=100,
            orient="horizontal",
            length=300,
            tickinterval=20,
            showvalue=False,
            font=self.font,
            command=lambda val: clip_value_label.config(text=f"{val}"),
        )
        self.clip_scale.pack(side="left")
        clip_value_label = tk.Label(clip_frame, text="0", width=10, font=self.font)
        clip_value_label.pack(side="left", anchor="n")
        clip_check = tk.Checkbutton(clip_frame, font=self.font)
        clip_check.select()
        clip_check.pack(side="left", anchor="n")

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
        if self.AD != None:
            self.AD.interrupt()

        self.root.destroy()

        # if messagebox.askokcancel("Quit", "Do you want to quit?"):
        #     self.running = False
        #     self.root.destroy()

    def show(self):
        print("Show windows...")
        self.root.mainloop()

    def run(self):
        print("Start running...")

        self.AD = Adjuster()        
        self.AD.DATA_BOOST = self.__prepare()

        run_thread = threading.Thread(
            target=self.AD.run,
            name="run",
            args=(self.input_box.get(), self.output_box.get()),
        )
        run_thread.start()

        self.root.focus_set()
        self.__set_state(self.root, "disable")

        while True:
            if run_thread.is_alive():
                time.sleep(0.1)
                self.root.update()
            else:
                self.__set_state(self.root, "normal")
                return

    def test(self):
        print("Start testing...")

        self.AD = Adjuster()
        self.AD.DATA_BOOST = self.__prepare()

        run_thread = threading.Thread(
            target=self.AD.run,
            name="test",
            args=(self.input_box.get(), self.monitor_box.get()),
        )
        run_thread.start()

        self.root.focus_set()
        self.__set_state(self.root, "disable")

        while True:
            if run_thread.is_alive():
                time.sleep(0.1)
                self.root.update()
            else:
                self.__set_state(self.root, "normal")
                return

    def __prepare(self) ->DataPack:
        data = DataPack()
        data.VolumeBoost = 1 + self.volume_scale.get() / 5.0
        data.Clip = 1 - (self.clip_scale.get() / 100.)

        return data

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

        self.root.bind_all("=", increase_font_size)
        self.root.bind_all("-", decrease_font_size)
        # self.root.bind_all("<Control-c>", state)

    def __set_state(self, parent, state):
        for widget in parent.winfo_children():
            if isinstance(widget, (tk.Frame, tk.LabelFrame, tk.Toplevel)):
                self.__set_state(widget, state)
            elif isinstance(widget, tk.Button):
                widget.config(state=state)
            elif isinstance(widget, ttk.Combobox):
                widget.config(state=state)
            elif isinstance(widget, tk.Scale):
                widget.config(state=state)
            elif isinstance(widget, tk.Checkbutton):
                widget.config(state=state)


if __name__ == "__main__":
    window = Window()
    window.show()
    