# Automated System Configuration Drift Analyzer

## 1. Project Overview

The **Automated System Configuration Drift Analyzer** is a Python-based desktop application designed to monitor Windows Firewall configurations and detect deviations from a predefined security baseline.

The application compares the current firewall status with the saved baseline, identifies configuration changes, stores scan history in a MySQL database, and generates CSV reports for further analysis.

## 2. Project Objectives

* Monitor Windows Firewall configuration status.
* Establish and maintain a baseline configuration.
* Detect unexpected changes in firewall status.
* Store configuration scan results in a MySQL database.
* Display scan history and drift statistics through a graphical interface.
* Export scan reports for documentation and analysis.

## 3. Technologies Used

| Technology             | Purpose                           |
| ---------------------- | --------------------------------- |
| Python                 | Core application development      |
| Tkinter                | Graphical user interface          |
| MySQL                  | Baseline and scan-history storage |
| MySQL Connector/Python | Database connectivity             |
| Subprocess             | Retrieve Windows Firewall status  |
| CSV                    | Export scan reports               |

## 4. System Requirements

* Windows operating system
* Python 3.x
* MySQL Server
* MySQL Connector/Python
* MySQL Workbench (optional, for database management)

## 5. Project Workflow

1. Connect to the MySQL database.
2. Initialize the required database tables.
3. Retrieve the current Windows Firewall status.
4. Check whether a baseline configuration exists.
5. If no baseline exists, save the current firewall status as the initial baseline.
6. If a baseline exists, compare the current status with the saved value.
7. Identify the result as `NORMAL` or `DRIFT DETECTED`.
8. Store the scan result in the MySQL database.
9. Display the result and scan history in the dashboard.
10. Export the scan history as a CSV report when required.

## 6. Input

The application uses the following inputs:

### A. System Configuration Input

* Current Windows Firewall status.
* Firewall status values: `ON` or `OFF`.

### B. Baseline Configuration

* Previously saved expected firewall status.
* The baseline is created automatically during the first successful scan.

### C. Database Configuration

* MySQL host
* MySQL username
* MySQL password
* Database name

### D. User Input

The user interacts with the application through the graphical interface using the following options:

* **Scan System:** Checks the current firewall status and detects configuration drift.
* **Refresh History:** Reloads the saved scan records into the dashboard.
* **Export CSV Report:** Exports the recorded scan history to a CSV file.

## 7. Processing

The application processes the input through the following steps:

### Step 1: Firewall Status Detection

The application retrieves the current Windows Firewall status using a Windows system command.

### Step 2: Baseline Creation

During the first successful scan, the detected firewall status is saved as the expected configuration.

### Step 3: Configuration Comparison

During subsequent scans, the current firewall status is compared with the saved baseline.

### Step 4: Drift Identification

| Condition                            | Result           |
| ------------------------------------ | ---------------- |
| No baseline exists                   | `BASELINE SAVED` |
| Current status matches baseline      | `NORMAL`         |
| Current status differs from baseline | `DRIFT DETECTED` |

### Step 5: Database Storage

The application records the expected value, current value, drift status, and scan timestamp in MySQL.

### Step 6: Dashboard Update

The graphical interface displays scan results, scan history, and drift statistics.

### Step 7: Report Generation

The user can export stored scan history to a CSV file for further analysis.

## 8. Output

The application generates the following outputs:

### A. Firewall Scan Result

Displays the expected firewall status, current firewall status, and scan result.

**Example 1: Normal Configuration**

```text
Expected: ON
Current: ON
Result: NORMAL
```

**Example 2: Configuration Drift Detected**

```text
Expected: ON
Current: OFF
Result: DRIFT DETECTED
```

**Example 3: Initial Baseline Creation**

```text
Initial firewall status: ON
Baseline saved successfully.
```

*Note: These are illustrative examples. Actual results depend on the firewall status of the system being scanned.*

### B. Dashboard Output

The dashboard displays:

