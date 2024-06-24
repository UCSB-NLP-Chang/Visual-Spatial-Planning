import pathlib
import textwrap

import google.generativeai as genai

import PIL.Image
import time
import os

import random
import numpy as np
def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
seed_everything(1)

levels = [3,4,5,6,7,8]
in_context_example_num = 0 # 0, 1, 2, 4, 8


GOOGLE_API_KEY='YOUR-API-KEY'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')
if in_context_example_num > 0:
    output_path = "output/output_img_%d/"%(in_context_example_num)
    input_backup_path = "input/input_backup_img_%d/"%(in_context_example_num)
else:
    output_path = "output/output_img/"
    input_backup_path = "input/input_backup_img/"

os.makedirs(output_path, exist_ok=True)
os.makedirs(input_backup_path, exist_ok=True)

loop_time = 0

EXAMPLE_DICT = {
    3: [],
    4: [],
    5: [],
    6: [],
    7: [],
    8: []
}

# Prepare examples
for level in levels:
    for example_id in range(8):
        example_path = "../example-spatial-relation/level%d/"%(level)
        img_input = PIL.Image.open(example_path + "%d.png"%(example_id))
        with open("../example-spatial-relation/level%d__sol/%d.txt"%(level, example_id), "r") as f:
            text_input = f.read()
        this_example = (img_input, text_input)
        EXAMPLE_DICT[level].append(this_example)

# import ipdb; ipdb.set_trace()
for level in levels:
    os.makedirs(output_path + "level%d"%(level), exist_ok=True)
    os.makedirs(input_backup_path + "level%d"%(level), exist_ok=True)
    start_idx = 0
    end_idx = 100
    runned_term = 0
    map_path = "../maps/level%d/"%(level)
    while True:
        try:
            curr_id = start_idx + runned_term
            if curr_id >= end_idx:
                break
            img_input = PIL.Image.open(map_path + "%d.png"%(curr_id))
            prompt_input_1 = '''
In this task, you will analyze a maze to determine the relative positions of the player and the goal.
The following figure illustrates the appearances of the player, holes, lands, and the goal within the maze. You will need to focus on the player and the goal.
'''
            prompt_input_2 = '''
To describe their relative positions, use the directional indicators from {"Above", "Below", "Left", "Right"}. We provide an example to illustrate how to interpret and describe these positions:
'''
            prompt_input_3 = '''
In this example:
- We focus on the position of the player and the goal.
- Rows: The player is at row 1, and the goal is at row 4. Here, the row number is from top to bottom. Comparing player (row=1) with goal (row=4), player is counted first. Therefore, the player is positioned above the target.
- Columns: The player is at column 1, and the goal is at column 4. Here, the column number is from left to right. Comparing player (column=1) with goal (column=4). Therefore, the player is to the left of the target.
- Remember that we should answer the player's position with respect to the goal, not the opposite. Therefore, we answer "Above,Left".

Your output should be two parts:
1. Analyze the rows and columns of the player and the goal like shown above. 
2. Following your analysis, output answer as "<Output> <Position>". For example, <Output> "Above,Left" means the player is above and to the left of the goal, and <Output> "Below" means the player is below the goal. 
Note that you should not output "Left" or "Right" if the plyaer and the goal are at the same column, and similarly, you should not output "Above" or "Below" if the player and the goal are at the same row.

'''
            prompt_examples = []
            image_examples = []
            if in_context_example_num > 0:
                prompt_examples.append("## Example:\n")
                example_indices = random.sample(range(8), in_context_example_num)
                for example_index in example_indices:
                    this_example = EXAMPLE_DICT[level][example_index]
                    image_examples.append(this_example[0])
                    prompt_examples.append(this_example[1] + "\n")
            prompt_input_4 = "\nNow you will analyze the following maze and determine the relative position of the player in relation to the goal."
            prompt_img_1 = PIL.Image.open('prompt-visual-images/system-figure-1.png')
            prompt_img_2 = PIL.Image.open('prompt-visual-images/system-figure-2.png')
            model_input_seq = [prompt_input_1, prompt_img_1, prompt_input_2, prompt_img_2, prompt_input_3]
            if in_context_example_num > 0:
                assert len(prompt_examples) == len(image_examples) + 1
                assert len(prompt_examples) == in_context_example_num + 1
                model_input_seq.append(prompt_examples[0])
                for example_index in range(in_context_example_num):
                    model_input_seq.append(image_examples[example_index])
                    model_input_seq.append(prompt_examples[example_index+1])
            model_input_seq += [prompt_input_4, img_input]

            response = model.generate_content(model_input_seq)
            with open(input_backup_path + "level%d/%d.txt"%(level, curr_id), "w") as f:
                contents = ""
                for input_prompt_index in range(len(model_input_seq)):
                    if type(model_input_seq[input_prompt_index]) == type("string"):
                        contents += model_input_seq[input_prompt_index]
                f.write(contents)
            with open(output_path + "level%d/%d.txt"%(level, curr_id), "w") as f:
                f.write(response.text)
            # import ipdb; ipdb.set_trace()
            # pass
            time.sleep(2)
            runned_term += 1
        except:
            time.sleep(2)
            pass
