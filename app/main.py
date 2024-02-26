from tkinter import Tk
from app.gui import WeatherApp

if __name__ == "__main__":
    root = Tk()
    app = WeatherApp(root)
    app.run()

