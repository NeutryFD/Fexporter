#
# Script for the calculation of the minimum entropy of a system following the NIST SP800-90B runtime scheme.
#
# Author: [Christian Bustelo] - [HPCNOW!]
# Date: [24/08/20023]
#
# Import packages
import numpy as np
import sys
import math
import subprocess
import random
import time
import multiprocessing

from scipy.stats import binom
from collections import Counter

#import the module for random generator
#from QusideQRNGLALUser.quside_QRNG_LAL_user import QusideQRNGLALUser

"""
 Seccion 1 : Data collection
"""
def data_collection(data_size):


    #""" To initialize the class is need the QRNG IP address. """
    #lib = QusideQRNGLALUser(ip='10.120.30.8')

    #""" This variable has to be set to 0. """
    #devIndex = 0

    # Get extracted random numbers in bytes
    #data = lib.get_random(data_size,devIndex)

    #"""
    #This function disconnect the QRNG.
    #"""
    #lib.disconnect()
    #time.sleep(20)
    #return data.tolist()

    
    # Moked section # #
    data = []
    if data_size == 1:
        for _ in range(1000000):
            random_number = random.randint(0, 2**32 - 1)
            data.append(random_number)
    elif data_size == 2:
        for _ in range(2000000):
            random_number = random.randint(0, 2**32 - 1)
            data.append(random_number)
    elif data_size == 3:
        for _ in range(3000000):
            random_number = random.randint(0, 2**32 - 1)
            data.append(random_number)
    return data
    """
        # Seccion mockeada #
    random_number = random.randint(0, 10)
    random_number_s = random.randint(0, 4)

    if data_size == 1:
        file_path = "/home/cbustelo/Desktop/Proyectos/Cesga_QRNG/finalTest/randomdata/random_data"+str(random_number)+".txt" #Salida de pruebas validas
    if data_size == 2:
        file_path = "/home/cbustelo/Desktop/Proyectos/Cesga_QRNG/finalTest/randomdata/random_data_big"+str(random_number_s)+".txt" #Salida de pruebas validas
    if data_size == 3:
        file_path = "/home/cbustelo/Desktop/Proyectos/Cesga_QRNG/finalTest/randomdata/random_data_bigger"+str(random_number_s)+".txt" #Salida de pruebas validas

    print("Utilizand datos de : random_data"+str(random_number)+".txt")
    with open(file_path, "r") as file:
        lines = file.readlines()
        data = [int(line.strip()) for line in lines] 

    return data
    """

# Entropy estimation
def estimate_entropy(data):
    estimate = most_common_value_estimate(data)
    return estimate

# Function for the calculation of minimum entropy
def most_common_value_estimate(dataset):
    # Step 1: Find the proportion of the most common value
    value_counts = {}
    for value in dataset:
        if value in value_counts:
            value_counts[value] += 1
        else:
            value_counts[value] = 1

    max_count = max(value_counts.values())
    p_hat = max_count / len(dataset)

    # Step 2: Calculate an upper bound on the probability of the most common value
    z_value = 2.576  # Z-score for 99.5% confidence interval
    p_upper_bound = min(1, p_hat + z_value * math.sqrt(p_hat * (1 - p_hat) / (len(dataset) - 1)))

    # Step 3: Calculate the estimated min-entropy
    min_entropy_estimate = -math.log2(p_upper_bound)

    return min_entropy_estimate


"""
Extra section : Support functions 
"""

# Transformation to 8-bit numbers by calling the least significant ones
def transform_to_8_bits(data):
    transformed_data = [(x >> 24) & 0xFF for x in data]
    return transformed_data

# Calculate binary bitstring entropy
def calculate_entropy_bitstring(sequence, n, max_bits=1000000):
    # Consider only first max_bits bits in total
    truncated_sequence = sequence[:max_bits]

    # Create "n" counters for each bit position
    bit_counters = [Counter() for _ in range(n)]

    # Fill in bit counters for each position
    for num in truncated_sequence:
        for i in range(n):
            bit = (num >> i) & 1
            bit_counters[i][bit] += 1

    # Calculate entropy per bit at each position
    entropy_per_bit = []
    for counter in bit_counters:
        total_bits = sum(counter.values())
        probabilities = [count / total_bits for count in counter.values()]
        entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
        entropy_per_bit.append(entropy)

    # Calculate the average entropy per bit for all positions
    avg_entropy_per_bit = sum(entropy_per_bit) / n

    # We return the entropy value per bit multiplied by the number of bits.
    return avg_entropy_per_bit * n

def fisher_yates_shuffle(arr):
    n = len(arr)
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]


"""
Main section
"""
if __name__ == "__main__":

    h_fabricante = "unknown"
#while True:
    # Checking arguments
    #verbose = "-v" in sys.argv

    # Step 1: Data collection and 8-bit formatting
    dataNor = data_collection(1) #use (1024*3907*1) for QRNG
    dataBig = data_collection(2) #use (1024*3907*2) for QRNG
    dataBigger = data_collection(3) #use (1024*3907*3) for QRNG

    h_i_results = []
    data_variables = [dataNor, dataBig, dataBigger]

    for data in data_variables:

        data_8b = transform_to_8_bits(data)
        h_estimada = estimate_entropy(data_8b)
        num_bits_per_sample = 8
        h_binary_addicional = calculate_entropy_bitstring(data_8b,num_bits_per_sample)
        h_i = min(h_estimada, h_binary_addicional)
        h_i_results.append(h_i)

    #if verbose:
    #with open("./statFile","w") as f:
    data = str(h_i_results[0]) +","+ str(h_i_results[1]) + "," +str(h_i_results[2])
    #    f.write(data)


    print(data,end="")
    # else:
    #    # Make the calculations and get the data you want to send to Elasticsearch.
    #    data = str(h_i_results[0]) +","+ str(h_i_results[1]) + "," +str(h_i_results[2])

    #    # Execute the shell script to send data to Elasticsearch
    #    try:
    #       subprocess.run(["bash", "/home/cbustelo/Desktop/Proyectos/Cesga_QRNG/finalTest/send_elastic_data.sh", data], check=True)
    #       print("Datos enviados a Elasticsearch exitosamente.")
    #    except subprocess.CalledProcessError as e:
    #    	  print(f"Error al enviar los datos a Elasticsearch: {e}")

