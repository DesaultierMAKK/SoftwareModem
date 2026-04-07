import numpy as np

def string_to_bits(text_string):
    """Converts a standard text string to a 1D numpy array of bits (0s and 1s)."""
    # Convert string to bytes
    byte_array = bytearray(text_string, 'utf-8')
    # Convert each byte to 8 bits
    bit_list = []
    for b in byte_array:
        # get bits, pad to 8 with leading zeros
        bits = [int(x) for x in format(b, '08b')]
        bit_list.extend(bits)
    return np.array(bit_list, dtype=int)

def bits_to_string(bit_array):
    """Converts a 1D numpy array of bits back to a text string."""
    # Group every 8 bits back to a byte
    bytes_list = bytearray()
    for i in range(0, len(bit_array), 8):
        byte_cluster = bit_array[i:i+8]
        if len(byte_cluster) < 8:
            break # Avoid incomplete bytes
        # convert bits to integer
        byte_val = int("".join(str(b) for b in byte_cluster), 2)
        bytes_list.append(byte_val)
    # decode back to string
    return bytes_list.decode('utf-8', errors='replace')
