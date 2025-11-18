# Quick Start Guide - Fan Speed Temperature Analysis

## Your Experiment Setup

You have a device with two fans where you can control speed (0.0-1.0).
You want to measure how temperature changes when you adjust fan speed.

## Step-by-Step Instructions

### 1. Initial Setup
- Set fan speed to **1.0** (maximum cooling)
- Wait until temperature stabilizes (stops changing)
- Note the stable temperature

### 2. Start the Experiment
- Change fan speed to **0.4** (reduced cooling)
- **Immediately** start the data collection script:

```bash
python3 temperature_fit.py --interactive --interval 10 --save-data fan_04_experiment.csv
```

### 3. Collect Measurements
- The script will prompt you every 10 seconds
- Enter the current temperature reading
- Continue until temperature appears to stabilize (at least 10-15 readings)
- Press **Ctrl+C** when done

Example session:
```
Temperature Data Collection
==================================================
Measurement interval: 10 seconds
Enter temperature when prompted (Ctrl+C to stop)
==================================================
[10:30:15] Elapsed: 0.0s - Enter temperature (°C): 45.0
  Recorded: 45.0°C at 0.0s
[10:30:25] Elapsed: 10.2s - Enter temperature (°C): 46.5
  Recorded: 46.5°C at 10.2s
[10:30:35] Elapsed: 20.1s - Enter temperature (°C): 47.8
  Recorded: 47.8°C at 20.1s
...
```

### 4. View Results
The script will automatically:
- Fit an exponential function to your data
- Calculate key parameters:
  - **Initial Temperature**: Where you started
  - **Final Temperature**: Where it's heading
  - **Time Constant (τ)**: How fast temperature changes
- Generate a plot showing your data and the fitted curve
- Save everything

### 5. Interpret Results

The output shows:
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

**What this means:**
- Your device heated from 45.2°C to 52.3°C (7.1°C increase)
- The time constant (τ) = 45.2 seconds means:
  - After 45.2 seconds, temperature reached 63.2% of total change
  - After ~135 seconds (3×τ), temperature reached ~95% of final value
- R² = 0.9987 means excellent fit (very close to 1.0)

### 6. Compare Different Fan Speeds

Repeat the experiment with different fan speeds (e.g., 0.2, 0.6, 0.8) to see how fan speed affects:
- Final steady-state temperature
- Time constant (how fast it responds)

## Using the Exponential Function

The fitted function is:
```
T(t) = T_final + (T_initial - T_final) × exp(-t/τ)
```

You can use this to:
- **Predict** temperature at any future time
- **Estimate** how long until temperature reaches a target
- **Compare** cooling efficiency at different fan speeds
- **Optimize** fan speed vs power consumption trade-offs

## Why Exponential and Not Polynomial?

You mentioned `np.polyfit` - while that works for many fits, **exponential functions are physically correct** for thermal systems:

- Polynomial fit: Can fit data but doesn't represent real physics
- Exponential fit: Matches Newton's Law of Cooling - the actual physics

Benefits of exponential fit:
- More accurate predictions outside measured range
- Provides meaningful parameters (time constant)
- Better for small datasets
- Physically interpretable results

## Example: Analyzing Saved Data

If you already collected data:
```bash
python3 temperature_fit.py --data-file fan_04_experiment.csv --output analysis_plot.png
```

## Troubleshooting

**Temperature not changing?**
- Make sure fan speed actually changed
- Wait longer for system to respond

**Poor fit (low R²)?**
- Collect more data points
- Ensure measurements are consistent
- Check for external disturbances

**Fitting errors?**
- Need at least 3 measurements (preferably 10+)
- Verify CSV format is correct
