from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from pytube import YouTube
import os
import subprocess
import threading

class YouTubeDownloader(App):

    def download_video(self, url, output_path):
        try:
            yt = YouTube(url)
            video = yt.streams.filter(only_audio=True).first()
            video.download(output_path=output_path)
            return video.default_filename
        except Exception as e:
            return None

    def convert_to_mp3(self, video_file, output_path):
        try:
            mp3_filename = os.path.splitext(video_file)[0] + '.mp3'
            subprocess.run(['ffmpeg', '-i', video_file, '-vn', '-ar', '44100', '-ac', '2', '-b:a', '128k', mp3_filename], capture_output=True)
            os.remove(video_file)
            return mp3_filename
        except Exception as e:
            return None

    def build(self):
        Window.size = (400, 200)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        self.url_input = TextInput(hint_text="Enter YouTube URL", size_hint_y=None, height=dp(40))
        layout.add_widget(self.url_input)

        download_button = Button(text="Download", size_hint_y=None, height=dp(40), background_color=(0.1, 0.5, 0.8, 1))
        download_button.bind(on_press=self.download)
        layout.add_widget(download_button)

        self.status_label = Label(text="", size_hint_y=None, height=dp(40))
        layout.add_widget(self.status_label)

        return layout

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        popup_label = Label(text=message)
        close_button = Button(text="Close", size_hint_y=None, height=dp(40), background_color=(0.8, 0.1, 0.1, 1))
        close_button.bind(on_press=lambda *args: popup.dismiss())

        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(close_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(None, None), size=(dp(300), dp(200)))
        popup.open()

    def download(self, instance):
        video_url = self.url_input.text.strip()
        if video_url == "":
            self.show_popup("Error", "Please enter a valid YouTube URL.")
            return

        self.status_label.text = "Downloading..."

        threading.Thread(target=self.download_thread, args=(video_url,)).start()

    def download_thread(self, video_url):
        output_dir = "Downloaded"

        video_file = self.download_video(video_url, output_dir)
        if video_file:
            mp3_file = self.convert_to_mp3(os.path.join(output_dir, video_file), output_dir)
            if mp3_file:
                self.status_label.text = "MP3 file saved as: " + mp3_file
            else:
                self.status_label.text = "Failed to convert to MP3."
        else:
            self.status_label.text = "Failed to download video."

if __name__ == '__main__':
    YouTubeDownloader().run()