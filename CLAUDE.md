# CLAUDE.md - Development & Contribution Guide

## Overview

This document provides instructions for Claude (or any AI assistant) and developers working on the ScenarioSync portfolio monitoring application. It covers architecture, development workflow, coding standards, and contribution guidelines.

## Project Context

**Project Name**: ScenarioSync
**Purpose**: Personal portfolio monitoring for Canadian expats moving to Europe
**Current Version**: 0.1 (MVP)
**Tech Stack**: Python 3.9+, Streamlit, Pandas, Yahoo Finance, CurrencyFreak API

## Architecture

### Directory Structure

```
scenario-sync/
├── .streamlit/
│   └── config.toml              # Streamlit configuration
├── data/                         # Local SQLite database (gitignored)
├── docs/                         # Documentation
│   ├── PROJECT_OVERVIEW.md
│   ├── INSTALLATION.md
│   ├── USER_GUIDE.md
│   ├── SCENARIO_DETECTION.md
│   └── API_REFERENCE.md
├── src/
│   ├── config.py                # Application configuration
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── portfolio.py        # Portfolio and Holding models
│   │   ├── scenario.py         # Scenario detection models
│   │   └── market_data.py      # Market data models
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── market_data_service.py
│   │   ├── scenario_detector.py
│   │   └── portfolio_service.py
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── formatters.py
│       └── validators.py
├── tests/                        # Unit tests
│   ├── __init__.py
│   ├── test_portfolio.py
│   ├── test_scenario.py
│   └── test_services.py
├── .env.example                  # Example environment variables
├── .gitignore
├── app.py                        # Main Streamlit application
├── CLAUDE.md                     # This file
├── LICENSE
├── README.md
└── requirements.txt
```

### Key Design Principles

1. **Separation of Concerns**
   - Models: Pure data structures
   - Services: Business logic
   - UI (app.py): Presentation layer only

2. **Dependency Direction**
   - UI depends on Services
   - Services depend on Models
   - Models have no dependencies

3. **Data Flow**
   ```
   External APIs → MarketDataService → Models → Services → UI
   ```

4. **State Management**
   - Streamlit session_state for UI state
   - No global variables
   - Services are stateless

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/scenario-sync.git
cd scenario-sync

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (including dev dependencies)
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys (optional)

# Run application
streamlit run app.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_portfolio.py -v

# Run with output
pytest -s tests/test_portfolio.py
```

### Code Quality

```bash
# Format code
black src/ app.py tests/

# Lint code
flake8 src/ app.py tests/

