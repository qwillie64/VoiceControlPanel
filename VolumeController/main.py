import pyaudio
import numpy as np

# 音量調整函數
def adjust_volume(audio_data, volume_factor):
    return np.int16(audio_data * volume_factor)

# 初始化 PyAudio
p = pyaudio.PyAudio()

# 打開實體麥克風輸入流
input_stream = p.open(format=pyaudio.paInt16,
                      channels=1,  # 麥克風通常是單聲道
                      rate=44100,
                      input=True,
                      frames_per_buffer=1024)

# 打開虛擬音訊裝置輸出流
# 找到虛擬音訊裝置的名稱，並設置 output=True
output_device_index = None
for i in range(p.get_device_count()):
    dev_info = p.get_device_info_by_index(i)
    if "CABLE Input" in dev_info["name"]:  # 假設使用 VB-Cable
        output_device_index = i
        break

if output_device_index is None:
    raise RuntimeError("未找到虛擬音訊裝置（如 VB-Cable）。請確認已安裝並啟用。")

output_stream = p.open(format=pyaudio.paInt16,
                       channels=1,
                       rate=44100,
                       output=True,
                       output_device_index=output_device_index,
                       frames_per_buffer=1024)

volume_factor = 3  # 音量調整倍數 (>1 放大, <1 縮小)

print("開始調整麥克風音量並輸出到虛擬麥克風，按 Ctrl+C 結束")
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
    p.terminate()