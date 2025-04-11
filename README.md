# OSINT Tracker

OSINT Tracker is a web-based tool for discovering and analyzing digital footprints using Open Source Intelligence techniques. This application helps security professionals, privacy researchers, and individuals assess their online exposure and security risks.

![OSINT Tracker Dashboard](https://github.com/RETR0-K/OSINT_APP/blob/37ee4a517687aa76f729dd42692a08f56de1ca68/static/images/dashboard.png)

## Features

### User Management
- User registration and authentication system
- Personal dashboard with scan history and statistics
- Profile management with settings and preferences
- Export functionality for scan results

### Username Search
- Discover accounts associated with usernames across multiple platforms
- Searches through hundreds of websites using Sherlock and WhatsMyName tools
- Real-time progress tracking
- Categorized results by platform type (Social Media, Professional, Gaming, etc.)
- Digital footprint risk assessment

### Data Breach Check
- Search for email addresses in known data breaches
- Reveal exposed passwords, personal information, and breach details
- Risk score calculation based on breach severity and exposure
- Security recommendations for compromised accounts
- Multiple data breach sources (BreachDirectory, BreachSearch, OSINT Search)

### AI Analysis
- AI-powered insights from collected OSINT data
- Pattern recognition across digital presence
- Identity correlation and risk assessment
- Tailored security recommendations
- Four analysis types: Username, Email, Domain, and Combined

## Technology Stack

- **Backend**: Python with Flask framework
- **Frontend**: HTML, CSS with Tailwind CSS framework
- **Database**: SQLAlchemy with SQLite (can be configured for MySQL/PostgreSQL)
- **Authentication**: Flask-Login
- **Dependencies**: Sherlock, WhatsMyName, OpenAI API
- **APIs**: Various breach database APIs via RapidAPI

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Sherlock installed (for username searches)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/osint-tracker.git
   cd osint-tracker
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root directory with your API keys:
   ```
   SECRET_KEY=your_secret_key
   RAPIDAPI_KEY=your_rapidapi_key
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=sqlite:///osint_tracker.db
   ```

5. Initialize the database:
   ```
   python setup.py
   ```

6. Run the application:
   ```
   python app.py
   ```

7. Access the application in your browser at `http://localhost:5000`

8. Log in with the default admin account:
   - Username: admin
   - Password: admin123
   (Remember to change this password after first login!)

## Usage Guide

### User Management

1. Register a new account or log in with existing credentials
2. View your personal dashboard with scan statistics
3. Manage your profile and account settings
4. View your scan history and export results

### Username Search

1. Navigate to the Username Search section
2. Enter a username to search across platforms
3. View real-time progress as the search runs
4. Analyze the discovered accounts and digital footprint score
5. Export results or run AI analysis

### Data Breach Check

1. Navigate to the Data Breach section
2. Enter an email address to check against breach databases
3. Review all breaches containing the email
4. Check exposed passwords and other data
5. Follow security recommendations

### AI Analysis

1. Navigate to the AI Analysis section
2. Select analysis type (Username, Email, Domain, or Combined)
3. Enter your target identifier
4. Review AI-generated insights and risk assessment
5. Implement security recommendations

## Scheduled Tasks

The application includes scheduled tasks for maintenance:

1. **Clean Old Scans**: Remove scan data older than the specified period
   ```
   python tasks.py clean_old_scans 30
   ```

2. **Send Inactive User Reminders**: Notify users who haven't logged in for a while
   ```
   python tasks.py send_inactive_user_reminders 60
   ```

3. **Generate User Reports**: Create monthly security reports for users
   ```
   python tasks.py generate_user_reports
   ```

Set up a cron job to run these tasks regularly.

## Development

### Project Structure

```
osint_tracker/
├── app.py                           # Application entry point
├── config.py                        # Configuration settings
├── models.py                        # Database models
├── requirements.txt                 # Project dependencies
├── setup.py                         # Database initialization script
├── tasks.py                         # Scheduled tasks
├── .env                             # Environment variables (not in repo)
├── .gitignore                       # Git ignore file
│
├── static/                          # Static files
│   ├── css/                         # CSS stylesheets
│   ├── js/                          # JavaScript files
│   └── images/                      # Image assets
│
├── templates/                       # Global templates
│   ├── base.html                    # Base template with common layout
│   └── error.html                   # Error page template
│
└── blueprints/                      # Flask blueprints (modules)
    ├── home/                        # Home/Dashboard module
    ├── auth/                        # Authentication module
    ├── username_search/             # Username search module
    ├── data_breach/                 # Data breach module
    └── ai_analysis/                 # AI analysis module
```

### Adding New Features

1. Create a new blueprint in the `blueprints` directory
2. Register the blueprint in `app.py`
3. Implement required routes and utilities
4. Create templates in the blueprint's template folder

## Security Considerations

- This tool should be used ethically and responsibly
- Always obtain proper authorization before performing OSINT on others
- User passwords are securely hashed using Werkzeug's security functions
- API keys are stored securely in environment variables
- The application includes session management and user authentication
- Scans older than 30 days are automatically deleted by default

## License

[MIT License](LICENSE)

## Acknowledgements

- [Sherlock Project](https://github.com/sherlock-project/sherlock)
- [WhatsMyName Project](https://github.com/WebBreacher/WhatsMyName)
- [Tailwind CSS](https://tailwindcss.com/)
- OpenAI for AI analysis features
- RapidAPI for breach database access
- Flask and SQLAlchemy communities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request