import threading
import time
import tkinter as tk
from tkinter import ttk, font, messagebox
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

        self.VOLUME_BOOSt = 0.0

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
            from_=0,
            to=20,
            orient="horizontal",
            length=300,
            tickinterval=5,
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
        self.root.destroy()

        # if messagebox.askokcancel("Quit", "Do you want to quit?"):
        #     self.running = False
        #     self.root.destroy()

    def show(self):
        print("Show windows...")
        self.root.mainloop()

    def run(self):
        print("Start running...")

        # 更新
        data_boost = {}
        data_boost["volume_boost"] = 1 + self.VOLUME_BOOSt

        ad = Adjuster()
        ad.DATA_BOOST = data_boost

        run_thread = threading.Thread(
            target=ad.run,
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
        # ad.run(self.input_box.get(), self.output_box.get())

    def test(self):
        print("Start testing...")

        # 更新
        data_boost = {}
        data_boost["volume_boost"] = 1 + self.VOLUME_BOOSt

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
