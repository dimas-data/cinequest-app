# Generated from: mainInterGUI.ipynb
# Converted at: 2026-01-03T09:48:22.577Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

#!/usr/bin/env python
# coding: utf-8

# In[5]:


import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import hashlib
import heapq
from collections import deque
import csv
import ast
import pandas as pd

# --- DATA STRUCTURES & LOGIC CLASSES ---

class UserNode:
    def __init__(self, username, password, per_list, next_node=None):
        self.username = username
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.per_list = per_list
        self.next = next_node

class UserManager:
    def __init__(self, filename="users_data.csv"):
        self.head = None
        self.username_hash = {}
        self.filename = filename
        self.global_movie_counts = {}
        self.load_from_csv()

    def save_to_csv(self):
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
        if username in self.username_hash:
            del self.username_hash[username]
            self.save_to_csv()
            return True
        return False

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

# --- GUI CLASS ---

class CinequestGUI:
    def __init__(self, root, df_prep):
        self.root = root
        self.root.title("Cinequest - Movie Catalog")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        
        self.df_prep = df_prep
        self.manager = UserManager()
        self.movie_search = MovieSearch()
        self.active_user = None
        
        # Initialize movie search
        for index, row in df_prep.iterrows():
            self.movie_search.insert(row["name"], row["genre"], index)
        
        self.category = CategoryByGenre(df_prep)
        self.genre_dict = self.category.movie_genre()
        self.trend = Recommendation()
        
        self.show_login_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text="🎬 CINEQUEST", font=('Arial', 32, 'bold'), bg='#1a1a2e', fg='#e94560').pack(pady=20)
        btn_frame = tk.Frame(main_frame, bg='#1a1a2e')
        btn_frame.pack(pady=30)
        tk.Button(btn_frame, text="LOGIN", width=20, height=2, bg='#e94560', fg='white', command=self.show_login_form).pack(pady=10)
        tk.Button(btn_frame, text="REGISTER", width=20, height=2, bg='#0f3460', fg='white', command=self.show_register_form).pack(pady=10)

    def show_login_form(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text="LOGIN", font=('Arial', 24, 'bold'), bg='#1a1a2e', fg='#e94560').pack(pady=30)
        tk.Label(main_frame, text="Username:", bg='#1a1a2e', fg='white').pack()
        username_entry = tk.Entry(main_frame)
        username_entry.pack(pady=5)
        tk.Label(main_frame, text="Password:", bg='#1a1a2e', fg='white').pack()
        password_entry = tk.Entry(main_frame, show='*')
        password_entry.pack(pady=5)
        def do_login():
            success, user = self.manager.login(username_entry.get(), password_entry.get())
            if success:
                self.active_user = user
                self.show_main_menu()
            else: messagebox.showerror("Error", "Invalid credentials")
        tk.Button(main_frame, text="LOGIN", command=do_login).pack(pady=20)
        tk.Button(main_frame, text="BACK", command=self.show_login_screen).pack()

    def show_register_form(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text="REGISTER", font=('Arial', 24, 'bold'), bg='#1a1a2e', fg='#e94560').pack(pady=30)
        tk.Label(main_frame, text="Username:", bg='#1a1a2e', fg='white').pack()
        u_entry = tk.Entry(main_frame); u_entry.pack(pady=5)
        tk.Label(main_frame, text="Password:", bg='#1a1a2e', fg='white').pack()
        p_entry = tk.Entry(main_frame, show='*'); p_entry.pack(pady=5)
        def do_reg():
            success, msg = self.manager.register(u_entry.get(), p_entry.get())
            if success: self.show_login_screen()
            else: messagebox.showerror("Error", msg)
        tk.Button(main_frame, text="REGISTER", command=do_reg).pack(pady=20)
        tk.Button(main_frame, text="BACK", command=self.show_login_screen).pack()

    def show_main_menu(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text=f"Welcome, {self.active_user.username}!", font=('Arial', 24), bg='#1a1a2e', fg='#e94560').pack(pady=20)
        tk.Button(main_frame, text="📝 My Personal List", width=25, command=self.show_personal_list).pack(pady=5)
        tk.Button(main_frame, text="🎬 Browse Movies", width=25, command=self.show_browse_movies).pack(pady=5)
        tk.Button(main_frame, text="🔍 Search Movies", width=25, command=self.show_search_menu).pack(pady=5)
        tk.Button(main_frame, text="🔥 Trending Movies", width=25, command=self.show_trending).pack(pady=5)
        tk.Button(main_frame, text="🚪 Logout", width=25, command=self.show_login_screen).pack(pady=20)

    def show_personal_list(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(main_frame, text="My Movie List", font=('Arial', 20), bg='#1a1a2e', fg='#e94560').pack()
        self.movie_listbox = tk.Listbox(main_frame, bg='#16213e', fg='white', width=50)
        self.movie_listbox.pack(pady=10)
        self.refresh_personal_list()
        tk.Button(main_frame, text="Delete Selected", command=self.delete_from_list).pack()
        tk.Button(main_frame, text="Back", command=self.show_main_menu).pack(pady=5)

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
                self.manager.global_movie_counts[m_title] -= 1
            self.manager.save_to_csv()
            self.refresh_personal_list()

    def show_browse_movies(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(expand=True, fill='both')
        self.movie_tree = ttk.Treeview(tree_frame, columns=('Index', 'Name', 'Genre'), show='headings')
        self.movie_tree.heading('Index', text='Index'); self.movie_tree.heading('Name', text='Name'); self.movie_tree.heading('Genre', text='Genre')
        self.movie_tree.pack(side='left', fill='both', expand=True)
        for index, row in self.df_prep.iterrows():
            self.movie_tree.insert('', 'end', values=(index, row['name'], row['genre']))
        tk.Button(main_frame, text="Add Selected", command=self.add_selected_movie).pack(pady=5)
        tk.Button(main_frame, text="Back", command=self.show_main_menu).pack()

    def add_selected_movie(self):
        selection = self.movie_tree.selection()
        if selection:
            item = self.movie_tree.item(selection[0])
            movie_title = item['values'][1]
            found = False
            for m in self.active_user.per_list:
                if m[0] == movie_title: m[1] += 1; found = True; break
            if not found:
                self.active_user.per_list.append([movie_title, 1])
                self.manager.global_movie_counts[movie_title] = self.manager.global_movie_counts.get(movie_title, 0) + 1
            self.manager.save_to_csv()
            messagebox.showinfo("Success", f"Added {movie_title}")

    def show_search_menu(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Button(main_frame, text="Search by Name", command=self.show_search_by_name).pack(pady=10)
        tk.Button(main_frame, text="Search by Genre", command=self.show_search_by_genre).pack(pady=10)
        tk.Button(main_frame, text="Back", command=self.show_main_menu).pack()

    def show_search_by_name(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        search_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=search_var, width=40).pack(pady=10)
        res_text = scrolledtext.ScrolledText(main_frame, height=15)
        res_text.pack(fill='both')
        def live_search(*args):
            query = search_var.get().strip()
            res_text.delete(1.0, tk.END)
            if len(query) >= 2:
                results = self.movie_search.search_movie(query)
                for i, m in enumerate(results, 1):
                    res_text.insert(tk.END, f"{i}. {m['name']} ({m['genre']})\n")
        search_var.trace_add("write", live_search)
        tk.Button(main_frame, text="Back", command=self.show_search_menu).pack(pady=10)

    def show_search_by_genre(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        genre_var = tk.StringVar()
        combo = ttk.Combobox(main_frame, textvariable=genre_var, values=list(self.genre_dict.keys()))
        combo.pack(pady=10)
        res_text = scrolledtext.ScrolledText(main_frame, height=15)
        res_text.pack(fill='both')
        def do_search():
            res_text.delete(1.0, tk.END)
            movies = self.category.search_by_genre(self.genre_dict, genre_var.get())
            for name, idx in movies: res_text.insert(tk.END, f"- {name}\n")
        tk.Button(main_frame, text="Search", command=do_search).pack(pady=5)
        tk.Button(main_frame, text="Back", command=self.show_search_menu).pack()

    def show_trending(self):
        """Displays the top 10 movies added by all users."""
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(main_frame, text="🔥 Trending Movies", font=('Arial', 24, 'bold'), 
                 bg='#1a1a2e', fg='#e94560').pack(pady=10)
        
        # Calculate top 10 from global data
        self.trend.formula(self.manager.global_movie_counts)
        
        res_text = scrolledtext.ScrolledText(main_frame, height=15, font=('Arial', 12), 
                                            bg='#16213e', fg='white')
        res_text.pack(pady=10, fill='both')
        
        if not self.trend.top_10:
            res_text.insert(tk.END, "No trending data yet. Movies appear here as users add them to lists!")
        else:
            for i, (name, count) in enumerate(self.trend.top_10, 1):
                res_text.insert(tk.END, f"{i}. {name} — Added {count} times\n")
        
        tk.Button(main_frame, text="Back to Menu", bg='#16213e', fg='white', 
                 command=self.show_main_menu).pack(pady=10)

# --- EXECUTION BLOCK ---

if __name__ == "__main__":
    try:
        # 1. Load and clean your data
        filename = "movies_updated.csv"
        df = pd.read_csv(filename, encoding="utf8")
        
        # Drop columns as per your logic
        df_prep = df.drop(columns=["score", "rating", "year", "released", "votes", "director", 
                                   "writer", "star", "country", "budget", "gross", 
                                   "company", "runtime"], axis=1)
        
        # Handle any potential NaN values in name/genre to avoid GUI errors
        df_prep = df_prep.fillna("Unknown")

        # 2. Launch the GUI
        root = tk.Tk()
        app = CinequestGUI(root, df_prep)
        root.mainloop()
        
    except FileNotFoundError:
        print(f"Error: Could not find {filename}. Please ensure the file is in the script directory.")
    except Exception as e:
        print(f"An error occurred: {e}")