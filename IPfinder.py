import socket
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import threading
import os
import json
import time
import pyperclip  # For clipboard functionality
try:
    from PIL import Image, ImageTk
    import requests
    from io import BytesIO
except ImportError:
    Image = ImageTk = None

HISTORY_FILE = "history.txt"
FAVORITES_FILE = "favorites.txt"

class IPFetcherApp:
    def __init__(self, master):
        self.master = master
        self.master.title("IP Fetcher")
        # Let the window auto-size; set a minimum size
        self.master.minsize(520, 450)
        self.master.attributes("-topmost", True)
        try:
            self.master.iconbitmap('favicon.ico')
        except Exception:
            pass

        # Advanced options settings
        self.auto_refresh_enabled = tk.BooleanVar(value=False)
        self.refresh_interval = 10  # seconds for auto refresh

        # Set up ttk style for a modern look
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#F5F5F5")
        self.style.configure("TLabel", background="#F5F5F5", font=("Helvetica", 14))
        self.style.configure("Header.TLabel", font=("Helvetica", 18, "bold"), background="#F5F5F5")
        self.style.configure("TButton", font=("Helvetica", 14))
        self.style.configure("TEntry", font=("Helvetica", 14, "bold"))

        # Main container frame (auto-adjusting)
        self.container = ttk.Frame(master, padding=10)
        self.container.grid(row=0, column=0, sticky="nsew")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        self.create_top_section()
        self.create_input_section()
        self.create_history_and_favorites_section()
        self.create_bottom_section()
        self.create_status_bar()
        self.create_menu()

        # Schedule auto-refresh if enabled
        self.master.after(1000, self.check_auto_refresh)

        self.set_status("Ready")
        self.master.update_idletasks()  # Ensure window resizes automatically

    def create_top_section(self):
        self.top_frame = ttk.Frame(self.container)
        self.top_frame.grid(row=0, column=0, sticky="ew", pady=(0,10))
        self.top_frame.columnconfigure(1, weight=1)

        # Emoji logo as a Label with large font
        self.logo_label = ttk.Label(self.top_frame, text="🌐", font=("Helvetica", 48))
        self.logo_label.grid(row=0, column=0, padx=5)
        # Title label
        self.title_label = ttk.Label(self.top_frame, text="IP Fetcher", style="Header.TLabel")
        self.title_label.grid(row=0, column=1, sticky="w", padx=5)
        # Theme toggle button
        self.theme_btn = ttk.Button(self.top_frame, text="Toggle Theme", command=self.toggle_theme)
        self.theme_btn.grid(row=0, column=2, padx=5)

    def create_input_section(self):
        self.input_frame = ttk.Frame(self.container)
        self.input_frame.grid(row=1, column=0, sticky="ew", pady=5)
        self.input_frame.columnconfigure(1, weight=1)

        # URL label and entry
        self.url_label = ttk.Label(self.input_frame, text="URL:")
        self.url_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.url_entry = ttk.Entry(self.input_frame)
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.clear_input_btn = ttk.Button(self.input_frame, text="Clear Input", command=lambda: self.url_entry.delete(0, tk.END))
        self.clear_input_btn.grid(row=0, column=2, padx=5, pady=5)

        # IP output label and Clear IP button
        self.ip_text_label = ttk.Label(self.input_frame, text="IP:")
        self.ip_text_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.ip_label = ttk.Label(self.input_frame, text="0.0.0.0", font=("Helvetica", 22, "bold"))
        self.ip_label.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.clear_ip_btn = ttk.Button(self.input_frame, text="Clear IP", command=lambda: self.ip_label.config(text="0.0.0.0"))
        self.clear_ip_btn.grid(row=1, column=2, padx=5, pady=5)

        # Buttons row: GET IP and Copy IP
        self.getip_button = ttk.Button(self.input_frame, text="GET IP", command=self.threaded_get_ip)
        self.getip_button.grid(row=2, column=0, columnspan=2, pady=10)
        self.copy_ip_btn = ttk.Button(self.input_frame, text="Copy IP", command=self.copy_ip)
        self.copy_ip_btn.grid(row=2, column=2, pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.input_frame, orient="horizontal", mode="indeterminate")
        self.progress.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

    def create_history_and_favorites_section(self):
        # Section for both Search History and Favorites side by side
        self.mid_frame = ttk.Frame(self.container)
        self.mid_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        self.mid_frame.columnconfigure(0, weight=1)
        self.mid_frame.columnconfigure(1, weight=1)

        # History Labelframe
        self.history_frame = ttk.Labelframe(self.mid_frame, text="Search History", padding=5)
        self.history_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.history_frame.columnconfigure(0, weight=1)
        self.history_listbox = tk.Listbox(self.history_frame, font=("Helvetica", 12))
        self.history_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.history_scroll = ttk.Scrollbar(self.history_frame, orient="vertical", command=self.history_listbox.yview)
        self.history_scroll.grid(row=0, column=1, sticky="ns", padx=5, pady=5)
        self.history_listbox.config(yscrollcommand=self.history_scroll.set)
        self.history_listbox.bind("<Double-Button-1>", self.on_history_double_click)
        self.load_history()
        self.clear_history_btn = ttk.Button(self.history_frame, text="Clear History", command=self.clear_history)
        self.clear_history_btn.grid(row=1, column=0, columnspan=2, pady=5)

        # Favorites Labelframe
        self.fav_frame = ttk.Labelframe(self.mid_frame, text="Favorites", padding=5)
        self.fav_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.fav_frame.columnconfigure(0, weight=1)
        self.fav_listbox = tk.Listbox(self.fav_frame, font=("Helvetica", 12))
        self.fav_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.fav_scroll = ttk.Scrollbar(self.fav_frame, orient="vertical", command=self.fav_listbox.yview)
        self.fav_scroll.grid(row=0, column=1, sticky="ns", padx=5, pady=5)
        self.fav_listbox.config(yscrollcommand=self.fav_scroll.set)
        self.fav_listbox.bind("<Double-Button-1>", self.on_fav_double_click)
        self.load_favorites()
        self.add_fav_btn = ttk.Button(self.fav_frame, text="Add to Favorites", command=self.add_favorite)
        self.add_fav_btn.grid(row=1, column=0, columnspan=2, pady=5)
        self.clear_fav_btn = ttk.Button(self.fav_frame, text="Clear Favorites", command=self.clear_favorites)
        self.clear_fav_btn.grid(row=2, column=0, columnspan=2, pady=5)

    def create_bottom_section(self):
        # Bottom section for additional advanced options
        self.bottom_frame = ttk.Frame(self.container)
        self.bottom_frame.grid(row=3, column=0, sticky="ew", pady=10)
        self.bottom_frame.columnconfigure(0, weight=1)
        self.adv_options_btn = ttk.Button(self.bottom_frame, text="Advanced Options", command=self.open_advanced_options)
        self.adv_options_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    def create_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.master, textvariable=self.status_var, relief="sunken", anchor="w", font=("Helvetica", 10))
        self.status_bar.grid(row=1, column=0, sticky="ew")

    def create_menu(self):
        self.menu = tk.Menu(self.master)
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="ABOUT", command=self.show_about)
        file_menu.add_command(label="GITHUB PAGE", command=lambda: webbrowser.open_new("https://github.com/kai9987kai/IPfinder"))
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="GET IP", command=self.threaded_get_ip)
        file_menu.add_command(label="EXIT", command=self.master.destroy)
        self.menu.add_cascade(label="Menu", menu=file_menu)
        help_menu = tk.Menu(self.menu, tearoff=0)
        help_menu.add_command(label="CONTACT", command=lambda: messagebox.showinfo("CONTACT", "Email-One: kai9987kai@gmail.com\nEmail-Two: kai.piper@aol.co.uk"))
        self.menu.add_cascade(label="Help", menu=help_menu)
        self.master.config(menu=self.menu)

    def toggle_theme(self):
        # Simple light/dark toggle
        current_bg = self.master.cget("background")
        if current_bg == "#F5F5F5":
            self.master.configure(background="#333333")
            self.style.configure("TFrame", background="#333333")
            self.style.configure("TLabel", background="#333333", foreground="#F5F5F5")
            self.status_bar.configure(background="#555555", foreground="#F5F5F5")
            self.set_status("Dark Theme Enabled")
        else:
            self.master.configure(background="#F5F5F5")
            self.style.configure("TFrame", background="#F5F5F5")
            self.style.configure("TLabel", background="#F5F5F5", foreground="#000000")
            self.status_bar.configure(background="#DDDDDD", foreground="#000000")
            self.set_status("Light Theme Enabled")

    def threaded_get_ip(self):
        threading.Thread(target=self.get_ip, daemon=True).start()

    def get_ip(self):
        self.set_status("Fetching IP...")
        self.progress.start(10)
        self.getip_button.config(state="disabled")
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Input Error", "Please enter a URL.")
            self.set_status("Ready")
            self.progress.stop()
            self.getip_button.config(state="normal")
            return
        try:
            if "://" in url:
                domain = url.split("://")[1].split("/")[0]
            else:
                domain = url.split("/")[0]
            start_time = time.time()
            ip_info = socket.gethostbyname(domain)
            elapsed = (time.time() - start_time) * 1000  # in ms
            self.ip_label.config(text=ip_info)
            self.add_history(url)
            self.set_status(f"IP Fetched in {int(elapsed)} ms")
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch IP for {url}.\nError: {str(e)}")
            self.set_status("Error fetching IP")
        finally:
            self.progress.stop()
            self.getip_button.config(state="normal")

    def copy_ip(self):
        ip_val = self.ip_label.cget("text")
        pyperclip.copy(ip_val)
        self.set_status("IP copied to clipboard")

    def set_status(self, text):
        self.status_var.set(text)

    # History functions
    def get_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as f:
                    return f.read().splitlines()
            except Exception:
                return []
        return []

    def save_history(self, history):
        try:
            with open(HISTORY_FILE, "w") as f:
                f.write("\n".join(history))
        except Exception as e:
            print("Error saving history:", e)

    def add_history(self, query):
        history = self.get_history()
        if query not in history:
            history.insert(0, query)
            history = history[:10]
            self.save_history(history)
            self.load_history()

    def load_history(self):
        history = self.get_history()
        self.history_listbox.delete(0, tk.END)
        for item in history:
            self.history_listbox.insert(tk.END, item)

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear history?"):
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
            self.load_history()
            self.set_status("History Cleared")

    def on_history_double_click(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            url = self.history_listbox.get(selection[0])
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)

    # Favorites functions
    def get_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, "r") as f:
                    return f.read().splitlines()
            except Exception:
                return []
        return []

    def save_favorites(self, favs):
        try:
            with open(FAVORITES_FILE, "w") as f:
                f.write("\n".join(favs))
        except Exception as e:
            print("Error saving favorites:", e)

    def add_favorite(self):
        url = self.url_entry.get().strip()
        if url:
            favs = self.get_favorites()
            if url not in favs:
                favs.insert(0, url)
                favs = favs[:10]
                self.save_favorites(favs)
                self.load_favorites()
                self.set_status("URL added to favorites")
            else:
                self.set_status("URL already in favorites")
        else:
            messagebox.showerror("Input Error", "Please enter a URL to add to favorites.")

    def load_favorites(self):
        favs = self.get_favorites()
        self.fav_listbox.delete(0, tk.END)
        for fav in favs:
            self.fav_listbox.insert(tk.END, fav)

    def clear_favorites(self):
        if messagebox.askyesno("Clear Favorites", "Are you sure you want to clear favorites?"):
            if os.path.exists(FAVORITES_FILE):
                os.remove(FAVORITES_FILE)
            self.load_favorites()
            self.set_status("Favorites Cleared")

    def on_fav_double_click(self, event):
        selection = self.fav_listbox.curselection()
        if selection:
            url = self.fav_listbox.get(selection[0])
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)

    # Advanced Options dialog with Ping and Auto Refresh
    def open_advanced_options(self):
        adv_win = tk.Toplevel(self.master)
        adv_win.title("Advanced Options")
        adv_win.transient(self.master)
        adv_win.grab_set()
        adv_win.resizable(False, False)
        adv_win.geometry("")  # Let it auto-size

        ttk.Label(adv_win, text="Advanced Options", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Always On Top toggle is already in settings; here add Ping and Auto Refresh
        ttk.Button(adv_win, text="Ping Domain", command=self.ping_domain).grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.ping_result = ttk.Label(adv_win, text="Ping: N/A", font=("Helvetica", 12))
        self.ping_result.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Auto Refresh option
        self.auto_refresh_chk = ttk.Checkbutton(adv_win, text="Auto Refresh IP", variable=self.auto_refresh_enabled)
        self.auto_refresh_chk.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        ttk.Button(adv_win, text="Close", command=adv_win.destroy).grid(row=3, column=0, columnspan=2, pady=10)

    def ping_domain(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Input Error", "Please enter a URL to ping.")
            return
        try:
            if "://" in url:
                domain = url.split("://")[1].split("/")[0]
            else:
                domain = url.split("/")[0]
            start = time.time()
            # Simple socket connection to port 80
            sock = socket.create_connection((domain, 80), timeout=2)
            sock.close()
            elapsed = (time.time() - start) * 1000  # in ms
            self.ping_result.config(text=f"Ping: {int(elapsed)} ms")
            self.set_status("Ping Successful")
        except Exception as e:
            messagebox.showerror("Ping Error", f"Could not ping {url}.\nError: {str(e)}")
            self.ping_result.config(text="Ping: Error")

    def open_settings(self):
        settings_win = tk.Toplevel(self.master)
        settings_win.title("Settings")
        settings_win.transient(self.master)
        settings_win.grab_set()
        settings_win.resizable(False, False)
        settings_win.geometry("")  # Auto-size
        try:
            settings_win.iconbitmap('favicon.ico')
        except Exception:
            pass

        ttk.Label(settings_win, text="Settings", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        chk_hide = tk.BooleanVar(value=False)
        chk_fs = tk.BooleanVar(value=False)

        def apply_hide():
            self.master.overrideredirect(True)
            settings_win.destroy()

        def apply_fullscreen():
            self.master.attributes('-fullscreen', True)
            self.master.bind('<Escape>', lambda e: self.master.attributes('-fullscreen', False))
            settings_win.destroy()

        ttk.Checkbutton(settings_win, text="Hide Title Bar", variable=chk_hide, command=apply_hide).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ttk.Checkbutton(settings_win, text="FullScreen", variable=chk_fs, command=apply_fullscreen).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        ttk.Button(settings_win, text="Close", command=settings_win.destroy).grid(row=2, column=0, columnspan=2, pady=10)

    def show_about(self):
        about_text = ("IP Fetcher v1.1\n"
                      "Developed by Kai Piper\n\n"
                      "This application fetches the IP address for a given URL, maintains a search history, and allows you to manage favorites.\n\n"
                      "New features include automatic window sizing, clipboard integration, pinging, auto refresh, and export options.")
        messagebox.showinfo("About", about_text)

    def check_auto_refresh(self):
        if self.auto_refresh_enabled.get():
            self.threaded_get_ip()
        self.master.after(self.refresh_interval * 1000, self.check_auto_refresh)

if __name__ == "__main__":
    root = tk.Tk()
    app = IPFetcherApp(root)
    root.mainloop()
