# 5G Network Software Modem Simulation

## Overview
This project is an end-to-end simulation of a Software Modem for Digital Communication Systems. It simulates the core stages of processing digital data over a wireless channel, typical of modern 5G and LTE networks.

The simulation guides text data through a complete pipeline: converting human-readable data into binary bits, mapping those bits into communication symbols via advanced modulation schemes, simulating external environmental noise, and finally demodulating the data back into its original text form.

## Features
- **Data Conversion**: Translates standard text/UTF-8 data into binary bit streams and reassembles them at the receiver end.
- **Modulation Schemes**: Implements Gray-coded Quadrature Phase Shift Keying (QPSK) and 16-Quadrature Amplitude Modulation (16-QAM).
- **Channel Simulation**: Models real-world transmission conditions by introducing Additive White Gaussian Noise (AWGN) based on configurable Signal-to-Noise Ratios (SNR).
- **Performance Evaluation**: Tracks and compares Empirical Bit Error Rate (BER) against Theoretical BER across different noise levels.
- **Visualizations**: Automatically generates Constellation Diagrams to visualize symbol spread and BER Curves (log scale) to analyze the accuracy of the transmission models.

## Project Structure
*   `utils.py`: Contains utility functions (`string_to_bits`, `bits_to_string`) to handle the conversion of text payloads to transmittable 1D binary arrays.
*   `modem.py`: Contains the core digital logic. Defines the `Modem` class for modulating/demodulating symbols and scaling power, alongside the `add_awgn` method for simulating channel noise.
*   `simulation.py`: The main test harness. Integrates the modules, manages the SNR sweeps (-4 dB to +15 dB), computes error rates, and generates graphical plots.

## Dependencies

The project relies on a few fundamental scientific computing packages in Python. To run the simulation, you will need to install the following dependencies:

*   [NumPy](https://numpy.org/)
*   [Matplotlib](https://matplotlib.org/)
*   [SciPy](https://scipy.org/)

You can easily install these using `pip`:

```bash
pip install numpy matplotlib scipy
```

## How to Run

Simply execute the main simulation script using Python.

```bash
python simulation.py
```

## Expected Outputs

Upon running the `simulation.py` script, the application will process an internal test text payload and write output artifacts directly to your directory:

1.  **`ber_curves.png`**: A semi-logarithmic plot comparing the empirical error rates of the QPSK and 16-QAM transmission against theoretical formulas over varying SNR levels.
2.  **`constellation_diagrams.png`**: A scatter plot showing the original ideal transmitted symbol locations versus the noisy received symbols at an intermediate SNR (10 dB default).
3.  **`simulation_results.txt`**: A detailed report covering the exact bit errors recorded at varying noise levels alongside samples of the partially corrupted decoded text at the receiver end.
