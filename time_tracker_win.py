# Load dependencies for the app
import tkinter as tk
import tkinter.ttk as ttk
from PIL import ImageTk, Image
from ttkthemes import ThemedTk
import pandas as pd
import time
from datetime import datetime
from pystray import MenuItem as item
import pystray

# First I create/load in a csv file containig the infrastructure for keeping the data in a nice and tidy format
def new_sheet():
    df = pd.DataFrame(data = None, columns = ["date", "start", "break", "end", "total"])
    total_row = {"date" : time.strftime('%B_%y', time.localtime()).lower(), "total" : 0}
    df = pd.concat([df, pd.DataFrame([total_row])], axis = 0, ignore_index = True)
    # Safe the df if it's the first time
    df.to_csv(f"timesheets_csv/timesheet_{sheet_spec}_{time.strftime('%B', time.localtime()).lower()}.csv",
             index = False)
    
# First I try to load the sheet of the current month but if that fails it creates a new sheet and loads that
def load_sheet():
    try:
        return pd.read_csv(f"timesheets_csv/timesheet_{sheet_spec}_{time.strftime('%B', time.localtime()).lower()}.csv")
    except:
        new_sheet()
        return pd.read_csv(f"timesheets_csv/timesheet_{sheet_spec}_{time.strftime('%B', time.localtime()).lower()}.csv")

# Now for the tkinter app and interface
# Create the window using a "modern" look
window = ThemedTk(theme = "equilux")

# Get screen width and height of the respective pc screen
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Use determined screen properties to scale the window size and coordinates (works perfectly for my pc)
width = int(screen_width / 4)
height = int(screen_height / 4)
x = (screen_width) - (width + 3)
y = (screen_height) - (height + 74)

# Assign the geometry to the window
window.geometry("%dx%d+%d+%d" % (width, height, x, y))
# Assign title
window.title("TrackTime")
# Set resizable to "False" so window can't be resized
window.resizable(False, False)

# Set a background image for the app
background = Image.open(r".pics/background1.jpg")
# Resize the image to fit window size
background = background.resize((width, height))
# Set picture as background
background = ImageTk.PhotoImage(background)
# Create a canvas on which to put the image
canvas = tk.Canvas(window, width = width, height = height)
# Place the canvas (minus values so there are not whit borders)
canvas.place(x = -2, y = -2)
# Finalize background
canvas.create_image((2, 2), image = background, anchor = "nw")

# Create input filed for sheet specification
sheet_spec_field = ttk.Entry(window, justify = tk.CENTER)
sheet_spec_field.place(x = 50, y = 280)
sheet_spec_field.focus()

# Change icon of window
window.iconbitmap(".pics/icon2.ico")

time_x = 50
time_y = 20
break_x = 50
break_y = 50


#---------------------------------------------------------------------------------------------------------------------------
# Initialize an empty dic that serves as new "row" in the df
new_entry = {"date" : time.strftime("%d.%m.%Y", time.localtime())}
# Create lists for the start/end time and break start/end as well as the duration of all summed breaks
time_list = []
break_list = []
breaks = []
# Define a list that must be empty for the stopwatch to run and stops the watch if it's filled
stopwatch_criteria = []
# Stopwatch criteria
crit = 1 

# Function that displays and starts the break stop watch
def time_disp():
    time_label = ttk.Label(window, 
                           font = ("calibri", 20, "bold"))
    time_label.place(x = time_x, y = time_y * 4)
    
    break_duration = time.gmtime((datetime.now() - break_list[0]).total_seconds())
    time_label.config(text = time.strftime("%H:%M:%S", break_duration))
    if stopwatch_criteria == []:
        time_label.after(1000, lambda: [time_label.destroy(), time_disp()])
    else:
        time_label.after(5000, time_label.destroy)

