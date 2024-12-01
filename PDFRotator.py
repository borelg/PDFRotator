import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import fitz  # PyMuPDF


class PDFViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Viewer with Rotation")

        # Maximum display size for the preview
        self.max_width = 800
        self.max_height = 600

        # Initialize variables
        self.pdf_doc = None
        self.current_page_index = 0
        self.rotation = 0
        self.pdf_file = None

        # Create UI elements
        self.canvas = tk.Canvas(root, width=self.max_width, height=self.max_height, bg="grey")
        self.canvas.pack()

        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(side=tk.BOTTOM, pady=10)

        self.open_button = tk.Button(self.buttons_frame, text="Open PDF", command=self.open_pdf)
        self.open_button.pack(side=tk.LEFT, padx=5)

        self.rotate_left_button = tk.Button(self.buttons_frame, text="Rotate Left", command=self.rotate_left)
        self.rotate_left_button.pack(side=tk.LEFT, padx=5)

        self.rotate_right_button = tk.Button(self.buttons_frame, text="Rotate Right", command=self.rotate_right)
        self.rotate_right_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.buttons_frame, text="Save", command=self.save_pdf)
        self.save_button.pack(side=tk.LEFT, padx=5)

    def open_pdf(self):
        self.pdf_file = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if self.pdf_file:
            self.pdf_doc = fitz.open(self.pdf_file)
            self.current_page_index = 0
            self.rotation = 0
            self.show_page()

    def show_page(self):
        if self.pdf_doc is None:
            return

        # Render the page
        page = self.pdf_doc[self.current_page_index]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2).prerotate(self.rotation))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Scale the image to fit within the max dimensions
        img = self.scale_image(img, self.max_width, self.max_height)

        # Display the image
        self.img_tk = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)

    def scale_image(self, img, max_width, max_height):
        """Scale the image to fit within the max dimensions while maintaining aspect ratio."""
        img_width, img_height = img.size
        scale = min(max_width / img_width, max_height / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def rotate_left(self):
        if self.pdf_doc is not None:
            self.rotation -= 90
            self.show_page()

    def rotate_right(self):
        if self.pdf_doc is not None:
            self.rotation += 90
            self.show_page()

    def save_pdf(self):
        if self.pdf_doc is None:
            messagebox.showerror("Error", "No PDF loaded!")
            return

        save_file = filedialog.asksaveasfilename(
            title="Save PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if save_file:
            for page_index in range(len(self.pdf_doc)):
                page = self.pdf_doc[page_index]
                page.set_rotation((page.rotation + self.rotation) % 360)
            self.pdf_doc.save(save_file)
            messagebox.showinfo("Success", "PDF saved successfully!")
            self.pdf_doc = fitz.open(save_file)  # Reload the saved document
            self.rotation = 0  # Reset rotation


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewer(root)
    root.mainloop()
