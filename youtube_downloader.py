import io
import tkinter as tk
from tkinter import messagebox, filedialog
import requests
from PIL import Image, ImageTk
import yt_dlp
import os

from matplotlib.image import thumbnail

download_folder = os.getcwd()

def is_valid_youtube_url(url):
    return "youtube.com" in url or "youtu.be" in url

def choose_folder():
    global download_folder
    folder = filedialog.askdirectory()
    if folder:
        download_folder = folder
        folder_label.config(text=f"Save to: {folder}")

def get_video_info(url):
    try:
        with yt_dlp.YoutubeDL({'quiet':True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail')
            }
    except Exception as e:
        print(f"Error fetching video info: {e}")
        return None

def show_video_info():
    url = url_entry.get().strip()
    if not is_valid_youtube_url(url):
        return
    info = get_video_info(url)
    if info:
        title_label.config(text=f"Title: {info['title']}")
        try:
            img_data = requests.get(info['thumbnail']).content
            img = Image.open(io.BytesIO(img_data)).resize((320,100))
            thumbnail_img = ImageTk.PhotoImage(img)
            thumbnail_label.config(image=thumbnail_img)
            thumbnail_label.image = thumbnail_img
        except Exception as e:
            print("Thumbnail error:", e)

def download():
    url = url_entry.get().strip()

    if not url:
        messagebox.showwarning("Input Error", "Please enter a YouTube video URL.")
        return


    if not is_valid_youtube_url(url):
        messagebox.showwarning("Input Error", "Please enter a YouTube video URL.")

    else:

        choice = download_choice.get()
        progress_label.config(text="Starting download...")

        def hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '').strip()
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('eta', 'N/A')
                progress_label.config(text=f"Downloading... {percent} | Speed: {speed} | ETA: {eta}s")
            elif d['status'] == 'finished':
                progress_label.config(text="Download complete!")

        ydl_opts = {
            'progress_hooks': [hook],
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s')
        }



        if choice == "MP3":
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(download_folder,'%(title)s.%(ext)s'),
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Success", f"{choice} download successfully!")
            url_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Download failed:\n{str(e)}")



window = tk.Tk()
window.title("YouTube Downloader")
window.geometry("900x850")
window.resizable(False, False)


tk.Label(window, text="Enter YouTube URL:", font=("Arial", 12)).pack(pady=10)
url_entry = tk.Entry(window, width=50, font=("Arial", 11))
url_entry.pack(pady=5)

tk.Button(window, text="Get Video Info", command=show_video_info, bg="#2196F3", fg="white").pack(pady=5)

title_label = tk.Label(window, text="", font=("Arial", 11))
title_label.pack(pady=5)

thumbnail_label = tk.Label(window)
thumbnail_label.pack(pady=5)

folder_label = tk.Label(window, text=f"Save to: {download_folder}", font=("Arial", 10), fg="blue")
folder_label.pack(pady=5)

tk.Button(window, text="Choose Folder", command=choose_folder, bg="#607D8B", fg="white").pack(pady=5)

download_choice = tk.StringVar(value="Video")
tk.Radiobutton(window, text="Download as Video", variable=download_choice, value="Video", font=("Arial",11)).pack()
tk.Radiobutton(window, text="Download as MP3", variable=download_choice, value="MP3", font=("Arial",11)).pack()

tk.Button(window, text="Download", command=download, bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=20)

progress_label = tk.Label(window, text="", font=("Arial", 10), fg="green")
progress_label.pack(pady=5)

window.mainloop()