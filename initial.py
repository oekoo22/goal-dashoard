import json
# Speichern
data = {"module": [{"name": "Mathe", "ects": 5, "note": 2.3}]}
with open("test.json", "w") as f:
    json.dump(data, f)
# Laden
with open("test.json", "r") as f:
    loaded = json.load(f)
print(loaded)



import tkinter as tk
root = tk.Tk()
root.title("Dashboard Test")
label = tk.Label(root, text="Semester: 3")
label.pack()
# Progress bar simuliert
progress = tk.Canvas(root, width=200, height=20)
progress.create_rectangle(0, 0, 130, 20, fill="green")
progress.pack()
root.mainloop()  

