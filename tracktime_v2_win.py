# Load dependencies for the app
import tkinter as tk
import tkinter.ttk as ttk
from PIL import ImageTk, Image
from ttkthemes import ThemedTk
import pandas as pd
import time
from datetime import datetime, timedelta
from pystray import MenuItem as item
import pystray
from sys import platform

path = ""

if platform == "linux" or platform == "linux2":
    canvas_spec = 1
else:
    canvas_spec = 2

# First I create/load in a csv file containig the infrastructure for keeping the data in a nice and tidy format
def new_sheet():
    df = pd.DataFrame(data=None, columns=["date", "start", "break", "end", "total"])

    total_row = {
        "date": f"{sheet_spec}_{time.strftime('%B_%y', time.localtime()).lower()}",
        "total": 0,
    }

    df = pd.concat([df, pd.DataFrame([total_row])], axis=0, ignore_index=True)

    return df


# First I try to load the sheet of the current month but if that fails it creates a new sheet and loads that
def load_sheet():
    try:
        return pd.read_csv(
            f"{path}timesheets_csv/timesheet_{sheet_spec}_{time.strftime('%B', time.localtime()).lower()}.csv"
        )

    except:
        return new_sheet()


# ---------------------------------------------------------------------------------------------------------------

# Now for the tkinter app and interface
# Create the window using a "modern" look
window = ThemedTk(theme="equilux")

# Get screen width and height of the respective pc screen and set some variables
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
time_x = 50
time_y = 20
break_x = 50
break_y = 50

# Use determined screen properties to scale the window size and coordinates (works perfectly for my pc)
width = int(screen_width / 4)

height = int(screen_height / 4)

x = (screen_width) - (width + 3)
y = (screen_height) - (height + 74)

window.geometry(
    "%dx%d+%d+%d" % (width, height, x, y)
)  # Assign the geometry to the window

window.title("TrackTime")  # Assign title

window.resizable(False, False)  # Set resizable to "False" so window can't be resized

background = Image.open(
    f"{path}.pics/background1.jpg"
)  # Set a background image for the app

background = background.resize((width, height))  # Resize the image to fit window size

background = ImageTk.PhotoImage(background)  # Set picture as background

canvas = tk.Canvas(
    window, width=width, height=height
)  # Create a canvas on which to put the image

canvas.place(
    x=-canvas_spec, y=-canvas_spec
)  # Place the canvas (minus values so there are no white borders)

canvas.create_image(canvas_spec, canvas_spec, image=background, anchor="nw")  # Finalize background

# Change icon of window
window.iconbitmap(".pics/icon2.ico")

# Initialize an empty dic that serves as new "row" in the df
new_entry = {"date": time.strftime("%d.%m.%Y", time.localtime())}


# Create lists for the start/end time and break start/end as well as the duration of all summed breaks
start_time = []
end_time = []
break_list = []
breaks = []

# Define a list that must be empty for the stopwatch to run and stops the watch if it's filled
stopwatch_criteria = []
crit = 1  # Stopwatch criteria


# Create input filed for sheet specification
sheet_spec_field = ttk.Entry(window, justify=tk.CENTER)

sheet_spec_field.place(x=time_x, y=280)

sheet_spec_field.focus()

break_start = ttk.Button(window, text="Start break", command=lambda: start_break())

break_end = ttk.Button(window, text="End break", command=lambda: end_break())


# ---------------------------------------------------------------------------------------------------------------------------


# Function that displays and starts the break stop watch
def break_time_disp():
    break_time_label = ttk.Label(window, font=("calibri", 20, "bold"))

    break_time_label.place(x=time_x, y=time_y * 4)

    break_duration = datetime.now() - break_list[-1]

    break_time_label.config(text=str(break_duration)[0:-10])

    if crit not in stopwatch_criteria:
        break_time_label.after(
            1000, lambda: [break_time_label.destroy(), break_time_disp()]
        )

    else:
        break_time_label.after(5000, break_time_label.destroy)


# Create the respective function for the start button that starts tracking and disables further interaction with the button
def start_tracking(event):
    window.bind("<Return>", pass_func)

    start_time.append(datetime.now())

    global sheet_spec
    # Get the content of the input field and close it once start is pressed
    sheet_spec = sheet_spec_field.get()
    sheet_spec_field.destroy()
    window.title(f"Project: {sheet_spec}")

    break_start.place(x=break_x, y=break_y)

    start_time_button = ttk.Label(
        window,
        text=start_time[-1].strftime("%H:%M"),
        font=("calibri", 8, "bold"),
    )

    start_time_button.place(x=time_x, y=time_y)


# Start the break and save the starting time for future
def start_break():
    if stopwatch_criteria != []:
        stopwatch_criteria.remove(crit)

    stopwatch_criteria.append(0)

    break_list.append(datetime.now())

    break_start.place_forget()

    # Once the break is started the "End break" button appears
    break_end.place(x=break_x, y=break_y)

    # The stopwatch is displayed and starts to stop break duration
    break_time_disp()


def end_break():
    break_list.append(datetime.now())

    stopwatch_criteria.append(crit)

    breaks.append((break_list[-1] - break_list[-2]))

    break_end.place_forget()

    break_start.place(x=break_x, y=break_y)


# Helper function that calculates the hours/mins between two timedeltas
def calc_duration():
    return end_time[-1] - start_time[-1]


