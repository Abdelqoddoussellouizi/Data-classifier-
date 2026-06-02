"""
Tkinter GUI application for Chinese personal data classification.
Features: File browsing, drag-and-drop support, and result export to CSV.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.ttk import Button, Label, Entry, Frame
from pathlib import Path
import threading

try:
    import tkinterdnd2
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False

from data_classifier import DataClassifier


class ClassifierGUI:
    """GUI application for data classification."""
    
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Chinese Data Classifier")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.classifier = DataClassifier()
        self.input_file = None
        self.results = []
        
        self._create_widgets()
        self._setup_drag_drop()
    
    def _create_widgets(self):
        """Create GUI widgets."""
        # Main container
        main_frame = Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # File selection section
        file_frame = Frame(main_frame)
        file_frame.pack(fill="x", pady=10)
        
        Label(file_frame, text="Input File:").pack(side="left", padx=5)
        
        self.file_label = Label(file_frame, text="No file selected", foreground="gray")
        self.file_label.pack(side="left", fill="x", expand=True, padx=5)
        
        Button(file_frame, text="Browse", command=self._browse_file).pack(side="right", padx=5)
        
        # Drag-and-drop hint
        if DRAG_DROP_AVAILABLE:
            hint_label = Label(main_frame, text="or drag and drop a file here", foreground="blue", font=("Arial", 9, "italic"))
            hint_label.pack(pady=5)
        
        # Output filename section
        # Output folder section
        output_dir_frame = Frame(main_frame)
        output_dir_frame.pack(fill="x", pady=6)

        Label(output_dir_frame, text="Output Folder:").pack(side="left", padx=5)
        self.output_dir_entry = Entry(output_dir_frame)
        self.output_dir_entry.insert(0, os.getcwd())
        self.output_dir_entry.pack(side="left", fill="x", expand=True, padx=5)
        Button(output_dir_frame, text="Browse Folder...", command=self._browse_output_folder).pack(side="left", padx=5)

        # Output filename section
        output_frame = Frame(main_frame)
        output_frame.pack(fill="x", pady=6)

        Label(output_frame, text="Output Filename:").pack(side="left", padx=5)

        self.output_entry = Entry(output_frame)
        self.output_entry.insert(0, "classification_results.csv")
        self.output_entry.pack(side="left", fill="x", expand=True, padx=5)
        # Browse for output filename (Save As) — will set folder and filename
        Button(output_frame, text="Browse File...", command=self._browse_output).pack(side="left", padx=5)
        
        # Process button
        button_frame = Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        self.process_button = Button(button_frame, text="Process File", command=self._process_file)
        self.process_button.pack(side="left", padx=5)
        
        Button(button_frame, text="Save Results", command=self._save_results, state="disabled").pack(side="left", padx=5)
        self.save_button = button_frame.winfo_children()[-1]
        
        # Log/status display
        log_frame = Frame(main_frame)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        Label(log_frame, text="Log Output:").pack(anchor="w")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=90, state="normal")
        self.log_text.pack(fill="both", expand=True)
        
        self._log("Application started. Ready to classify data.")
        if not DRAG_DROP_AVAILABLE:
            self._log("Note: tkinterdnd2 not available. Drag-and-drop disabled. Use Browse button instead.")
    
    def _setup_drag_drop(self):
        """Setup drag-and-drop functionality."""
        if not DRAG_DROP_AVAILABLE:
            return
        try:
            # If the root already supports drop_target_register/dnd_bind, use it
            if hasattr(self.root, 'drop_target_register') and hasattr(self.root, 'dnd_bind'):
                self.root.drop_target_register(tkinterdnd2.DND_FILES)
                self.root.dnd_bind('<<Drop>>', self._drop_file)
            else:
                # Otherwise, try to create a TkinterDnD root if available and replace root
                if hasattr(tkinterdnd2, 'TkinterDnD') and hasattr(tkinterdnd2.TkinterDnD, 'Tk'):
                    try:
                        new_root = tkinterdnd2.TkinterDnD.Tk()
                        # transfer geometry and title
                        new_root.geometry(self.root.geometry())
                        new_root.title(self.root.title())
                        # reparent main widgets by setting self.root to new_root
                        self.root = new_root
                        self.root.drop_target_register(tkinterdnd2.DND_FILES)
                        self.root.dnd_bind('<<Drop>>', self._drop_file)
                    except Exception:
                        self._log('Drag-and-drop not available for this environment.')
                else:
                    self._log('Drag-and-drop not available for this environment.')
        except Exception as e:
            self._log(f"Drag-and-drop setup error: {e}")
    
    def _drop_file(self, event):
        """Handle file drop event."""
        try:
            # Parse the dropped file path
            file_path = event.data
            # Remove curly braces if present
            if isinstance(file_path, str):
                file_path = file_path.strip('{}')
            
            if os.path.isfile(file_path):
                self.input_file = file_path
                self.file_label.config(text=os.path.basename(file_path), foreground="black")
                self._log(f"File selected: {file_path}")
        except Exception as e:
            self._log(f"Error handling dropped file: {e}")
    
    def _browse_file(self):
        """Open file browser dialog."""
        file_path = filedialog.askopenfilename(
            title="Select input file",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.input_file = file_path
            self.file_label.config(text=os.path.basename(file_path), foreground="black")
            self._log(f"File selected: {file_path}")

    def _browse_output(self):
        """Open Save As dialog to choose output CSV filename."""
        file_path = filedialog.asksaveasfilename(
            title="Select output CSV file",
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
            initialfile=self.output_entry.get().strip() or 'classification_results.csv',
            initialdir=self.output_dir_entry.get().strip() or os.getcwd(),
        )

        if file_path:
            # Ensure .csv extension
            if not file_path.lower().endswith('.csv'):
                file_path += '.csv'
            folder = os.path.dirname(file_path)
            name = os.path.basename(file_path)
            # Update both folder and filename fields
            self.output_dir_entry.delete(0, 'end')
            self.output_dir_entry.insert(0, folder)
            self.output_entry.delete(0, 'end')
            self.output_entry.insert(0, name)
            self._log(f"Output file set: {file_path}")

    def _browse_output_folder(self):
        """Open folder dialog to choose output directory."""
        folder = filedialog.askdirectory(
            title="Select output folder",
            initialdir=self.output_dir_entry.get().strip() or os.getcwd()
        )
        if folder:
            self.output_dir_entry.delete(0, 'end')
            self.output_dir_entry.insert(0, folder)
            self._log(f"Output folder set: {folder}")
    
    def _process_file(self):
        """Process the selected file in a separate thread."""
        if not self.input_file:
            messagebox.showwarning("Warning", "Please select a file first.")
            return
        
        self._log("Starting file processing...")
        self.process_button.config(state="disabled")
        
        # Run processing in a separate thread to avoid freezing GUI
        thread = threading.Thread(target=self._process_file_thread)
        thread.daemon = True
        thread.start()
    
    def _process_file_thread(self):
        """Thread function for file processing."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                data_list = [line.strip() for line in f.readlines() if line.strip()]
            
            self._log(f"Read {len(data_list)} items from file.")
            
            # Classify data
            self.results = self.classifier.classify_data(data_list)
            
            # Count classifications
            name_count = sum(1 for r in self.results if r['classification'] == 'Name')
            id_count = sum(1 for r in self.results if r['classification'] == 'ID Card')
            phone_count = sum(1 for r in self.results if r['classification'] == 'Phone')
            unknown_count = sum(1 for r in self.results if r['classification'] == 'Unknown')
            
            self._log(f"Classification complete!")
            self._log(f"  Names: {name_count}")
            self._log(f"  ID Cards: {id_count}")
            self._log(f"  Phones: {phone_count}")
            self._log(f"  Unknown: {unknown_count}")
            
            # Enable save button
            self.root.after(0, lambda: self.save_button.config(state="normal"))
            
        except Exception as e:
            self._log(f"Error processing file: {e}")
        finally:
            self.root.after(0, lambda: self.process_button.config(state="normal"))
    
    def _save_results(self):
        """Save classification results to CSV."""
        if not self.results:
            messagebox.showwarning("Warning", "No results to save. Process a file first.")
            return
        
        output_filename = self.output_entry.get().strip()
        
        if not output_filename:
            messagebox.showwarning("Warning", "Please specify an output filename.")
            return
        
        # Determine final output path: if output_entry is absolute path, use it;
        # otherwise combine output_dir_entry + output_entry
        if os.path.isabs(output_filename):
            final_path = output_filename
        else:
            out_dir = self.output_dir_entry.get().strip() or os.getcwd()
            final_path = os.path.join(out_dir, output_filename)
        # Normalize and ensure .csv
        final_path = os.path.abspath(final_path)
        if not final_path.lower().endswith('.csv'):
            final_path += '.csv'
        # Confirm with the user before saving
        confirm = messagebox.askyesno("Confirm Save", f"Save results to:\n{final_path}\n\nProceed?")
        if not confirm:
            self._log("Save cancelled by user.")
            return

        # Ensure output directory exists
        output_dir = os.path.dirname(final_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                self._log(f"Created output directory: {output_dir}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create output directory:\n{e}")
                return

        try:
            if self.classifier.save_to_csv(self.results, final_path):
                self._log(f"Results saved to: {final_path}")
                messagebox.showinfo("Success", f"Results saved to:\n{os.path.abspath(final_path)}")
            else:
                messagebox.showerror("Error", "Failed to save results.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving file: {e}")
    
    def _log(self, message: str):
        """Add message to log display."""
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="normal")


def main():
    """Main entry point for the GUI application."""
    if DRAG_DROP_AVAILABLE:
        try:
            root = tkinterdnd2.TkinterDnD.Tk()
        except Exception:
            root = tk.Tk()
    else:
        root = tk.Tk()

    app = ClassifierGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
