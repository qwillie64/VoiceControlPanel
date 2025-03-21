import pyaudio
import keyboard
import time
import numpy as np
from playsound import playsound


class Effect:
    def __init__(self):
        pass

    def run(self):
        pass


class Adjuster:
    def __init__(self):
        self.DATA_NORMAL: DataPack = None
        self.DATA_BOOST: DataPack = None
        self.HINT = "sound/hint.mp3"
        self.KEY = "f"

        self.running = False

    def interrupt(self):
        self.running = False
        print("Finish")

    def run(self, input_device: str, output_device: str):
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
            rate=int(pa.get_device_info_by_index(idi).get("defaultSampleRate")),
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
            self.running = True
            while self.running:

                # 讀取
                data = input_stream_device.read(1024, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)

                start = time.time()

                # 調整
                if keyboard.is_pressed(self.KEY):
                    if shout == False:
                        shout = True
                        playsound(self.HINT)
                        print("Shout!")

                    # 失真
                    audio_data = np.clip(
                        audio_data,
                        -32768 * self.DATA_BOOST.Clip,
                        32767 * self.DATA_BOOST.Clip,
                    )

                    # 音量
                    audio_data = np.int16(audio_data * self.DATA_BOOST.VolumeBoost)

                    # 噪音
                    # audio_data = audio_data + (np.random.uniform(-10, 10, size=len(audio_data)))
                    audio_data = audio_data + np.random.randint(
                        -1000, 1000, size=len(audio_data), dtype=np.int16
                    )

                else:
                    shout = False

                end = time.time()
                print(f"Execution Time: {end - start:.10f} seconds")

                # 輸出
                output_stream_device.write(audio_data.tobytes())

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


class DataPack:
    def __init__(self):
        self.VolumeBoost = 0.0
        self.Clip = 0.0
        self.Noise = 0.0


if __name__ == "__main__":
    print(np.random.randn(50) * 10)