* Total scan records currently shown
* Number of records marked `DRIFT DETECTED`
* Configuration setting name
* Expected firewall status
* Current firewall status
* Drift detection result
* Scan timestamp

### C. Database Output

The application stores scan records in the MySQL `configurations` table.

Each record contains:

* Setting name
* Expected value
* Current value
* Drift status
* Scan timestamp

The `config_baseline` table stores the expected configuration used for comparison.

### D. CSV Report Output

The application allows users to export scan history to a CSV file.

The report contains the following columns:

| Column         | Description                   |
| -------------- | ----------------------------- |
| Setting Name   | Configuration being monitored |
| Expected Value | Saved baseline value          |
| Current Value  | Detected system value         |
| Drift Status   | Result of the comparison      |
| Scanned At     | Date and time of the scan     |

**Example CSV Output**

```csv
Setting Name,Expected Value,Current Value,Drift Status,Scanned At
Windows Firewall,ON,ON,NORMAL,2026-10-21 10:30:00
Windows Firewall,ON,OFF,DRIFT DETECTED,2026-10-21 10:35:00
```

*The dates and values above are illustrative examples, not actual scan records.*

## 9. Database Structure

### Table 1: `config_baseline`

Stores the expected configuration baseline.

| Column         | Description                   |
| -------------- | ----------------------------- |
| id             | Unique record identifier      |
| setting_name   | Name of the monitored setting |
| expected_value | Expected configuration value  |

### Table 2: `configurations`

Stores historical scan results.

| Column         | Description                   |
| -------------- | ----------------------------- |
| id             | Unique scan record identifier |
| setting_name   | Name of the monitored setting |
| expected_value | Baseline value                |
| current_value  | Detected value                |
| drift_status   | Scan result                   |
| scanned_at     | Scan timestamp                |

## 10. Installation and Execution

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/system-configuration-drift-analyzer.git
```

Replace `YOUR_USERNAME` with your GitHub username.

### Step 2: Navigate to the Project Directory

```bash
cd system-configuration-drift-analyzer
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bat
.venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 5: Configure MySQL

Create the `drift_analyzer` database in MySQL and configure the database connection using the environment variables documented in the project.

Example for Windows Command Prompt:

```bat
set DB_HOST=localhost
set DB_USER=root
set DB_PASSWORD=your_mysql_password
set DB_NAME=drift_analyzer
```

Replace `your_mysql_password` with your actual MySQL password.

Do not upload your actual database credentials to GitHub.

### Step 6: Run the Application

```bash
python main.py
```

The application will initialize the required tables, connect to MySQL, and open the graphical interface if initialization succeeds.

## 11. Expected Results

After running the application, users can:

* Detect whether the Windows Firewall status differs from the saved baseline.
* Identify normal and drifted firewall configurations.
* Review stored scan history.
* View scan statistics on the dashboard.
* Export scan records to CSV.
* Maintain a historical record of detected configuration changes.

## 12. Limitations

* The current implementation monitors Windows Firewall status only.
* The application requires a Windows environment to execute the firewall detection command.
* MySQL Server must be available and correctly configured.
* The application detects differences in firewall status but does not automatically repair configuration changes.
* The first successful scan establishes the baseline; therefore, the initial firewall configuration should be verified before scanning.

## 13. Future Enhancements

* Monitor additional operating system security settings.
* Implement scheduled automated scans.
* Add email or desktop notifications for detected drift.
* Introduce graphical charts for historical scan analysis.
* Support baseline editing and reset functionality.
* Generate PDF security reports.
* Add user authentication and role-based access control.

## 14. Conclusion

The Automated System Configuration Drift Analyzer provides a simple approach to monitoring Windows Firewall configuration changes. By combining baseline comparison, drift detection, MySQL-based history tracking, and CSV reporting, the application helps users identify configuration differences and maintain visibility into firewall status over time.

## License

This project can be published under the MIT License by including an appropriate `LICENSE` file in the repository.