# Type checking (optional)
mypy src/
```

## Coding Standards

### Python Style

- Follow PEP 8
- Use `black` for formatting (line length: 88)
- Use type hints for all function signatures
- Docstrings for all public functions (Google style)

### Example Function

```python
def calculate_drift(
    self,
    target_allocations: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate allocation drift from target.

    Args:
        target_allocations: Dictionary with target percentages
                           e.g., {"CAD": 60.0, "EUR": 40.0}

    Returns:
        Dictionary with drift percentages

    Example:
        >>> service.calculate_drift({"CAD": 60.0, "EUR": 40.0})
        {"CAD": 2.5, "EUR": -2.5}
    """
    # Implementation
```

### Model Design

- Use `dataclasses` for models
- Immutable by default (use `frozen=True` when appropriate)
- Properties for computed values
- Type hints for all fields

### Service Design

- Stateless classes (no instance variables except configuration)
- Dependency injection via constructor
- Return values, don't modify inputs
- Handle errors gracefully (return None or raise specific exceptions)

### UI/Streamlit Design

- Keep app.py focused on presentation
- Extract complex logic to services
- Use `st.session_state` for state management
- Clear separation between data fetching and display

## Feature Development

### Adding a New Feature

1. **Plan** - Document in GitHub Issues
2. **Model** - Update/create data models if needed
3. **Service** - Implement business logic
4. **UI** - Add to Streamlit dashboard
5. **Test** - Write unit tests
6. **Document** - Update relevant docs

### Example: Adding Historical Tracking

**Step 1: Model** (src/models/history.py)
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PortfolioSnapshot:
    """Historical portfolio snapshot."""
    timestamp: datetime
    total_value_cad: float
    total_value_eur: float
    cad_allocation: float
    eur_allocation: float
    active_scenario: int
```

**Step 2: Service** (src/services/history_service.py)
```python
class HistoryService:
    """Service for managing portfolio history."""

    def save_snapshot(self, portfolio: Portfolio, scenario_id: int) -> None:
        """Save current portfolio state to history."""
        # Implementation

    def get_history(self, days: int = 30) -> List[PortfolioSnapshot]:
        """Retrieve historical snapshots."""
        # Implementation
```

**Step 3: UI** (app.py)
```python
def render_history_chart(history: List[PortfolioSnapshot]):
    """Render historical portfolio value chart."""
    # Plotly chart implementation
```

**Step 4: Tests** (tests/test_history.py)
```python
def test_save_snapshot():
    """Test saving portfolio snapshot."""
    # Test implementation
```

## Release Process

### Version Numbering

- Format: `MAJOR.MINOR` (e.g., 0.1, 0.2, 1.0)
- MVP releases: 0.x
- Production ready: 1.0+

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in relevant files
- [ ] Tagged in git
- [ ] Release notes written

### Current Roadmap

**Release 0.1** ✅ (Current)
- Basic portfolio tracking
- Scenario detection
- Simple dashboard

**Release 0.2** (Next)
- DCA planning
- Historical tracking
- Projections

**Release 0.3**
- Scenario-aware recommendations
- Alert system

**Release 0.4**
- Questrade API integration
- Auto-sync

## Common Tasks

### Adding a New Market Data Source

1. Create model in `src/models/market_data.py`
2. Add fetching logic to `MarketDataService`
3. Update `MarketSnapshot` to include new data
4. Update UI to display new data

### Adding a New Scenario

1. Add to `ScenarioType` enum in `src/models/scenario.py`
2. Add definition to `SCENARIOS` in `src/config.py`
3. Implement scoring logic in `ScenarioDetector`
4. Update documentation in `docs/SCENARIO_DETECTION.md`

### Modifying UI Layout

All UI code is in `app.py`. Key sections:
- `render_header()` - Top banner
- `render_sidebar()` - Left sidebar with inputs
- `render_market_overview()` - Market data display
- `render_scenario_detection()` - Scenario card
- `render_portfolio_summary()` - Portfolio metrics
- `render_holdings_table()` - Holdings list
- `render_rebalancing_recommendation()` - Recommendations

## API Integrations

### Current Integrations

**Yahoo Finance** (via `yfinance`)
- Purpose: ETF prices
- Authentication: None required
- Rate limits: Informal (~2000 requests/hour)
- Docs: https://github.com/ranaroussi/yfinance

**CurrencyFreak**
- Purpose: FX rates
- Authentication: API key
- Rate limits: 1000 requests/month (free tier)
- Docs: https://currencyfreaks.com/documentation.html

### Adding New Integrations

Example: TradingEconomics for real yield data

1. **Get API credentials**
   ```bash
   # Add to .env
   TRADING_ECONOMICS_API_KEY=your_key
   ```

2. **Add to config.py**
   ```python
   TRADING_ECONOMICS_API_KEY = os.getenv("TRADING_ECONOMICS_API_KEY", "")
   ```

3. **Update MarketDataService**
   ```python
   def get_yield_data_real(self, country: str, maturity: str) -> Optional[YieldData]:
       """Fetch real yield data from TradingEconomics."""
       # Implementation
   ```

4. **Update tests**
   ```python
   def test_get_yield_data_real():
       """Test TradingEconomics yield fetching."""
       # Mock API response and test
   ```

## Testing Strategy

### Unit Tests

Test individual components in isolation:
- Models: Data validation, computed properties
- Services: Business logic, edge cases
- Utils: Formatting, validation

### Integration Tests (Future)

Test component interactions:
- MarketDataService → Models
- Services → Database
- Full workflow tests

### Manual Testing

Before each release:
- [ ] Add holding works
- [ ] Remove holding works
- [ ] Market data updates
- [ ] Scenario detection runs
- [ ] Charts render correctly
- [ ] Recommendations make sense

## Debugging

### Common Issues

**Issue**: Streamlit app won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Check dependencies
pip list | grep streamlit

# Run with verbose output
streamlit run app.py --logger.level=debug
```

**Issue**: Market data not loading
```bash
# Test Yahoo Finance directly
python -c "import yfinance as yf; print(yf.Ticker('ZCS.TO').history(period='1d'))"

# Check API key
echo $CURRENCYFREAKS_API_KEY
```

**Issue**: Tests failing
```bash
# Run specific test with output
pytest tests/test_portfolio.py::test_portfolio_allocation -v -s

# Check test coverage
pytest --cov=src --cov-report=html
# Open htmlcov/index.html
```

### Logging

Add logging for debugging:
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Portfolio value: {portfolio.total_value_cad}")
```

## Security Considerations

### API Keys

- Never commit API keys
- Always use environment variables
- Add to `.gitignore`: `.env`, `*.key`
- Provide `.env.example` with dummy values

### Data Privacy

- All data stored locally by default
- No cloud sync unless explicitly enabled
- Clear data deletion instructions

### Dependencies

- Regularly update dependencies
- Review security advisories
- Use `pip-audit` to check for vulnerabilities

## Performance Optimization

### Current Bottlenecks

1. **Market data fetching** - Sequential API calls
2. **Streamlit reloading** - Full app reruns on interaction

### Optimization Strategies

**Caching** (already implemented in services)
```python
import streamlit as st

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_market_data():
    # Expensive operation
```

**Parallel API calls** (future)
```python
import asyncio

async def fetch_all_prices(tickers):
    tasks = [fetch_price(ticker) for ticker in tickers]
    return await asyncio.gather(*tasks)
```

## Documentation

### What to Document

**Always document**:
- Public APIs and functions
- Configuration options
- Setup procedures
- Architectural decisions

**Don't document**:
- Obvious code (self-explanatory)
- Implementation details that change frequently

### Documentation Style

- User-facing: Simple, example-driven
- Developer-facing: Technical, comprehensive
- Inline comments: Explain "why", not "what"

## Contributing

### Contribution Process

1. **Fork** the repository
2. **Create branch** - `git checkout -b feature/your-feature`
3. **Make changes** - Follow coding standards
4. **Test** - Ensure all tests pass
5. **Commit** - Clear, descriptive messages
6. **Push** - `git push origin feature/your-feature`
7. **Pull Request** - Describe changes, link issues

### Commit Message Format

```
type(scope): Short description

Longer description if needed

Fixes #123
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Examples**:
```
feat(scenario): Add scenario transition alerts
fix(portfolio): Correct allocation drift calculation
docs(readme): Update installation instructions
```

## Getting Help

### Resources

- **Documentation**: `/docs` folder
- **API Reference**: `docs/API_REFERENCE.md`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

### Questions to Ask

Before starting work:
- Does this fit the product vision?
- Is there a simpler approach?
- What are the edge cases?
- How will this be tested?

## Future Enhancements

### Planned Features

See [PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) for full roadmap.

**High Priority**:
- DCA planning and tracking
- Historical portfolio visualization
- Email/SMS alerts

**Medium Priority**:
- Questrade API integration
- Tax reporting features
- Mobile-responsive UI

**Low Priority**:
- Machine learning scenario detection
- Multi-user support
- Cloud sync option

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contact

For questions about development:
- Open an issue on GitHub
- Tag with "question" or "discussion"
- Provide context and examples

---

**Last Updated**: 2026-01-21
**Author**: ScenarioSync Team
**Version**: 0.1
