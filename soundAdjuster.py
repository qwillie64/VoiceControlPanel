import pyaudio
import keyboard
import numpy as np
from playsound import playsound


class Adjuster:
    def __init__(self):
        self.DATA_NORMAL = {}
        self.DATA_BOOST = {}
        self.HINT = "Sound/hint.mp3"
        self.KEY = "f"

    def run(self, input_device: str, output_device: str):
        def adjust_volume(audio_data, volume_factor):
            return np.int16(audio_data * volume_factor)

        pa = pyaudio.PyAudio()

        idi = None
        for i in range(pa.get_device_count()):
            dev_info = pa.get_device_info_by_index(i)
            if input_device == dev_info["name"]:
                idi = i
                print("Input -> " + dev_info["name"])
                break

        if idi is None:
            raise RuntimeError("無效的輸入來源。")

        input_stream_device = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=int(pa.get_device_info_by_index(idi).get('defaultSampleRate')),
            input=True,
            input_device_index=idi,
            frames_per_buffer=1024,
        )

        odi = None
        for i in range(pa.get_device_count()):
            dev_info = pa.get_device_info_by_index(i)
            if output_device == dev_info["name"]:
                odi = i
                print("Output -> " + dev_info["name"])
                break

        if odi is None:
            raise RuntimeError(
                "未找到虛擬音訊裝置（如 VB-Cable）。請確認已安裝並啟用。"
            )

        output_stream_device = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=int(pa.get_device_info_by_index(odi).get("defaultSampleRate")),
            output=True,
            output_device_index=odi,
            frames_per_buffer=1024,
        )

        try:
            shout = False
            running = True
            while running:
                # 讀取
                data = input_stream_device.read(1024, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)

                # 調整
                if keyboard.is_pressed(self.KEY):
                    if shout == False:
                        shout = True
                        # playsound("Sound/hint.mp3", False)
                        print("Shout!")

                    adjusted_data = adjust_volume(
                        audio_data, self.DATA_BOOST["volume_boost"]
                    )
                else:
                    shout = False
                    adjusted_data = audio_data

                # 輸出
                output_stream_device.write(adjusted_data.tobytes())

                # 結束
                if keyboard.is_pressed("esc"):
                    print("Relax...")
                    return

        except KeyboardInterrupt:
            input_stream_device.stop_stream()
            input_stream_device.close()
            output_stream_device.stop_stream()
            output_stream_device.close()
            pa.terminate()

    def get_audio_devices():
        pa = pyaudio.PyAudio()
        input_devices = []
        output_devices = []
        info = pa.get_host_api_info_by_index(0)
        numdevices = info.get("deviceCount")

        for i in range(0, numdevices):
            if (
                pa.get_device_info_by_host_api_device_index(0, i).get(
                    "maxInputChannels"
                )
            ) > 0:
                input_devices.append(
                    pa.get_device_info_by_host_api_device_index(0, i).get("name")
                )

            if (
                pa.get_device_info_by_host_api_device_index(0, i).get(
                    "maxOutputChannels"
                )
            ) > 0:
                output_devices.append(
                    pa.get_device_info_by_host_api_device_index(0, i).get("name")
                )

        pa.terminate()
        return input_devices, output_devices
