# MemoryCycle Setup Guide

This guide will help you set up and run the MemoryCycle application.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed
  - Check version: `python --version` or `python3 --version`
- **pip** package manager
  - Check version: `pip --version` or `pip3 --version`

## Installation Steps

### 1. Navigate to Project Directory

```bash
cd memory_cycle
```

### 2. (Optional) Create Virtual Environment

It's recommended to use a virtual environment to avoid package conflicts:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt when activated.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- streamlit (web application framework)
- pandas (data manipulation)
- numpy (numerical computing)
- scipy (scientific computing)
- statsmodels (statistical models)
- scikit-learn (machine learning)
- plotly (interactive charts)
- pyyaml (configuration)

### 4. Verify Installation

```bash
streamlit --version
```

You should see something like: `Streamlit, version 1.28.0` or higher.

## Running the Application

### Start the Application

```bash
streamlit run app.py
```

The application will:
1. Start a local web server
2. Automatically open your default browser
3. Display the MemoryCycle home page

If the browser doesn't open automatically, navigate to:
```
http://localhost:8501
```

### Stopping the Application

- Press `Ctrl+C` in the terminal where Streamlit is running
- Or close the terminal window

## First-Time Setup

### Step 1: Prepare Your Data

You have two options:

#### Option A: Use the Template (Quick Start)

1. Download the CSV template from the **Data Input** page
2. Fill in your historical data (minimum 10 quarters)
3. Upload via the **Data Input** page

#### Option B: Manual Entry

1. Navigate to **Data Input** page
2. Use the "Manual Entry" tab
3. Enter data one quarter at a time

### Step 2: Load Historical Data

**Required fields:**
- Date (quarter end)
- DRAM contract price index
- Inventory weeks at suppliers
- Utilization rate

**Optional but recommended:**
- HBM ASP, Capex, HBM revenue share
- Nvidia datacenter revenue, DRAM revenue

**Minimum data requirement:** 10 quarters (2.5 years)

### Step 3: Explore the Dashboard

Once data is loaded:
1. Go to **Dashboard** page
2. View current regime probabilities
3. Check market state visualization

### Step 4: Generate Investment Signals

1. Navigate to **Signals** page
2. Review current BUY/HOLD/SELL signal
3. Check signal confidence and rationale

## Configuration

### Customizing Settings

Edit `config/settings.yaml` to adjust:

```yaml
model:
  equilibrium:
    utilization: 0.85        # Adjust based on your analysis
    inventory_weeks: 12.0    # Adjust based on your analysis

signals:
  buy_threshold: 0.60        # Increase for more conservative signals
  sell_threshold: 0.60       # Increase for more conservative signals
```

Save changes and restart the application.

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Problem:** Python can't find required packages

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: "Port 8501 is already in use"

**Problem:** Another Streamlit app is running

**Solution:**
```bash
# Find and kill the process, or specify a different port
streamlit run app.py --server.port 8502
```

### Issue: "No data available"

**Problem:** Historical data not loaded

**Solution:**
1. Go to **Data Input** page
2. Upload CSV or enter data manually
3. Verify data saved by checking "Current Data" tab

### Issue: Application is slow

**Problem:** Large dataset or many simulations

**Solution:**
- Reduce Monte Carlo simulations (sidebar in Price Forecast)
- Use smaller datasets for testing
- Ensure only necessary data is loaded

### Issue: Charts not displaying

**Problem:** Browser compatibility or JavaScript disabled

**Solution:**
- Try a different browser (Chrome, Firefox, Safari)
- Ensure JavaScript is enabled
- Clear browser cache

## Data Management

### Backing Up Data

Your data is stored in:
```
memory_cycle/data/historical_data.csv
memory_cycle/data/regime_labels.csv
```

**Recommended:** Regularly back up these files

```bash
# Create backup
cp data/historical_data.csv data/historical_data_backup_$(date +%Y%m%d).csv
```

### Exporting Data

1. Go to **Data Input** page
2. Select "Current Data" tab
3. Click "Download Current Data as CSV"

### Importing Data from Backup

1. Go to **Data Input** page
2. Select "CSV Upload" tab
3. Upload your backup CSV file

## Performance Tips

### Faster Loading

- Keep historical dataset to necessary periods (e.g., last 10 years)
- Remove incomplete or unnecessary data points

### Faster Forecasting

- Reduce number of Monte Carlo simulations (100-500 for quick analysis)
- Use shorter forecast horizons (4 quarters vs 12)

### Faster Backtesting

- Limit test period to recent years
- Increase minimum training periods to reduce iterations

## Updating the Application

### Getting Updates

If you receive application updates:

1. Stop the running application (Ctrl+C)
2. Pull new code or replace files
3. Update dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   ```
4. Restart the application

### Preserving Your Data

Your data files (`data/historical_data.csv`) are preserved during updates unless explicitly deleted.

## Advanced Configuration

### Custom Port

```bash
streamlit run app.py --server.port 8080
```

### Headless Mode (Server)

```bash
streamlit run app.py --server.headless true
```

### Custom Theme

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor="#FF6347"
backgroundColor="#0E1117"
secondaryBackgroundColor="#262730"
textColor="#FAFAFA"
font="sans serif"
```

## Development Mode

### Enabling Debug Mode

Edit `.streamlit/config.toml`:

```toml
[runner]
fastReruns = true

[server]
runOnSave = true

[logger]
level = "debug"
```

### Running Tests

If tests are available:

```bash
pytest tests/
```

## Next Steps

Once set up:

1. **Learn the Model**: Read the README to understand regime-switching methodology
2. **Explore Historical Data**: Use Backtest page to validate on past cycles
3. **Set Up Data Updates**: Establish quarterly data collection routine
4. **Monitor Signals**: Check weekly for regime changes and signal updates
5. **Refine Parameters**: Adjust thresholds based on your investment style

## Support

### Documentation

- **README.md**: Full application documentation
- **DATASOURCES.md**: Data collection guide (in `data/` folder)
- **This file**: Setup and troubleshooting

### Common Questions

**Q: How often should I update data?**
A: Quarterly, after all major suppliers report earnings (typically 2 weeks into new quarter)

**Q: Can I use monthly data?**
A: Model is designed for quarterly data. Monthly data can be interpolated but may reduce accuracy.

**Q: What if I don't have all data fields?**
A: Minimum required: date, price index, inventory, utilization. Other fields enhance but aren't critical.

**Q: Can I modify the model?**
A: Yes! The code is open for modification. See `models/regime_model.py` for core logic.

## Getting Help

If you encounter issues:

1. Check this guide's Troubleshooting section
2. Review error messages in terminal
3. Verify data format matches template
4. Check configuration file syntax

## Success Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Application starts (`streamlit run app.py`)
- [ ] Browser opens to home page
- [ ] Historical data uploaded (minimum 10 quarters)
- [ ] Dashboard displays regime probabilities
- [ ] Signals page shows current recommendation
- [ ] Backtest runs successfully (if enough data)

If all items are checked, you're ready to use MemoryCycle!

---

**Happy Analyzing!** 💾📊
