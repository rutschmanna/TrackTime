# TrackTime
Official GitHub Repo of the TrackTime personal time tracking and scheduling app for Microsoft Windows 11.

# Installation
## Setup
You will need to enter the .pics folder and specify your desired background as well as the desired app icon. The background needs to be saves as "background1.jpg" and the icon must be saved as "icon2.ico".
Note: If you do not exactly copy the file names the app won't run.

## Run the App
1. Via .exe
Open the .exe file and you are promted to enter the name of your current task (eg. my_personal_project). Confirm by pressing the enter-button. The app creates a new timetable with that name and the current month if there is no such timetable already existing. Otherwise it will load the respective timetable and add your trackings to it.
Sadly there is no way to customize the app if you use the .exe approach.
2. Via source code
You can easily open the .py file and edit it to your hearts content. Using pyinstaller or some other means, you can then convert your .py file into a .exe file and run that one on your machine.

# Access your data
The app saves the data of your tracked hours in the timesheets_csv/timesheets_xls folders by default. The paths can be changed if you modify the source code and create a .exe file using the approach described above (2).
If you use the default safe location you can just create a shortcut to the timesheets_csv or timesheets_xls folder and comfortably access them from any other location on your machine.

# System Setup
The .exe file is tuned to work on a Microsoft Windows 11 machine with WQHD display (2560x1600) and a Scale ratio of 125% (Settings > System > Display > Scale).
For other setups the app might be off centre (which can be changed in the source code though)

# Feedback and Improvement
Feel free to contact me regarding possible improvements and such. I am no tkinter expert by any means and do not claim the impeccability of the app.

# Open Source
Have fun and share :)