# Create the respective function for the start button that starts tracking and disables further interaction with the button
def start_tracking(event):
    new_entry["start"] = time.strftime("%H:%M", time.localtime())
    time_list.append(datetime.now())
    
    global break_start
    break_start = ttk.Button(window,
                        text = "Start break",
                        command = lambda: start_break())
    break_start.place(x = break_x, y = break_y)
    
    quit = ttk.Button(window,
                  text = "Quit",
                  command = lambda: exit())
    quit.place(x = time_x, y = time_y)
    
    global sheet_spec
    # Get the content of the input field and close it once start is pressed
    sheet_spec = sheet_spec_field.get()
    sheet_spec_field.destroy()

# Start the break and save the starting time for future
def start_break():
    if stopwatch_criteria != []:
        stopwatch_criteria.remove(crit)
    if break_list == []:
        break_list.append(datetime.now())
    else:
        break_list[0] = datetime.now()
    break_start.destroy()
    # Once the break is started the "End break" button appears
    global break_end
    break_end = ttk.Button(window,
                        text = "End break",
                        command = lambda: end_break())
    break_end.place(x = break_x, y = break_y)
    # The stopwatch is displayed and starts to stop break duration
    time_disp()
    
def end_break():
    if len(break_list) == 1:
        break_list.append(datetime.now())
    else:
        break_list[1] = datetime.now()
    stopwatch_criteria.append(crit)
    breaks.append((break_list[1] - break_list[0]).total_seconds())
    break_end.destroy()
    
    global break_start
    break_start = ttk.Button(window,
                        text = "Start break",
                        command = lambda: start_break())
    break_start.place(x = break_x, y = break_y)
    

# Helper function that calculates the hours/mins between two timedeltas
def calc_duration(time_list):
    delta = time.gmtime((time_list[1] - time_list[0]).total_seconds())
    return delta

# Create a function that opens a secondary dialogue once the "x" button is pressen asking for save & exit
def exit():
    # Create a new window and define title + size and location
    save_window = tk.Toplevel(window)
    save_window.title("Save & Exit TrackTime?")
    save_window.resizable(False, False)
    save_width = width / 2 - 50
    save_heigth = height / 2
    # window.update()
    save_x = window.winfo_rootx()
    save_y = window.winfo_rooty()
    save_window.geometry("%dx%d+%d+%d" % (save_width, save_heigth, (x + 3), (y + 27)))
    # Remove window buttons
    save_window.overrideredirect(1)
    
    canvas = tk.Canvas(save_window, width = save_width, height = save_heigth)
    # Place the canvas (minus values so there are not whit borders)
    canvas.place(x = -2, y = -2)
    # Finalize background
    canvas.create_image((2, 2), image = background, anchor = "nw")
    
    cancel = ttk.Button(save_window,
                       text = "Cancel",
                       command = lambda: save_window.destroy())
    cancel.place(x = time_x, y = time_y)
    
    save_exit = ttk.Button(save_window,
                          text = "Save & Exit",
                          command = lambda: save_on_exit())
    save_exit.place(x = break_x, y = break_y)
    
    exit = ttk.Button(save_window,
                          text = "Exit",
                          command = lambda: no_save_exit())
    exit.place(x = break_x, y = break_y + 30)

