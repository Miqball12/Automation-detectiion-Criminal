import cv2
from ultralytics import YOLO
import requests
import threading
import pygame
import os
import subprocess
import time

# Load model hasil training
model = YOLO("best.pt")

# Telegram setup
TOKEN = "8091692684:AAHJ0i7HUQbGjN2n4teT4dCCEdD8eR8RVe0"
CHAT_ID = "1317913224"

# Kelas yang dianggap bahaya
BAHAYA_CLASSES = ['human_with_weapon', 'knife', 'pistol']

# Cegah spam notifikasi
last_alert_time = 0
alert_delay = 5  # detik

# Fungsi kirim pesan Telegram di thread
def kirim_pesan_telegram(pesan):
    def kirim():
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            data = {"chat_id": CHAT_ID, "text": pesan}
            requests.post(url, data=data, timeout=10)
        except Exception as e:
            print(f"[!] Gagal kirim Telegram: {e}")
    threading.Thread(target=kirim, daemon=True).start()

# Fungsi putar suara (di thread juga)
def putar_suara(path='alarm.mp3'):
    def mainkan():
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(1.0)  # Volume maksimal
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
            pygame.mixer.quit()
        except Exception as e:
            print(f"[!] Gagal putar suara: {e}")
    threading.Thread(target=mainkan, daemon=True).start()

# Inisialisasi tampilan
cv2.namedWindow("Deteksi Bahaya", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Deteksi Bahaya", 800, 600)

# Jendela always on top
if os.name == 'posix':
    try:
        subprocess.Popen(['wmctrl', '-r', 'Deteksi Bahaya', '-b', 'add,above'])
    except:
        print("⚠️ wmctrl tidak tersedia.")

# Buka kamera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hasil = model.predict(frame, conf=0.5, stream=True)

    for hasil_deteksi in hasil:
        for box in hasil_deteksi.boxes:
            kelas = int(box.cls[0])
            nama_kelas = model.names[kelas]

            # Gambar kotak
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, nama_kelas, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Deteksi bahaya
            if nama_kelas in BAHAYA_CLASSES:
                now = time.time()
                if now - last_alert_time > alert_delay:
                    pesan = f"🚨 Bahaya terdeteksi: {nama_kelas.upper()}!"
                    kirim_pesan_telegram(pesan)
                    putar_suara()
                    last_alert_time = now
                break

    cv2.imshow("Deteksi Bahaya", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
