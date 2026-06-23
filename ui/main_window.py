"""
Main window UI for the application.
"""
import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from utils.logger import logger
from utils.constants import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, OUTPUT_DIR
from services.pdf_reader import PDFReader
from services.parser import DataParser
from services.transformer import DataTransformer
from services.excel_generator import ExcelGenerator

class MainWindow(ctk.CTk):
    """
    The main graphical user interface for the PDF to Excel Converter.
    """
    def __init__(self):
        super().__init__()
        
        ctk.set_appearance_mode("Dark")
        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(700, 550)
        self.configure(fg_color="#11111B")  # Deep dark background
        
        # Configure grid layout (1x1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.selected_file_path = None
        self.pdf_reader = PDFReader()
        self.data_parser = DataParser()
        self.data_transformer = DataTransformer()
        self.excel_generator = ExcelGenerator()
        self.last_saved_dir = None
        
        self.setup_ui()
        logger.info("MainWindow initialized")

    def setup_ui(self):
        """
        Sets up the UI elements.
        """
        # Main Frame (Card Style)
        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#1E1E2E")
        self.main_frame.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        
        # Configure main_frame grid for responsiveness
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # 1. Application Header
        self.header_label = ctk.CTkLabel(
            self.main_frame, 
            text="✨ Post level reader", 
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color="#89B4FA"
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=(40, 5))
        
        self.sub_label = ctk.CTkLabel(
            self.main_frame,
            text="Extract AutoCAD Graph Data to Excel format instantly",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#A6ADC8"
        )
        self.sub_label.grid(row=1, column=0, padx=20, pady=(0, 40))
        
        # 2. Select PDF Button
        self.select_btn = ctk.CTkButton(
            self.main_frame, 
            text="📄 Choose PDF File", 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            height=45,
            corner_radius=10,
            fg_color="#89B4FA",
            hover_color="#74C7EC",
            text_color="#11111B",
            command=self.select_pdf
        )
        self.select_btn.grid(row=2, column=0, padx=20, pady=(10, 5))
        
        # 3. Selected File Label
        self.file_label = ctk.CTkLabel(
            self.main_frame, 
            text="No file selected", 
            font=ctk.CTkFont(family="Segoe UI", size=14, slant="italic"),
            text_color="#6C7086"
        )
        self.file_label.grid(row=3, column=0, padx=20, pady=(0, 30))
        
        # 4. Generate Excel Button
        self.generate_btn = ctk.CTkButton(
            self.main_frame, 
            text="🚀 Generate Excel", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            height=55,
            corner_radius=15,
            fg_color="#A6E3A1",  
            hover_color="#94E2D5",
            text_color="#11111B",
            state="disabled",
            command=self.generate_excel
        )
        self.generate_btn.grid(row=4, column=0, padx=20, pady=10)
        
        # 5. Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame, 
            mode="determinate",
            height=10,
            corner_radius=5,
            progress_color="#F9E2AF",
            fg_color="#313244"
        )
        self.progress_bar.grid(row=5, column=0, padx=80, pady=(30, 10), sticky="ew")
        self.progress_bar.set(0)
        
        # 6. Status Label
        self.status_label = ctk.CTkLabel(
            self.main_frame, 
            text="Ready to process...", 
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#BAC2DE",
            width=300,
            anchor="center"
        )
        self.status_label.grid(row=6, column=0, padx=20, pady=5)
        
        # Spacer to push bottom buttons down
        self.main_frame.grid_rowconfigure(7, weight=1)
        
        # 7. Open Containing Folder Button
        self.open_output_btn = ctk.CTkButton(
            self.main_frame, 
            text="📂 Open Containing Folder", 
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="transparent",
            border_width=1,
            border_color="#CBA6F7",
            text_color="#CBA6F7",
            hover_color="#313244",
            corner_radius=8,
            state="disabled",
            command=self.open_output_folder
        )
        self.open_output_btn.grid(row=8, column=0, padx=20, pady=(10, 40))

    def select_pdf(self):
        """
        Handles PDF file selection.
        """
        logger.info("Opening file dialog for PDF selection")
        file_path = filedialog.askopenfilename(
            title="Select a PDF File",
            filetypes=[("PDF Files", "*.pdf")]
        )
        
        if file_path:
            if not file_path.lower().endswith('.pdf'):
                messagebox.showerror("Invalid File", "Please select a valid PDF file.")
                return
                
            self.selected_file_path = file_path
            self.file_label.configure(text=os.path.basename(file_path), text_color="#A6E3A1")
            self.generate_btn.configure(state="normal")
            self.status_label.configure(text="PDF selected. Ready to extract.", text_color="#BAC2DE")
            self.progress_bar.set(0)
            logger.info(f"Selected PDF: {file_path}")

    def generate_excel(self):
        """
        Starts the PDF reading and Excel generation process.
        """
        if not self.selected_file_path:
            return
            
        input_filename = os.path.basename(self.selected_file_path)
        name_without_ext, _ = os.path.splitext(input_filename)
        default_output_filename = f"{name_without_ext}_Output.xlsx"
        
        save_path = filedialog.asksaveasfilename(
            title="Save Excel File",
            initialfile=default_output_filename,
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        
        if not save_path:
            return
            
        logger.info("Generate Excel button clicked")
        
        # Disable buttons during processing
        self.generate_btn.configure(state="disabled")
        self.select_btn.configure(state="disabled")
        self.status_label.configure(text="Starting PDF extraction...")
        self.progress_bar.set(0)
        
        self.last_saved_dir = os.path.dirname(save_path)
        
        # Run processing in a background thread to keep UI responsive
        threading.Thread(target=self._process_pdf, args=(save_path,), daemon=True).start()

    def _process_pdf(self, save_path):
        """
        Background task orchestrating the full conversion pipeline.
        """
        try:
            # Phase 1: Read PDF
            extracted_text = self.pdf_reader.read_pdf(
                self.selected_file_path, 
                progress_callback=self._update_progress
            )
            
            logger.info(f"Extracted {len(extracted_text)} characters of text. Starting parsing...")
            
            # Phase 2: Parse
            self.after(0, self._set_progress_ui, 0.8, "Parsing extracted data...")
            parsed_blocks = self.data_parser.parse_data(extracted_text)
            
            if not parsed_blocks:
                raise ValueError("No valid NAYA PYNE blocks found in the PDF.")
                
            logger.info(f"Successfully parsed {len(parsed_blocks)} NAYA PYNE blocks.")
            
            # Phase 3: Transform
            self.after(0, self._set_progress_ui, 0.9, "Transforming data format...")
            transformed_data = self.data_transformer.transform_data(parsed_blocks)
            logger.info(f"Transformed into {len(transformed_data)} rows.")
            
            # Phase 4: Generate Excel
            self.after(0, self._set_progress_ui, 0.95, "Generating Excel file...")
            
            final_path = self.excel_generator.generate_excel(transformed_data, save_path)
            
            # Success
            self.after(0, self._set_progress_ui, 1.0, "Finalizing...")
            self.after(0, lambda: self._on_processing_success(final_path))
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            self.after(0, self._on_processing_error, str(e))

    def _update_progress(self, current_page, total_pages):
        """
        Callback to update progress bar and status label from background thread.
        Allocates 0.0 to 0.7 of the progress bar for PDF reading.
        """
        progress = (current_page / total_pages) * 0.7
        status_text = f"Reading PDF... Page {current_page} of {total_pages}"
        
        # Safely update UI from thread using self.after
        self.after(0, self._set_progress_ui, progress, status_text)

    def _set_progress_ui(self, progress, status_text):
        """
        Updates the UI elements for progress.
        """
        self.progress_bar.set(progress)
        self.status_label.configure(text=status_text)

    def _on_processing_success(self, final_path=""):
        """
        Handles successful PDF processing.
        """
        filename = os.path.basename(final_path) if final_path else "Unknown"
        self.status_label.configure(text=f"✅ Completed successfully!", text_color="#A6E3A1")
        self.generate_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.open_output_btn.configure(state="normal")
        self.show_custom_popup("Success! 🎉", f"Excel sheet generated successfully!\n\nFile saved to:\n{filename}")

    def show_custom_popup(self, title, message):
        """
        Shows a custom themed popup window matching the app UI.
        """
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("400x200")
        popup.resizable(False, False)
        popup.configure(fg_color="#1E1E2E")
        
        # Make it modal (blocks main window)
        popup.transient(self)
        popup.grab_set()
        
        # Center the popup relative to the main window
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (400 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (200 // 2)
        popup.geometry(f"+{x}+{y}")
        
        lbl_title = ctk.CTkLabel(
            popup, 
            text=title, 
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"), 
            text_color="#A6E3A1"
        )
        lbl_title.pack(pady=(20, 10))
        
        lbl_msg = ctk.CTkLabel(
            popup, 
            text=message, 
            font=ctk.CTkFont(family="Segoe UI", size=14), 
            text_color="#BAC2DE", 
            wraplength=350
        )
        lbl_msg.pack(pady=(0, 20))
        
        btn_ok = ctk.CTkButton(
            popup, 
            text="Awesome!", 
            command=popup.destroy, 
            width=120, 
            height=35,
            corner_radius=8,
            fg_color="#89B4FA", 
            hover_color="#74C7EC", 
            text_color="#11111B", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        btn_ok.pack()

    def _on_processing_error(self, error_message):
        """
        Handles errors during PDF processing.
        """
        self.progress_bar.set(0)
        self.status_label.configure(text=f"Error occurred.")
        self.generate_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        messagebox.showerror("Processing Error", f"An error occurred during processing:\n\n{error_message}")

    def open_output_folder(self):
        """
        Opens the containing folder of the saved Excel file.
        """
        if not self.last_saved_dir or not os.path.exists(self.last_saved_dir):
            return
            
        logger.info(f"Opening folder: {self.last_saved_dir}")
        try:
            os.startfile(self.last_saved_dir)
        except Exception as e:
            logger.error(f"Failed to open directory: {e}")
            self.status_label.configure(text=f"Error opening folder")
            messagebox.showerror("Directory Error", f"Could not open folder:\n{e}")
