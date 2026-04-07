import numpy as np
import scipy.special

class Modem:
    def __init__(self, scheme):
        """
        Initializes the modem.
        `scheme` can be 'QPSK' or '16QAM'
        """
        self.scheme = scheme
        
        # Gray Coded mappings
        if self.scheme == 'QPSK':
            # Map 2 bits to symbols. Scale to unit average power (1/sqrt(2))
            # 00 -> -1 - 1j, 01 -> -1 + 1j, 11 -> 1 + 1j, 10 -> 1 - 1j
            self.bit_to_sim = {
                (0,0): -1 - 1j,
                (0,1): -1 + 1j,
                (1,1):  1 + 1j,
                (1,0):  1 - 1j
            }
            self.power = 2.0  # Average power before scaling
            self.k = 2  # Bits per symbol
            
        elif self.scheme == '16QAM':
            # I and Q mapping for Gray Code: 00->-3, 01->-1, 11->1, 10->3
            self.pam_map = {(0,0): -3, (0,1): -1, (1,1): 1, (1,0): 3}
            
            self.bit_to_sim = {}
            for b0 in [0, 1]:
                for b1 in [0, 1]:
                    for b2 in [0, 1]:
                        for b3 in [0, 1]:
                            i_val = self.pam_map[(b0, b1)]
                            q_val = self.pam_map[(b2, b3)]
                            self.bit_to_sim[(b0, b1, b2, b3)] = complex(i_val, q_val)
                            
            self.power = 10.0 # Average power of 16-QAM is 10
            self.k = 4 # Bits per symbol
            
        else:
            raise ValueError("Modulation scheme not supported")
            
        # Create inverse mapping for demodulation
        self.sim_to_bit = {np.round(v / np.sqrt(self.power), 5): k for k, v in self.bit_to_sim.items()}
        # Constellation points correctly scaled
        self.constellation = np.array(list(self.bit_to_sim.values())) / np.sqrt(self.power)
        self.constellation_bits = list(self.bit_to_sim.keys())

    def modulate(self, bits):
        """Modulates a 1D array of bits into complex symbols."""
        # Pad bits with zeros to make divisible by k
        pad_len = (self.k - len(bits) % self.k) % self.k
        padded_bits = np.pad(bits, (0, pad_len), 'constant')
        
        bit_groups = padded_bits.reshape(-1, self.k)
        symbols = []
        for bg in bit_groups:
            tuple_key = tuple(bg)
            sym = self.bit_to_sim[tuple_key] / np.sqrt(self.power)
            symbols.append(sym)
            
        return np.array(symbols), pad_len

    def demodulate(self, symbols):
        """Demodulates complex symbols back into bits using minimum-distance rule."""
        # Broadcast subtraction to find closest constellation point
        # symbols shape: (N, 1), constellation shape: (M,)
        sym_reshaped = np.reshape(symbols, (-1, 1))
        const_reshaped = np.reshape(self.constellation, (1, -1))
        
        distances = np.abs(sym_reshaped - const_reshaped)
        closest_indices = np.argmin(distances, axis=1)
        
        demod_bits = []
        for idx in closest_indices:
            demod_bits.extend(self.constellation_bits[idx])
            
        return np.array(demod_bits, dtype=int)


def add_awgn(symbols, snr_db, k):
    """
    Adds AWGN to symbols at a specific Eb/No (in dB).
    k: bits per symbol
    """
    # Convert SNR from dB to linear scale for Eb/No
    eb_no_linear = 10.0 ** (snr_db / 10.0)
    
    # Calculate noise variance
    # SNR = Eb / No. 
    # Es = k * Eb. Average symbol power = 1.
    # So noise power No = 1 / (k * Eb/No)
    # Since complex noise: variance per dimension is No / 2
    N0 = 1.0 / (k * eb_no_linear)
    
    noise_real = np.random.normal(0, np.sqrt(N0 / 2), len(symbols))
    noise_imag = np.random.normal(0, np.sqrt(N0 / 2), len(symbols))
    noise = noise_real + 1j * noise_imag
    
    return symbols + noise
