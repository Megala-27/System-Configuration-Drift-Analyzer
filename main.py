# Automated System Configuration Drift Analyzer

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import subprocess
import csv
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "drift_analyzer")

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        connection_timeout=5
    )

def initialize_database():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config_baseline (
                id INT AUTO_INCREMENT PRIMARY KEY,
                setting_name VARCHAR(100) NOT NULL UNIQUE,
                expected_value VARCHAR(100) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configurations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                setting_name VARCHAR(100) NOT NULL,
                expected_value VARCHAR(100),
                current_value VARCHAR(100),
                drift_status VARCHAR(50),
                scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()

        return True

    except mysql.connector.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Database initialization failed:\n{error}"
        )
        return False

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


#FIREWALL STATUS 
def get_firewall_status():

    try:
        result = subprocess.run(
            [
                "netsh",
                "advfirewall",
                "show",
                "allprofiles",
                "state"
            ],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0:
            error_message = result.stderr.strip()
            print("Firewall command error:", error_message)
            return None

        states = []

        for line in result.stdout.splitlines():

            parts = line.strip().split()

            if (
                len(parts) >= 2
                and parts[0].lower() == "state"
            ):
                state = parts[-1].upper()

                if state in ("ON", "OFF"):
                    states.append(state)

        if not states:
            print("Firewall status could not be detected.")
            return None

        if all(state == "ON" for state in states):
            return "ON"

        if all(state == "OFF" for state in states):
            return "OFF"

        return None

    except (subprocess.SubprocessError, OSError) as error:
        print("Firewall detection error:", error)
        return None


#SCAN SYSTEM 

def scan_system():

    current = get_firewall_status()

    if current is None:
        messagebox.showwarning(
            "Scan Error",
            "Could not determine a consistent firewall status.\n\n"
            "Please check Windows Firewall and try again."
        )
        return

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Retrieve saved baseline.
        cursor.execute(
            """
            SELECT expected_value
            FROM config_baseline
            WHERE setting_name = %s
            """,
            ("Windows Firewall",)
        )

        baseline = cursor.fetchone()

        if baseline is None:

            # First scan: save current value as baseline.
            cursor.execute(
                """
                INSERT INTO config_baseline
                (setting_name, expected_value)
                VALUES (%s, %s)
                """,
                ("Windows Firewall", current)
            )

            expected = current
            status = "BASELINE SAVED"

        else:

            expected = baseline[0]

            if current == expected:
                status = "NORMAL"
            else:
                status = "DRIFT DETECTED"

        # Save every scan into history.
        cursor.execute(
            """
            INSERT INTO configurations
            (
                setting_name,
                expected_value,
                current_value,
                drift_status
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                "Windows Firewall",
                expected,
                current,
                status
            )
        )

        connection.commit()

        print(
            f"Saved scan: Expected={expected}, "
            f"Current={current}, Status={status}"
        )

        result_text.config(
            text=(
                f"Expected: {expected} | "
                f"Current: {current} | "
                f"Result: {status}"
            )
        )

        # Reload the database records into the GUI.
        load_history()

        if status == "DRIFT DETECTED":

            messagebox.showwarning(
                "Configuration Drift",
                f"Expected firewall status: {expected}\n"
                f"Current firewall status: {current}\n\n"
                "Configuration drift detected!"
            )

        elif status == "BASELINE SAVED":

            messagebox.showinfo(
                "Baseline Created",
                f"Initial firewall status: {current}\n\n"
                "Baseline saved successfully."
            )

        else:

            messagebox.showinfo(
                "Scan Complete",
                f"Firewall status: {current}\n"
                "Result: NORMAL"
            )

    except mysql.connector.Error as error:

        if connection is not None and connection.is_connected():
            connection.rollback()

        messagebox.showerror(
            "Database Error",
            f"Unable to save scan:\n{error}"
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            str(error)
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# REFRESH HISTORY

def load_history():
    """Show all saved scans, newest first."""
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT setting_name, expected_value, current_value,
                   drift_status, scanned_at
            FROM configurations
            ORDER BY id DESC
            """
        )
        rows = cursor.fetchall()

        for item in history_table.get_children():
            history_table.delete(item)

        drift_count = 0
        for row in rows:
            history_table.insert("", tk.END, values=row)
            if row[3] == "DRIFT DETECTED":
                drift_count += 1

        total_label.config(text=f"Total Scans: {len(rows)}")
        drift_label.config(text=f"Drift Detected: {drift_count}")

    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", str(error))

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def refresh_history():
    """Reload all saved scan records without deleting database history."""
    load_history()


# EXPORT CSV REPORT

def export_report():

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                setting_name,
                expected_value,
                current_value,
                drift_status,
                scanned_at
            FROM configurations
            ORDER BY id DESC
            """
        )

        rows = cursor.fetchall()

        if not rows:
            messagebox.showinfo(
                "No Records",
                "There is no scan history to export."
            )
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Drift Report",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="drift_report.csv"
        )

        if not file_path:
            return

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Setting Name",
                "Expected Value",
                "Current Value",
                "Drift Status",
                "Scanned At"
            ])

            writer.writerows(rows)

        messagebox.showinfo(
            "Export Successful",
            f"Report saved successfully!\n\n{file_path}"
        )

    except (mysql.connector.Error, OSError, csv.Error) as error:

        messagebox.showerror(
            "Export Error",
            str(error)
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def main():
    #GUI

    root = tk.Tk()

    root.title(
        "Automated System Configuration Drift Analyzer"
    )

    root.geometry("1100x600")
    root.minsize(850, 450)


    heading = tk.Label(
        root,
        text="SYSTEM CONFIGURATION DRIFT ANALYZER",
        font=("Arial", 17, "bold")
    )

    heading.pack(pady=15)


    summary_frame = tk.Frame(root)
    summary_frame.pack(pady=10)


    total_label = tk.Label(
        summary_frame,
        text="Total Scans: 0",
        font=("Arial", 12)
    )

    total_label.pack(side=tk.LEFT, padx=20)


    drift_label = tk.Label(
        summary_frame,
        text="Drift Detected: 0",
        font=("Arial", 12)
    )

    drift_label.pack(side=tk.LEFT, padx=20)


    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)


    tk.Button(
        button_frame,
        text="Scan System",
        command=scan_system,
        font=("Arial", 11),
        width=18
    ).pack(side=tk.LEFT, padx=10)


    tk.Button(
        button_frame,
        text="Refresh History",
        command=refresh_history,
        font=("Arial", 11),
        width=18
    ).pack(side=tk.LEFT, padx=10)


    tk.Button(
        button_frame,
        text="Export CSV Report",
        command=export_report,
        font=("Arial", 11),
        width=18
    ).pack(side=tk.LEFT, padx=10)


    result_text = tk.Label(
        root,
        text="Ready to scan",
        font=("Arial", 11)
    )

    result_text.pack(pady=10)


    columns = (
        "Setting",
        "Expected",
        "Current",
        "Status",
        "Scanned At"
    )


    history_table = ttk.Treeview(
        root,
        columns=columns,
        show="headings"
    )


    for column in columns:

        history_table.heading(
            column,
            text=column
        )

        history_table.column(
            column,
            width=205,
            anchor="center"
        )


    history_table.pack(
        fill=tk.BOTH,
        expand=True,
        padx=15,
        pady=15
    )

    if initialize_database():

        load_history()

        root.mainloop()

    else:

        root.destroy()


if __name__ == "__main__":
    main()
