# 🚀 Polkadot Grant Analyzer

A comprehensive analysis tool for Polkadot grant proposals across multiple grant programs. This tool fetches grant proposals from GitHub repositories, analyzes them for various metrics, and provides interactive visualizations through a Streamlit dashboard.

## Features

### 📊 Analytics & Metrics

- **Approval Time Analysis**: Track how long grants take to be approved
- **Milestone Tracking**: Extract and analyze milestone information from proposals
- **Author Performance**: Analyze success rates and patterns for grant authors
- **Curator Analysis**: Track curator involvement and effectiveness
- **Category Classification**: Categorize proposals (ADMIN-REVIEW, PENDING, REJECTED, etc.)
- **Rejection Analysis**: Extract reasons for rejected proposals
- **Bounty Amount Tracking**: Extract and analyze grant amounts

### 🎯 Grant Programs Supported

- **Web3 Foundation Grants Program** (`w3f/Grants-Program`)
- **Polkadot Fast Grants** (`Polkadot-Fast-Grants/apply`)
- **Use Inkubator Ecosystem Grants** (`use-inkubator/Ecosystem-Grants`)
- **Polkadot Open Source Grants** (`PolkadotOpenSourceGrants/apply`)

### 📈 Visualizations

- Interactive dashboard with multiple views
- Real-time data filtering and analysis
- Performance trends over time
- Repository-specific analysis
- Author performance tracking

## Installation

### Prerequisites

- Python 3.8 or higher
- Git

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd polkadot-grant-analyzer
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up GitHub API token** (optional but recommended)

   Create a `.env` file in the project root:

   ```bash
   echo "GITHUB_TOKEN=your_github_token_here" > .env
   ```

   To get a GitHub token:

   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate a new token with `repo` and `public_repo` permissions
   - Add the token to your `.env` file

## Usage

### 🖥️ Streamlit Dashboard

Run the interactive dashboard:

```bash
streamlit run streamlit_app.py
```

The dashboard will open in your browser with:

- **Overview**: General statistics and charts
- **Repository Analysis**: Program-specific performance
- **Author Analysis**: Individual author performance
- **Performance Trends**: Time-based analysis
- **Detailed Data**: Filterable data table

### 💻 Command Line Interface

The tool also provides a CLI for data operations:

#### Fetch Data

```bash
python main.py fetch
```

#### Generate Report

```bash
python main.py report --output report.json
```

#### Show Statistics

```bash
python main.py stats
```

#### Clear Database

```bash
python main.py clear
```

## Data Pipeline

### 1. Data Fetching (`github_client.py`)

- Fetches pull requests from configured repositories
- Handles GitHub API rate limiting
- Extracts comments, reviews, and metadata

### 2. Data Processing (`data_processor.py`)

- Extracts metrics from proposal content
- Calculates approval times
- Identifies curators and authors
- Categorizes proposals

### 3. Data Storage (`database.py`)

- SQLite database for persistent storage
- Optimized queries with indexes
- JSON serialization for complex data

### 4. Visualization (`streamlit_app.py`)

- Interactive Streamlit dashboard
- Real-time filtering and analysis
- Export capabilities

## Configuration

### Repository Configuration (`config.py`)

Add new grant programs by updating `GRANT_REPOSITORIES`:

```python
GRANT_REPOSITORIES = {
    "new_program": {
        "owner": "organization",
        "repo": "repository-name",
        "type": "pull_request",
        "description": "Program Description"
    }
}
```

### Categories

Customize proposal categories in `config.py`:

```python
CATEGORIES = {
    "ADMIN-REVIEW": "Under administrative review",
    "PENDING": "Pending approval",
    "REJECTED": "Rejected proposals",
    "APPROVED": "Approved proposals",
    "MERGED": "Successfully merged",
    "CLOSED": "Closed without merging"
}
```

## Metrics Extracted

### Proposal Information

- **Title & Description**: Full proposal content
- **Author**: GitHub username of proposer
- **Repository**: Source grant program
- **State**: Current status (open/closed)
- **Merged**: Whether proposal was accepted

### Timing Metrics

- **Created At**: When proposal was submitted
- **Updated At**: Last modification time
- **Closed At**: When proposal was closed
- **Merged At**: When proposal was accepted
- **Approval Time**: Days from creation to approval/rejection

### Analysis Metrics

- **Milestones**: Number of project milestones
- **Curators**: GitHub users who reviewed/commented
- **Category**: Classification (PENDING, REJECTED, etc.)
- **Rejection Reason**: Extracted from comments
- **Bounty Amount**: Extracted grant amount
- **Labels**: GitHub labels applied

### Performance Metrics

- **Approval Rate**: Percentage of accepted proposals
- **Average Approval Time**: Mean time to decision
- **Author Success Rates**: Individual performance
- **Repository Performance**: Program-specific metrics

## API Reference

### GitHubClient

```python
from github_client import GitHubClient

client = GitHubClient(token="your_token")
proposals = client.fetch_all_grant_proposals()
```

### GrantDataProcessor

```python
from data_processor import GrantDataProcessor

processor = GrantDataProcessor()
df = processor.process_all_proposals(proposals)
metrics = processor.calculate_performance_metrics(df)
```

### GrantDatabase

```python
from database import GrantDatabase

db = GrantDatabase()
db.save_proposals(df)
df = db.load_proposals()
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

- Create an issue on GitHub
- Check the documentation
- Review the code comments

## Roadmap

- [ ] Add more grant programs
- [ ] Enhanced NLP for proposal analysis
- [ ] Machine learning for approval prediction
- [ ] Real-time notifications
- [ ] API endpoints for external access
- [ ] Advanced filtering and search
- [ ] Export to various formats (PDF, Excel)
- [ ] Email reporting
- [ ] Slack/Discord integration

## Acknowledgments

- Web3 Foundation for the grant programs
- Polkadot ecosystem contributors
- GitHub API for data access
- Streamlit for the dashboard framework
