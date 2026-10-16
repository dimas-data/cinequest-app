#!/usr/bin/env python
# coding: utf-8

# In[1]:

from pathlib import Path
import pandas as pd

filename = "movies_updated.csv"
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / filename
USERS_PATH = BASE_DIR / "data" / "users_data.csv"

df = pd.read_csv(DATA_PATH)
rows = df.index
print(f"Successfully loaded dataset with {len(df)} entries.")

print("--- Movie Dataset ---")
print(f"The columns are: {df.columns.tolist()}")  # Checking the columns and rows of the preprocessed dataset
print(f"There are {len(rows)} rows \n")
print(df.head(3))
missing = df.isnull().sum()
print(f"\nMissing data based on columns are \n{missing}")

# Drop columns which aren't suitable for our project
# (FIX: removed axis=1; "columns=" already implies the axis in newer pandas)
df_prep = df.drop(columns=["score", "rating", "year", "released", "votes", "director",
                           "writer", "star", "country", "budget", "gross", "company", "runtime"])
print("\n--- Cleaned Movie Dataset ---")
print(f"Rows and Columns: {df_prep.shape}")  # Checking the columns and rows of the processed dataset
print(f"The new columns are: {df_prep.columns.tolist()}")
print(f"\n{df_prep.head(3)}")

# Checking duplicates based on the columns name and genre only
duplicate_rows1 = df_prep[df_prep.duplicated(subset=['name', 'genre'], keep=False)][['name', 'genre']]
print(f"Duplicates by name and genre:\n {duplicate_rows1.sort_values(by='name')}\n")
# Checking duplicates by adding another column (year) to determine whether the data really is a duplicate
# (uses df, not df_prep, because year was dropped from df_prep)
duplicate_rows2 = df[df.duplicated(subset=['name', 'genre', 'year'], keep=False)][['name', 'genre', 'year']]
print(f"Duplicates by name, genre and year:\n {duplicate_rows2.sort_values(by='name')}")


# In[2]:

from tkinter import ttk, messagebox, scrolledtext
import tkinter as tk
import hashlib
import heapq
from collections import deque
import csv
import ast

# --- DATA STRUCTURES & LOGIC CLASSES ---

class UserNode:
    def __init__(self, username, password, per_list, next_node=None):
        self.username = username
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.per_list = per_list
        self.next = next_node


