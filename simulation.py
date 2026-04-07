import numpy as np
import matplotlib.pyplot as plt
import scipy.special
from utils import string_to_bits, bits_to_string
from modem import Modem, add_awgn

def theoretical_ber(snr_db, scheme):
    """Calculates theoretical BER for QPSK or 16-QAM"""
    eb_no_linear = 10.0 ** (snr_db / 10.0)
    
    if scheme == 'QPSK':
        # BER = Q(sqrt(2 * Eb/No)) -> but since Eb/No is per bit, for QPSK it's just Q-function
        return 0.5 * scipy.special.erfc(np.sqrt(eb_no_linear))
    elif scheme == '16QAM':
        # BER approx = 3/8 * erfc(sqrt(2/5 * Eb/No)) -> using average energy per bit
        return (3.0 / 8.0) * scipy.special.erfc(np.sqrt((2.0 * eb_no_linear) / 5.0))
    return np.zeros_like(snr_db)

def run_simulation(message):
    print("--- 5G Software Modem Simulation ---")
    print(f"Original Message: '{message}'")
    
    # 1. Data Generation
    tx_bits = string_to_bits(message)
    print(f"Number of transmitted bits: {len(tx_bits)}")

    snr_range_db = np.arange(-4, 16, 1) # Support -4 to +15 dB
    schemes = ['QPSK', '16QAM']
    plot_snr = 10 # SNR to plot constellation
    
    # Store empirical BER
    ber_results = {'QPSK': [], '16QAM': []}
    constellations = {'QPSK': (None, None), '16QAM': (None, None)} # (tx, rx)

    # 2. Iterate through schemes and SNRs
    for scheme in schemes:
        modem = Modem(scheme)
        
        for snr in snr_range_db:
            # Modulation
            tx_symbols, pad_len = modem.modulate(tx_bits)
            
            # Channel (AWGN)
            rx_symbols = add_awgn(tx_symbols, snr, modem.k)
            
            # Demodulation
            rx_bits_padded = modem.demodulate(rx_symbols)
            
            # Remove padding
            rx_bits = rx_bits_padded[:len(tx_bits)]
            
            # Calculate BER
            errors = np.sum(tx_bits != rx_bits)
            ber = errors / len(tx_bits)
            ber_results[scheme].append(ber)
            
            # Save constellation at specific SNR for plotting
            if snr == plot_snr:
                constellations[scheme] = (tx_symbols, rx_symbols)
                
                # Try to decode string back to verify end-to-end success
                try:
                    decoded_msg = bits_to_string(rx_bits)
                    print(f"[{scheme} @ {snr}dB SNR] Decoded Msg: '{decoded_msg[:50]}...'")
                except Exception as e:
                    print(f"[{scheme} @ {snr}dB SNR] Failed to decode string: {e}")

    # 3. Plotting Constellations
    plt.figure(figsize=(12, 6))
    for i, scheme in enumerate(schemes):
        tx_sym, rx_sym = constellations[scheme]
        plt.subplot(1, 2, i+1)
        plt.scatter(np.real(rx_sym), np.imag(rx_sym), marker='o', alpha=0.5, label='Rx (Noisy)', s=10)
        plt.scatter(np.real(tx_sym), np.imag(tx_sym), marker='x', color='red', label='Tx (Ideal)', s=100, linewidth=2)
        plt.title(f"{scheme} Constellation at {plot_snr} dB $E_b/N_0$")
        plt.xlabel("In-Phase")
        plt.ylabel("Quadrature")
        plt.grid(True)
        plt.legend()
    plt.tight_layout()
    plt.savefig('constellation_diagrams.png')
    
    # 4. Plotting BER Curves
    plt.figure(figsize=(10, 7))
    for scheme in schemes:
        theoretical = theoretical_ber(snr_range_db, scheme)
        empirical = ber_results[scheme]
        
        plt.semilogy(snr_range_db, theoretical, '--', label=f'{scheme} (Theoretical)')
        plt.semilogy(snr_range_db, empirical, '-o', label=f'{scheme} (Empirical)')
        
    plt.title("Bit Error Rate (BER) vs $E_b/N_0$")
    plt.xlabel("$E_b/N_0$ (dB)")
    plt.ylabel("Bit Error Rate (BER)")
    plt.ylim([1e-5, 1])
    plt.grid(True, which="both", ls="-")
    plt.legend()
    plt.savefig('ber_curves.png')
    
    print("\nSimulation complete. Outputs saved as 'constellation_diagrams.png' and 'ber_curves.png'.")
    
    # Write results to a text file
    with open('simulation_results.txt', 'w', encoding='utf-8') as f:
        f.write("--- 5G Software Modem Simulation Results ---\n\n")
        f.write(f"Original Message: '{message[:50]}...'\n")
        f.write(f"Number of transmitted bits: {len(tx_bits)}\n\n")
        
        for scheme in schemes:
            f.write(f"=== {scheme} Results ===\n")
            f.write(f"{'SNR (dB)':>10} | {'Theoretical BER':>18} | {'Empirical BER':>18}\n")
            f.write("-" * 52 + "\n")
            
            theoretical_vals = theoretical_ber(snr_range_db, scheme)
            empirical_vals = ber_results[scheme]
            
            for snr, t_ber, e_ber in zip(snr_range_db, theoretical_vals, empirical_vals):
                f.write(f"{snr:>10.1f} | {t_ber:>18.2e} | {e_ber:>18.2e}\n")
            f.write("\n")
            
        f.write("Decoded Strings at 10dB SNR:\n")
        try:
            for scheme in schemes:
                specific_modem = Modem(scheme)
                rx_bits = specific_modem.demodulate(constellations[scheme][1])[:len(tx_bits)]
                decoded_msg = bits_to_string(rx_bits)
                f.write(f"[{scheme}]: '{decoded_msg[:100]}...'\n")
        except Exception as e:
            f.write(f"Failed to decode strings: {e}\n")
            
    print("Results also saved to 'simulation_results.txt'.")

if __name__ == "__main__":
    # Create a long message so we have enough bits for a smooth BER curve
    test_message = "Hello 5G! This is a comprehensive test of our software modem. " * 50
    run_simulation(test_message)
