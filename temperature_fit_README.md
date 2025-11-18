# Temperature Fit Function

A Python tool for analyzing temperature changes over time when fan speed is adjusted on a device.

## Overview

This tool helps you:
1. Collect temperature measurements at regular intervals (e.g., every 10 seconds)
2. Fit an exponential function to the temperature rise/fall data
3. Visualize the results and get key parameters (time constant, final temperature, etc.)

## Installation

Install required Python packages:
```bash
pip install numpy scipy matplotlib
```

## Usage

### Scenario: Fan Speed Change Experiment

You have a device with fans (speed 0.0-1.0) and want to analyze temperature changes:

1. **Set fan speed to 1.0** and let temperature stabilize
2. **Change fan speed to 0.4** and start collecting data
3. **Measure temperature every 10 seconds**

### Interactive Data Collection

Collect temperature data interactively:

```bash
python temperature_fit.py --interactive --interval 10 --save-data measurements.csv
```

The script will prompt you to enter temperature readings. Press Ctrl+C when done.

### Analyze Existing Data

If you already have a CSV file with measurements:

```bash
python temperature_fit.py --data-file measurements.csv --output temp_plot.png
```

### CSV File Format

The CSV file should have two columns:
```csv
time_seconds,temperature_celsius
0.0,45.2
10.0,46.8
20.0,48.1
30.0,49.2
...
```

## How It Works

The tool fits your data to an exponential rise/fall function:

```
T(t) = T_final + (T_initial - T_final) × exp(-t/τ)
```

Where:
- **T_initial**: Starting temperature (°C)
- **T_final**: Final/steady-state temperature (°C)
- **τ (tau)**: Time constant - time to reach 63.2% of total change (seconds)

### Why Exponential?

Temperature changes in thermal systems typically follow exponential curves due to Newton's law of cooling. This is more physically accurate than polynomial fitting for this type of data.

## Output

The tool provides:
1. **Fitted parameters** with uncertainties
2. **Time constant (τ)** - how fast the system responds
3. **R² value** - goodness of fit (closer to 1.0 is better)
4. **Plot** showing measured data and fitted curve

## Example Output

```
Fit Results:
==================================================
Initial Temperature (T₀):  45.20 ± 0.15 °C
Final Temperature (T∞):    52.30 ± 0.12 °C
Time Constant (τ):         45.20 ± 2.30 seconds
Temperature Change:        7.10 °C
63.2% rise time:           45.20 seconds
==================================================
R² (goodness of fit):      0.9987
```

## Tips

- Collect at least 10-15 data points for reliable fitting
- Continue measurements until temperature appears to stabilize
- The time constant (τ) tells you how responsive your cooling system is
- A smaller τ means faster temperature changes (better cooling/heating)
- The R² value should be > 0.95 for a good fit

## Advanced Options

```bash
# Collect for specific duration
python temperature_fit.py --interactive --interval 10 --duration 5 --save-data data.csv

# Custom output plot name
python temperature_fit.py --data-file data.csv --output my_analysis.png
```

## Troubleshooting

If fitting fails:
- Ensure you have enough data points (at least 3, preferably 10+)
- Check that temperature is changing (not constant)
- Verify CSV file format matches the expected structure
