import tkinter as tk
from tkinter import messagebox
from whatif import generate_modified_sql, retrieve_aqp
from preprocessing import parse_query, prepare_modifications
import graphviz
from PIL import Image, ImageTk
import os

class QEPWhatIfTool:
    def __init__(self, root):
        self.root = root
        self.root.title("QEP What-If Analysis Tool")

        # Query Panel
        self.query_label = tk.Label(root, text="Enter SQL Query:")
        self.query_label.pack()
        self.query_text = tk.Text(root, height=5, width=80)
        self.query_text.pack()

        # Load QEP Button
        self.load_qep_button = tk.Button(root, text="Load QEP", command=self.load_qep)
        self.load_qep_button.pack()

        # QEP Panel
        self.qep_panel_label = tk.Label(root, text="QEP Visualization:")
        self.qep_panel_label.pack()
        self.qep_canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.qep_canvas.pack()

        # Modification Options
        self.modification_label = tk.Label(root, text="Select Modification:")
        self.modification_label.pack()

        self.modification_var = tk.StringVar(value="None")
        self.modification_options = ["Hash Join to Merge Join", "Seq Scan to Index Scan"]
        self.modification_menu = tk.OptionMenu(root, self.modification_var, *self.modification_options)
        self.modification_menu.pack()

        # Generate AQP Button
        self.generate_aqp_button = tk.Button(root, text="Generate AQP", command=self.generate_aqp)
        self.generate_aqp_button.pack()

        # Modified SQL Panel
        self.modified_sql_label = tk.Label(root, text="Modified SQL:")
        self.modified_sql_label.pack()
        self.modified_sql_text = tk.Text(root, height=5, width=80)
        self.modified_sql_text.pack()

        # Cost Comparison Panel
        self.cost_label = tk.Label(root, text="Cost Comparison:")
        self.cost_label.pack()
        self.cost_text = tk.Text(root, height=2, width=80)
        self.cost_text.pack()

    def load_qep(self):
        """
        Load the QEP for the entered SQL query and visualize it.
        """
        sql_query = self.query_text.get("1.0", "end-1c")
        if not sql_query:
            messagebox.showerror("Error", "Please enter a SQL query.")
            return

        # Parse the query to visualize the QEP
        parsed_query = parse_query(sql_query)
        self.qep_structure = parsed_query  # Store parsed QEP for modification

        # Generate the QEP visualization
        self.visualize_qep(self.qep_structure)

    def visualize_qep(self, qep_structure):
        """
        Visualizes the QEP structure in a tree format using Graphviz.
        """
        # Create a Graphviz Digraph
        dot = graphviz.Digraph(comment="QEP Tree")

        # Example static structure. Replace with dynamic logic as needed.
        dot.node("A", "Seq Scan on nation")
        dot.node("B", "Hash on nation")
        dot.node("C", "Seq Scan on region")
        dot.node("D", "Hash on region")
        dot.node("E", "Hash Join")
        dot.node("F", "Seq Scan on supplier")
        dot.node("G", "Hash on supplier")
        dot.node("H", "Hash Inner Join")
        dot.node("I", "Hash Inner Join (Final)")

        dot.edge("A", "B")
        dot.edge("B", "E")
        dot.edge("C", "D")
        dot.edge("D", "E")
        dot.edge("F", "G")
        dot.edge("G", "H")
        dot.edge("E", "H")
        dot.edge("H", "I")

        # Save and render the graph without specifying .png in the filename
        output_path = os.path.join(os.getcwd(), "qep_graph")
        dot.render(filename=output_path, format='png', cleanup=True)

        # The actual file path will be "qep_graph.png" after rendering
        output_image_path = output_path + ".png"
        
        # Verify if the image file is created
        if os.path.exists(output_image_path):
            # Display the graph in tkinter canvas
            self.display_graph_image(output_image_path)
        else:
            messagebox.showerror("Error", "QEP visualization image could not be generated.")

    def display_graph_image(self, image_path):
        """
        Display the generated Graphviz image on the tkinter canvas.
        """
        try:
            # Open the image using PIL
            img = Image.open(image_path)
            img = img.resize((600, 400), Image.Resampling.LANCZOS)
            self.qep_image = ImageTk.PhotoImage(img)

            # Clear the canvas and display the image
            self.qep_canvas.delete("all")
            self.qep_canvas.create_image(0, 0, anchor="nw", image=self.qep_image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def generate_aqp(self):
        """
        Generate AQP based on modifications and display modified SQL and cost comparison.
        """
        modification = self.modification_var.get()
        if modification == "None":
            messagebox.showinfo("Info", "Please select a modification.")
            return

        # Define modifications based on selection
        modifications = []
        if modification == "Hash Join to Merge Join":
            modifications.append({'type': 'join_change', 'new_type': 'Merge Join'})
        elif modification == "Seq Scan to Index Scan":
            modifications.append({'type': 'scan_change', 'new_type': 'Index Scan'})

        # Generate modified SQL
        modified_sql = generate_modified_sql(self.qep_structure, modifications)
        self.modified_sql_text.delete("1.0", "end")
        self.modified_sql_text.insert("1.0", modified_sql)

        # Retrieve and display AQP
        aqp_data = retrieve_aqp(modified_sql)
        if aqp_data:
            aqp_cost = aqp_data.get("Total Cost", "N/A")  # Assume Total Cost is in JSON
            self.cost_text.delete("1.0", "end")
            self.cost_text.insert("1.0", f"Modified Cost: {aqp_cost}")
        else:
            messagebox.showerror("Error", "Failed to retrieve AQP.")