# Get window back from sys tray
def show_window(icon, item):
    icon.stop()
    window.deiconify()
    window.lift()
    window.focus_force()


# Function that closes the app without saving tracked data
def systray_exit(icon, item):
    window.destroy()
    icon.stop()


def systray_save_exit(icon, item):
    if 0 in stopwatch_criteria and crit not in stopwatch_criteria:
        end_break()

    # Load the current sheet or create a new one
    df = load_sheet()
    # Safe end time
    end_time.append(datetime.now())

    last_index = len(df) - 1

    if new_entry["date"] != df["date"][len(df) - 1]:
        new_entry["start"] = start_time[-1].strftime("%H:%M")
        new_entry["end"] = end_time[-1].strftime("%H:%M")

        try:
            # Add new total duration using the calc_duration function
            work_time = end_time[-1] - start_time[-1]

            break_time = sum(breaks, timedelta())

            effective_work = work_time - break_time

            new_entry["total"] = delta_to_string(effective_work)

            # Add the break time (if there is no break add 0)
            try:
                new_entry["break"] = delta_to_string(break_time)

            except:
                new_entry["break"] = "00:00"
            # Appned new entry as row
            df = pd.concat([df, pd.DataFrame([new_entry])], axis=0, ignore_index=True)

            # Update the total amount of hours done this month
            df_2 = pd.DataFrame(columns=["timedeltas"])

            ts = pd.Series(df["total"][1:])

            secs = 60 * ts.apply(lambda x: 60 * int(x[:-3]) + int(x[-2:]))

            df_2["timedeltas"] = pd.to_timedelta(secs, "s")

            total_work = df_2["timedeltas"].sum()

            df["total"][0] = delta_to_string(total_work)
            # Save
            df.to_csv(
                f"{path}timesheets_csv/timesheet_{sheet_spec}_{time.strftime('%B', time.localtime()).lower()}.csv",
                index=False,
            )

            df.to_excel(
                f"{path}timesheets_xls/timesheet_{sheet_spec}_{time.strftime('%B', time.localtime()).lower()}.xlsx",
                index=False,
            )

        except:
            pass

    else:
        # Add new total duration using the calc_duration function
        earlier_break_sum = timedelta(
            hours=int(df["break"][last_index][0:2]),
            minutes=int(df["break"][last_index][3:5]),
        )

        session_start = timedelta(
            hours=int(str(start_time[-1])[11:13]),
            minutes=int(str(start_time[-1])[14:16]),
        )

        session_end = timedelta(
            hours=int(str(end_time[-1])[11:13]), minutes=int(str(end_time[-1])[14:16])
        )

        prev_session_end = timedelta(
            hours=int(df["end"][last_index][0:2]),
            minutes=int(df["end"][last_index][3:5]),
        )

        prev_session_start = timedelta(
            hours=int(df["start"][last_index][0:2]),
            minutes=int(df["start"][last_index][3:5]),
        )

        work_time = session_end - prev_session_start

        df["end"][len(df) - 1] = end_time[-1].strftime("%H:%M")

        try:
            break_sum = sum(breaks, timedelta())
            break_time = (
                break_sum + earlier_break_sum + (session_start - prev_session_end)
            )
        except:
            break_time = earlier_break_sum + (session_start - prev_session_end)

        if (work_time - break_time) > timedelta(seconds=0):
            effective_work = work_time - break_time
        else:
            effective_work = timedelta(seconds=0)

        df["break"][len(df) - 1] = delta_to_string(break_time)

        df["total"][len(df) - 1] = delta_to_string(effective_work)

        # Update the total amount of hours done this month
        df_2 = pd.DataFrame(columns=["timedeltas"])

        ts = pd.Series(df["total"][1:])

        secs = 60 * ts.apply(lambda x: 60 * int(x[:-3]) + int(x[-2:]))

        df_2["timedeltas"] = pd.to_timedelta(secs, "s")

        total_work = df_2["timedeltas"].sum()

        df["total"][0] = delta_to_string(total_work)
        # Save
        df.to_csv(
            f"{path}timesheets_csv/timesheet_{sheet_spec}_{time.strftime('%B', time.localtime()).lower()}.csv",
            index=False,
        )

        df.to_excel(
            f"{path}timesheets_xls/timesheet_{sheet_spec}_{time.strftime('%B', time.localtime()).lower()}.xlsx",
            index=False,
        )

    icon.stop()
    window.destroy()


def hide_window():
    window.withdraw()
    tray_icon()


def tray_icon():
    tray_image = Image.open(f"{path}.pics/icon2.ico")

    menu = (
        item("Open", show_window),
        item("Save&Quit", systray_save_exit),
        item("Quit", systray_exit),
    )

    icon = pystray.Icon("name", tray_image, "TrackTime", menu)

    icon.run()


def pass_func(event):
    pass


def delta_to_string(delta):
    hours, remainder = divmod(delta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    # Reshape
    return f"{int(hours):02}:{int(minutes):02}"


# ---------------------------------------------------------------------------------------------------------------------------

# Assign the function save_on_exit to the "x" button that opens the save & exit dialogue
window.protocol("WM_DELETE_WINDOW", hide_window)

window.bind("<Return>", start_tracking)

# Start the app
window.mainloop()