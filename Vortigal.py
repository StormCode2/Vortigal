import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk  # Import ttk for themed widgets
from pytube import YouTube

# Function to download the video
def download_video():
    video_url = url_entry.get()
    download_dir = output_folder.get()

    try:
        yt = YouTube(video_url)

        # Get the video's available stream resolutions
        available_resolutions = get_available_resolutions(yt)

        # Get the selected resolution
        selected_resolution = quality_var.get()

        if selected_resolution not in available_resolutions:
            status_label.config(text="Error: Selected resolution not available.")
            return

        # Get the stream with the selected resolution
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=selected_resolution).first()

        # Set the download directory
        sanitized_title = sanitize_filename(yt.title)
        download_path = os.path.join(download_dir, f"{sanitized_title}.mp4")

        # Check if the file already exists and increment the filename if needed
        count = 1
        while os.path.isfile(download_path):
            new_filename = f"{sanitized_title}_{count}.mp4"
            download_path = os.path.join(download_dir, new_filename)
            count += 1

        # Download the video with audio
        stream.download(output_path=download_dir, filename=os.path.basename(download_path))

        status_label.config(text="Download completed!")
    except Exception as e:
        status_label.config(text=f"An error occurred: {str(e)}")

# Function to get the video's available stream resolutions
def get_available_resolutions(yt):
    available_streams = yt.streams.filter(progressive=True, file_extension='mp4')
    available_resolutions = set([stream.resolution for stream in available_streams])
    return sorted(list(available_resolutions))

# Function to move to the next step (Quality Options)
def next_step_quality():
    # Hide the current step (URL Input)
    url_frame.pack_forget()

    # Show the Quality Options step
    quality_frame.pack(pady=10)

    # Update the available resolutions in the dropdown menu
    update_resolution_options()

# Function to move to the next step (Output Folder)
def next_step_output():
    # Hide the current step (Quality Options)
    quality_frame.pack_forget()

    # Show the Output Folder step
    output_frame.pack(pady=10)

# Function to update the available resolutions in the dropdown menu
def update_resolution_options():
    # Get the selected video's available resolutions
    video_url = url_entry.get()
    yt = YouTube(video_url)
    available_resolutions = get_available_resolutions(yt)

    # Clear and re-populate the dropdown menu with the available resolutions
    quality_var.set("Select Quality")  # Set the initial text
    quality_option_menu['menu'].delete(0, 'end')  # Clear existing options
    for resolution in available_resolutions:
        quality_option_menu['menu'].add_command(label=resolution, command=tk._setit(quality_var, resolution))

# Function to select the output folder
def select_output_folder():
    folder_path = filedialog.askdirectory()
    output_folder.set(folder_path)

# Function to start the download process
def start_download():
    # Hide the current step (Output Folder)
    output_frame.pack_forget()

    # Create a progress bar
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="indeterminate", style="TProgressbar", maximum=100)
    progress_bar.pack(pady=10)

    # Function to update the progress bar
    def update_progress():
        progress_bar["mode"] = "indeterminate"
        progress_bar.start(15)

    # Start updating the progress bar
    update_progress()

    # Start the download process in a separate thread (to prevent freezing the GUI)
    import threading

    def download_thread():
        download_video()
        progress_bar.stop()
        progress_bar.destroy()

    download_thread = threading.Thread(target=download_thread)
    download_thread.start()

# Function to sanitize a string for use as a file name using a blacklist
def sanitize_filename(filename):
    # Define a blacklist of characters not allowed in filenames
    blacklist = "/\\?%*:|\"<>"

    # Replace any blacklisted characters with an underscore "_"
    for char in blacklist:
        filename = filename.replace(char, "_")

    return filename

# Create the main window
root = tk.Tk()
root.title("Vortigal")
root.geometry("550x350")
root.iconbitmap("icon.ico")
root.configure(bg="#1a2538")

# Create and configure the frames for each step
url_frame = tk.Frame(root, bg="#1a2538")
quality_frame = tk.Frame(root, bg="#1a2538")
output_frame = tk.Frame(root, bg="#1a2538")

# Create and configure the URL input step
url_label = tk.Label(url_frame, text="Input Youtube URL to begin", bg="#1a2538", fg="white")
url_label.pack(pady=10)
url_entry = tk.Entry(url_frame, width=50)
url_entry.pack(pady=10)

# Add a "Next" button for Step 1 to progress to Step 2 (Quality Options)
next_button_quality = tk.Button(url_frame, text="Next (Quality Options)", command=next_step_quality, bg="#3e66ab", fg="white", relief="flat")
next_button_quality.pack(pady=10)

# Create a variable to store the selected resolution with initial text "Select Quality"
quality_var = tk.StringVar()
quality_var.set("Select Quality")

# Create and configure the Quality Options step
quality_label = tk.Label(quality_frame, text="Select video Export Quality", bg="#1a2538", fg="white")
quality_label.pack(pady=10)

# Create a drop-down menu for selecting resolution
quality_option_menu = tk.OptionMenu(quality_frame, quality_var, "Select Quality", "")
quality_option_menu.pack(pady=10)

# Add a "Next" button for Step 2 to progress to Step 3 (Output Folder)
next_button_output = tk.Button(quality_frame, text="Next (Output Folder)", command=next_step_output, bg="#3e66ab", fg="white", relief="flat")
next_button_output.pack(pady=10)

# Create and configure the Output Folder step
output_label = tk.Label(output_frame, text="Edit Video Destination", bg="#1a2538", fg="white")
output_label.pack(pady=10)
output_folder = tk.StringVar()
output_folder.set(os.path.dirname(os.path.realpath(__file__)))
output_folder_entry = tk.Entry(output_frame, textvariable=output_folder, width=50)
output_folder_entry.pack(pady=10)
output_folder_button = tk.Button(output_frame, text="Browse", command=select_output_folder, bg="#3e66ab", fg="white", relief="flat")
output_folder_button.pack(pady=10)
download_button = tk.Button(output_frame, text="Download", command=start_download, bg="#3e66ab", fg="white", relief="flat")
download_button.pack(pady=10)

# Bar
bar = tk.Label(root, text="Vortigal Downloader", bg="#3e66ab", fg="white", width=1500, font=("Bahnschrift", 20))
bar.pack(pady=10)

# Create and configure the status label
status_label = tk.Label(root, text="", bg="#1a2538", fg="white")
status_label.pack(pady=10)

# Initially, show the URL input step
url_frame.pack(pady=20)

# Start the GUI main loop
root.mainloop()
