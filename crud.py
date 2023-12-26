from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter.ttk import Treeview
from pymongo import MongoClient
from bson import ObjectId
from PIL import Image
from io import BytesIO
import webbrowser
from tkinter import Tk, Label, Entry, Button, messagebox
import customtkinter 

# MongoDB Connection
client = MongoClient('mongodb://localhost:27017/')
db = client['projecthci']
collection = db['students']

# Login Window
def login_window():
    def login():
        global name
        name = entry_name.get()
        password = entry_password.get()  # Get the entered password
        
        if name == "Mostafa" and password == "password":  # Hardcoded username and password
            window_login.destroy()
            library_window()
        else:
            messagebox.showerror("Login Error", "Invalid username or password!")  # Show error message for incorrect credentials

    window_login = customtkinter.CTk()
    window_login.title("Login page")
    window_login.geometry("400x400")


    # Title Label
    label_title = customtkinter.CTkLabel(
    window_login,
    text="Welcome to the HCI System",
    font=("Arial", 18)
)
    label_title.pack(pady=10)

    frame = customtkinter.CTkFrame(master=window_login)  
    frame.pack(pady=20,padx=40,fill='both',expand=True)  
    
    label = customtkinter.CTkLabel(master=frame,text='Please log-in here')  
    label.pack(pady=12,padx=10)  
    
    entry_name= customtkinter.CTkEntry(master=frame,placeholder_text="Username")  
    entry_name.pack(pady=12,padx=10)  
    
    entry_password= customtkinter.CTkEntry(master=frame,placeholder_text="Password",show="*")  
    entry_password.pack(pady=12,padx=10)  
    
    button = customtkinter.CTkButton(master=frame,text='Login',command=login)  
    button.pack(pady=12,padx=10)  
    
    checkbox = customtkinter.CTkCheckBox(master=frame,text='Remember Me')  
    checkbox.pack(pady=12,padx=10) 

    window_login.mainloop()

def library_display():
    
    library_display = customtkinter.CTk()
    
    library_display.title("HCI System Page")
    
    library_display.geometry("1000x1000")
    
    library_display.state('zoomed')
    
    library_display.mainloop()


