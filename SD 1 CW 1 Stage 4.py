import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Define the Task class to represent each task
class Task:
    def __init__(self, name, description, priority, due_date):
        self.name = name
        self.description = description
        self.priority = priority
        self.due_date = due_date

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date
        }

# Define the TaskManager class to handle task operations
class TaskManager:
    def __init__(self, json_file='tasks.json'):
        self.tasks = []
        self.json_file = json_file
        self.load_tasks_from_json()

    def load_tasks_from_json(self):
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r') as file:
                    task_dicts = json.load(file)
                    self.tasks = [Task(
                        task_dict["name"],
                        task_dict["description"],
                        task_dict["priority"],
                        task_dict["due_date"]
                    ) for task_dict in task_dicts]
                print(f"Loaded {len(self.tasks)} tasks from '{self.json_file}'.")
            else:
                self.tasks = []
                print(f"No existing tasks file found. Starting with empty task list.")
        except json.JSONDecodeError:
            print(f"Error: The file '{self.json_file}' is not a valid JSON file.")
            self.tasks = []
        except Exception as e:
            print(f"Error loading tasks: {str(e)}")
            self.tasks = []

    def save_tasks_to_json(self):
        try:
            with open(self.json_file, 'w') as file:
                task_dicts = [task.to_dict() for task in self.tasks]
                json.dump(task_dicts, file, indent=2)
            return True
        except Exception as e:
            print(f"Error saving tasks: {str(e)}")
            return False

    def add_task(self, task):
        self.tasks.append(task)
        self.save_tasks_to_json()

    def update_task(self, index, task):
        if 0 <= index < len(self.tasks):
            self.tasks[index] = task
            self.save_tasks_to_json()
            return True
        return False

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            self.save_tasks_to_json()
            return True
        return False

    def get_filtered_tasks(self, name_filter=None, priority_filter=None, due_date_filter=None):
        filtered_tasks = self.tasks.copy()
        
        if name_filter and name_filter.strip():
            filtered_tasks = [task for task in filtered_tasks if name_filter.lower() in task.name.lower()]
        
        if priority_filter and priority_filter != "All":
            filtered_tasks = [task for task in filtered_tasks if task.priority == priority_filter]
        
        if due_date_filter and due_date_filter.strip():
            filtered_tasks = [task for task in filtered_tasks if task.due_date == due_date_filter]
        
        return filtered_tasks

    def sort_tasks(self, sort_key='name', reverse=False):
        if sort_key == 'name':
            self.tasks.sort(key=lambda task: task.name.lower(), reverse=reverse)
        elif sort_key == 'priority':
            # Custom priority order: High > Medium > Low
            priority_order = {"High": 1, "Medium": 2, "Low": 3}
            self.tasks.sort(key=lambda task: priority_order.get(task.priority, 4), reverse=reverse)
        elif sort_key == 'due_date':
            self.tasks.sort(key=lambda task: datetime.strptime(task.due_date, "%Y-%m-%d"), reverse=reverse)
        return self.tasks

