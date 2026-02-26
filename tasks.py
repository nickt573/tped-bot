import gspread
from google.oauth2.service_account import Credentials

IDs = {
    "PRESIDENT": 928901718161391677,
    "VICE PRESIDENT": 343055950229405696,
    "TREASURER": 232914628177297408,
    "SECRETARY": 460826614368960512,
    "HISTORIAN": 699427677383294986,
    "EVENTS COORDINATOR": 1389031753766666371,
    "PUBLIC RELATIONS 0": 764647197438246942, # Suta
    "PUBLIC RELATIONS 1": 699288806129664061 # Grace
}

class Task:
    def __init__(self, title, due_date, task_type, status):
        self.title = title
        self.due_date = due_date   # date or None
        self.task_type = task_type # specific or weekly
        self.status = status

def get_tasks():
    tasks = {}
    pie = {}
    try:
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        creds = Credentials.from_service_account_file(
        "trim-sum-488518-f5-6cb113ea1c8b.json",
        scopes=SCOPES
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_url(
            "https://docs.google.com/spreadsheets/d/10Zr7n1pl_yXPaeptUzy-Poep_TsZ3nmS5y-CmoFt09A/edit?gid=1705587382#gid=1705587382"
        )
        worksheets = spreadsheet.worksheets()

        for ws in worksheets[:8]:
            role = ws.title
            try:
                rows = ws.get_all_values()
            except Exception as e:
                print(f"Failed to read tab {role}: {e}")
                continue
            if not rows or len(rows) < 2:
                print("Tab is empty or has no data rows.")
                continue

            if role == "🥧":
                row = rows[1]
                for r, k in zip(row[:7], IDs.keys()):
                    pie[k] = int(r)
                    if k == "PUBLIC RELATIONS 0":
                        pie["PUBLIC RELATIONS 1"] = int(r)
            elif role == "PUBLIC RELATIONS":
                specific_tasks_0= []
                specific_tasks_1 = []
                weekly_tasks = []

                for row in rows[2:]:
                    while len(row) < 6:
                        row.append("")
                    specific_title_0 = row[0].strip()
                    specific_title_1 = row[1].strip()
                    due_date = row[2].strip()
                    if due_date and due_date == "--":
                        due_date = "N/A"
                    status = row[3].strip()
                    # PR 0 specific tasks
                    if specific_title_0 and specific_title_0 != "--" and (status != "COMPLETED" and status != "DISMISSED"):
                        specific_tasks_0.append(
                            Task(
                                title=specific_title_0,
                                due_date=due_date,
                                task_type="specific",
                                status=status
                            )
                    )
                    # PR 1 specific tasks
                    if specific_title_1 and specific_title_1 != "--" and (status != "COMPLETED" and status != "DISMISSED"):
                        specific_tasks_1.append(
                            Task(
                                title=specific_title_1,
                                due_date=due_date,
                                task_type="specific",
                                status=status
                            )
                        )     
                    # PR 1 and 2 weekly tasks
                    weekly_title = row[4].strip()
                    status = row[5].strip()
                    if weekly_title and (status != "COMPLETED" and status != "DISMISSED"):
                        weekly_tasks.append(
                                Task(
                                    title=weekly_title,
                                    due_date=None,
                                    task_type="weekly",
                                    status=status
                                )
                            )
                tasks["PUBLIC RELATIONS 0"] = specific_tasks_0 + weekly_tasks
                tasks["PUBLIC RELATIONS 1"] = specific_tasks_1 + weekly_tasks
            else:
                # Rest of team tasks
                specific_tasks = []
                weekly_tasks = []
                for row in rows[1:]:
                    while len(row) < 6:
                        row.append("")
                    specific_title = row[0].strip()
                    due_date = row[1].strip()
                    if due_date and due_date == "--":
                        due_date = "N/A"
                    weekly_title = row[3].strip()

                    # Specific task
                    status = row[2].strip()
                    if specific_title and (status != "COMPLETED" and status != "DISMISSED") :
                        specific_tasks.append(
                            Task(
                                title=specific_title,
                                due_date=due_date,
                                task_type="specific",
                                status=status
                            )
                        )
                    # Weekly task
                    status = row[4].strip()
                    if weekly_title and (status != "COMPLETED" and status != "DISMISSED") :
                        weekly_tasks.append(
                            Task(
                                title=weekly_title,
                                due_date=None,
                                task_type="weekly",
                                status=status
                            )
                        )
                    tasks[role] = specific_tasks + weekly_tasks

        return tasks, pie
    except Exception as e:
        print(f"Failed to parse tasks sheet, {e}")
    
def get_pie():
    import random
    warnings = [
        "Better finish those tasks… or I hope you like pie in the face",
        "Let me know how the pie tastes",
        "You’ve earned yourself dessert… it’s coming at you, full speed",
        "Tasks unfinished = face-full of pie",
        "Hope you enjoy whipped cream in your hair",
        "Procrastination smells like pie… soon, you’ll taste it too",
        "Some people chase success… you apparently chase pie",
        "Warning: Ignoring tasks may lead to severe pastry consequences",
        "A friendly reminder: the pie has your name on it",
        "Tasks pending? Pie incoming. I hope you like pumpkin",
        "You can’t outrun the pie, but you can try finishing your work",
        "Pro tip: finishing tasks reduces your pie exposure",
        "This is your official warning: pies are literal",
        "Face it: the pie knows your to-do list better than you do",
        "If you ignore your tasks, the pie will introduce itself personally",
        "Some deadlines bring stress. Yours bring pie",
        "I hope you like your desserts cold… because they’re coming soon",
        "You’ve got three strikes… the pie doesn’t forget",
        "Completing work keeps pies off your face. You choose",
        "Finish your tasks or the pie finishes you",
        "Your face has been scheduled for dessert",
        "Completion is optional; pie is guaranteed",
        "The pastry of justice awaits the negligent",
        "Tasks avoided are pies deployed"
    ]
    return random.choice(warnings)