import datetime
import pickle
import json
import tkinter as tk
from tkinter import messagebox
from plyer import notification
import threading
import time

class TimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.time):
            return obj.strftime("%I:%M %p")
        return super().default(obj)
class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DailyNeedsReminder")
        self.reminders = self.load_reminders()
        self.timer_thread = threading.Thread(target=self.check_reminders_loop, daemon=True)

        # GUI Components
        self.task_entry = tk.Entry(root, width=30)
        self.time_entry = tk.Entry(root, width=15)
        self.am_pm_var = tk.StringVar()
        self.am_pm_var.set("AM")  # Default choice
        self.reminder_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50, height=10)

        # Layout
        self.task_entry.grid(row=0, column=0, padx=10, pady=10)
        self.time_entry.grid(row=0, column=1, padx=10, pady=10)
        tk.OptionMenu(self.root, self.am_pm_var, "AM", "PM").grid(row=0, column=2, padx=10, pady=10)
        self.reminder_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # Buttons
        tk.Button(root, text="Add Reminder", command=self.add_reminder).grid(row=2, column=0, pady=10)
        tk.Button(root, text="View Reminders", command=self.view_reminders).grid(row=2, column=1, pady=10)
        tk.Button(root, text="Delete Reminder", command=self.delete_reminder).grid(row=2, column=2, pady=10)

        self.timer_thread.start()

    def add_reminder(self):
        task = self.task_entry.get()
        time_str = self.time_entry.get()
        am_pm = self.am_pm_var.get()

        if task and time_str and am_pm:
            try:
                time_format = "%I:%M %p"
                time_str = f"{time_str} {am_pm.upper()}"
                time = datetime.datetime.strptime(time_str, time_format).time()

                self.reminders.append({'task': task, 'time': time})
                self.save_reminders()
                self.show_notification(task)
                messagebox.showinfo("Success", "Reminder added successfully!")
                self.task_entry.delete(0, tk.END)
                self.time_entry.delete(0, tk.END)
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid time format. {str(e)}")
        else:
            messagebox.showwarning("Warning", "Task, time, and AM/PM cannot be empty.")


    def view_reminders(self):
        self.reminder_listbox.delete(0, tk.END)
        for reminder in self.reminders:
            self.reminder_listbox.insert(tk.END, f"{reminder['task']} - {reminder['time']}")

    def delete_reminder(self):
        selected_index = self.reminder_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            del self.reminders[index]
            self.save_reminders()
            self.view_reminders()
            messagebox.showinfo("Success", "Reminder deleted successfully!")
        else:
            messagebox.showwarning("Warning", "Please select a reminder to delete.")

    def save_reminders(self):
        with open('reminders.json', 'w') as file:
            json.dump(self.reminders, file, cls=TimeEncoder)


    def load_reminders(self):
        try:
            with open('reminders.json', 'r') as file:
                data = file.read()
                if not data:
                    return []
                return json.loads(data)
        except FileNotFoundError:
            return []
        except json.decoder.JSONDecodeError:
            return []
        

    def check_reminders_loop(self):
        while True:
            current_time = datetime.datetime.now().strftime('%I:%M %p')
            for reminder in self.reminders:
                if current_time >= reminder['time']:
                    self.show_notification(reminder['task'])
                    self.reminders.remove(reminder)  # Remove the reminder after notifying
                    self.save_reminders()

            # Check for reminders every minute
            time.sleep(60)

    def show_notification(self, task):
        notification.notify(
            title='Reminder',
            message=f"It's time for {task}!",
        )

    def create_widgets(self):
       

        # AM/PM Choice
        am_pm_choices = ['AM', 'PM']
        self.am_pm_var = tk.StringVar()
        self.am_pm_var.set(am_pm_choices[0])  # Default choice
        am_pm_menu = tk.OptionMenu(self.root, self.am_pm_var, *am_pm_choices)
        am_pm_menu.grid(row=1, column=2, padx=10, pady=10)

def main():
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()