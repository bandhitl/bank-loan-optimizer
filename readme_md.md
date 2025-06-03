# 🏦 Bank Loan Optimization Calculator

A sophisticated loan optimization tool that helps find the best loan strategy across multiple banks, handling cross-month penalties and weekend adjustments intelligently.

## 🌟 Features

- **Multi-Bank Comparison**: Compare strategies across CITI, SCBT, CIMB, and Permata banks
- **Smart Cross-Month Handling**: Automatically switches to CITI Call (7.75%) to avoid high cross-month penalties (9.20%)
- **Weekend/Holiday Adjustments**: Properly handles non-business days by adjusting segment lengths
- **Interactive Dashboard**: Beautiful Streamlit interface with charts and visualizations
- **Real-time Calculations**: Instant strategy optimization with detailed breakdowns

## 🚀 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

## 📋 Quick Start

### Option 1: Run on Streamlit Cloud (Recommended)

1. Fork this repository
2. Go to [streamlit.io](https://streamlit.io/)
3. Connect your GitHub account
4. Deploy from your forked repository
5. Your app will be live at `https://your-app-name.streamlit.app`

### Option 2: Run Locally

```bash
# Clone the repository
git clone https://github.com/yourusername/bank-loan-optimizer.git
cd bank-loan-optimizer

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

## 📁 Project Structure

```
bank-loan-optimizer/
├── streamlit_app.py          # Main Streamlit application
├── loan_calculator.py        # Core calculation engine
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── .streamlit/
    └── config.toml           # Streamlit configuration (optional)
```

## 🔧 Configuration

### Default Parameters
- **Principal**: 38,000,000,000 IDR (38 billion)
- **Period**: 30 days
- **Start Date**: 2025-05-29
- **Month End**: 2025-05-31

### Bank Rates (Default)
- **CITI 3-Month**: 8.69%
- **CITI Call Loan**: 7.75%
- **SCBT 1-Week**: 6.20%
- **SCBT 2-Week**: 6.60%
- **CIMB 1-Month**: 7.00%
- **Permata 1-Month**: 7.00%
- **Cross-Month Penalty**: 9.20%

## 🎯 How It Works

### 1. Strategy Generation
The calculator generates multiple loan strategies:
- CITI 3-month baseline
- SCBT 1-week rolling
- SCBT 2-week rolling
- CIMB 1-month (optional)
- Permata 1-month (optional)

### 2. Smart Optimization
- **Cross-Month Detection**: Identifies segments that would cross month-end
- **Automatic Switching**: Uses CITI Call (7.75%) instead of high penalty rates (9.20%)
- **Weekend Handling**: Adjusts segment lengths to avoid ending on non-business days

### 3. Best Strategy Selection
Selects the strategy with the lowest total interest cost while maintaining validity.

## 📊 Dashboard Features

### 🏆 Optimal Strategy Overview
- Average interest rate
- Total interest cost
- Savings vs baseline
- Daily savings breakdown

### 📈 Interactive Charts
- **Timeline Visualization**: Gantt chart showing loan segments
- **Strategy Comparison**: Bar chart comparing all strategies
- **Rate Analysis**: Visual comparison of interest rates

### 📋 Detailed Tables
- **Loan Schedule**: Day-by-day breakdown of each segment
- **Strategy Comparison**: Side-by-side comparison with savings
- **Calculation Logs**: Detailed processing logs for transparency

## 🛠️ API Usage

You can also use the calculator programmatically:

```python
from loan_calculator import BankLoanCalculator
from datetime import datetime

# Initialize calculator
calculator = BankLoanCalculator()

# Set parameters
principal = 38_000_000_000
total_days = 30
start_date = datetime(2025, 5, 29)
month_end = datetime(2025, 5, 31)

bank_rates = {
    'citi_3m': 8.69,
    'citi_call': 7.75,
    'scbt_1w': 6.20,
    'scbt_2w': 6.60,
    'cimb': 7.00,
    'permata': 7.00,
    'general_cross_month': 9.20
}

# Calculate optimal strategy
all_strategies, best_strategy = calculator.calculate_optimal_strategy(
    principal=principal,
    total_days=total_days,
    start_date=start_date,
    month_end=month_end,
    bank_rates=bank_rates,
    include_banks={'CIMB': True, 'Permata': False}
)

# Print results
calculator.print_best_strategy_details(best_strategy)
```

## 🔧 Customization

### Adding New Banks
1. Update the `bank_rates` dictionary with new rates
2. Add the bank logic in `create_standard_segments()`
3. Update the Streamlit interface to include new bank options

### Modifying Strategies
- Edit the `calculate_optimal_strategy()` method
- Add new segment creation logic
- Update the comparison logic

### Custom Holiday Calendars
- Modify the `holidays_2025` set in `BankLoanCalculator`
- Update `is_holiday()` and `is_weekend_or_holiday()` methods

## 📈 Performance

- **Calculation Speed**: < 1 second for typical 30-day loans
- **Memory Usage**: Minimal - suitable for cloud deployment
- **Scalability**: Handles loan periods up to 90 days efficiently

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/bank-loan-optimizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/bank-loan-optimizer/discussions)
- **Email**: your.email@example.com

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Charts powered by [Plotly](https://plotly.com/python/)
- Data handling with [Pandas](https://pandas.pydata.org/)

---

**Made with ❤️ for optimal loan strategies**