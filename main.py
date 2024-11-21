import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import calendar

class SchedulingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scheduling App")
        self.geometry("1200x800")

        # Initialize scheduled_events list before creating the UI
        self.scheduled_events = []
        self._drag_data = None

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # First tab - Original view
        self.original_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.original_tab, text='List View')

        # Second tab - Gantt chart
        self.gantt_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.gantt_tab, text='Gantt Chart')

        # Initialize both views
        self.setup_original_view()
        self.setup_gantt_view()

    def setup_original_view(self):
        # Frame for the treeview and scrollbar
        tree_frame = tk.Frame(self.original_tab)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tree_scroll = tk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the tree structure
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.tree.yview)

        # Add departments
        self.department1 = self.tree.insert("", "end", "department1", text="Department 1")
        self.department2 = self.tree.insert("", "end", "department2", text="Department 2")

        # Department management buttons
        self.department_buttons_frame = tk.Frame(self.original_tab)
        self.department_buttons_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.add_department_button = tk.Button(self.department_buttons_frame, text="Add Department", command=self.add_department)
        self.edit_department_button = tk.Button(self.department_buttons_frame, text="Edit Department", command=self.edit_department)
        self.delete_department_button = tk.Button(self.department_buttons_frame, text="Delete Department", command=self.delete_department)

        self.add_department_button.pack(side=tk.LEFT)
        self.edit_department_button.pack(side=tk.LEFT)
        self.delete_department_button.pack(side=tk.LEFT)

        # Original calendar view setup
        calendar_frame = tk.Frame(self.original_tab)
        calendar_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        calendar_scroll = tk.Scrollbar(calendar_frame, orient="horizontal")
        calendar_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.calendar = ttk.Treeview(calendar_frame, columns=("staff_needed", "event_duration", "equipment_needed"), xscrollcommand=calendar_scroll.set)
        self.calendar.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        calendar_scroll.config(command=self.calendar.xview)
        
        self.calendar.heading("#0", text="Event")
        self.calendar.heading("staff_needed", text="Staff Breakdown")
        self.calendar.heading("event_duration", text="Event Duration")
        self.calendar.heading("equipment_needed", text="Equipment Needed")

        # Event management setup
        self.setup_event_management(self.original_tab)

    def setup_gantt_view(self):
        # Top control panel for Gantt chart
        control_frame = tk.Frame(self.gantt_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Date navigation
        self.prev_week_btn = tk.Button(control_frame, text="◀ Previous Week", command=self.prev_week)
        self.prev_week_btn.pack(side=tk.LEFT, padx=5)
        
        self.current_date = datetime.now()
        self.date_label = tk.Label(control_frame, text=self.get_week_range_text())
        self.date_label.pack(side=tk.LEFT, padx=10)
        
        self.next_week_btn = tk.Button(control_frame, text="Next Week ▶", command=self.next_week)
        self.next_week_btn.pack(side=tk.LEFT, padx=5)

        # Create Gantt chart canvas with scrollbar
        self.gantt_frame = tk.Frame(self.gantt_tab)
        self.gantt_frame.pack(fill=tk.BOTH, expand=True)

        # Add vertical scrollbar
        self.v_scrollbar = tk.Scrollbar(self.gantt_frame, orient="vertical")
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add horizontal scrollbar
        self.h_scrollbar = tk.Scrollbar(self.gantt_frame, orient="horizontal")
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create canvas
        self.gantt_canvas = tk.Canvas(self.gantt_frame, bg='white',
                                    xscrollcommand=self.h_scrollbar.set,
                                    yscrollcommand=self.v_scrollbar.set)
        self.gantt_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbars
        self.h_scrollbar.config(command=self.gantt_canvas.xview)
        self.v_scrollbar.config(command=self.gantt_canvas.yview)

        # Bind mouse events for drag and drop
        self.gantt_canvas.tag_bind("event_block", "<Button-1>", self.start_drag)
        self.gantt_canvas.tag_bind("event_block", "<B1-Motion>", self.drag)
        self.gantt_canvas.tag_bind("event_block", "<ButtonRelease-1>", self.drop)

        # Initial draw
        self.draw_gantt_chart()

    def get_week_range_text(self):
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return f"{start_of_week.strftime('%B %d')} - {end_of_week.strftime('%B %d, %Y')}"

    def setup_event_management(self, parent):
        self.event_buttons_frame = tk.Frame(parent)
        self.event_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.staff_inputs_frame = tk.Frame(self.event_buttons_frame)
        self.staff_inputs_frame.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=10)

        # Staff input fields
        labels = ["Prod. Manager:", "Audio Techs:", "Lighting Techs:", "Stage Crew:"]
        self.staff_inputs = {}
        
        for i, label in enumerate(labels):
            tk.Label(self.staff_inputs_frame, text=label).grid(row=0, column=i*2)
            entry = tk.Entry(self.staff_inputs_frame, width=5)
            entry.grid(row=0, column=i*2+1)
            self.staff_inputs[label] = entry

        # Event management buttons
        self.add_event_button = tk.Button(self.event_buttons_frame, text="Add Event", command=self.add_event)
        self.edit_event_button = tk.Button(self.event_buttons_frame, text="Edit Event", command=self.edit_event)
        self.delete_event_button = tk.Button(self.event_buttons_frame, text="Delete Event", command=self.delete_event)

        self.add_event_button.pack(side=tk.LEFT)
        self.edit_event_button.pack(side=tk.LEFT)
        self.delete_event_button.pack(side=tk.LEFT)

    def draw_gantt_chart(self):
        self.gantt_canvas.delete("all")
        
        # Calculate dimensions
        hours_per_day = 24
        hour_width = 50
        row_height = 40
        header_height = 50
        total_width = hours_per_day * 7 * hour_width
        total_height = max(500, len(self.scheduled_events) * row_height + header_height)
        
        # Configure canvas scrollable area
        self.gantt_canvas.configure(scrollregion=(0, 0, total_width, total_height))
        
        # Draw time grid
        for day in range(7):
            date = self.current_date - timedelta(days=self.current_date.weekday()) + timedelta(days=day)
            day_label = date.strftime('%A\n%m/%d')
            
            # Draw day header
            x = day * hours_per_day * hour_width
            self.gantt_canvas.create_text(
                x + (hours_per_day * hour_width) / 2,
                header_height / 2,
                text=day_label,
                font=('Arial', 10, 'bold')
            )
            
            # Draw vertical day separator
            self.gantt_canvas.create_line(
                x, 0,
                x, total_height,
                fill='gray80'
            )
            
            # Draw hour lines and labels
            for hour in range(hours_per_day + 1):
                x = (day * hours_per_day + hour) * hour_width
                # Vertical hour line
                self.gantt_canvas.create_line(
                    x, header_height,
                    x, total_height,
                    fill='gray90'
                )
                
                # Hour label
                if hour < hours_per_day:
                    self.gantt_canvas.create_text(
                        x + hour_width/2,
                        header_height - 10,
                        text=f"{hour:02d}:00",
                        font=('Arial', 8)
                    )

        # Draw events
        for i, event in enumerate(self.scheduled_events):
            self.draw_event_block(event, i, row_height, header_height)

    def draw_event_block(self, event, index, row_height, header_height):
        hour_width = 50
        event_height = row_height - 10
        
        # Calculate position
        start_x = event['start_time'] * hour_width
        width = event['duration'] * hour_width
        y = header_height + (index * row_height) + 5
        
        # Create event block with rounded corners
        block = self.gantt_canvas.create_rectangle(
            start_x, y,
            start_x + width, y + event_height,
            fill='lightblue',
            outline='steelblue',
            tags=("event_block", f"event_{event['id']}"),
            width=2
        )
        
        # Add event label
        self.gantt_canvas.create_text(
            start_x + width/2,
            y + event_height/2,
            text=f"{event['name']} ({event['duration']}h)",
            tags=("event_block", f"event_{event['id']}"),
            font=('Arial', 9, 'bold')
        )

    def start_drag(self, event):
        closest = self.gantt_canvas.find_closest(event.x, event.y)
        if "event_block" in self.gantt_canvas.gettags(closest):
            self._drag_data = {
                'x': event.x,
                'y': event.y,
                'item': closest
            }

    def drag(self, event):
        if self._drag_data:
            dx = event.x - self._drag_data['x']
            tags = self.gantt_canvas.gettags(self._drag_data['item'])
            for item in self.gantt_canvas.find_withtag(tags[1]):
                self.gantt_canvas.move(item, dx, 0)
            self._drag_data['x'] = event.x

    def drop(self, event):
        if self._drag_data:
            hour_width = 50
            new_time = max(0, int(event.x / hour_width))
            tags = self.gantt_canvas.gettags(self._drag_data['item'])
            event_id = int(tags[1].split('_')[1])
            
            for event in self.scheduled_events:
                if event['id'] == event_id:
                    event['start_time'] = new_time
            
            self._drag_data = None
            self.draw_gantt_chart()

    def add_event(self):
        event_name = simpledialog.askstring("Event Name", "Enter the event name:")
        if not event_name:
            return

        staff_breakdown = {label: entry.get() for label, entry in self.staff_inputs.items()}
        duration = simpledialog.askfloat("Add Event", "Enter the event duration (in hours):")
        if not duration:
            return

        new_event = {
            'id': len(self.scheduled_events),
            'name': event_name,
            'start_time': 0,
            'duration': duration,
            'staff': staff_breakdown
        }
        
        self.scheduled_events.append(new_event)
        staff_text = ", ".join([f"{k} {v}" for k, v in staff_breakdown.items() if v])
        self.calendar.insert("", "end", text=event_name, values=(staff_text, duration, ""))
        self.draw_gantt_chart()

        for entry in self.staff_inputs.values():
            entry.delete(0, tk.END)

    def prev_week(self):
        self.current_date -= timedelta(days=7)
        self.date_label.config(text=self.get_week_range_text())
        self.draw_gantt_chart()

    def next_week(self):
        self.current_date += timedelta(days=7)
        self.date_label.config(text=self.get_week_range_text())
        self.draw_gantt_chart()

    def add_department(self):
        new_name = simpledialog.askstring("Add Department", "Enter department name:")
        if new_name:
            self.tree.insert("", "end", text=new_name)

    def edit_department(self):
        selected_department = self.tree.selection()
        if selected_department and self.tree.parent(selected_department[0]) == "":
            new_name = simpledialog.askstring("Edit Department", "Enter the new department name:")
            if new_name:
                self.tree.item(selected_department[0], text=new_name)

    def delete_department(self):
        selected_department = self.tree.selection()
        if selected_department and self.tree.parent(selected_department[0]) == "":
            confirm = messagebox.askyesno("Delete Department", "Are you sure you want to delete this department?")
            if confirm:
                self.tree.delete(selected_department[0])

    def edit_event(self):
        selected_event = self.calendar.selection()
        if selected_event:
            event_info = self.calendar.item(selected_event[0])
            
            # Get new event name
            new_name = simpledialog.askstring("Edit Event", "Enter the new event name:", 
                                            initialvalue=event_info['text'])
            if not new_name:
                return

            # Get new duration
            new_duration = simpledialog.askfloat("Edit Event", "Enter the new event duration (in hours):",
                                               initialvalue=event_info['values'][1])
            if not new_duration:
                return

            # Update both views
            self.calendar.item(selected_event[0], text=new_name,
                             values=(event_info['values'][0], new_duration, event_info['values'][2]))

            # Update scheduled events list
            for event in self.scheduled_events:
                if event['name'] == event_info['text']:
                    event['name'] = new_name
                    event['duration'] = new_duration
                    break

            # Redraw Gantt chart
            self.draw_gantt_chart()

    def delete_event(self):
        selected_event = self.calendar.selection()
        if selected_event:
            event_info = self.calendar.item(selected_event[0])
            confirm = messagebox.askyesno("Delete Event", 
                                        f"Are you sure you want to delete '{event_info['text']}'?")
            if confirm:
                # Remove from calendar view
                self.calendar.delete(selected_event[0])
                
                # Remove from scheduled events list
                self.scheduled_events = [event for event in self.scheduled_events 
                                       if event['name'] != event_info['text']]
                
                # Redraw Gantt chart
                self.draw_gantt_chart()

if __name__ == "__main__":
    app = SchedulingApp()
    app.mainloop()