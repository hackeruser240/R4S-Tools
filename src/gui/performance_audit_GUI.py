import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import webbrowser
import os
from functions_folder import performance_audit  # import from your package

class AuditGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lighthouse Performance Audit")
        self.root.geometry("900x500")

        # URL Entry
        self.url_label = ttk.Label(root, text="Enter URL:")
        self.url_label.pack(pady=(10, 0))
        self.url_entry = ttk.Entry(root, width=80)
        self.url_entry.pack(pady=(0, 10))

        # Buttons
        self.button_frame = ttk.Frame(root)
        self.button_frame.pack(pady=5)

        self.process_button = ttk.Button(self.button_frame, text="Process", command=self.run_audit_thread)
        self.process_button.grid(row=0, column=0, padx=10)

        self.view_button = ttk.Button(self.button_frame, text="View HTML", command=self.view_html)
        self.view_button.grid(row=0, column=1, padx=10)

        # Console Output
        self.console = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20)
        self.console.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.audit_result = None

    def run_audit_thread(self):
        threading.Thread(target=self.run_audit, daemon=True).start()

    def run_audit(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Input Error", "Please enter a valid URL.")
            return

        self.console.delete("1.0", tk.END)
        self.console.insert(tk.END, f"Running audit on: {url}. Please wait...\n")

        result = performance_audit.run_lighthouse_audit(url)
        self.audit_result = result

        self.console.insert(tk.END, "\n📊 Audit Result:\n")
        for key, value in result.items():
            self.console.insert(tk.END, f"{key}: {value}\n")

        if "html" in result:
            self.console.insert(tk.END, "\n✅ HTML report generated.\n")
        else:
            self.console.insert(tk.END, "\n⚠️ No HTML report generated.\n")

    def view_html(self):
        if self.audit_result and "html" in self.audit_result:
            full_path = os.path.abspath(self.audit_result["html"])
            webbrowser.open(f'file:///{full_path}')
        else:
            messagebox.showwarning("No Report", "No HTML report available to view.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AuditGUI(root)
    root.mainloop()