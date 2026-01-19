import PyPDF2
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from html.parser import HTMLParser
import csv

def count_vulnerabilities_in_fix_groups(pdf_path):
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    section_started = False
    section_text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if not text:
                continue
            if not section_started:
                idx = text.find("Issues - By Fix Groups:")
                if idx != -1:
                    section_started = True
                    section_text += text[idx + len("Issues - By Fix Groups:") :]
            elif section_started:
                # Stop if another heading is found (e.g., a line with only uppercase letters and colon)
                import re
                match = re.search(r"\n[A-Z][A-Z\s\-]+:", text)
                if match:
                    section_text += text[: match.start()]
                    break
                else:
                    section_text += text
    # Count severities in the extracted section
    for severity in counts.keys():
        counts[severity] = section_text.count(severity)
    return counts

class LicenseRiskHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_section = False
        self.risk_counts = {}
        self.capture = False
        self.current_risk = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_section = True
        if self.in_section and tag == "tr":
            self.capture = True

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_section = False
        if tag == "tr":
            self.capture = False
            self.current_risk = None

    def handle_data(self, data):
        if self.in_section and self.capture:
            data = data.strip()
            if data in ["High", "Medium", "Low", "None", "Unknown"]:
                self.current_risk = data
            elif self.current_risk and data.isdigit():
                self.risk_counts[self.current_risk] = self.risk_counts.get(self.current_risk, 0) + int(data)
                self.current_risk = None

def count_license_risks(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    parser = LicenseRiskHTMLParser()
    # Find the section "Total Open Source License Types:"
    section_start = html_content.find("Total Open Source License Types:")
    if section_start == -1:
        return {}
    # Parse only the relevant section (from the heading to the next heading or end)
    section = html_content[section_start:]
    parser.feed(section)
    return parser.risk_counts

def count_issues_by_severity_in_fix_groups_html(html_path):
    severities = ["Critical", "High", "Medium", "Low", "Informational"]
    counts = {sev: 0 for sev in severities}
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    # Find the section "Issues - By Fix Groups:"
    section_start = html_content.find("Issues - By Fix Groups:")
    if section_start == -1:
        return counts
    section = html_content[section_start:]
    # Optionally, stop at the next heading (e.g., next <h1>, <h2>, or similar marker)
    import re
    match = re.search(r"<h[1-6][^>]*>.*:</h[1-6]>", section)
    if match and match.start() > 0:
        section = section[:match.start()]
    # Count severities in the section
    for sev in severities:
        counts[sev] = section.count(sev)
    return counts

def count_issues_by_severity_from_csv(csv_path):
    severities = ["Critical", "High", "Medium", "Low", "Informational"]
    counts = {sev: 0 for sev in severities}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            severity = row.get("Severity", "").capitalize()
            if severity in counts:
                counts[severity] += 1
    return counts

def count_severity_from_csv(csv_path):
    counts = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            severity = row.get("Severity", "").strip()
            if severity:
                counts[severity] = counts.get(severity, 0) + 1
    return counts

def count_severity_from_issue_counters(csv_path):
    severities = [
        "Critical Issues",
        "High Issues",
        "Medium Issues",
        "Low Issues",
        "Informational Issues"
    ]
    counts = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Find the line with "Issue Counters:"
    for i, line in enumerate(lines):
        if line.strip().startswith("Issue Counters:"):
            # Next line is header, next-next line is values
            header = [h.strip() for h in lines[i+1].split(",")]
            values = [v.strip().strip('"') for v in lines[i+2].split(",")]
            for sev in severities:
                if sev in header:
                    idx = header.index(sev)
                    counts[sev] = int(values[idx])
            break
    return counts

def select_file_and_count():
    root = tk.Tk()
    root.withdraw()
    pdf_file = filedialog.askopenfilename(
        title="Select PDF Report",
        filetypes=[("PDF files", "*.pdf")]
    )
    if pdf_file:
        try:
            result = count_vulnerabilities_in_fix_groups(pdf_file)
            msg = "Vulnerability Counts (Issues - By Fix Groups):\n" + "\n".join(f"{severity}: {count}" for severity, count in result.items())
            messagebox.showinfo("Results", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file:\n{e}")
    else:
        messagebox.showinfo("Info", "No file selected.")

def select_html_file_and_count():
    root = tk.Tk()
    root.withdraw()
    html_file = filedialog.askopenfilename(
        title="Select SCA-API License HTML Report",
        filetypes=[("HTML files", "*.html")]
    )
    if html_file:
        try:
            result = count_license_risks(html_file)
            if result:
                msg = "License Risk Counts (Total Open Source License Types):\n" + "\n".join(f"{risk}: {count}" for risk, count in result.items())
            else:
                msg = "No risk data found in the selected HTML file."
            messagebox.showinfo("Results", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file:\n{e}")
    else:
        messagebox.showinfo("Info", "No file selected.")

def select_html_file_and_count_sca_api():
    root = tk.Tk()
    root.withdraw()
    html_file = filedialog.askopenfilename(
        title="Select SCA API HTML Report",
        filetypes=[("HTML files", "*.html")]
    )
    if html_file:
        try:
            result = count_issues_by_severity_in_fix_groups_html(html_file)
            msg = "SCA API Issues (By Fix Groups):\n" + "\n".join(f"{sev}: {count}" for sev, count in result.items())
            messagebox.showinfo("Results", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file:\n{e}")
    else:
        messagebox.showinfo("Info", "No file selected.")

def select_csv_file_and_count():
    root = tk.Tk()
    root.withdraw()
    csv_file = filedialog.askopenfilename(
        title="Select CSV Report",
        filetypes=[("CSV files", "*.csv")]
    )
    if csv_file:
        try:
            result = count_severity_from_issue_counters(csv_file)
            msg = "Issue Counts (CSV Summary):\n" + "\n".join(f"{sev}: {count}" for sev, count in result.items())
            messagebox.showinfo("Results", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file:\n{e}")
    else:
        messagebox.showinfo("Info", "No file selected.")

def main():
    root = tk.Tk()
    root.withdraw()
    choices = [
        "SCA API License",
        "SCA API",
        "SCA UI License",
        "SCA UI",
        "SAST API",
        "SAST UI",
        "DAST"
    ]
    choice = simpledialog.askstring(
        "Select Report Type",
        "Enter your choice:\n" + "\n".join(f"{i+1}. {c}" for i, c in enumerate(choices))
    )
    if not choice:
        messagebox.showinfo("Info", "No choice selected.")
        return

    choice = choice.strip().lower()
    if choice in ["1", "sca api license", "3", "sca ui license"]:
        select_html_file_and_count()
    elif choice in ["2", "sca api", "4", "sca ui", "5", "sast api", "6", "sast ui", "7", "dast"]:
        select_csv_file_and_count()
    else:
        messagebox.showinfo("Info", f"No functionality implemented for '{choice}' yet.")

if __name__ == "__main__":
    main()