class UserManager:
    def __init__(self, filename=USERS_PATH):
        self.head = None
        self.username_hash = {}
        self.filename = filename
        self.global_movie_counts = {}
        self.load_from_csv()

    def save_to_csv(self):
        Path(self.filename).parent.mkdir(parents=True, exist_ok=True)
        with open(self.filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["username", "password_hash", "per_list"])
            for username, node in self.username_hash.items():
                writer.writerow([node.username, node.password_hash, str(node.per_list)])

    def load_from_csv(self):
        try:
            with open(self.filename, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    username = row['username']
                    pwd_hash = row['password_hash']
                    per_list = ast.literal_eval(row['per_list'])
                    for movie_name, count in per_list:
                        self.global_movie_counts[movie_name] = self.global_movie_counts.get(movie_name, 0) + count
                    new_node = UserNode(username, "dummy", per_list, self.head)
                    new_node.password_hash = pwd_hash
                    self.head = new_node
                    self.username_hash[username] = new_node
        except FileNotFoundError:
            pass

    def register(self, username, password):
        if not username or not password:
            return False, "Username and password cannot be empty"
        if username in self.username_hash:
            return False, "Username already taken"
        new_node = UserNode(username, password, [], self.head)
        self.head = new_node
        self.username_hash[username] = new_node
        self.save_to_csv()
        return True, "Account created successfully"

    def login(self, username, password):
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        user = self.username_hash.get(username)
        if user and user.password_hash == input_hash:
            return True, user
        return False, None

    def delete_account(self, username):
        node = self.username_hash.get(username)
        if not node:
            return False

        # FIX 1: subtract this user's movies from the global (trending) counts
        for movie_name, count in node.per_list:
            if movie_name in self.global_movie_counts:
                self.global_movie_counts[movie_name] -= count
                if self.global_movie_counts[movie_name] <= 0:
                    del self.global_movie_counts[movie_name]

        # FIX 2: unlink the node from the linked list
        if self.head is node:
            self.head = node.next
        else:
            current = self.head
            while current and current.next is not node:
                current = current.next
            if current:
                current.next = node.next

        del self.username_hash[username]
        self.save_to_csv()
        return True


class MovieSearch:
    def __init__(self):
        self.table = {}

    def insert(self, movie_name, genre, index):
        key = movie_name.lower().strip()
        if key not in self.table:
            self.table[key] = []
        self.table[key].append({"name": movie_name, "genre": genre, "index": index})

    def search_movie(self, query):
        query = query.lower().strip()
        results = []
        if query in self.table:
            results.extend(self.table[query])
        else:
            for key, movies in self.table.items():
                if query in key:
                    results.extend(movies)
        return results


class CategoryByGenre:
    def __init__(self, df_prep):
        self.df_prep = df_prep
        self.genre_dict = {}

    def movie_genre(self):
        for i, row in self.df_prep.iterrows():
            genre = row['genre']
            movie_name = row['name']
            if genre not in self.genre_dict:
                self.genre_dict[genre] = []
            self.genre_dict[genre].append((movie_name, i))
        return self.genre_dict

    def search_by_genre(self, genre_dict, search_genre):
        search_genre = search_genre.lower()
        matched_movies = []
        for genre, movies in genre_dict.items():
            if search_genre in genre.lower():
                matched_movies.extend(movies)
        return matched_movies


class Recommendation:
    def __init__(self):
        self.top_10 = deque()

    def formula(self, global_counts):
        self.top_10.clear()
        heap = []
        for movie_item in global_counts.items():
            name = movie_item[0]
            count = movie_item[1]
            heapq.heappush(heap, (-count, name))
        for _ in range(10):
            if heap:
                neg_count, movie_name = heapq.heappop(heap)
                self.top_10.append((movie_name, -neg_count))
            else:
                break


# In[9]:

BG_MAIN      = "#0b132b"   # very dark blue
BG_PANEL     = "#16213e"   # dark blue panels
ACCENT       = "#8B0000"   # dark red
ACCENT_HOVER = "#6d1b1b"   # darker red hover
HIGHLIGHT    = "#fbc531"   # gold
TEXT_MAIN    = "#f5f5f5"   # soft white


class CinequestGUI:
    def __init__(self, root, df_prep):
        self.root = root
        self.root.title("Cinequest - Movie Catalog")
        self.root.state("zoomed")
        self.root.configure(bg=BG_MAIN)

        self.df_prep = df_prep
        self.manager = UserManager()
        self.movie_search = MovieSearch()
        self.active_user = None

        for index, row in df_prep.iterrows():
            self.movie_search.insert(row["name"], row["genre"], index)

        self.category = CategoryByGenre(df_prep)
        self.genre_dict = self.category.movie_genre()
        self.trend = Recommendation()

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Treeview",
                             background=BG_PANEL,
                             foreground=TEXT_MAIN,
                             fieldbackground=BG_PANEL,
                             rowheight=25)
        self.style.configure("Treeview.Heading",
                             background=ACCENT,
                             foreground="white",
                             font=('Arial', 10, 'bold'))

        self.style.map("Treeview", background=[('selected', ACCENT)])

        self.show_login_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- Shared helper: add a movie to the active user's list (blocks duplicates) ---
    def add_to_personal_list(self, movie_title):
        movie_title = str(movie_title)  # Treeview may turn numeric titles (e.g. "1917") into ints
        for m in self.active_user.per_list:
            if m[0] == movie_title:
                return False
        self.active_user.per_list.append([movie_title, 1])
        self.manager.global_movie_counts[movie_title] = self.manager.global_movie_counts.get(movie_title, 0) + 1
        self.manager.save_to_csv()
        return True

    def show_login_screen(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg=BG_MAIN)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text="🎬 CINEQUEST", font=('Arial', 64, 'bold'), bg=BG_MAIN, fg=ACCENT).pack(pady=20)
        btn_frame = tk.Frame(main_frame, bg=BG_MAIN)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="LOGIN", width=30, height=2, font=('Arial', 15), bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_login_form).pack(pady=10)
        tk.Button(btn_frame, text="REGISTER", width=30, height=2, font=('Arial', 15), bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_register_form).pack(pady=10)

    def show_login_form(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg=BG_MAIN)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text="LOGIN", font=('Arial', 60, 'bold'), bg=BG_MAIN, fg=ACCENT).pack(pady=30)
        tk.Label(main_frame, text="Username:", font=('Arial', 14), bg=BG_MAIN, fg=TEXT_MAIN).pack()
        username_entry = tk.Entry(main_frame, width=20, font=('Arial', 13), justify='center')
        username_entry.pack(pady=5)
        tk.Label(main_frame, text="Password:", font=('Arial', 14), bg=BG_MAIN, fg=TEXT_MAIN).pack()
        password_entry = tk.Entry(main_frame, width=20, font=('Arial', 13), justify='center', show='*')
        password_entry.pack(pady=5)
        username_entry.bind("<Return>", lambda event: do_login())
        password_entry.bind("<Return>", lambda event: do_login())

        def do_login():
            success, user = self.manager.login(username_entry.get().strip(), password_entry.get().strip())
            if success:
                self.active_user = user
                self.show_main_menu()
            else:
                messagebox.showerror("Error", "Invalid credentials")

        button_container = tk.Frame(main_frame, bg=BG_MAIN)
        button_container.pack(pady=20)
        tk.Button(button_container, text="LOGIN", font=('Arial', 10), bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=do_login).pack(pady=20, padx=20, side='left')
        tk.Button(button_container, text="BACK", font=('Arial', 10), bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_login_screen).pack(padx=20, side='left')

    def show_register_form(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg=BG_MAIN)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text="REGISTER", font=('Arial', 60, 'bold'), bg=BG_MAIN, fg=ACCENT).pack(pady=30)
        tk.Label(main_frame, text="Username:", font=('Arial', 14), bg=BG_MAIN, fg=TEXT_MAIN).pack()
        username_entry = tk.Entry(main_frame, width=20, font=('Arial', 13), justify='center')
        username_entry.pack(pady=5)
        tk.Label(main_frame, text="Password:", font=('Arial', 14), bg=BG_MAIN, fg=TEXT_MAIN).pack()
        password_entry = tk.Entry(main_frame, width=20, font=('Arial', 13), justify='center', show='*')
        password_entry.pack(pady=5)

        def do_reg():
            success, msg = self.manager.register(username_entry.get().strip(), password_entry.get().strip())
            if success:
                self.show_login_screen()
            else:
                messagebox.showerror("Error", msg)

        username_entry.bind("<Return>", lambda event: do_reg())
        password_entry.bind("<Return>", lambda event: do_reg())
        button_container = tk.Frame(main_frame, bg=BG_MAIN)
        button_container.pack(pady=10)
        tk.Button(button_container, text="REGISTER", font=('Arial', 10), bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=do_reg).pack(pady=20, padx=20, side='left')
        tk.Button(button_container, text="BACK", font=('Arial', 10), bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_login_screen).pack(padx=20, side='left')

    def show_main_menu(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg=BG_MAIN)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text=f"Welcome, {self.active_user.username}!", font=('Arial', 40), bg=BG_MAIN, fg=ACCENT).pack(pady=20)
        tk.Button(main_frame, text="📝 My Personal List", font=('Arial', 13), width=25, bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_personal_list).pack(pady=5)
        tk.Button(main_frame, text="🎬 Browse Movies", font=('Arial', 13), width=25, bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_browse_movies).pack(pady=5)
        tk.Button(main_frame, text="🔍 Search Movies", font=('Arial', 13), width=25, bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_search_menu).pack(pady=5)
        tk.Button(main_frame, text="🔥 Trending Movies", font=('Arial', 13), width=25, bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_trending).pack(pady=5)
        tk.Button(main_frame, text="🚪 Logout", font=('Arial', 13), width=25, bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_login_screen).pack(pady=5)
        tk.Button(main_frame, text="🗑 Delete Account", font=('Arial', 13), width=25, bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.confirm_delete_account).pack(pady=20)

    def confirm_delete_account(self):
        answer = messagebox.askyesno("Delete Account", "Are you absolutely sure? This will delete your personal list and cannot be undone.")
        if answer:
            username_to_delete = self.active_user.username
            success = self.manager.delete_account(username_to_delete)
            if success:
                messagebox.showinfo("Deleted", f"{username_to_delete}'s account has been successfully removed.")
                self.active_user = None
                self.show_login_screen()
            else:
                messagebox.showerror("Error", "Could not delete account.")

    def show_personal_list(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg=BG_MAIN)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text=f"{self.active_user.username}'s Movie List", font=('Arial', 20, 'bold'), bg=BG_MAIN, fg=ACCENT).pack()
        list_container = tk.Frame(main_frame, bg=BG_MAIN)
        list_container.pack(pady=10, fill='both', expand=True)
        scrollbar = tk.Scrollbar(list_container, orient="vertical")
        scrollbar.pack(side='right', fill='y')
        self.movie_listbox = tk.Listbox(
            list_container,
            bg=BG_PANEL,
            fg=TEXT_MAIN,
            selectbackground=ACCENT,
            selectforeground='white',
            width=50,
            height=15,
            font=('Arial', 11),
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.movie_listbox.yview)
        self.movie_listbox.pack(side='left', fill='both', expand=True)
        self.refresh_personal_list()
        tk.Button(main_frame, text="Delete Selected", font=('Arial', 14), bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.delete_from_list).pack(pady=20, padx=70, side='left')
        tk.Button(main_frame, text="Back", font=('Arial', 14), bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_main_menu).pack(padx=60, side='left')

    def refresh_personal_list(self):
        self.movie_listbox.delete(0, tk.END)
        for i, movie in enumerate(self.active_user.per_list, 1):
            self.movie_listbox.insert(tk.END, f"{i}. {movie[0]}")

    def delete_from_list(self):
        selection = self.movie_listbox.curselection()
        if selection:
            idx = selection[0]
            removed = self.active_user.per_list.pop(idx)
            m_title = removed[0]
            if m_title in self.manager.global_movie_counts:
                self.manager.global_movie_counts[m_title] -= removed[1]
                if self.manager.global_movie_counts[m_title] <= 0:
                    del self.manager.global_movie_counts[m_title]
            self.manager.save_to_csv()
            self.refresh_personal_list()

    def show_browse_movies(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg=BG_MAIN)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(expand=True, fill='both')
        style = ttk.Style()

        style.theme_use("default")

        style.configure(
            "Treeview",
            background=BG_PANEL,
            foreground=TEXT_MAIN,
            fieldbackground=BG_PANEL,
            rowheight=25
        )

        style.configure(
            "Treeview.Heading",
            background=ACCENT,
            foreground="white",
            font=('Arial', 10, 'bold'),
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", "white")]
        )

        self.movie_tree = ttk.Treeview(tree_frame, columns=('Index', 'Name', 'Genre'), show='headings')
        self.movie_tree.heading('Index', text='Index')
        self.movie_tree.heading('Name', text='Name')
        self.movie_tree.heading('Genre', text='Genre')
        scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.movie_tree.yview)
        self.movie_tree.configure(yscrollcommand=scrollbar.set)
        self.movie_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        for index, row in self.df_prep.iterrows():
            self.movie_tree.insert('', 'end', values=(index, row['name'], row['genre']))
        tk.Button(main_frame, text="Add Selected", bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.add_selected_movie).pack(pady=5, padx=10, side='left')
        tk.Button(main_frame, text="Back", bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_main_menu).pack(side='left')

    def add_selected_movie(self):
        selection = self.movie_tree.selection()
        if selection:
            item = self.movie_tree.item(selection[0])
            movie_title = str(item['values'][1])
            # FIX: now behaves like the search versions (no silent duplicate increments)
            if self.add_to_personal_list(movie_title):
                messagebox.showinfo("Success", f"Added {movie_title}")
            else:
                messagebox.showwarning("Notice", "You have already added this movie!")

    def show_search_menu(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg=BG_MAIN)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text="Movie Search", font=('Arial', 60, 'bold'), bg=BG_MAIN, fg=ACCENT).pack(pady=30)
        tk.Button(main_frame, text="Search by Name", font=('Arial', 15), bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_search_by_name).pack(pady=10)
        tk.Button(main_frame, text="Search by Genre", font=('Arial', 15), bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_search_by_genre).pack(pady=10)
        tk.Button(main_frame, text="Back", font=('Arial', 15), bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', command=self.show_main_menu).pack(pady=10)

    def show_search_by_name(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg=BG_MAIN)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text="Movie Name Search", font=('Arial', 45, 'bold'), bg=BG_MAIN, fg=ACCENT).pack(pady=20)
        search_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=search_var, width=40).pack(pady=10)
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill='both', pady=10)
        scrollbar = tk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side='right', fill='y')
        search_tree = ttk.Treeview(
            tree_frame,
            columns=('Name', 'Genre'),
            show='headings',
            height=10,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=search_tree.yview)
        search_tree.heading('Name', text='Movie Title')
        search_tree.heading('Genre', text='Genre')
        search_tree.pack(side='left', fill='both', expand=True)

        def live_search(*args):
            query = search_var.get().strip()
            for item in search_tree.get_children():
                search_tree.delete(item)
            if len(query) >= 2:
                results = self.movie_search.search_movie(query)
                for m in results:
                    search_tree.insert('', 'end', values=(m['name'], m['genre']))
        search_var.trace_add("write", live_search)

        def add_from_search():
            selection = search_tree.selection()
            if selection:
                item = search_tree.item(selection[0])
                movie_title = str(item['values'][0])
                if self.add_to_personal_list(movie_title):
                    messagebox.showinfo("Success", f"Added {movie_title} to your list!")
                else:
                    messagebox.showwarning("Notice", "You have already added this movie!")

        btn_container = tk.Frame(main_frame, bg=BG_MAIN)
        btn_container.pack(pady=10)
        tk.Button(btn_container, text="Add Selected", font=('Arial', 12), bg=ACCENT, fg='white',
                  command=add_from_search).pack(side='left', padx=10)
        tk.Button(btn_container, text="Back", font=('Arial', 12), bg=ACCENT, fg='white',
                  command=self.show_search_menu).pack(side='left')

    def show_search_by_genre(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg=BG_MAIN)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text="Genre Search", font=('Arial', 50, 'bold'), bg=BG_MAIN, fg=ACCENT).pack(pady=20)
        genre_var = tk.StringVar()
        combo = ttk.Combobox(main_frame, textvariable=genre_var, values=list(self.genre_dict.keys()))
        combo.pack(pady=10)
        tree_container = tk.Frame(main_frame, bg=BG_PANEL)
        tree_container.pack(pady=10)
        search_scroll = tk.Scrollbar(tree_container, orient="vertical")
        search_scroll.pack(side='right', fill='y')
        search_tree = ttk.Treeview(
            tree_container,
            columns=('Name',),
            show='headings',
            height=10,
            yscrollcommand=search_scroll.set
        )
        search_scroll.config(command=search_tree.yview)

        search_tree.heading('Name', text='Movie Title')
        search_tree.column('Name', width=400)
        search_tree.pack(side='left', fill='both')

        def do_search():
            for item in search_tree.get_children():
                search_tree.delete(item)
            selected_genre = genre_var.get()
            if selected_genre:
                movies = self.category.search_by_genre(self.genre_dict, selected_genre)
                for name, idx in movies:
                    search_tree.insert('', 'end', values=(name,))

        def add_from_genre():
            selection = search_tree.selection()
            if selection:
                item = search_tree.item(selection[0])
                movie_title = str(item['values'][0])
                if self.add_to_personal_list(movie_title):
                    messagebox.showinfo("Success", f"Added {movie_title}!")
                else:
                    messagebox.showwarning("Notice", "You have already added this movie!")

        btn_container = tk.Frame(main_frame, bg=BG_MAIN)
        btn_container.pack(pady=10)
        tk.Button(btn_container, text="Search", font=('Arial', 12), bg=ACCENT, fg='white',
                  command=do_search).pack(side='left', padx=10)
        tk.Button(btn_container, text="Add Selected", font=('Arial', 12), bg=ACCENT, fg='white',
                  command=add_from_genre).pack(side='left', padx=10)
        tk.Button(btn_container, text="Back", font=('Arial', 12), bg=ACCENT, fg='white',
                  command=self.show_search_menu).pack(side='left', padx=10)

    def show_trending(self):
        """Displays the top 10 movies added by all users."""
        self.clear_window()
        main_frame = tk.Frame(self.root, bg=BG_MAIN)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text="🔥 Trending Movies", font=('Arial', 26, 'bold'),
                 bg=BG_MAIN, fg=ACCENT).pack(pady=15)
        self.trend.formula(self.manager.global_movie_counts)
        res_text = scrolledtext.ScrolledText(main_frame, height=15, font=('Arial', 12), bg=BG_PANEL, fg=TEXT_MAIN, insertbackground='white', selectbackground=ACCENT, selectforeground='white', wrap='word')
        res_text.pack(pady=10, fill='both', expand=True)
        res_text.tag_config("rank", foreground=HIGHLIGHT, font=('Arial', 14, 'bold'))
        res_text.tag_config("movie", foreground=TEXT_MAIN, font=('Arial', 12))
        res_text.tag_config("count", foreground=HIGHLIGHT, font=('Arial', 12, 'bold'))
        if not self.trend.top_10:
            res_text.insert(tk.END, "No trending data yet. Movies appear here as users add them to lists!", "movie")
        else:
            for i, (name, count) in enumerate(self.trend.top_10, 1):
                res_text.insert(tk.END, f"{i}. ", "rank")
                res_text.insert(tk.END, f"{name} ", "movie")
                res_text.insert(tk.END, f"— Added {count} times\n", "count")
        res_text.config(state='disabled')
        tk.Button(main_frame, text="Back to Menu", bg=ACCENT, fg='white', activebackground=ACCENT_HOVER, activeforeground='white', relief='flat', font=('Arial', 12, 'bold'), command=self.show_main_menu).pack(pady=15)


# In[11]:

if __name__ == "__main__":
    # FIX: reuse the DATA_PATH built at the top (works regardless of where you launch from),
    # and use the trimmed df_prep created above instead of reloading the full CSV.
    root = tk.Tk()
    app = CinequestGUI(root, df_prep)
    root.mainloop()