# Add the function that saves the current progress upon closing the window
def save_on_exit():
    # Load the current sheet or create a new one
    df = load_sheet()
    # Safe end time
    new_entry["end"] = time.strftime("%H:%M", time.localtime())
    time_list.append(datetime.now())
    try:
        # Add new total duration using the calc_duration function
        work = datetime(*calc_duration(time_list)[:6])
        break_t = datetime(*time.gmtime(sum(breaks))[:6])
        effective_work = work - break_t
        new_entry["total"] = time.strftime("%H:%M", time.gmtime(effective_work.total_seconds()))
        # Add the break time (if there is no break add 0)
        try:
            new_entry["break"] = time.strftime("%H:%M", time.gmtime(sum(breaks)))
        except:
            new_entry["break"] = "00:00"
        # Appned new entry as row
        df = pd.concat([df, pd.DataFrame([new_entry])], axis = 0, ignore_index = True)
        # Update the total amount of hours done this month
        df_2 = pd.DataFrame(columns = ["timedeltas"])
        ts = pd.Series(df["total"][1:])
        secs = 60 * ts.apply(lambda x: 60 * int(x[:-3]) + int(x[-2:]))
        df_2["timedeltas"] = pd.to_timedelta(secs, "s")
        total_work = df_2["timedeltas"].sum().total_seconds()
        df["total"][0] = f"{int(total_work / 60 / 60)}:{int(total_work / 60 % 60)}"
        # Save
        df.to_csv(f"timesheets_csv/timesheet_{sheet_spec}_{time.strftime('%B', time.localtime()).lower()}.csv",
                 index = False)
        df.to_excel(f"timesheets_xls/timesheet_{sheet_spec}_{time.strftime('%B', time.localtime()).lower()}.xlsx",
                 index = False)
    except:
        pass
    # Close app
    try:
        save_window.destroy()
    except:
        pass
    window.destroy()

# Function that closes the app without saving tracked data
def no_save_exit():
    try:
        save_window.destroy()
    except:
        pass
    window.destroy()
    
def show_window(icon, item):
        icon.stop()
        window.deiconify()
        window.lift()
        window.focus_force()
        
def systray_exit(icon, item):
    icon.stop()
    window.destroy()
    
def systray_save_exit(icon, item):
    # Load the current sheet or create a new one
    df = load_sheet()
    # Safe end time
    new_entry["end"] = time.strftime("%H:%M", time.localtime())
    time_list.append(datetime.now())
    try:
        # Add new total duration using the calc_duration function
        work = datetime(*calc_duration(time_list)[:6])
        break_t = datetime(*time.gmtime(sum(breaks))[:6])
        effective_work = work - break_t
        new_entry["total"] = time.strftime("%H:%M", time.gmtime(effective_work.total_seconds()))
        # Add the break time (if there is no break add 0)
        try:
            new_entry["break"] = time.strftime("%H:%M", time.gmtime(sum(breaks)))
        except:
            new_entry["break"] = "00:00"
        # Appned new entry as row
        df = pd.concat([df, pd.DataFrame([new_entry])], axis = 0, ignore_index = True)
        # Update the total amount of hours done this month
        df_2 = pd.DataFrame(columns = ["timedeltas"])
        ts = pd.Series(df["total"][1:])
        secs = 60 * ts.apply(lambda x: 60 * int(x[:-3]) + int(x[-2:]))
        df_2["timedeltas"] = pd.to_timedelta(secs, "s")
        total_work = df_2["timedeltas"].sum().total_seconds()
        df["total"][0] = f"{int(total_work / 60 / 60)}:{int(total_work / 60 % 60)}"
        # Save
        df.to_csv(f"timesheets_csv/timesheet_{sheet_spec}_{time.strftime('%B', time.localtime()).lower()}.csv",
                 index = False)
        df.to_excel(f"timesheets_xls/timesheet_{sheet_spec}_{time.strftime('%B', time.localtime()).lower()}.xlsx",
                 index = False)
    except:
        pass
    icon.stop()
    window.destroy()
    
def hide_window():
        window.withdraw()
        image = Image.open(".pics/icon2.ico")
        menu = (item("Open", show_window), item("Save&Quit", systray_save_exit), item("Quit", systray_exit))
        icon = pystray.Icon("name", image, "TrackTime", menu)
        icon.run()

#---------------------------------------------------------------------------------------------------------------------------
# Assigne the function save_on_exit to the "x" button that opens the save & exit dialogue
window.protocol("WM_DELETE_WINDOW", hide_window)

window.bind("<Return>", start_tracking)

# Start the app
window.mainloop()