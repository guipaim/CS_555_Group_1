# GEDCOM Parser - CS555 Project

A Python application that parses GEDCOM genealogy files and displays family and individual data in formatted tables. This project implements Sprint 1 requirements for CS555 Agile Development, including version control setup, GEDCOM parsing, and structured data display.

## 🚀 Quick Start

### Prerequisites
- Python 3.6+
- pip (Python package installer)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd CS_555_Group_1
   ```

2. **Install dependencies**
   ```bash
   pip install prettytable
   ```

3. **Run the application**
   ```bash
   python CS_555_WN_Project2_Code.py
   ```

### CLI Examples

```bash
# Run with default GEDCOM file
python CS_555_WN_Project2_Code.py

# Run with custom GEDCOM file (modify the filename in the script)
# Edit line 260 in CS_555_WN_Project2_Code.py:
# individuals, families = readGedcomFile("your-file.ged")
```

## 📁 Project Structure

```
├── CS_555_WN_Project2_Code.py    # Main application
├── Gedcom-file.ged               # Sample GEDCOM file
└── README.md                     # This file
```

## 🤝 Contributing

### Git Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and test**
   ```bash
   python CS_555_WN_Project2_Code.py
   ```

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "Brief description of your changes"
   ```

4. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   # Then create PR on GitHub
   ```

### Development Guidelines

- **Code Style**: Follow PEP 8 Python conventions
- **Testing**: Test your changes with the provided GEDCOM file
- **Documentation**: Add comments for complex logic
- **Branch Naming**: Use `feature/`, `bugfix/`, or `hotfix/` prefixes


## 🏗️ Code Structure

- `parse_line()` - Validates and parses GEDCOM line format (Sprint 1 requirement)
- `readGedcomFile()` - Main parser that extracts individuals and families into lists (Sprint 1 requirement)
- `organizeFamilyData()` - Formats family data with spouse names
- `organizeIndividualData()` - Calculates ages and formats individual data
- `createTable()` - Generates PrettyTable output matching Sprint 1 specifications

## 🏃‍♂️ Agile Methodology & Sprint Tracking

This project follows CS555 Agile Development practices using the **Project Sprint Report** system:

### Sprint Structure
- **4 Sprints Total** (Sprint 1-4)
- **2 User Stories per team member per sprint**
- **Sprint Planning & Review Meetings** for each iteration
- **Burndown Charts** to track velocity and progress

### Project Sprint Report Sheets
- **Team**: Team members & GitHub repository info
- **Backlog**: Complete user story inventory  
- **Burndown**: Visual progress tracking
- **Sprint1-4**: Individual sprint planning & execution
- **Stories**: Master list of available user stories

## 📝 Supported GEDCOM Tags

The parser supports these standard GEDCOM tags:
- `INDI`, `NAME`, `SEX`, `BIRT`, `DEAT`, `FAMC`, `FAMS`
- `FAM`, `MARR`, `HUSB`, `WIFE`, `CHIL`, `DIV`, `DATE`
- `HEAD`, `TRLR`, `NOTE`

## 🐛 Troubleshooting

**Import Error**: Make sure PrettyTable is installed
```bash
pip install prettytable
```

**File Not Found**: Ensure `Gedcom-file.ged` is in the same directory as the Python script

**Date Format Error**: GEDCOM dates must be in format "DD MMM YYYY" (e.g., "15 JAN 1990")
