import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

import PIL.Image
import time
import os

import random
import numpy as np
def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    # torch.manual_seed(seed)
    # torch.cuda.manual_seed(seed)
    # torch.backends.cudnn.deterministic = True
    # env.seed(seed)
seed_everything(1)

levels = [1,3,5,7,9]
in_context_example_num = 0 # 0, 1, 2, 4, 8
formal_action_dict = {'D': "Down", 'U': "Up", 'L': "Left", 'R': "Right"}

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

EXAMPLE_DICT = {
    1: [],
    3: [],
    5: [],
    7: [],
    9: [],
}

# Prepare examples
for level in levels:
    for example_id in range(8):
        curr_example_pack = {}
        curr_example_pack["image_path"] = "example/level_step%d/img/%d.png"%(level, example_id)
        with open("example/level_step%d/question/%d.txt"%(level, example_id), 'r') as f:
            curr_example_pack["question"] = f.read()
        with open("example/level_step%d/analysis/%d.txt"%(level, example_id), 'r') as f:
            curr_example_pack["answer"] = f.read()
        EXAMPLE_DICT[level].append(curr_example_pack)

# import ipdb; ipdb.set_trace()
example_img_1 = PIL.Image.open('prompt-visual-images/system-figure-1.png')
example_img_2 = PIL.Image.open('prompt-visual-images/system-figure-2.png')   
for level in levels:
    os.makedirs(output_path + "level%d"%(level), exist_ok=True)
    os.makedirs(input_backup_path + "level%d"%(level), exist_ok=True)
    start_idx = 0
    end_idx = 100
    runned_term = 0
    input_img_path = "maps/level_step%d/img/"%(level)
    input_txt_path = "maps/level_step%d/question/"%(level)
    while True:
        try:
            curr_id = start_idx + runned_term
            if curr_id >= end_idx:
                break
            prompt_input_1 = '''
You are a maze-solving agent playing a pixelated maze videogame.
Mazes are presented on grid maps, where each tile can be empty land, or contain a player, hole, or goal.
Each of the above tile types are represented as square pixel art images.

In this task, you will analyze a grid-based map and determine if a provided action plan is safe. A safe action plan avoids stepping into holes in the map.
The following figure illustrates the appearances of the player, holes, lands, and the goal within the maze.
'''

            prompt_input_2 = '''
## Moving Rules
- The action plan involves a series of moves: 'L' (left), 'R' (right), 'U' (up), or 'D' (down).
- Each move transfers the player to the adjacent square in that direction, provided it is a safe square. The player cannot move more than one square at a time.
- Moving off the edge of the map has no effect. The player will remain at the same square.
- DO NOT MOVE INTO A HOLE! Falling into a hole results in defeat.
- Locating at the grid containing the goal results in victory.
We provide an example to further illustrate the rules.
'''
            
            prompt_input_3 = '''
In this provided example:
- The player is at Row 1, Column 1;
- The goal is at Row 4, Column 4;
- There are two holes: one at Row 1, Column 2, and another at Row 4, Column 1.
- The player can move DOWN. This is because moving down brings them to Row 2, Column 1, and this cell is safe (without holes).
- Moving UP has no effects. This is because the player is already in the topmost row.
- Similarly, moving LEFT has no effects because the player is already in the left-most column.
- Moving RIGHT places the player at Row 1, Column 2. Since there is a hole at this grid, this move results in a loss.

## Procedure and Output
Your output should include the following parts:
1. First, interpret map. List where the player is at now, where is the goal, and where are the holes.
2. Then, reasoning by following the given action plan. At each step, you should check:
    (a) Where the current move leads the player to (the row and column);
    (b) What is in that grid. Is it a hole? Is it the goal? Is it an empty space?
    (c) Determine if that is a safe action.
3. Output if the action sequence is safe using "<Output> Yes" or "<Output> No". A safe action sequence should not include any unsafe actions.
'''
            prompt_examples = []
            image_examples = []
            if in_context_example_num > 0:
                prompt_examples.append("## Example:\n")
                example_indices = random.sample(range(8), in_context_example_num)
                for example_index in example_indices:
                    this_example = EXAMPLE_DICT[level][example_index]
                    this_action = this_example["question"]
                    asking_action_sequence = ""
                    for each_action_char in this_action:
                        asking_action_sequence += formal_action_dict[each_action_char]
                        asking_action_sequence += ", "
                    asking_action_sequence = asking_action_sequence[:-2]
                    image_examples.append(PIL.Image.open(this_example["image_path"]))
                    prompt_examples.append("\nThe action sequence is:\n" + asking_action_sequence + "\n" + this_example["answer"] + "\n")
            prompt_input_4 = "\n\nNow please determine if the action sequence is safe for this given maze:"
            prompt_input_5 = "\nThe action sequence is:\n"
            begin_img = PIL.Image.open('maps/level_step%d/img/%d.png'%(level, curr_id))
            with open(input_txt_path + "%d.txt"%(curr_id), 'r') as f:
                question = f.read()
                asking_action_sequence = ""
                for each_action_char in question:
                    asking_action_sequence += formal_action_dict[each_action_char]
                    asking_action_sequence += ", "
                asking_action_sequence = asking_action_sequence[:-2]
            model_input_seq = [prompt_input_1, example_img_1, prompt_input_2, example_img_2, prompt_input_3]
            if in_context_example_num > 0:
                assert len(prompt_examples) == len(image_examples) + 1
                assert len(prompt_examples) == in_context_example_num + 1
                model_input_seq.append(prompt_examples[0])
                for example_index in range(in_context_example_num):
                    model_input_seq.append(image_examples[example_index])
                    model_input_seq.append(prompt_examples[example_index+1])
            model_input_seq += [prompt_input_4, begin_img, prompt_input_5, asking_action_sequence]

            response = model.generate_content(model_input_seq)
            with open(input_backup_path + "level%d/%d.txt"%(level, curr_id), "w") as f:
                contents = ""
                for input_prompt_index in range(len(model_input_seq)):
                    if type(model_input_seq[input_prompt_index]) == type("string"):
                        contents += model_input_seq[input_prompt_index]
                f.write(contents)
            with open(output_path + "level%d/%d.txt"%(level, curr_id), "w") as f:
                f.write(response.text)
            time.sleep(2)
            runned_term += 1
        except:
            time.sleep(2)
            pass



