# File: gui/keyword_monitor_GUI.py

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from functions_folder.keyword_monitor import track_keyword_rankings
import os

class KeywordMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Keyword Monitor")

        # API Key and CS ID on same line
        frame_top = tk.Frame(root)
        frame_top.pack(pady=10)

        tk.Label(frame_top, text="Google API Key:").grid(row=0, column=0, padx=5)
        self.api_key_entry = tk.Entry(frame_top, width=50)
        self.api_key_entry.insert(0, "AIzaSyCypKkAsjIUYVjsZa0NcC-S1n9lagZefh0")
        self.api_key_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame_top, text="Google CS ID:").grid(row=0, column=2, padx=5)
        self.cx_id_entry = tk.Entry(frame_top, width=25)
        self.cx_id_entry.insert(0, "45df9fdbe77ed4d15")
        self.cx_id_entry.grid(row=0, column=3, padx=5)

        # Keyword input
        tk.Label(root, text="Enter keywords (one per line):").pack()
        self.keyword_text = tk.Text(root, height=8, width=80)
        self.keyword_text.pack(pady=5)

        # Run button
        tk.Button(root, text="Track Rankings", command=self.run_monitor).pack(pady=10)

        # Download button
        tk.Button(root, text="Download Result", command=self.download_result).pack(pady=10)

        # ✅ New dynamic layout using grid
        frame_results = tk.Frame(root)
        frame_results.pack(fill="both", expand=True)

        tk.Label(frame_results, text="Results:").grid(row=0, column=0, sticky="w")

        self.result_window = scrolledtext.ScrolledText(frame_results)
        self.result_window.grid(row=1, column=0, sticky="nsew")

        # ✅ Make result window expand with resizing
        frame_results.rowconfigure(1, weight=1)
        frame_results.columnconfigure(0, weight=1)

        self.result_data = {}

    def run_monitor(self):
        self.result_window.delete("1.0", tk.END)
        keywords = self.keyword_text.get("1.0", tk.END).strip().split("\n")
        keywords = [kw.strip() for kw in keywords if kw.strip()]
        api_key = self.api_key_entry.get().strip()
        cx_id = self.cx_id_entry.get().strip()

        if not keywords or not api_key or not cx_id:
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        try:
            output, _ = track_keyword_rankings(keywords, api_key, cx_id)
            self.result_data = output

            for kw, data in output.items():
                self.result_window.insert(tk.END, f"Keyword: {kw}\n")
                for k, v in data.items():
                    self.result_window.insert(tk.END, f"  {k}: {v}\n")
                self.result_window.insert(tk.END, "\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def download_result(self):
        if not self.result_data:
            messagebox.showwarning("No Data", "No results to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json")],
                                                 title="Save Result As")
        if file_path:
            try:
                import json
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.result_data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Saved", f"Results saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = KeywordMonitorGUI(root)
    root.mainloop()