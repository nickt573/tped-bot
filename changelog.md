**Updates for week of March 1**
*Changes:*
* Tasks due before the configured day of the week will have an asynchronous reminder at the configured time on set day
* Tasks with a due date will have an asynchronous reminder the day before due date at the configured time
* !set_interval --> !set_disc_time
* !get_interval --> !get_disc_time
* !get_disc_time now reports status
* !enable --> !enable_disc
* !disable --> !disable_disc
* !task --> !tasks
* !tasks manually reports all tasks and is the only way to do so
* Default task reminders 5:00PM --> 4:00PM
* Default discussion interval: 3 days --> 2 days
* !help reformatting

*Additions*
* Weekly tasks automatically remind day before set day
* Specific tasks automatically remind day before due date
* Reminder if changing task or discussion time while disabled

*Removals*
* !status (see !get_disc_time for functionality)

*Code/File System*
* Renamed util files to more accurately describe purpose
* Reorganized main file by bot functionality 
* Added changelog and README to GitHub
* Standardized timezone procedures
* Delete branch history for security

**Updates for week of February 22**
*Changes*:
* !get has been changed to !pull

*Additions*
* Re-added scheduling capabilities with !schedule
* Added asynchronous E-Board task reminders linked to Google Sheets
* Added several commands to customize task reminding (time interval, manual reminders, disable reminders)
* Added pie warnings to members with several incomplete tasks

*Removals*
None

--> For a complete view of the changes, visit https://github.com/nickt573/tped-bot