def library_window():
    # Create the main window
    library_window = Tk()
    library_window.title("HCI System")
    library_window.geometry("800x420")
    # Set a custom background color
    library_window.configure(bg="#DCF8C6")

    
    title_label = Label(library_window, text="Name", bg="#f2f2f2", fg="#333333", font=("Helvetica", 12))
    title_label.grid(row=1, column=0, sticky=W, padx=10, pady=5)
    title_entry = Entry(library_window, font=("Helvetica", 12))
    title_entry.grid(row=1, column=1, padx=10, pady=5)
    
    title_labell = Label(library_window, text="ID", bg="#f2f2f2", fg="#333333", font=("Helvetica", 12))
    title_labell.grid(row=2, column=0, sticky=W, padx=10, pady=5)
    title_entryy = Entry(library_window, font=("Helvetica", 12))
    title_entryy.grid(row=2, column=1, padx=10, pady=5)
    

    file_labelll = Label(library_window, text="Image", bg="#f2f2f2", fg="#333333", font=("Helvetica", 12))
    file_labelll.grid(row=3, column=0, sticky=W, padx=10, pady=5)
    file_entryyy = Entry(library_window, state=DISABLED, font=("Helvetica", 12))
    file_entryyy.grid(row=3, column=1, padx=10, pady=5)

    # Treeview widget to display the item list
    item_list = Treeview(library_window, columns=("Name", "ID", "Image"), show="headings", selectmode="browse")
    item_list.heading("#0", text="ID")
    item_list.heading("Name", text="Name")
    item_list.heading("ID", text="ID")
    item_list.heading("Image", text="Image")
    item_list.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    # Configure the Treeview style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#ffffff", foreground="#333333", fieldbackground="#ffffff", font=("Helvetica", 11))
    style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))

    
    def insert_item():
        title = title_entry.get()
        titlee = title_entryy.get()
        file_path = file_entryyy.get()

        # Check if a file path is selected
        if not file_path:
            messagebox.showerror("Error", "Please select a file.")
            return

        try:
            # Read the file content
            with open(file_path, 'rb') as file:
                file_data = file.read()

            # Insert the item into MongoDB
            item = {
                'title': title,
                'titlee': titlee,
                'file': file_data
            }
            collection.insert_one(item)

            # Clear the entry fields
            title_entry.delete(0, END)
            title_entryy.delete(0, END)
            file_entryyy.delete(0, END)

            # Update the item list
            update_item_list()
            print("Item has successfully created..")

        except FileNotFoundError:
            messagebox.showerror("Error", "File not found.")
    
    def update_item_list():
        # Clear the item list
        item_list.delete(*item_list.get_children())
        
        # Retrieve all items from MongoDB
        items = collection.find()
        
        # Display the items in the item list
        for item in items:
            item_id = str(item['_id'])
            item_type = item['title']
            titlee = item['titlee']
            file = item['file']
            item_list.insert("", "end", text=item_id, values=(item_type, titlee,file))

    def update_item():
    # Get the selected item from the Treeview
     selected_item = item_list.selection()

     if selected_item:
        item_id = item_list.item(selected_item)['text']  # Get the ID from the first column

        # Retrieve the item from MongoDB
        item = collection.find_one({'_id': ObjectId(item_id)})

        # Create a new window for updating item details
        update_window = Tk()
        update_window.title("Update Item")
        update_window.geometry("400x200")
        update_window.configure(bg="#f2f2f2")

        type_label = Label(update_window, text="Name", bg="#f2f2f2", fg="#333333", font=("Helvetica", 12))
        type_label.grid(row=0, column=0, sticky=W, padx=10, pady=5)
        type_entry = Entry(update_window, font=("Helvetica", 12))
        type_entry.grid(row=0, column=1, padx=10, pady=5)

        title_label = Label(update_window, text="ID", bg="#f2f2f2", fg="#333333", font=("Helvetica", 12))
        title_label.grid(row=1, column=0, sticky=W, padx=10, pady=5)
        title_entry = Entry(update_window, font=("Helvetica", 12))
        title_entry.grid(row=1, column=1, padx=10, pady=5)

        # Populate entry widgets with existing values
        type_entry.insert(0, item['title'])
        title_entry.insert(0, item['titlee'])

        def save_changes():
            # Get the updated values from the entry widgets
            updated_type = type_entry.get()
            updated_title = title_entry.get()     

            # Update the item in MongoDB
            collection.update_one(
                {'_id': ObjectId(item_id)},
                {'$set': {'title': updated_type, 'titlee': updated_title}}
            )

            # Update the item list
            update_item_list()
            print("Item has been successfully updated.")

            # Close the update window
            update_window.destroy()

        # Button to save changes
        save_button = Button(update_window, text="Save Changes", command=save_changes, font=("Helvetica", 12), bg="#4CAF50", fg="#ffffff", padx=10, pady=5)
        save_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Start the main loop for the update window
        update_window.mainloop()
     else:
        messagebox.showinfo("Info", "Please select an item to update.")

    
    def browse_file():
        file_path = filedialog.askopenfilename()
        file_entryyy.config(state=NORMAL)  # Enable the entry widget
        file_entryyy.delete(0, END)
        file_entryyy.insert(0, file_path)
        file_entryyy.config(state=DISABLED)  # Disable the entry widget again

    def delete_item():
     selected_item = item_list.focus()
     if selected_item:
        item_id = item_list.item(selected_item)['text']  # Get the ID from the first column

        # Ask for confirmation before deleting
        confirmation = messagebox.askyesno("Delete Item", "Are you sure you want to delete this item?")
        
        if confirmation:
            # Delete the item from MongoDB
            collection.delete_one({'_id': ObjectId(item_id)})

            # Update the item list
            update_item_list()
            print("Item has been successfully deleted.")
     else:
        messagebox.showinfo("Info", "Please select an item to delete.")

    def show_item():
            selected_item = item_list.focus()
            if selected_item:
                item_id = item_list.item(selected_item)['text']  # Get the ID from the first column

                # Retrieve the item from MongoDB
                item = collection.find_one({'_id': ObjectId(item_id)})

                file_data = item['file']
                image = Image.open(BytesIO(file_data))
                image.show()
            
            else:
                messagebox.showinfo("Info", "Please select an item to show.")
    
    insert_button = Button(library_window, text="Add Item", command=insert_item, font=("Helvetica", 12), bg="#4CAF50", fg="#ffffff", padx=10, pady=5)
    insert_button.grid(row=5, column=0, pady=5)

    browse_button = Button(library_window, text="Browse collection", command=browse_file, font=("Helvetica", 12), bg="#008CBA", fg="#ffffff", padx=10, pady=5)
    browse_button.grid(row=3, column=2, padx=5)

    delete_button = Button(library_window, text="Delete Item", command=delete_item, font=("Helvetica", 12), bg="#f44336", fg="#ffffff", padx=10, pady=5)
    delete_button.grid(row=5, column=2, pady=5)

    update_button = Button(library_window, text="Update Item", command=update_item, font=("Helvetica", 12), bg="#FF9800", fg="#ffffff", padx=10, pady=5)
    update_button.grid(row=5, column=1, pady=5)
    
    show_button = Button(library_window, text="Show Image", command=show_item, font=("Helvetica", 12), bg="black", fg="#ffffff", padx=10, pady=5)
    show_button.grid(row=4, column=2, pady=5)

    # Initial item list update
    update_item_list()

    # Start the main loop
    library_window.mainloop()

login_window()