import pickle as pkl
import os

output_dir = "your_output_dir/"
answer_dir = "s2/"

import re

def extract_float_info(text):
    # Define the regex pattern to match labels followed by float numbers
    pattern = r'(Car|Person):\s*([0-9]*\.?[0-9]+)'
    
    # Find all matches of the pattern in the text, re.IGNORECASE can be used if keys might have case variance
    matches = re.findall(pattern, text)
    
    # Convert the found matches to the desired format, parsing the number as float
    result = {match[0]: float(match[1]) for match in matches}
    
    return result


corr = 0
total = 0
for test_id in range(100):
    try:
        file_path = output_dir + "%d.txt"%(test_id)
        with open(file_path, "r") as f:
            contents = f.read()
            info = extract_float_info(contents)
        with open(answer_dir + "car-answer.txt", "r") as f:
            gt_answer_car = f.read().split('\n')
        with open(answer_dir + "person-answer.txt", "r") as f:
            gt_answer_person = f.read().split('\n')
        if abs(float(gt_answer_car[test_id]) - float(info['Car'])) <= 1.0:
            corr += 1
        if abs(float(gt_answer_person[test_id]) - info['Person'][0]) <= 1.0:
            corr += 1
        total += 2
    except:
        total += 2

print(total)
print(corr)