# Define the TaskManagerGUI class to create the Tkinter interface
class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.task_manager = TaskManager()
        self.setup_gui()
        self.populate_tree()
        
        # Track sorting state
        self.sort_columns = {
            "name": {"order": "", "index": 0},
            "priority": {"order": "", "index": 2},
            "due_date": {"order": "", "index": 3}
        }

    def setup_gui(self):
        # Configure root window
        self.root.title("Personal Task Manager")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create title label
        title_label = ttk.Label(main_frame, text="Personal Task Manager", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Create search and filter frame
        filter_frame = ttk.LabelFrame(main_frame, text="Search and Filter", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Name filter
        ttk.Label(filter_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_filter = ttk.Entry(filter_frame, width=20)
        self.name_filter.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Priority filter
        ttk.Label(filter_frame, text="Priority:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.priority_filter = ttk.Combobox(filter_frame, values=["All", "High", "Medium", "Low"], width=10)
        self.priority_filter.current(0)
        self.priority_filter.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Due date filter
        ttk.Label(filter_frame, text="Due Date (YYYY-MM-DD):").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.due_date_filter = ttk.Entry(filter_frame, width=15)
        self.due_date_filter.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        # Filter button
        self.filter_button = ttk.Button(filter_frame, text="Apply Filter", command=self.apply_filter)
        self.filter_button.grid(row=0, column=6, padx=5, pady=5)
        
        # Clear filter button
        self.clear_button = ttk.Button(filter_frame, text="Clear Filter", command=self.clear_filter)
        self.clear_button.grid(row=0, column=7, padx=5, pady=5)
        
        # Create task treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create Treeview
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Description", "Priority", "Due Date"), 
                                show="headings", yscrollcommand=y_scrollbar.set)
        
        # Configure scrollbars
        y_scrollbar.config(command=self.tree.yview)
        
        # Configure column headings
        self.tree.heading("ID", text="#", command=lambda: self.on_column_click("ID"))
        self.tree.heading("Name", text="Name", command=lambda: self.on_column_click("name"))
        self.tree.heading("Description", text="Description")
        self.tree.heading("Priority", text="Priority", command=lambda: self.on_column_click("priority"))
        self.tree.heading("Due Date", text="Due Date", command=lambda: self.on_column_click("due_date"))
        
        # Configure column widths
        self.tree.column("ID", width=30, anchor=tk.CENTER)
        self.tree.column("Name", width=150, anchor=tk.W)
        self.tree.column("Description", width=300, anchor=tk.W)
        self.tree.column("Priority", width=100, anchor=tk.CENTER)
        self.tree.column("Due Date", width=100, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Create button frame for CRUD operations
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Add buttons for CRUD operations
        self.add_button = ttk.Button(button_frame, text="Add Task", command=self.add_task_dialog)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.edit_button = ttk.Button(button_frame, text="Edit Task", command=self.edit_task_dialog)
        self.edit_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(button_frame, text="Delete Task", command=self.delete_task)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # Sort buttons frame
        sort_frame = ttk.LabelFrame(main_frame, text="Sort Options", padding="10")
        sort_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Sort buttons
        self.sort_name_button = ttk.Button(sort_frame, text="Sort by Name", 
                                          command=lambda: self.sort_tasks("name"))
        self.sort_name_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.sort_priority_button = ttk.Button(sort_frame, text="Sort by Priority", 
                                              command=lambda: self.sort_tasks("priority"))
        self.sort_priority_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.sort_date_button = ttk.Button(sort_frame, text="Sort by Due Date", 
                                          command=lambda: self.sort_tasks("due_date"))
        self.sort_date_button.grid(row=0, column=2, padx=5, pady=5)

    def populate_tree(self, tasks=None):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Use provided tasks or get all tasks
        if tasks is None:
            tasks = self.task_manager.tasks
        
        # Add tasks to treeview
        for i, task in enumerate(tasks, 1):
            self.tree.insert("", "end", values=(i, task.name, task.description, task.priority, task.due_date))

    def apply_filter(self):
        name_filter = self.name_filter.get()
        priority_filter = self.priority_filter.get()
        due_date_filter = self.due_date_filter.get()
        
        filtered_tasks = self.task_manager.get_filtered_tasks(
            name_filter, 
            priority_filter if priority_filter != "All" else None,
            due_date_filter
        )
        
        self.populate_tree(filtered_tasks)

    def clear_filter(self):
        self.name_filter.delete(0, tk.END)
        self.priority_filter.current(0)
        self.due_date_filter.delete(0, tk.END)
        self.populate_tree()

    def on_column_click(self, column):
        if column == "ID":
            return  # Don't sort by ID column
        
        # Toggle sort order
        if self.sort_columns[column]["order"] == "":
            reverse = False
            self.sort_columns[column]["order"] = "asc"
        elif self.sort_columns[column]["order"] == "asc":
            reverse = True
            self.sort_columns[column]["order"] = "desc"
        else:
            reverse = False
            self.sort_columns[column]["order"] = "asc"
        
        # Reset other columns' order
        for col in self.sort_columns:
            if col != column:
                self.sort_columns[col]["order"] = ""
        
        # Sort and update the display
        self.task_manager.sort_tasks(column, reverse)
        self.populate_tree()

    def sort_tasks(self, sort_key):
        # Toggle sort order
        if self.sort_columns[sort_key]["order"] == "":
            reverse = False
            self.sort_columns[sort_key]["order"] = "asc"
        elif self.sort_columns[sort_key]["order"] == "asc":
            reverse = True
            self.sort_columns[sort_key]["order"] = "desc"
        else:
            reverse = False
            self.sort_columns[sort_key]["order"] = "asc"
        
        # Reset other columns' order
        for col in self.sort_columns:
            if col != sort_key:
                self.sort_columns[col]["order"] = ""
        
        # Sort and update the display
        self.task_manager.sort_tasks(sort_key, reverse)
        self.populate_tree()

    def add_task_dialog(self):
        # Create a dialog window for adding a task
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Task")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create form elements
        ttk.Label(dialog, text="Task Name:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Description:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        desc_entry = tk.Text(dialog, width=30, height=5)
        desc_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Priority:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        priority_combo = ttk.Combobox(dialog, values=["High", "Medium", "Low"], width=10)
        priority_combo.current(1)  # Default to Medium
        priority_combo.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        
        ttk.Label(dialog, text="Due Date (YYYY-MM-DD):").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        date_entry = ttk.Entry(dialog, width=15)
        date_entry.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)
        
        def validate_and_save():
            # Get form values
            name = name_entry.get().strip()
            description = desc_entry.get("1.0", tk.END).strip()
            priority = priority_combo.get()
            due_date = date_entry.get().strip()
            
            # Validate input
            if not name:
                messagebox.showerror("Input Error", "Task name cannot be empty!")
                return
            
            if not priority in ["High", "Medium", "Low"]:
                messagebox.showerror("Input Error", "Invalid priority level!")
                return
            
            # Validate date format
            try:
                if due_date:
                    datetime.strptime(due_date, "%Y-%m-%d")
                else:
                    messagebox.showerror("Input Error", "Due date cannot be empty!")
                    return
            except ValueError:
                messagebox.showerror("Input Error", "Invalid date format! Use YYYY-MM-DD.")
                return
            
            # Create and add the task
            new_task = Task(name, description, priority, due_date)
            self.task_manager.add_task(new_task)
            
            # Refresh the tree and close the dialog
            self.populate_tree()
            dialog.destroy()
        
        # Add buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=validate_and_save).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    def edit_task_dialog(self):
        # Get selected item
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please select a task to edit.")
            return
        
        # Get task index (ID from tree - 1)
        item_values = self.tree.item(selected_item[0], "values")
        task_id = int(item_values[0]) - 1
        
        # Check if valid task index
        if task_id < 0 or task_id >= len(self.task_manager.tasks):
            messagebox.showerror("Error", "Invalid task selection.")
            return
        
        # Get the task to edit
        task = self.task_manager.tasks[task_id]
        
        # Create edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Task")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create form elements with current values
        ttk.Label(dialog, text="Task Name:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.insert(0, task.name)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Description:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        desc_entry = tk.Text(dialog, width=30, height=5)
        desc_entry.insert("1.0", task.description)
        desc_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Priority:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        priority_combo = ttk.Combobox(dialog, values=["High", "Medium", "Low"], width=10)
        priority_combo.set(task.priority)
        priority_combo.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        
        ttk.Label(dialog, text="Due Date (YYYY-MM-DD):").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        date_entry = ttk.Entry(dialog, width=15)
        date_entry.insert(0, task.due_date)
        date_entry.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)
        
        def validate_and_update():
            # Get form values
            name = name_entry.get().strip()
            description = desc_entry.get("1.0", tk.END).strip()
            priority = priority_combo.get()
            due_date = date_entry.get().strip()
            
            # Validate input
            if not name:
                messagebox.showerror("Input Error", "Task name cannot be empty!")
                return
            
            if not priority in ["High", "Medium", "Low"]:
                messagebox.showerror("Input Error", "Invalid priority level!")
                return
            
            # Validate date format
            try:
                if due_date:
                    datetime.strptime(due_date, "%Y-%m-%d")
                else:
                    messagebox.showerror("Input Error", "Due date cannot be empty!")
                    return
            except ValueError:
                messagebox.showerror("Input Error", "Invalid date format! Use YYYY-MM-DD.")
                return
            
            # Update the task
            updated_task = Task(name, description, priority, due_date)
            success = self.task_manager.update_task(task_id, updated_task)
            
            if success:
                # Refresh the tree and close the dialog
                self.populate_tree()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to update task.")
        
        # Add buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Update", command=validate_and_update).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    def delete_task(self):
        # Get selected item
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please select a task to delete.")
            return
        
        # Get task index (ID from tree - 1)
        item_values = self.tree.item(selected_item[0], "values")
        task_id = int(item_values[0]) - 1
        task_name = item_values[1]
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the task '{task_name}'?")
        if confirm:
            # Delete task
            success = self.task_manager.delete_task(task_id)
            
            if success:
                # Refresh the tree
                self.populate_tree()
            else:
                messagebox.showerror("Error", "Failed to delete task.")

# Main program execution
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()