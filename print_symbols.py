#!/usr/bin/python3
import pickle
# Load array from the file
with open('symbols.pickle', 'rb') as file:
    loaded_array = pickle.load(file)

print(loaded_array)
