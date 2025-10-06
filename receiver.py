"""
LAN Screen Cast Receiver (Pro TV Edition v4)
---------------------------------------------
- Auto-discover sender on LAN (no IP input)
- Auto-reconnect if stream drops
- Real-time FPS and bandwidth display
- Remote-friendly touch controls
- Adaptive fullscreen scaling
- Optional resolution scaling for performance
"""

from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.utils import platform
import cv2
import threading
import socket
import time

BROADCAST_PORT = 5001  # port for sender discovery
STREAM_PORT = 5000

class Receiver(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, spacing=10, **kwargs)
        Window.clearcolor = (0, 0, 0, 1)

        # --- UI Elements ---
        self.status = Label(text="[b][color=ff4444]🔴 Searching for sender...[/color][/b]", markup=True, size_hint_y=None, height=40, font_size='18sp')
        self.fps_label = Label(text="", size_hint_y=None, height=30, font_size='16sp')
        self.bandwidth_label = Label(text="", size_hint_y=None, height=30, font_size='16sp')
        self.start_btn = Button(text="▶️ Start Stream", size_hint_y=None, height=70, font_size='20sp', background_color=(0.1,0.6,0.2,1))
        self.stop_btn = Button(text="⏹ Stop Stream", size_hint_y=None, height=70, font_size='20sp', background_color=(0.7,0.1,0.1,1))
        self.fullscreen_btn = Button(text="🖵 Toggle Fullscreen", size_hint_y=None, height=50, font_size='18sp', background_color=(0.3,0.3,0.7,1))

        self.stop_btn.disabled = True

        self.start_btn.bind(on_press=self.start_stream)
        self.stop_btn.bind(on_press=self.stop_stream)
        self.fullscreen_btn.bind(on_press=self.toggle_fullscreen)

        self.image = Image(allow_stretch=True, keep_ratio=True)

        # Layout
        self.add_widget(self.image)
        self.add_widget(self.status)
        self.add_widget(self.fps_label)
        self.add_widget(self.bandwidth_label)
        self.add_widget(self.start_btn)
        self.add_widget(self.stop_btn)
        self.add_widget(self.fullscreen_btn)

        # --- Stream vars ---
        self.cap = None
        self.running = False
        self.stream_url = ""
        self.lock = threading.Lock()
        self.last_time = time.time()
        self.frame_count = 0
        self.current_fps = 0
        self.current_bandwidth = 0
        self.reconnect_delay = 2  # seconds
        self.sender_ip = None

        # Start auto-discovery thread
        threading.Thread(target=self.discover_sender, daemon=True).start()

    def discover_sender(self):
        """Listen for sender broadcast messages to auto-discover IP."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", BROADCAST_PORT))
        while self.sender_ip is None:
            try:
                data, addr = sock.recvfrom(1024)
                if data == b"LAN_CAST_SENDER":
                    self.sender_ip = addr[0]
                    self.status.text = f"[b][color=ffaa00]🟢 Sender found: {self.sender_ip}[/color][/b]"
            except:
                pass

    def start_stream(self, *args):
        if self.running:
            return
        if not self.sender_ip:
            self.status.text = "[b][color=ff4444]❌ Waiting for sender...[/color][/b]"
            return
        self.stream_url = f"udp://@{self.sender_ip}:{STREAM_PORT}"
        self.status.text = "[b][color=ffaa00]🟢 Connecting...[/color][/b]"
        threading.Thread(target=self._open_stream, daemon=True).start()

    def _open_stream(self):
        while not self.running:
            with self.lock:
                self.cap = cv2.VideoCapture(self.stream_url)
            if self.cap.isOpened():
                self.running = True
                self.start_btn.disabled = True
                self.stop_btn.disabled = False
                self.status.text = "[b][color=44ff44]🟢 Receiving stream...[/color][/b]"
                Clock.schedule_interval(self.update, 1.0 / 30.0)
                break
            else:
                self.status.text = f"[b][color=ffaa00]⚠️ Failed to connect. Retrying in {self.reconnect_delay}s[/color][/b]"
                time.sleep(self.reconnect_delay)

    def stop_stream(self, *args):
        if not self.running:
            return
        self.running = False
        Clock.unschedule(self.update)
        with self.lock:
            if self.cap:
                self.cap.release()
                self.cap = None
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.status.text = "[b][color=ff4444]🔴 Stream stopped[/color][/b]"
        self.fps_label.text = ""
        self.bandwidth_label.text = ""

    def toggle_fullscreen(self, *args):
        Window.fullscreen = not Window.fullscreen

    def update(self, dt):
        if not self.running or not self.cap:
            return
        with self.lock:
            ret, frame = self.cap.read()
        if ret:
            width, height = Window.size
            max_width = 1920
            max_height = 1080
            scale_w = min(width, max_width)
            scale_h = min(height, max_height)
            frame = cv2.resize(frame, (scale_w, scale_h))

            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture

            # FPS calculation
            self.frame_count += 1
            now = time.time()
            if now - self.last_time >= 1.0:
                self.current_fps = self.frame_count
                self.frame_count = 0
                self.last_time = now
                self.fps_label.text = f"[b][color=00ff00]FPS: {self.current_fps}[/color][/b]"
                self.current_bandwidth = frame.nbytes * self.current_fps / (1024*1024)
                self.bandwidth_label.text = f"[b][color=00ffff]Bandwidth: {self.current_bandwidth:.2f} MB/s[/color][/b]"
        else:
            self.status.text = "[b][color=ffaa00]⚠️ Waiting for signal...[/color][/b]"
            # Auto-reconnect
            if self.running:
                with self.lock:
                    if self.cap:
                        self.cap.release()
                    time.sleep(self.reconnect_delay)
                    self.cap = cv2.VideoCapture(self.stream_url)

class ReceiverApp(App):
    def build(self):
        if platform == "android":
            Window.fullscreen = True
        else:
            Window.size = (1280, 720)
            Window.fullscreen = False
        return Receiver()

if __name__ == "__main__":
    ReceiverApp().run()
