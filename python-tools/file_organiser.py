files = ["report.docx", "photo.jpg", "music.mp3", "video.mp4", "notes.txt"]

folders = {
    "Documents": [],
    "Images": [],
    "Audio": [],
    "Video": [],
    "Other": []
}

for file in files:
    if file.endswith(".docx") or file.endswith(".txt"):
        folders["Documents"].append(file)
    elif file.endswith(".jpg"):
        folders["Images"].append(file)
    elif file.endswith(".mp3"):
        folders["Audio"].append(file)
    elif file.endswith(".mp4"):
        folders["Video"].append(file)
    else:
        folders["Other"].append(file)

for folder, items in folders.items():
    print(folder, ":", items)
