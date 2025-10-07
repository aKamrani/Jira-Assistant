# 🚀 Jira Sub-task Creator and Work Logger

> **Automate your Jira workflow with style!** 🎯

This Python script automates the creation of Jira sub-tasks and work logging for different types of projects. It intelligently detects the parent issue based on your CSV filename and uses the official Jira REST API for reliable operation.

## ✨ Features

- 🎯 **Smart Parent Detection**: Automatically chooses the right parent issue based on CSV filename
- 👤 **Auto-Assignment**: Assigns all tasks to Amirhossein Kamrani
- 🏷️ **Auto-Labeling**: Sets Components and Labels to "DevOps"
- ⏱️ **Time Tracking**: Logs work with the same time as original estimate
- ✅ **Auto-Complete**: Sets the status to "Done" automatically
- 🔐 **Secure**: Uses official Jira REST API with multiple authentication methods
- 🛡️ **Error Handling**: Comprehensive error handling and logging
- 🎨 **User-Friendly**: Clear progress messages and status updates

## 🎯 Parent Issue Detection

The script automatically detects which parent issue to use based on your CSV filename:

| 📁 Filename Contains | 🎯 Parent Issue Key | 📝 Description |
|---------------------|-------------------|----------------|
| `maintenance` | `MAINTENANCE_PARENT_ISSUE_KEY` | For maintenance and support tasks |
| `develop` | `DEVELOP_PARENT_ISSUE_KEY` | For development tasks |
| *anything else* | `MAINTENANCE_PARENT_ISSUE_KEY` | Defaults to maintenance |

## 🛠️ Setup

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Configure Environment
```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your actual values
nano .env
```

### 3️⃣ Environment Variables
Your `.env` file should contain:
```env
# 🔑 Your Jira credentials
JIRA_TOKEN=your_jira_token_here
JIRA_BASE_URL=https://your-jira-instance.com
ASSIGNEE_USERNAME=your.username

# 🎯 Parent issue keys
MAINTENANCE_PARENT_ISSUE_KEY=PROJECT-1234
DEVELOP_PARENT_ISSUE_KEY=PROJECT-5678
```

## 🚀 Usage

### 📋 Basic Usage
```bash
python3 jira-subtask-creator.py <input_file.csv>
```

### 📝 Examples
```bash
# For maintenance tasks
python3 jira-subtask-creator.py maintenance-subtasks.csv

# For development tasks  
python3 jira-subtask-creator.py develop-subtasks.csv

# Any filename with 'maintenance' in it
python3 jira-subtask-creator.py my-maintenance-tasks.csv

# Any filename with 'develop' in it
python3 jira-subtask-creator.py new-develop-features.csv
```

## 📊 Input File Format

Your CSV file should have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `Summary` | Task description | "Install K8S on local nodes for test" |
| `Original Estimate` | Time estimate | "6h", "4h 30m", "2d", "1w" |

### 📄 Example CSV Content
```csv
Summary,Original Estimate
Install Minio cluster with 3 nodes by using Operator,3h
Configure monitoring for production servers,4h
Update SSL certificates,2h
Deploy new version to staging environment,3h
Setup backup automation,5h
```

## 🔄 What the Script Does

For each row in your CSV, the script:

1. 🎯 **Detects Parent**: Determines the correct parent issue based on filename
2. 🆕 **Creates Sub-task**: Creates a new sub-task under the parent issue
3. ⚙️ **Sets Properties**: 
   - 👤 Assignee: Amirhossein Kamrani
   - 🏷️ Components: DevOps
   - 🏷️ Labels: DevOps
   - ⏱️ Original Estimate: From CSV
4. 📝 **Logs Work**: Creates a work log with the same time as original estimate
5. ✅ **Sets Status**: Changes the sub-task status to "Done"

## 📁 Project Files

| File | Description | 🔒 Security |
|------|-------------|-------------|
| `jira-subtask-creator.py` | 🐍 Main Python script | ✅ Safe to share |
| `maintenance-subtasks.csv` | 📋 Example maintenance tasks | ✅ Safe to share |
| `develop-subtasks.csv` | 📋 Example development tasks | ✅ Safe to share |
| `requirements.txt` | 📦 Python dependencies | ✅ Safe to share |
| `.env` | 🔐 Your actual credentials | ❌ **KEEP PRIVATE!** |
| `.env.example` | 📝 Template for credentials | ✅ Safe to share |
| `.gitignore` | 🚫 Git ignore rules | ✅ Safe to share |
| `README.md` | 📖 This documentation | ✅ Safe to share |

## ✅ Test Results

🎉 **Successfully tested with both CSV types!**

### 🔧 Maintenance Test
- ✅ Created sub-task: BM-****
- 📝 Summary: "Install Minio cluster with 3 nodes by using Operator"
- ⏱️ Original Estimate: 3h
- ✅ Status: Set to "Done"
- 📝 Work logged: 3h
- 👤 Assignee: Amirhossein Kamrani
- 🏷️ Components: DevOps
- 🏷️ Labels: DevOps

### 💻 Development Test
- ✅ Created sub-task: BM-****
- 📝 Summary: "Generate and analyze SLA compliance reports"
- ⏱️ Original Estimate: 2h
- ✅ Status: Set to "Done"
- 📝 Work logged: 2h
- 👤 Assignee: Amirhossein Kamrani
- 🏷️ Components: DevOps
- 🏷️ Labels: DevOps

## 🔐 Security Features

- 🛡️ **Environment Variables**: Sensitive data stored in `.env` (not in code)
- 🚫 **Git Protection**: `.gitignore` prevents accidental credential commits
- 🔑 **Multiple Auth Methods**: Supports Bearer tokens and Basic Auth
- 🔒 **Token Security**: Your Jira token is never logged or exposed

## ⚠️ Important Notes

- 🐌 **Rate Limiting**: Script includes delays between operations to avoid API limits
- 🎯 **Parent Issues**: All sub-tasks are created under the detected parent issue
- 🔑 **Permissions**: Make sure your Jira token has necessary permissions
- 📝 **Time Format**: Supports various time formats (h, m, d, w)
- 🌐 **Timezone**: Work logs use Tehran timezone (+0330)

## 🆘 Troubleshooting

### ❌ Authentication Issues
```bash
# Check your .env file
cat .env

# Verify your token is correct
# Try regenerating your API token in Jira
```

### ❌ Permission Issues
- Ensure your Jira user can create issues
- Check if you can create sub-tasks in the target project
- Verify you can log work and change issue status

### ❌ File Not Found
```bash
# Make sure your CSV file exists
ls -la *.csv

# Check the filename contains 'maintenance' or 'develop'
```

## 🤝 Contributing

1. 🍴 Fork the repository
2. 🌿 Create a feature branch
3. 💾 Commit your changes
4. 📤 Push to the branch
5. 🔄 Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- 🎯 Built for Jira automation
- 🐍 Powered by Python
- 🔗 Uses official Jira REST API
- 🎨 Made with ❤️ and lots of emojis!

---

**Happy automating!** 🚀✨