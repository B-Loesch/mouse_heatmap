import time 
from pynput import mouse
from win32gui import FindWindow, GetWindowRect
import matplotlib.pyplot as plt
import numpy as np
import keyboard
from datetime import datetime


mouse_clicks = []

def on_click(x,y, button, pressed):
    if pressed:
        mouse_clicks.append((x,y))
        
def get_window_coord(win_name,resolution):
    window = FindWindow(None, win_name)
    window_rect = GetWindowRect(window)
    corner_x = window_rect[0]
    corner_y = resolution[1] - window_rect[3]
    corner = (corner_x, corner_y)
    return(corner)

def generate_heatmap(data, resolution = (2560,1440), sigma  = 5):
    import scipy.ndimage
    heatmap, xedges, yedges = np.histogram2d(
        [pos[0] for pos in data],
        [pos[1] for pos in data],
        bins = (resolution[0], resolution[1]),
        range=[[0, resolution[0]], [0, resolution[1]]])
    heatmap = np.rot90(heatmap)
    heatmap = np.flipud(heatmap)
    
    heatmap = scipy.ndimage.gaussian_filter(heatmap, sigma = sigma)
    
    return heatmap, xedges, yedges

def plot_heatmap(heatmap, xedges, yedges, duration, num_clicks, corner, output_path = "mouse_heatmap.png"):
    plt.figure(figsize = (19.2, 10.8))
    plt.imshow(heatmap, extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]], cmap='inferno')
    
    client = plt.Rectangle(corner, 1000, 600, linewidth = 1, edgecolor = "grey", facecolor = 'none')
    plt.gca().add_patch(client)
    
    plt.xticks([])
    plt.yticks([])
    
    note = f"Duration: {int(duration)} seconds \n# Clicks: {num_clicks}\nCPM: {round(num_clicks/int(duration)*60,2)}"
    plt.text(0.85,0.15, note, 
             ha='left', va='top', 
             color='white', fontsize='small',
             transform = plt.gca().transAxes,
             bbox = dict(facecolor = 'none'))
    
    colorbar = plt.colorbar(shrink=0.5, ticks=[heatmap.min(), heatmap.max()], location = 'bottom')
    # colorbar.set_label("Mouse Position", rotation=270, labelpad=15)
    colorbar.set_ticks([heatmap.min(), heatmap.max()])
    colorbar.set_ticklabels(['Low', 'High'])
    
    plt.savefig(output_path, dpi = 800)
    plt.show()
    
def main():
    start_time = time.time()
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H-%M-%S")
    file_save = f"heatmap_{dt_string}.png"
    with mouse.Listener(on_click=on_click) as listener:
        print("Mouse tracking started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            listener.stop()
    duration = (time.time() - start_time)
    num_clicks = len(mouse_clicks)
    resolution = (2560,1440)
    corner = get_window_coord("RuneLite", resolution)
    heatmap, xedges, yedges = generate_heatmap(mouse_clicks, resolution, sigma = 10) 
    plot_heatmap(heatmap, xedges, yedges, duration, num_clicks, corner, output_path = f"C:/Users/Brandon Loesch/.runelite/screenshots/{file_save}")

if __name__ == "__main__":
    try:
        main()
    except keyboard.KeyboardInterrupt:
        print("\nMouse tracking stopped.")