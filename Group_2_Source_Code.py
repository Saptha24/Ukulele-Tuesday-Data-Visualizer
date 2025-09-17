import datetime
from warnings import filters
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
import tkinter as tk
from matplotlib.backends.backend_pdf import PdfPages
from tkinter import E, W, Canvas, Menu, Menubutton, Tk, Label, Button, Entry, messagebox, Listbox, MULTIPLE, END, Toplevel, StringVar, OptionMenu, filedialog, Scrollbar, Frame, ttk
from tkinter.ttk import Separator, Style, Treeview, Combobox
import re
from tkinter import messagebox
from matplotlib import pyplot as plt
from tkmacosx import Button

def validate_date_format(date_str):
        #Checking if the given date is in the correct format YYYYMMDD."""
        # RE to match YYYYMMDD format
        pattern = re.compile(r"^\d{4}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])$")
        return bool(pattern.match(date_str))

class UkuleleTuesdayApp:
    def __init__(self, master):
            self.master = master
            self.master.title("Ukulele Tuesday Data Visualizer")
            self.master.geometry("800x600")
            self.master.configure(bg="#2e2e2e")  

            
            sidebar = tk.Frame(master, bg="#1e1e1e", width=200)
            sidebar.pack(side="left", fill="y")

            
            button_container = tk.Frame(sidebar, bg="#1e1e1e")
            button_container.pack(expand=True)

            
            self.tabdb_path = None
            self.playdb_path = None
            self.requestdb_path = None

            
            self.tabdb = None
            self.playdb = None
            self.requestdb = None

            
            self.difficulty_from = None  
            self.difficulty_to = None  

            
            self.start_date_var = tk.StringVar()
            self.end_date_var = tk.StringVar()
            self.filters = {}

            
            self.filter_frame = tk.Frame(master, bg="#2e2e2e")
            self.filter_frame.pack_forget()

            
            self.graph_var = tk.StringVar(master)
            self.graph_var.set("Select") 

            # CSVs Upload Buttons in the Sidebar
            self.tabdb_button = self.create_button(button_container, "Upload Tab File", lambda: self.upload_tabdb(self.tabdb_button))
            self.tabdb_button.pack(pady=(20, 10), padx=10, fill="x")  # Aligning Center

            self.playdb_button = self.create_button(button_container, "Upload Play File", lambda: self.upload_playdb(self.playdb_button))
            self.playdb_button.pack(pady=10, padx=10, fill="x") 

            self.requestdb_button = self.create_button(button_container, "Upload Request File", lambda: self.upload_requestdb(self.requestdb_button))
            self.requestdb_button.pack(pady=(10, 20), padx=10, fill="x")  

            self.date_from_var = tk.StringVar()
            self.date_to_var = tk.StringVar()
            self.filters["date_from_var"] = self.date_from_var
            self.filters["date_to_var"] = self.date_to_var
            self.song_var = tk.StringVar()
            self.filters["song"] = self.song_var
            self.artist_var = tk.StringVar()
            self.filters["artist"] = self.artist_var
            self.specialbooks_var = tk.StringVar()
            self.filters["specialbooks"] = self.specialbooks_var
            self.columns_to_display = []  # Initialising attribute(s) for selected columns
            self.column_checkbuttons = {}  # Dictionary to store checkbutton variables
            self.duration_from_var = tk.StringVar()
            self.duration_to_var = tk.StringVar()
            self.filters["duration_from"] = self.duration_from_var
            self.filters["duration_to"] = self.duration_to_var


    def validate_dates(self):
        #Validating that the dates entered are in the correct format.
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()

        try:
            # Checking if the dates are valid
            start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            if start_date_obj > end_date_obj:
                messagebox.showerror("Error while Validation", "Start date must be before or equal to end date.")
            else:
                messagebox.showinfo("Validation Success", "Dates are valid!")
        except ValueError:
            messagebox.showerror("Error while Validation", "Please enter dates in the format YYYYMMDD.")
    
    def create_button(self, parent, text, command):
        #Function to create customized CSV upload buttons
        button = Button(
            parent,
            text=text,
            command=command, 
            bg="#B7B7B7",
            fg="black",
            font=("Arial", 10, "bold"),
            relief="flat",
            activebackground="#505050",
            activeforeground="black",
            borderless=1 
        )
        button.pack(pady=10, padx=10, fill="x")
        return button 

    def upload_tabdb(self, button):
        self.tabdb_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.tabdb_path.endswith("tabdb.csv"):
            try:
                self.load_data()  # Loading the data into the application
                if button:
                    button.config(state="disabled", bg="#d3d3d3", fg="#a9a9a9")  # Disabling and greying out the button once the file is uploaded
                messagebox.showinfo("Success", "tabdb.csv uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load tabdb.csv:\n{e}")
        else:
            messagebox.showerror("Error", "Please select the correct tabdb.csv file.")

    def upload_playdb(self, button):
        self.playdb_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.playdb_path.endswith("playdb.csv"):
            try:
                self.load_data()
                if button:
                    button.config(state="disabled", bg="#d3d3d3", fg="#a9a9a9") 
                messagebox.showinfo("Success", "playdb.csv uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load playdb.csv:\n{e}")
        else:
            messagebox.showerror("Error", "Please select the correct playdb.csv file.")

    def upload_requestdb(self, button):
        self.requestdb_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.requestdb_path.endswith("requestdb.csv"):
            try:
                self.load_data()
                if button:
                    button.config(state="disabled", bg="#d3d3d3", fg="#a9a9a9") 
                messagebox.showinfo("Success", "requestdb.csv uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load requestdb.csv:\n{e}")
        else:
            messagebox.showerror("Error", "Please select the correct requestdb.csv file.")
   
    def load_data(self):
        """Load data from CSV files and convert dates to datetime."""
        if not self.tabdb_path or not self.playdb_path or not self.requestdb_path:
            self.filter_frame.pack_forget()  # Hiding the frame if files are missing
            return

        try:
            # Loading CSV files
            self.tabdb = pd.read_csv(self.tabdb_path)
            self.playdb = pd.read_csv(self.playdb_path)
            self.requestdb = pd.read_csv(self.requestdb_path)
            tabdb = pd.read_csv(self.tabdb_path)
            playdb = pd.read_csv(self.playdb_path)
            requestdb = pd.read_csv(self.requestdb_path)

            # Standardizing column names to lowercase
            self.tabdb.columns = self.tabdb.columns.str.lower()

            # Converting 'date' column to datetime format
            if 'date' in tabdb.columns:
                tabdb['date'] = pd.to_datetime(tabdb['date'], errors='coerce', format='%Y%m%d').dt.date

           # Converting the 'difficulty' column to numeric, coercing errors to NaN
            if 'difficulty' in tabdb.columns:
                tabdb['difficulty'] = pd.to_numeric(tabdb['difficulty'], errors='coerce')

            # Droping the 'tabber' column if it exists
            if "tabber" in tabdb.columns:
                tabdb.drop(columns=["tabber"], inplace=True)

            self.tabdb, self.playdb, self.requestdb = tabdb, playdb, requestdb

            if self.tabdb is not None and self.playdb is not None:
                self.tabdb = self.add_play_counts(self.tabdb, self.playdb)

            # Displaying the filter frame after successful uploads
            self.filter_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
            self.update_filters()
            self.update_song_options()
            self.update_artist_options()
            self.update_specialbooks_options()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            self.filter_frame.pack_forget()  # Ensuring filters are hidden on error
        

    def update_filters(self):
            
            for widget in self.filter_frame.winfo_children():
                widget.destroy()
 
            centered_frame = tk.Frame(self.filter_frame, bg="#2e2e2e")
            centered_frame.pack(expand=True, fill=None, pady=20, padx=20)

            filter_section = tk.Frame(centered_frame, bg="#4a4a4a", padx=20, pady=20, relief="groove", bd=2)
            filter_section.pack(pady=20)

            # Title for the filter section
            tk.Label(
                filter_section, text="🎵Ukulele Tuesday🎵", bg="#4a4a4a", fg="white",
                font=("Arial", 18, "bold"), anchor="center"
            ).pack(pady=(5, 15))

            # Define fields with their labels
            fields = [
                ("Song:", "song"),
                ("Artist:", "artist"),
                ("Type:", "type"),
                ("Gender:", "gender"),
                ("Language:", "language"),
                ("Source:", "source"),
                ("Special Books:", "specialbooks"),
            ]

            # Rendering each field with consistent alignment and spacing
            for label_text, field_name in fields:
                field_frame = tk.Frame(filter_section, bg="#4a4a4a", pady=5)
                field_frame.pack(fill="x")

                tk.Label(
                    field_frame, text=label_text, bg="#4a4a4a", fg="white",
                    font=("Arial", 12), width=25, anchor="w"
                ).pack(side="left", padx=10)

                if field_name in ["type", "gender", "language", "source"]:  # Multi-select fields
                    listbox = tk.Listbox(
                        field_frame, selectmode=tk.MULTIPLE, height=3, font=("Arial", 10),
                        bg="#f2f2f2", fg="#3a3a3a", relief="flat", exportselection=False
                    )
                    options = self.get_dropdown_options(field_name)
                    for option in options:
                        listbox.insert(tk.END, option)
                    listbox.pack(side="right", padx=10, fill="x", expand=True)
                    self.filters[field_name] = listbox
                elif field_name == "song":
                    self.song_combobox = Combobox(
                        field_frame, textvariable=self.song_var, font=("Arial", 10)
                    )
                    self.song_combobox.pack(side="right", padx=10, fill="x", expand=True)
                    self.song_combobox.bind('<<ComboboxSelected>>', self.search_song)
                    self.song_combobox.bind('<KeyRelease>', self.search_song)
                elif field_name == "artist":
                    self.artist_combobox = Combobox(
                        field_frame, textvariable=self.artist_var, font=("Arial", 10)
                    )
                    self.artist_combobox.pack(side="right", padx=10, fill="x", expand=True)
                    self.artist_combobox.bind('<<ComboboxSelected>>', self.search_artist)
                    self.artist_combobox.bind('<KeyRelease>', self.search_artist)
                elif field_name == "specialbooks":
                    self.specialbooks_combobox = Combobox(
                        field_frame, textvariable=self.specialbooks_var, font=("Arial", 10)
                    )
                    self.specialbooks_combobox.pack(side="right", padx=10, fill="x", expand=True)
                    self.specialbooks_combobox.bind('<<ComboboxSelected>>', self.search_specialbooks)
                    self.specialbooks_combobox.bind('<KeyRelease>', self.search_specialbooks)
                else:  # Input fields
                    entry = tk.Entry(
                        field_frame, textvariable=self.filters.setdefault(field_name, tk.StringVar()),
                        font=("Arial", 10), bg="#f2f2f2", fg="#3a3a3a", relief="flat"
                    )
                    entry.pack(side="right", padx=10, fill="x", expand=True)
                    self.filters[field_name] = entry

            # Duration Range Section
            duration_frame = tk.Frame(filter_section, bg="#4a4a4a", pady=10)
            duration_frame.pack(fill="x")

            tk.Label(
                duration_frame, text="Duration (minutes):", bg="#4a4a4a", fg="white",
                font=("Arial", 12), width=25, anchor="w"
            ).pack(side="left", padx=10)
            self.duration_from_entry = tk.Entry(duration_frame, textvariable=self.duration_from_var, font=("Arial", 10), bg="#f2f2f2", fg="#3a3a3a", relief="flat")
            self.duration_from_entry.pack(side="left", padx=5, fill="x", expand=True)
            tk.Label(
                duration_frame, text="to", bg="#4a4a4a", fg="white",
                font=("Arial", 12)
            ).pack(side="left", padx=5)
            self.duration_to_entry = tk.Entry(duration_frame, textvariable=self.duration_to_var, font=("Arial", 10), bg="#f2f2f2", fg="#3a3a3a", relief="flat")
            self.duration_to_entry.pack(side="left", padx=5, fill="x", expand=True)

            self.filters["duration_from_var"] = self.duration_from_var
            self.filters["duration_to_var"] = self.duration_to_var
            
            # Dates Field Range Section
            dates_frame = tk.Frame(filter_section, bg="#4a4a4a", pady=10)
            dates_frame.pack(fill="x")

            tk.Label(
                dates_frame, text="Dates (YYYYMMDD):", bg="#4a4a4a", fg="white",
                font=("Arial", 12), width=25, anchor="w"
            ).pack(side="left", padx=10)
            self.date_from_entry = tk.Entry(dates_frame, textvariable=self.date_from_var, font=("Arial", 10), bg="#f2f2f2", fg="#3a3a3a", relief="flat")
            self.date_from_entry.pack(side="left", padx=5, fill="x", expand=True)
            tk.Label(
                dates_frame, text="to", bg="#4a4a4a", fg="white",
                font=("Arial", 12)
            ).pack(side="left", padx=5)
            self.date_to_entry = tk.Entry(dates_frame, textvariable=self.date_to_var, font=("Arial", 10), bg="#f2f2f2", fg="#3a3a3a", relief="flat")
            self.date_to_entry.pack(side="left", padx=5, fill="x", expand=True)

            self.filters["date_from_var"] = self.date_from_var
            self.filters["date_to_var"] = self.date_to_var

            # Difficulty Range Section
            difficulty_frame = tk.Frame(filter_section, bg="#4a4a4a", pady=10)
            difficulty_frame.pack(fill="x")

            tk.Label(
                difficulty_frame, text="Difficulty:", bg="#4a4a4a", fg="white",
                font=("Arial", 12), width=25, anchor="w"
            ).pack(side="left", padx=10)
            self.difficulty_from = tk.Entry(difficulty_frame, font=("Arial", 10), bg="#f2f2f2", fg="#3a3a3a", relief="flat")
            self.difficulty_from.pack(side="left", padx=5, fill="x", expand=True)
            tk.Label(
                difficulty_frame, text="to", bg="#4a4a4a", fg="white",
                font=("Arial", 12)
            ).pack(side="left", padx=5)
            self.difficulty_to = tk.Entry(difficulty_frame, font=("Arial", 10), bg="#f2f2f2", fg="#3a3a3a", relief="flat")
            self.difficulty_to.pack(side="left", padx=5, fill="x", expand=True)

            # Start and End Date Section
            start_end_date_frame = tk.Frame(filter_section, bg="#4a4a4a", pady=10)
            start_end_date_frame.pack(fill="x")

            tk.Label(
                start_end_date_frame, text="Start Date (YYYYMMDD):", bg="#4a4a4a", fg="white",
                font=("Arial", 12), width=25, anchor="w"
            ).pack(side="left", padx=10)
            self.start_date_entry = tk.Entry(start_end_date_frame, textvariable=self.start_date_var, font=("Arial", 10), bg="#f2f2f2", fg="#3a3a3a", relief="flat")
            self.start_date_entry.pack(side="left", padx=5, fill="x", expand=True)
            tk.Label(
                start_end_date_frame, text="to", bg="#4a4a4a", fg="white",
                font=("Arial", 12)
            ).pack(side="left", padx=5)
            self.end_date_entry = tk.Entry(start_end_date_frame, textvariable=self.end_date_var, font=("Arial", 10), bg="#f2f2f2", fg="#3a3a3a", relief="flat")
            self.end_date_entry.pack(side="left", padx=5, fill="x", expand=True)

            self.filters["start_date_var"] = self.start_date_var
            self.filters["end_date_var"] = self.end_date_var
            
            # Column Selection Section 
            column_selection_frame = tk.Frame(filter_section, bg="#4a4a4a", pady=8)
            column_selection_frame.pack(pady=(10, 5))

            tk.Label(
                column_selection_frame, text="Select Columns to Display:", bg="#4a4a4a", fg="white",
                font=("Arial", 12), width=25, anchor="w"
            ).pack(side="left", padx=10)

            columns_frame = tk.Frame(column_selection_frame, bg="#4a4a4a")
            columns_frame.pack(side="right", padx=10, fill="x", expand=True)

            # Adding checkboxes for column names in two rows with 6 checkboxes each
            if self.tabdb is not None:
                current_row = tk.Frame(columns_frame, bg="#4a4a4a")  
                current_row.pack(pady=5)
                count = 0

                for col_name in self.tabdb.columns:
                    var = tk.BooleanVar()
                    display_name = col_name.replace('_', ' ').title()
                    chk = tk.Checkbutton(current_row, text=display_name, variable=var, bg="#4a4a4a", fg="white", selectcolor="#4a4a4a")
                    chk.pack(side="left", padx=5)  
                    self.column_checkbuttons[col_name] = var
                    count += 1
                    # After every 6 checkboxes, start a new row
                    if count % 6 == 0:
                        current_row = tk.Frame(columns_frame, bg="#4a4a4a")  
                        current_row.pack(fill="x", pady=5)

            # Graph Menu Section
            graph_menu_frame = tk.Frame(filter_section, bg="#4a4a4a")
            graph_menu_frame.pack(fill="x",padx=10, pady=5)

            tk.Label(
                graph_menu_frame, text="Choose Graph to Display:", bg="#4a4a4a", fg="white",
                font=("Arial", 12), anchor="w", width=25
            ).pack(side="left", padx=10)

            self.graph_var.set("Select Graph")  # Default placeholder
            graph_options = [
                "Select Graph",
                "Histogram of Songs by Difficulty",
                "Histogram of Songs by Duration",
                "Songs by Language",
                "Songs by Source",
                "Songs by Decade",
                "Cumulative Line Chart of Songs Played",
                "Pie Chart of Songs by Gender",
            ]
            self.graph_menu = tk.OptionMenu(graph_menu_frame, self.graph_var, *graph_options)
            self.graph_menu.configure(
                font=("Arial", 10), bg="#f2f2f2", fg="#3a3a3a", relief="flat",
                activebackground="#505050", activeforeground="white"
            )
            self.graph_menu.pack(side="left", padx=10, fill="x", expand=True)

            # Buttons Section
            button_frame = tk.Frame(filter_section, bg="#4a4a4a")
            button_frame.pack(fill="x", pady=10)

            self.query_button = self.create_button(button_frame, "Query and Display Data", self.display_data)
            self.query_button.pack(side="left", padx=10, pady=5, expand=True, fill="x")

            self.show_graph_button = self.create_button(button_frame, "Show Selected Graph", self.show_selected_graph)
            self.show_graph_button.pack(side="left", padx=10, pady=5, expand=True, fill="x")

            self.export_button = self.create_button(button_frame, "Export All Plots to PDF", self.export_plots_to_pdf)
            self.export_button.pack(side="top", padx=10, pady=5, expand=True)

    def get_dropdown_options(self, field_name):
        """Helper function to fetch dropdown options."""
        if self.tabdb is not None and field_name in self.tabdb.columns:
            return sorted(self.tabdb[field_name].dropna().astype(str).unique(), key=str.lower, reverse=False)
        return []

        
    def add_label_and_widget(self, parent, row, label_text, widget_type, values=None):
        """Helper function to add a label and a widget to the parent frame."""
        tk.Label(parent, text=label_text, bg="#2e2e2e", fg="white", font=("Arial", 10)).grid(row=row, column=0, sticky="w", padx=10, pady=5)

        if widget_type == "listbox":
            listbox = tk.Listbox(parent, selectmode="multiple", height=5)
            for value in values:
                listbox.insert("end", value)
            listbox.grid(row=row, column=1, padx=10, pady=5)
            return listbox
        elif widget_type == "difficulty":
            from_entry = tk.Entry(parent, width=10)
            to_entry = tk.Entry(parent, width=10)
            from_entry.grid(row=row, column=1, sticky="w", padx=(10, 5))
            to_entry.grid(row=row, column=1, sticky="e", padx=(5, 10))
            return from_entry, to_entry
        elif widget_type == "entry":
            entry = tk.Entry(parent)
            entry.grid(row=row, column=1, padx=10, pady=5)
            return entry

    def add_play_counts(self, tabdb, playdb):
        playdb['play_count'] = playdb.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').notnull().sum(axis=1)
        tabdb = pd.merge(tabdb, playdb[['song', 'play_count']], on='song', how='left')
        tabdb['play_count'] = tabdb['play_count'].fillna(0).astype(int)
        return tabdb

    def get_play_count_and_requests_by_date_range(self, playdb, requestdb, song_name, start_date, end_date):
        """
        Calculate the play count and fetch requests for a specific song within a specified date range.
        """
        # Converting the start and end date strings to datetime objects
        start_date = pd.to_datetime(start_date, format='%Y%m%d', errors='coerce')
        end_date = pd.to_datetime(end_date, format='%Y%m%d', errors='coerce')

        # Ensuring valid date range
        if pd.isnull(start_date) or pd.isnull(end_date):
            messagebox.showerror("Invalid Date Format", "Please use YYYYMMDD format.")
            return pd.DataFrame()

        # Filtering by song name and make a copy to avoid SettingWithCopyWarning
        playdb_filtered = playdb[playdb['song'].str.lower().str.strip() == song_name.lower().strip()].copy()
        requestdb_filtered = requestdb[requestdb['song'].str.lower().str.strip() == song_name.lower().strip()].copy()

        if playdb_filtered.empty and requestdb_filtered.empty:
            return pd.DataFrame()

        # Extracting columns that fall within the specified date range
        date_columns = [
            col for col in playdb_filtered.columns[1:]
            if pd.to_datetime(col, format='%Y%m%d', errors='coerce') >= start_date and pd.to_datetime(col, format='%Y%m%d', errors='coerce') <= end_date
        ]

        if not date_columns:
            return pd.DataFrame()

        # Calculating the play count for the filtered date range
        playdb_filtered['play_count'] = playdb_filtered[date_columns].notna().sum(axis=1)

        # Extract request data for the filtered date range
        requestdb_filtered = requestdb_filtered[['song'] + date_columns].copy()
        requestdb_filtered = requestdb_filtered.melt(id_vars=['song'], var_name='date', value_name='requester')
        requestdb_filtered = requestdb_filtered.dropna(subset=['requester'])
        requestdb_filtered = requestdb_filtered.groupby('song')['requester'].apply(lambda x: ', '.join(x)).reset_index()

        # Merging play count and request data
        result = playdb_filtered[['song', 'play_count']].copy()
        if not requestdb_filtered.empty:
            result = pd.merge(result, requestdb_filtered, on='song', how='left')

        return result

   
    def query_data(self):
        """Query the tabdb data based on filters provided in the UI."""
        # Step 1: Copying the original tabdb for filtering
        filtered_data = self.tabdb.copy()

        # Step 2: Applying filters for each column (e.g., artist, year, type, language, etc.)
        for col, widget in self.filters.items():
            if isinstance(widget, tk.Listbox):  # Multi-select fields
                selected_values = [widget.get(i) for i in widget.curselection()]
                if selected_values:
                    filtered_data[col] = filtered_data[col].astype(str).str.strip()
                    filtered_data = filtered_data[filtered_data[col].isin(selected_values)]
            else:  # Single-value filters
                filter_value = widget.get().strip()
                if filter_value:
                    if col in ["song", "artist", "specialbooks"]:
                        filtered_data[col] = filtered_data[col].astype(str).str.strip().str.lower()
                        filter_value = filter_value.lower()
                        filtered_data = filtered_data[filtered_data[col] == filter_value]
                    elif col == "date":
                        try:
                            filter_value = pd.to_datetime(filter_value, format='%Y%m%d', errors='coerce')
                            filtered_data['date'] = pd.to_datetime(filtered_data['date'], errors='coerce')
                            filtered_data = filtered_data[filtered_data['date'] == filter_value]
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid date format for {col}. Please use YYYYMMDD format.")
                            return None

        # Step 3: Handling difficulty range filtering
        difficulty_from = self.difficulty_from.get().strip()
        difficulty_to = self.difficulty_to.get().strip()
        if difficulty_from or difficulty_to:
            try:
                if difficulty_from:
                    difficulty_from = float(difficulty_from)
                    filtered_data = filtered_data[filtered_data['difficulty'] >= difficulty_from]
                if difficulty_to:
                    difficulty_to = float(difficulty_to)
                    filtered_data = filtered_data[filtered_data['difficulty'] <= difficulty_to]
            except ValueError:
                return None
        
        # Step 4: Handling duration range filtering
        duration_from = self.filters.get("duration_from", tk.StringVar()).get().strip()
        duration_to = self.filters.get("duration_to", tk.StringVar()).get().strip()
        if duration_from or duration_to:
            try:
                if duration_from:
                    duration_from_minutes = float(duration_from)
                    filtered_data['duration_converted'] = filtered_data['duration'].apply(self.convert_duration_to_minutes)
                    filtered_data = filtered_data[filtered_data['duration_converted'] >= duration_from_minutes]
                if duration_to:
                    duration_to_minutes = float(duration_to)
                    filtered_data['duration_converted'] = filtered_data['duration'].apply(self.convert_duration_to_minutes)
                    filtered_data = filtered_data[filtered_data['duration_converted'] <= duration_to_minutes]
            except ValueError as e:
                print(f"Error converting duration: {e}")
                return None


        
         # Step 5: Applying song filter if provided
        song_name = self.filters['song'].get().strip() if 'song' in self.filters else ""
        if song_name:
            filtered_data = filtered_data[filtered_data['song'].str.lower().str.strip() == song_name.lower().strip()]

        # Step 6: Applying date range filter to get play counts and requests
        start_date = self.filters['start_date_var'].get().strip() 
        end_date = self.filters['end_date_var'].get().strip()

        if start_date and end_date:
            # Fetching play counts and requests only for the filtered songs
            songs_to_filter = filtered_data['song'].unique() if not filtered_data.empty else []
            play_counts_requests_list = []

            for song in songs_to_filter:
                play_counts_requests = self.get_play_count_and_requests_by_date_range(self.playdb, self.requestdb, song, start_date, end_date)
                if not play_counts_requests.empty:
                    play_counts_requests_list.append(play_counts_requests)

            # Combining play counts and requests if any were found
            if play_counts_requests_list:
                all_play_counts_requests = pd.concat(play_counts_requests_list, ignore_index=True)
                all_play_counts_requests['song'] = all_play_counts_requests['song'].astype(str).str.strip().str.lower()
                filtered_data['song'] = filtered_data['song'].astype(str).str.strip().str.lower()

                # Merging play counts and requests with filtered_data
                filtered_data = pd.merge(filtered_data, all_play_counts_requests, on='song', how='left', suffixes=('', '_new'))

                # Handling conflicts after merging
                if 'play_count_new' in filtered_data.columns:
                    filtered_data['play_count'] = filtered_data['play_count_new'].fillna(0).astype(int)
                    filtered_data.drop(columns=['play_count_new'], inplace=True)
                elif 'play_count' in filtered_data.columns:
                    filtered_data['play_count'] = filtered_data['play_count'].fillna(0).astype(int)
                else:
                    filtered_data['play_count'] = 0

                if 'requester_new' in filtered_data.columns:
                    filtered_data['requester'] = filtered_data['requester_new']
                    filtered_data.drop(columns=['requester_new'], inplace=True)
            else:
                filtered_data['play_count'] = 0
                filtered_data['requester'] = ""

        date_from = self.filters['date_from_var'].get().strip()
        date_to = self.filters['date_to_var'].get().strip()
        if date_from and date_to:
            try:
                date_from = pd.to_datetime(date_from, format='%Y%m%d', errors='coerce')
                date_to = pd.to_datetime(date_to, format='%Y%m%d', errors='coerce')
                filtered_data['date'] = pd.to_datetime(filtered_data['date'], errors='coerce')
                filtered_data = filtered_data[(filtered_data['date'] >= date_from) & (filtered_data['date'] <= date_to)]
            except ValueError:
                messagebox.showerror("Error", "Invalid date range values. Please use YYYYMMDD format.")
                return None

        artist_name = self.filters['artist'].get().strip() if 'artist' in self.filters else ""
        if artist_name:
            filtered_data = filtered_data[filtered_data['artist'].str.lower().str.strip() == artist_name.lower().strip()]

        specialbooks_name = self.filters['specialbooks'].get().strip() if 'specialbooks' in self.filters else ""
        if specialbooks_name:
            filtered_data = filtered_data[filtered_data['specialbooks'].str.lower().str.strip() == specialbooks_name.lower().strip()]
        
        # Droping the temporary 'duration_converted' column before returning the data
        if 'duration_converted' in filtered_data.columns:
            filtered_data.drop(columns=['duration_converted'], inplace=True)
        return filtered_data
    
    def convert_duration_to_minutes(self, duration):
        if isinstance(duration, (float, int)):
            return duration
        try:
            h, m, s = map(int, duration.split(':'))
            return h * 60 + m + s / 60
        except (ValueError, AttributeError):
            return None
    
    def convert_duration_to_seconds(self, duration):
        try:
            h, m, s = map(int, duration.split(':'))
            return h * 3600 + m * 60 + s
        except ValueError:
            return None
        
    def display_data(self):
        """ Display the filtered data in a new window """
        start_date = self.filters.get("start_date_var", tk.StringVar()).get()
        end_date = self.filters.get("end_date_var", tk.StringVar()).get()

        # Validating Start Date
        if start_date and not validate_date_format(start_date):
            messagebox.showerror("Invalid Date", "Start Date must be in YYYYMMDD format.")
            return

        # Validating End Date
        if end_date and not validate_date_format(end_date):
            messagebox.showerror("Invalid Date", "End Date must be in YYYYMMDD format.")
            return

        date_from = self.filters.get("date_from_var", tk.StringVar()).get()
        date_to = self.filters.get("date_to_var", tk.StringVar()).get()

        # Validating Date From
        if date_from and not validate_date_format(date_from):
            messagebox.showerror("Invalid Date", "Date From must be in YYYYMMDD format.")
            return

        # Validating Date To
        if date_to and not validate_date_format(date_to):
            messagebox.showerror("Invalid Date", "Date To must be in YYYYMMDD format.")
            return

        # Proceeding with querying data if dates are valid
        try:
            filtered_data = self.query_data()  # Assume query_data is already implemented
            if filtered_data is None or filtered_data.empty:
                # Showing a "No Data" message if filtered data is empty
                messagebox.showinfo("No Data", "No data available for the given filters.")
            else:
                # Proceeding to display data (you can add your display logic here)
                pass
        except Exception as e:
            # Showing an error message if querying fails
            messagebox.showerror("Error", f"Failed to query data: {e}")
        result = self.query_data()
        if result is not None and not result.empty:
            selected_columns = [col for col, var in self.column_checkbuttons.items() if var.get()]
            if selected_columns:
                result = result[selected_columns]
            table_window = Toplevel(self.master)
            table_window.geometry("1200x800")  
            tree = Treeview(table_window)
            tree['columns'] = list(result.columns)
            tree.heading("#0", text="", anchor="w")
            tree.column("#0", anchor="w", width=1)
            for col in result.columns:
                tree.heading(col, text=col, anchor="w", command=lambda _col=col: self.sort_column(tree, _col, False))
                tree.column(col, anchor="w", width=100)
            for _, row in result.iterrows():
                row_data = list(row)
                if 'date' in result.columns:
                    date_index = result.columns.get_loc('date')
                    if pd.notnull(row_data[date_index]):
                        row_data[date_index] = row_data[date_index].strftime('%Y-%m-%d')
                tree.insert("", "end", values=row_data)
            tree.pack(fill="both", expand=True)

            # Adding a horizontal and vertical scrollbar
            hsb = Scrollbar(table_window, orient="horizontal", command=tree.xview)
            hsb.pack(side="bottom", fill="x")
            tree.configure(xscrollcommand=hsb.set)

            vsb = Scrollbar(table_window, orient="vertical", command=tree.yview)
            vsb.pack(side="right", fill="y")
            tree.configure(yscrollcommand=vsb.set)

    def show_data_table(self, data):
        """Show the filtered data in a new window with sorting options."""
        table_window = tk.Toplevel(self.master)
        table_window.title("Filtered Data")

        # Creating a Treeview widget
        tree = ttk.Treeview(table_window, columns=list(data.columns), show="headings")
        tree.pack(fill="both", expand=True)

        # Adding a scrollbar
        scrollbar = ttk.Scrollbar(table_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Defining a function to sort the data
        def sort_column(col, reverse):
            sorted_data = data.sort_values(by=col, ascending=not reverse)
            for row in tree.get_children():
                tree.delete(row)
            for _, row in sorted_data.iterrows():
                tree.insert("", "end", values=list(row))
            # Update the column header to show the sorting direction
            tree.heading(col, text=f"{col} {'▲' if reverse else '▼'}", command=lambda: sort_column(col, not reverse))

        # Adding column headings with sorting options
        for col in data.columns:
            tree.heading(col, text=col, command=lambda _col=col: sort_column(_col, False))
            tree.column(col, anchor="w")

        # Inserting data into the Treeview
        for _, row in data.iterrows():
            tree.insert("", "end", values=list(row))       

    def show_selected_graph(self):
        filtered_data = self.query_data()
        graph_choice = self.graph_var.get()
        if self.graph_var.get()=="Select Graph":
            messagebox.showerror("Error", "No Graph Selected")
            return
        self.plot_graph(graph_choice, filtered_data)

    def plot_graph(self, graph_choice, data, for_display=True):
            """Plot the graph based on the user's choice and optionally display it."""
            # Closing any previous figures to prevent multiple windows
            plt.close('all')

            if data.empty:
                messagebox.showinfo("No Data", "No data available for the selected filters.")
                return

            plt.figure()  # Creating a new figure
            if graph_choice == "Histogram of Songs by Difficulty":
                data['difficulty'].dropna().plot(kind='hist', bins=10, edgecolor='black', color="#4a4a4a")
                plt.title("Histogram of Songs by Difficulty")
                plt.xlabel("Difficulty")
                plt.ylabel("Frequency")
            elif graph_choice == "Histogram of Songs by Duration":
                data['duration'] = data['duration'].apply(self.convert_duration_to_minutes)
                data['duration'].dropna().plot(kind='hist', bins=10, edgecolor='black', color="#4a4a4a")
                plt.title("Histogram of Songs by Duration")
                plt.xlabel("Duration (minutes)")
                plt.ylabel("Frequency")
            elif graph_choice == "Songs by Language":
                data['language'].value_counts().plot(kind='bar', color="#4a4a4a")
                plt.title("Songs by Language")
                plt.xlabel("Language")
                plt.ylabel("Count")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
            elif graph_choice == "Songs by Source":
                data['source'].value_counts().plot(kind='bar', color="#4a4a4a")
                plt.title("Songs by Source")
                plt.xlabel("Source")
                plt.ylabel("Count")
                plt.xticks(rotation=45, ha='right')  
                plt.tight_layout()  
            elif graph_choice == "Songs by Decade":
                data['year'] = pd.to_numeric(data['year'], errors='coerce')
                data = data.dropna(subset=['year'])
                data['decade'] = (data['year'] // 10) * 10
                data['decade'].value_counts().sort_index().plot(kind='bar', edgecolor='black', color="#4a4a4a")
                plt.title("Songs by Decade")
                plt.xlabel("Decade")
                plt.ylabel("Count")
                plt.xticks(rotation=45, ha='right')  
                plt.tight_layout() 
            elif graph_choice == "Cumulative Line Chart of Songs Played":
                data['date'] = pd.to_datetime(data['date'], errors='coerce')
                data = data.dropna(subset=['date'])
                data = data.sort_values('date')
                cumulative_counts = data['date'].value_counts().sort_index().cumsum()
                cumulative_counts.plot(kind='line', linestyle='-', color="#4a4a4a")
                plt.title("Cumulative Line Chart of Songs Played")
                plt.xlabel("Date")
                plt.ylabel("Cumulative Songs Played")
            elif graph_choice == "Pie Chart of Songs by Gender":
                gender_counts = data['gender'].value_counts()
                gender_counts.plot(kind='pie', autopct='', labels=None)
                plt.ylabel('')
                plt.title("Pie Chart of Songs by Gender")
                plt.legend(gender_counts.index, title="Gender", bbox_to_anchor=(0, 1), loc='upper right',prop={'size': 8})

            # Displaying the plot only if for_display is True
            if for_display:
                plt.show()

    def convert_duration_to_minutes(self, duration):
        if isinstance(duration, (float, int)):
            return duration
        try:
            h, m, s = map(int, duration.split(':'))
            return h * 60 + m + s / 60
        except (ValueError, AttributeError):
            return None
        
    def export_plots_to_pdf(self):
        """Generate all plots and allow the user to save them to a chosen PDF file."""
        # Prompting the user to choose a file location for saving the PDF
        pdf_file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Plots as PDF"
        )

        # Checking if the user canceled the save dialog
        if not pdf_file_path:
            return

        try:
            # Temporarily use the 'Agg' backend
            with plt.rc_context({'backend': 'Agg'}):
                with PdfPages(pdf_file_path) as pdf:
                    # Listing of all graph types to generate
                    graph_types = [
                        "Histogram of Songs by Difficulty",
                        "Histogram of Songs by Duration",
                        "Songs by Language",
                        "Songs by Source",
                        "Songs by Decade",
                        "Cumulative Line Chart of Songs Played",
                        "Pie Chart of Songs by Gender"
                    ]

                    # Generating each plot and save it to the PDF
                    for graph_choice in graph_types:
                        # Close all figures before creating a new one
                        plt.close('all')

                        # Querying data to be used for each plot
                        filtered_data = self.query_data()

                        if filtered_data is not None and not filtered_data.empty:
                            plt.figure()
                            self.plot_graph(graph_choice, filtered_data, for_display=False)

                            # Saving the current figure to the PDF
                            pdf.savefig()
                            plt.close()  # Closing the figure to free up memory

            # Showing a success message after saving
            messagebox.showinfo("Success", f"All plots have been saved to {pdf_file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save plots: {e}")

    def update_song_options(self):
        #Updating the song options in the combobox based on the loaded data
        if self.tabdb is not None:
            songs = [str(song).title() for song in sorted(self.tabdb['song'].dropna().unique(), key=str.lower)]
            self.song_combobox['values'] = songs

    def search_song(self, event):
        #Filtering the song options based on the user's input
        value = self.song_combobox.get().lower()
        if value == '':
            data = sorted(self.tabdb['song'].dropna().unique(), key=str.lower)
        else:
            data = [item for item in self.tabdb['song'].dropna().unique() if value in item.lower()]
        self.song_combobox['values'] = data

    def update_artist_options(self):
        #Updating the artist options in the combobox based on the loaded data
        if self.tabdb is not None:
           artists = [artist.title() for artist in sorted(self.tabdb['artist'].dropna().unique(), key=str.lower)]
           self.artist_combobox['values'] = artists

    def search_artist(self, event):
        #Filter the artist options based on the user's input
        value = self.artist_combobox.get().lower()
        if value == '':
            data = sorted(self.tabdb['artist'].dropna().unique(), key=str.lower)
        else:
            data = [item for item in self.tabdb['artist'].dropna().unique() if value in item.lower()]
        self.artist_combobox['values'] = data

    def update_specialbooks_options(self):
        #Update the special books options in the combobox based on the loaded data
        if self.tabdb is not None:
            specialbooks = [book.title() for book in sorted(self.tabdb['specialbooks'].dropna().unique(), key=str.lower)]
            self.specialbooks_combobox['values'] = specialbooks

    def search_specialbooks(self, event):
        #Filtering the special books options based on the user's input
        value = self.specialbooks_combobox.get().lower()
        if value == '':
            data = sorted(self.tabdb['specialbooks'].dropna().unique(), key=str.lower)
        else:
            data = [item for item in self.tabdb['specialbooks'].dropna().unique() if value in item.lower()]
        self.specialbooks_combobox['values'] = data

    def on_combobox_select(self, event):
        #Handle combobox selection to prevent flickering
        event.widget.selection_clear()

    def sort_column(self, tree, col, reverse):
        #Sort treeview column when a heading is clicked
        data_list = [(tree.set(child, col), child) for child in tree.get_children('')]
        data_list.sort(reverse=reverse)

        for index, (val, child) in enumerate(data_list):
            tree.move(child, '', index)

        # Update the column header to show the sorting direction
        tree.heading(col, text=f"{col} {'▲' if reverse else '▼'}", command=lambda: self.sort_column(tree, col, not reverse))

if __name__ == "__main__":
    root = Tk()
    app = UkuleleTuesdayApp(root)
    root.mainloop()


