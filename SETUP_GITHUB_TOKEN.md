# 🔑 Setting Up GitHub Token for Real Data

## Why You Need a GitHub Token

The GitHub API has rate limits:

- **Without token**: 60 requests per hour (very limited)
- **With token**: 5000 requests per hour (sufficient for our needs)

## How to Get a GitHub Token

### Step 1: Create a GitHub Personal Access Token

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a name like "Polkadot Grant Analyzer"
4. Select these permissions:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `public_repo` (Access public repositories)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

### Step 2: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env
```

Add your token to the `.env` file:

```env
# GitHub API Configuration
GITHUB_TOKEN=your_actual_token_here

# Database Configuration (optional)
DATABASE_PATH=grants_database.db

# Logging Configuration (optional)
LOG_LEVEL=INFO
```

### Step 3: Test the Token

```bash
# Test the token
source venv/bin/activate
python main.py fetch
```

You should see output like:

```
INFO:github_client:Fetching proposals from w3f/Grants-Program
INFO:github_client:Fetched 1100 pull requests from w3f/Grants-Program
INFO:github_client:Fetching proposals from Polkadot-Fast-Grants/apply
INFO:github_client:Fetched 150 pull requests from Polkadot-Fast-Grants/apply
...
```

## Current Status

### ✅ **What We Have Now**

- **Realistic simulated data**: 1083 proposals with realistic distributions
- **All features working**: Stale detection, approved proposals, program analysis, AI evaluation
- **Proper statistics**:
  - 400 approved (36.9% approval rate)
  - 200 rejected
  - 400 pending
  - 83 stale proposals

### 🔄 **To Get Real GitHub Data**

1. **Set up GitHub token** (see steps above)
2. **Run fetch command**:
   ```bash
   source venv/bin/activate
   python main.py fetch
   ```
3. **Verify real data**:
   ```bash
   python main.py stats
   ```

## Data Quality Comparison

### Simulated Data (Current)

- ✅ Realistic proposal titles and descriptions
- ✅ Proper category distribution
- ✅ Realistic approval rates and times
- ✅ All features working perfectly
- ✅ Good for testing and demonstration

### Real GitHub Data (After Token Setup)

- ✅ Actual proposal data from GitHub
- ✅ Real author names and timestamps
- ✅ Actual curator assignments
- ✅ Real bounty amounts and milestones
- ✅ Live data that updates with new proposals

## Features Working with Both Data Types

All the implemented features work with both simulated and real data:

1. **Stale Detection** ⏰ - Identifies proposals over 60 days old
2. **Approved Proposals** ✅ - Correctly identifies approved proposals
3. **Program-Specific Analysis** 📊 - Separate metrics per grant program
4. **Program Selection Filter** 🔍 - Filter by specific programs
5. **AI Evaluation System** 🤖 - Comprehensive proposal analysis

## Next Steps

1. **For immediate use**: The current simulated data is perfect for testing all features
2. **For production use**: Set up GitHub token to get real data
3. **For development**: Continue using simulated data for feature development

The system is fully functional with realistic data and all features are working correctly!
