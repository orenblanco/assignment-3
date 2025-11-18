#!/usr/bin/env python3
"""
Temperature Fit Function - Analyze temperature changes over time

This script helps analyze how device temperature changes when fan speed is adjusted.
It fits an exponential function to temperature rise data collected over time.

Usage:
    python temperature_fit.py --data-file measurements.csv
    python temperature_fit.py --interactive
"""

import argparse
import csv
import time
from datetime import datetime
from typing import List, Tuple, Optional
import sys

try:
    import numpy as np
    from scipy.optimize import curve_fit
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"Error: Required package not found - {e}", file=sys.stderr)
    print("Please install required packages: pip install numpy scipy matplotlib", file=sys.stderr)
    sys.exit(1)


def exponential_rise(t: np.ndarray, T_final: float, T_initial: float, tau: float) -> np.ndarray:
    """
    Exponential rise function: T(t) = T_final + (T_initial - T_final) * exp(-t/tau)
    
    Args:
        t: Time array
        T_final: Final/steady-state temperature
        T_initial: Initial temperature
        tau: Time constant (characterizes how fast temperature changes)
    
    Returns:
        Temperature array
    """
    return T_final + (T_initial - T_final) * np.exp(-t / tau)


def fit_temperature_data(times: List[float], temperatures: List[float]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fit exponential function to temperature vs time data.
    
    Args:
        times: List of time values (seconds from start)
        temperatures: List of temperature measurements
    
    Returns:
        Tuple of (optimized parameters, covariance matrix)
        Parameters are [T_final, T_initial, tau]
    """
    times_array = np.array(times)
    temps_array = np.array(temperatures)
    
    # Initial parameter guesses
    T_initial_guess = temps_array[0]
    T_final_guess = temps_array[-1]
    tau_guess = (times_array[-1] - times_array[0]) / 3  # Rough estimate
    
    initial_guess = [T_final_guess, T_initial_guess, tau_guess]
    
    try:
        # Fit the data
        popt, pcov = curve_fit(exponential_rise, times_array, temps_array, p0=initial_guess)
        return popt, pcov
    except Exception as e:
        print(f"Error fitting data: {e}", file=sys.stderr)
        raise


def collect_measurements(interval_seconds: int = 10, duration_minutes: Optional[int] = None) -> List[Tuple[float, float]]:
    """
    Collect temperature measurements interactively.
    
    Args:
        interval_seconds: Time between measurements
        duration_minutes: Total duration (None for manual stop)
    
    Returns:
        List of (time_elapsed, temperature) tuples
    """
    measurements = []
    start_time = time.time()
    
    print("Temperature Data Collection")
    print("=" * 50)
    print(f"Measurement interval: {interval_seconds} seconds")
    print("Enter temperature when prompted (Ctrl+C to stop)")
    print("=" * 50)
    
    measurement_num = 0
    try:
        while True:
            current_time = time.time()
            elapsed = current_time - start_time
            
            if duration_minutes and elapsed > duration_minutes * 60:
                break
            
            if measurement_num == 0 or elapsed >= measurement_num * interval_seconds:
                timestamp = datetime.now().strftime("%H:%M:%S")
                temp_str = input(f"[{timestamp}] Elapsed: {elapsed:.1f}s - Enter temperature (°C): ")
                
                try:
                    temperature = float(temp_str)
                    measurements.append((elapsed, temperature))
                    measurement_num += 1
                    print(f"  Recorded: {temperature}°C at {elapsed:.1f}s")
                except ValueError:
                    print("  Invalid temperature value, skipping...")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\nData collection stopped.")
    
    return measurements


def save_measurements(measurements: List[Tuple[float, float]], filename: str):
    """Save measurements to CSV file."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['time_seconds', 'temperature_celsius'])
        writer.writerows(measurements)
    print(f"Data saved to {filename}")


def load_measurements(filename: str) -> List[Tuple[float, float]]:
    """Load measurements from CSV file."""
    measurements = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            time_val = float(row['time_seconds'])
            temp_val = float(row['temperature_celsius'])
            measurements.append((time_val, temp_val))
    return measurements


def analyze_and_plot(measurements: List[Tuple[float, float]], output_file: Optional[str] = None):
    """
    Analyze temperature data and create plots.
    
    Args:
        measurements: List of (time, temperature) tuples
        output_file: Optional filename to save plot
    """
    if len(measurements) < 3:
        print("Error: Need at least 3 measurements for fitting", file=sys.stderr)
        return
    
    times, temps = zip(*measurements)
    
    # Fit the data
    print("\nFitting exponential function to data...")
    popt, pcov = fit_temperature_data(list(times), list(temps))
    
    T_final, T_initial, tau = popt
    perr = np.sqrt(np.diag(pcov))
    
    print("\nFit Results:")
    print("=" * 50)
    print(f"Initial Temperature (T₀):  {T_initial:.2f} ± {perr[1]:.2f} °C")
    print(f"Final Temperature (T∞):    {T_final:.2f} ± {perr[0]:.2f} °C")
    print(f"Time Constant (τ):         {tau:.2f} ± {perr[2]:.2f} seconds")
    print(f"Temperature Change:        {abs(T_final - T_initial):.2f} °C")
    print(f"63.2% rise time:           {tau:.2f} seconds")
    print("=" * 50)
    
    # Generate fit curve
    times_array = np.array(times)
    times_fit = np.linspace(times_array.min(), times_array.max(), 200)
    temps_fit = exponential_rise(times_fit, *popt)
    
    # Calculate R-squared
    temps_array = np.array(temps)
    temps_predicted = exponential_rise(times_array, *popt)
    residuals = temps_array - temps_predicted
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((temps_array - np.mean(temps_array))**2)
    r_squared = 1 - (ss_res / ss_tot)
    print(f"R² (goodness of fit):      {r_squared:.4f}")
    print()
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.scatter(times, temps, label='Measured Data', color='blue', s=50, alpha=0.6)
    plt.plot(times_fit, temps_fit, label='Exponential Fit', color='red', linewidth=2)
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.ylabel('Temperature (°C)', fontsize=12)
    plt.title('Temperature vs Time - Exponential Fit', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    
    # Add equation to plot
    equation_text = f'T(t) = {T_final:.2f} + {T_initial - T_final:.2f} × exp(-t/{tau:.2f})\nR² = {r_squared:.4f}'
    plt.text(0.05, 0.95, equation_text, transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=150)
        print(f"Plot saved to {output_file}")
    else:
        plt.savefig('temperature_fit_plot.png', dpi=150)
        print("Plot saved to temperature_fit_plot.png")
    
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description='Fit exponential function to temperature rise/fall data'
    )
    parser.add_argument(
        '--data-file',
        type=str,
        help='CSV file with temperature measurements (time_seconds, temperature_celsius)'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Collect data interactively'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Measurement interval in seconds (default: 10)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        help='Collection duration in minutes (default: manual stop with Ctrl+C)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output filename for plot (default: temperature_fit_plot.png)'
    )
    parser.add_argument(
        '--save-data',
        type=str,
        help='Save collected measurements to CSV file'
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        # Collect data interactively
        measurements = collect_measurements(args.interval, args.duration)
        
        if args.save_data:
            save_measurements(measurements, args.save_data)
        
        if measurements:
            analyze_and_plot(measurements, args.output)
    
    elif args.data_file:
        # Load and analyze existing data
        try:
            measurements = load_measurements(args.data_file)
            analyze_and_plot(measurements, args.output)
        except FileNotFoundError:
            print(f"Error: File '{args.data_file}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error loading data: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()
        print("\nExample usage:")
        print("  # Collect data interactively")
        print("  python temperature_fit.py --interactive --interval 10 --save-data measurements.csv")
        print()
        print("  # Analyze existing data file")
        print("  python temperature_fit.py --data-file measurements.csv --output temp_plot.png")


if __name__ == '__main__':
    main()
