import cv2
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy
import pymysql
import os

class PencilSketchApp:
    def __init__(self, root, user_id):
        self.root = root
        self.root.title("Pencil Sketch App")
        self.user_id = user_id

        # Initialize variables
        self.image_path = None
        self.original_image = None
        self.pencil_sketch = None

        # Create buttons
        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=10)

        self.process_button = tk.Button(root, text="Generate Pencil Sketch", command=self.generate_pencil_sketch)
        self.process_button.pack(pady=10)

        self.save_button = tk.Button(root, text="Save Sketch to Database", command=self.save_to_database)
        self.save_button.pack(pady=10)

        self.download_button = tk.Button(root, text="Download Sketch", command=self.download_sketch)
        self.download_button.pack(pady=10)

        self.view_history_button = tk.Button(root, text="View History", command=self.view_history)
        self.view_history_button.pack(pady=10)

        self.exit_button = tk.Button(root, text="Exit", command=root.destroy)
        self.exit_button.pack(pady=10)

    def load_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if self.image_path:
            self.original_image = cv2.imread(self.image_path)
            self.display_image(self.original_image, "Original Image")

    def generate_pencil_sketch(self):
        if self.original_image is not None:
            gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            inverted_image = 255 - gray_image
            blurred = cv2.GaussianBlur(inverted_image, (21, 21), 0)
            inverted_blurred = 255 - blurred
            self.pencil_sketch = cv2.divide(gray_image, inverted_blurred, scale=256.0)
            self.display_image(self.pencil_sketch, "Pencil Sketch")

    def save_to_database(self):
        if self.user_id is not None and self.image_path is not None and self.pencil_sketch is not None:
            try:
                connection = pymysql.connect(
                    host="localhost",
                    user="root",
                    password="1409Cse@srm",
                    database="pencilsketch"
                )

                with connection.cursor() as cursor:
                    image_data = cv2.imencode('.jpg', self.pencil_sketch)[1].tobytes()
                    sql = "INSERT INTO user_sketches (user_id, image_path, sketch_data) VALUES (%s, %s, %s)"
                    values = (self.user_id, self.image_path, image_data)
                    cursor.execute(sql, values)
                    connection.commit()
                    messagebox.showinfo("Success", "Sketch saved to database successfully!")

            except pymysql.Error as e:
                print("Error:", e)

            finally:
                if connection and connection.open:
                    connection.close()

    def download_sketch(self):
        if self.pencil_sketch is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
            if save_path:
                cv2.imwrite(save_path, self.pencil_sketch)
                messagebox.showinfo("Success", f"Sketch saved to {save_path}")

    def view_history(self):
        try:
            connection = pymysql.connect(
                host="localhost",
                user="root",
                password="1409Cse@srm",
                database="pencilsketch"
            )

            with connection.cursor() as cursor:
                sql = "SELECT image_path, sketch_data FROM user_sketches WHERE user_id = %s"
                cursor.execute(sql, (self.user_id,))
                sketches = cursor.fetchall()

                if not sketches:
                    messagebox.showinfo("Info", "No sketches found for this user.")
                else:
                    self.show_history_window(sketches)

        except pymysql.Error as e:
            print("Error:", e)

        finally:
            if connection and connection.open:
                connection.close()

    def show_history_window(self, sketches):
        history_window = tk.Toplevel(self.root)
        history_window.title("Sketch History")

        tree = ttk.Treeview(history_window)
        tree["columns"] = ("Image Path", "Actions")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("Image Path", anchor=tk.W, width=400)
        tree.column("Actions", anchor=tk.W, width=100)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("Image Path", text="Image Path", anchor=tk.W)
        tree.heading("Actions", text="Actions", anchor=tk.W)

        for index, sketch in enumerate(sketches):
            image_path = sketch[0]
            item_id = f"{index + 1}"  # Unique identifier for each item
            tree.insert("", "end", iid=item_id, values=(image_path,), tags=(image_path,))
            tree.tag_configure(image_path, background="lightgray")
            tree.insert(item_id, "end", text="Actions", values=("Download",), tags=(image_path,))

        tree.pack(expand=tk.YES, fill=tk.BOTH)

    def download_from_history(self, image_path):
        try:
            connection = pymysql.connect(
                host="localhost",
                user="root",
                password="1409Cse@srm",
                database="pencilsketch"
            )

            with connection.cursor() as cursor:
                sql = "SELECT sketch_data FROM user_sketches WHERE image_path = %s"
                cursor.execute(sql, (image_path,))
                sketch_data = cursor.fetchone()[0]

                if sketch_data:
                    sketch_image = cv2.imdecode(numpy.frombuffer(sketch_data, numpy.uint8), cv2.IMREAD_UNCHANGED)
                    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
                    save_path = os.path.join(downloads_dir, os.path.basename(image_path))
                    cv2.imwrite(save_path, sketch_image)
                    messagebox.showinfo("Success", f"Sketch saved to {save_path}")
                else:
                    messagebox.showinfo("Info", "Sketch data not found.")

        except pymysql.Error as e:
            print("Error:", e)

        finally:
            if connection and connection.open:
                connection.close()

    def display_image(self, image, window_name="Image"):
        cv2.imshow(window_name, image)
        cv2.waitKey(1)  # This allows the window to update without waiting for a key press

class LoginRegisterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login/Register")

        # Create variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.login_status = tk.StringVar()
        self.user_id = None

        # Create labels
        tk.Label(root, text="Username:").pack(pady=10)
        username_entry = tk.Entry(root, textvariable=self.username_var)
        username_entry.pack(pady=10)

        tk.Label(root, text="Password:").pack(pady=10)
        password_entry = tk.Entry(root, textvariable=self.password_var, show="*")
        password_entry.pack(pady=10)

        # Create buttons
        login_button = tk.Button(root, text="Login", command=self.login)
        login_button.pack(pady=10)

        register_button = tk.Button(root, text="Register", command=self.register)
        register_button.pack(pady=10)

        # Display login status
        login_status_label = tk.Label(root, textvariable=self.login_status)
        login_status_label.pack(pady=10)

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        try:
            connection = pymysql.connect(
                host="localhost",
                user="root",
                password="1409Cse@srm",
                database="pencilsketch"
            )

            with connection.cursor() as cursor:
                sql = "SELECT user_id FROM users WHERE username = %s AND password = %s"
                cursor.execute(sql, (username, password))
                result = cursor.fetchone()

                if result:
                    self.user_id = result[0]
                    self.open_main_app()
                else:
                    self.login_status.set("Invalid username or password.")

        except pymysql.Error as e:
            print("Error:", e)

        finally:
            if connection and connection.open:
                connection.close()

    def register(self):
        username = self.username_var.get()
        password = self.password_var.get()

        try:
            connection = pymysql.connect(
                host="localhost",
                user="root",
                password="1409Cse@srm",
                database="pencilsketch"
            )

            with connection.cursor() as cursor:
                sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
                cursor.execute(sql, (username, password))
                connection.commit()
                self.login_status.set("Registration successful. Please login.")

        except pymysql.Error as e:
            print("Error:", e)
            self.login_status.set("Registration failed. Try a different username.")

        finally:
            if connection and connection.open:
                connection.close()

    def open_main_app(self):
        self.root.destroy()
        main_root = tk.Tk()
        app = PencilSketchApp(main_root, self.user_id)
        main_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginRegisterApp(root)
    root.mainloop()
