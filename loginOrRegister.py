from pymongo import MongoClient
from datetime import datetime, timedelta
import bcrypt

# MongoDB connection string
conn_string = "mongodb+srv://"-----":ruA1qSmaCxb4Hgs5@cluster0.tngwqyo.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(conn_string)
db = client['user-database']
users_collection = db['users']



def process_request(request):
    # Splitting the request 
    parts = request.split(":")
    command = parts[0]
    arguments = parts[1].split(",") if len(parts) > 1 else []

    try:
        if command == "login" and len(arguments) == 2:
            return login(*arguments)
        elif command == "register" and len(arguments) == 6:
            return register(*arguments)
        elif command == "reset_password" and len(arguments) == 3:
            return reset_password(*arguments)
        elif command == "add_task" and len(arguments) == 5:
            return addingTasks(*arguments)
        elif command == "show_lists" and len(arguments) == 1:
            return show_lists(*arguments)
        elif command == "change_task_status" and len(arguments) == 4:
            return change_task_status(*arguments) 
        elif command == "change_task_deadline" and len(arguments) == 4:
            return change_task_deadline(*arguments)
        else:
            return "Unknown command or incorrect arguments."
    except Exception as e:
        return f"Error processing request. Please contact support."

#login function helps user login anf after login it notify the user above the
#tasks that are need to be done in next 7 days.
def login(username, password, attempts=3):

    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return notify(username)
    else:
        attempts -= 1
        if attempts > 0:
            return f"Invalid username or password. Attempts remaining: {attempts}"
        else:
            return "Login failed. No attempts remaining. Choose 1 to register, 2 to reset password."

#helps user register
def register(name, lastname, username, email, postalcode, password):
    
     # Check if a user with the same username already exists
    if users_collection.find_one({"username": username}):
        return "A user with this username already exists."

     # Hash the user's password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


    # Create a new user
    new_user = {
        "name": name,
        "lastname": lastname,
        "username": username,
        "email": email,
        "postalcode": postalcode,
        "password": hashed_password
    }

    #adds data to database
    users_collection.insert_one(new_user)
    return "Registration successful! Welcome to ProNote: An Advanced To-Do List Application"

#user can reset password
def reset_password(email, new_password, re_type_new_password):
    # Check if the new passwords match
    if new_password != re_type_new_password:
        return "Passwords do not match."

    # Find the user by email
    user = users_collection.find_one({"email": email})
    if not user:
        return "No account found with that email."

    # Hash the new password
    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    # Update the user's password in the database
    users_collection.update_one({"email": email}, {"$set": {"password": hashed_new_password}})
    return "Password reset successfully."

def notify(username):
    result ="The tasks due in next 7 days:\n"
    user = users_collection.find_one({"username": username})
    
    # Check if the user exists
    if user is None:
        return "User not found."

    
    if "Lists" in user:
        lists = user["Lists"]
        for list_name, tasks in lists.items():
            result += f"List: {list_name}\n"

            # Check if tasks is a list
            if isinstance(tasks, list):
                for task_details in tasks:
                    deadline_date = datetime.strptime(task_details['deadline'], "%Y-%m-%d")
                    if deadline_Check(deadline_date):
                        result += f"  Task: {task_details['task']}\n"
                        result += f"    Status: {task_details['status']}\n"
                        result += f"    Deadline: {task_details['deadline']}\n"

                return result
    else:
        print("No lists found for this user.")


def deadline_Check(deadline_date):
    
    # Get the current date and time
    current_date = datetime.now()
    
    one_week_later = current_date + timedelta(days=7)
    
    # Check if the deadline_date is within the next 7 days
    deadline =current_date <= deadline_date <= one_week_later
    return deadline
    
def show_lists(username):
    result ="List of all the tasks\n"
    
    # Find the user document in the database
    user = users_collection.find_one({"username": username})
    if user is None:
        return "User not found."

    if "Lists" in user:
        lists = user["Lists"]
        for list_name, tasks in lists.items():
            result += f"List: {list_name}\n"

            # Check if tasks is a list
            if isinstance(tasks, list):
                for task_details in tasks:
                    result += f"  Task: {task_details['task']}\n"
                    result += f"    Status: {task_details['status']}\n"
                    result += f"    Deadline: {task_details['deadline']}\n"

                return result
    else:
        print("No lists found for this user.")

def addingTasks(username, list_name, task,important, deadline):
    if not username or not list_name or not task:
        return "Missing username, list name, or tasks."
        
    # Initialize a dictionary to store task details
    tasks={}
    
    try:
        datetime.strptime(deadline, "%Y-%m-%d")
        tasks[task] = {"status": "Not Completed", "important": important,"deadline": deadline}
    except ValueError:
        print("Invalid date format, please try again.")
    
    # Update the user's document in the database
    update_result = users_collection.update_one(
        {"username": username},
        {"$push": {f"Lists.{list_name}": {"$each": [{"task": task, "status": "Not Completed", "important": important,"deadline": deadline}]}}},
        upsert=True
    )

    # Check if the update was successful
    if update_result.modified_count:
        return f"Task '{task}' added to list '{list_name}' successfully."
    else:
        return "No changes made to the database."

def change_task_status(username, list_name, task, new_status):
    user = users_collection.find_one({"username": username})
    if not user or list_name not in user.get("Lists", {}):
        return "User or list not found."
        
    # Updating the task status
    for task_details in user["Lists"][list_name]:
        if task_details['task'] == task:
            task_details['status'] = new_status
            users_collection.update_one(
                {"username": username},
                {"$set": {f"Lists.{list_name}": user["Lists"][list_name]}}
            )
            return "Task status updated successfully."

    return "Task not found."

def change_task_deadline(username, list_name, task, new_deadline):
    user = users_collection.find_one({"username": username})
    if not user or list_name not in user.get("Lists", {}):
        return "User or list not found."

    try:
        datetime.strptime(new_deadline, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format, please use YYYY-MM-DD."
    
    # Updating the task deadline
    for task_details in user["Lists"][list_name]:
        if task_details['task'] == task:
            task_details['deadline'] = new_deadline
            users_collection.update_one(
                {"username": username},
                {"$set": {f"Lists.{list_name}": user["Lists"][list_name]}}
            )
            return "Task deadline updated successfully."

    return "Task not found."
