import pyaudio
import numpy as np
import tkinter as tk
from tkinter import ttk, font


KEY = "f"


def get_audio_devices():
    pa = pyaudio.PyAudio()
    input_devices = []
    output_devices = []

    for i in range(pa.get_device_count()):
        device_info = pa.get_device_info_by_index(i)
        if device_info["maxInputChannels"] > 0:
            input_devices.append(device_info["name"])
        if device_info["maxOutputChannels"] > 0:
            output_devices.append(device_info["name"])

    pa.terminate()
    return input_devices, output_devices


class Window:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Volume Controller")
        self.root.geometry("600x400")
        self.font = font.Font(family="Arial", size=10)
        self.running = False

        # 獲取音訊設備
        input_devices, output_devices = get_audio_devices()

        # 音訊輸入/輸出區
        devices_frame = tk.Frame(self.root, padx=10, pady=10)
        devices_frame.pack()

        # 音訊輸入設備選單
        input_frame = tk.Frame(devices_frame)
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        input_label = tk.Label(input_frame, text="Input : ", font=self.font)
        input_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        input_box = ttk.Combobox(input_frame, values=input_devices, width=25, font=self.font)
        input_box.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # 音訊輸出設備選單
        output_frame = tk.Frame(devices_frame)
        output_frame.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        output_label = tk.Label(output_frame, text="Output : ", font=self.font)
        output_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        output_menu = ttk.Combobox(output_frame, values=output_devices, width=25, font=self.font)
        output_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # 音量增益滑桿
        def update_label(value):
            volume_value_label.config(text=f"{value}")

        volume_frame = tk.Frame(padx=10, pady=10)
        volume_frame.pack()
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
        start_button = tk.Button(self.root, text="Start", font=self.font, padx=10, pady=8)
        start_button.pack(side='bottom', anchor='se', padx=10, pady=10)

        # 綁定按鍵事件
        self.__key_event()

    def show(self):
        print("Show windows...")
        self.root.mainloop()
        self.root.focus_set()

    def run(self):
        print("Start running...")

        def adjust_volume(audio_data, volume_factor):
            return np.int16(audio_data * volume_factor)


        pa = pyaudio.PyAudio()

        input_stream = pa.open(format=pyaudio.paInt16,
                              channels=1,
                              rate=44100,
                              input=True,
                              frames_per_buffer=1024)
        
        output_stream = pa.open(format=pyaudio.paInt16,
                               channels=1,
                               rate=44100,
                               output=True,
                               output_device_index=output_device_index,
                               frames_per_buffer=1024)
        
        output_device_index = None
        for i in range(pa.get_device_count()):
            dev_info = pa.get_device_info_by_index(i)
            if "CABLE Input" in dev_info["name"]:  # 假設使用 VB-Cable
                output_device_index = i
                break

        if output_device_index is None:
            raise RuntimeError("未找到虛擬音訊裝置（如 VB-Cable）。請確認已安裝並啟用。")



        volume_factor = 3  # 音量調整倍數 (>1 放大, <1 縮小)

        try:
            while True:
                # 從實體麥克風讀取音訊
                data = input_stream.read(1024, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)

                # 調整音量
                adjusted_data = adjust_volume(audio_data, volume_factor)

                # 將調整後的音訊輸出到虛擬麥克風
                output_stream.write(adjusted_data.tobytes())
        except KeyboardInterrupt:
            print("\n結束程式")
            # 停止並關閉音訊流
            input_stream.stop_stream()
            input_stream.close()
            output_stream.stop_stream()
            output_stream.close()
            pa.terminate()

    def stop(self):
        if self.running:
            self.running = False
            print("Stop")

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

        def shout(event=None):
            print("Shout!")

        def state(event=None):
            if self.running:
                self.stop()
            else:
                self.run()

        self.root.bind_all("=", increase_font_size)
        self.root.bind_all("-", decrease_font_size)
        self.root.bind_all("f", shout)
        self.root.bind_all("<Control-c>", state)


if __name__ == "__main__":
    window = Window()
    window.show()
