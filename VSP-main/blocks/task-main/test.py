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

levels = [1,3,5,7]
in_context_example_num = 0 # 0, 1, 2, 4

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
}

# Prepare examples
for level in levels:
    for example_id in range(8):
        curr_example_pack = {}
        curr_example_pack["start_image_path"] = "example/level%d/begin/%d.jpg"%(level, example_id)
        curr_example_pack["end_image_path"] = "example/level%d/end/%d.jpg"%(level, example_id)
        example_path = "example/level%d/"%(level)
        curr_example_pack["question1"] = "\n\nPlease generate the moving plan. The beginning state is:"
        curr_example_pack["question2"] = "\nThe end state is:"
        with open(example_path + "sol_%d.txt"%(example_id), "r") as f:
            curr_example_pack["answer"] = f.read()
        EXAMPLE_DICT[level].append(curr_example_pack)

example_img = PIL.Image.open('prompt-visual-images/example0.jpg')        

# import ipdb; ipdb.set_trace()
for level in levels:
    os.makedirs(output_path + "level%d"%(level), exist_ok=True)
    os.makedirs(input_backup_path + "level%d"%(level), exist_ok=True)
    start_idx = 0
    end_idx = 100
    runned_term = 0
    input_img_path = "level%d/input_img"%(level)
    output_img_path = "level%d/output_img"%(level)
    while True:
        try:
            curr_id = start_idx + runned_term
            if curr_id >= end_idx:
                break
            prompt_input_1 = '''You are a robot that sorts and organizes colored blocks by adding and removing them to stacks.
You can move them between stacks to produce a desired end state.

In this task, you will see two photos of blocks. These photos show the beginning and end state of the blocks. Your task is to find a shortest movement plan to transit from the beginning state to the end state. Since coding is not within your skill set, your approach relies on logical reasoning of the map.

## Game Setup
- The stacks of blocks are presented in images. You must view and interpret the image in order to determine which blocks are in which stack and determine how to move them.
- Each block has a unique color (blue, yellow, purple, orange, red, green).
- Blocks are stacked vertically in a stack, forming multiple stacks. All stacks are on the table.
- In a single move, you can only move the top block of any pile. Attempting to move lower blocks is considered an invalid move.
- You can either (a) move the top block to the top of another stack, or (b) place the top block on the table, creating a new stack with just one block.
'''

            prompt_input_2 = '''
We provide an example to further illustrate the rules:
'''
            
            prompt_input_3 = '''
This example features four blocks arranged in three stacks:
- Stack 1: Purple block (alone)
- Stack 2: Blue block (alone)
- Stack 3: From bottom to top: Orange block, Red block
You can only move the top block of each stack: the purple block, the blue block, and the red block. The orange block is stuck underneath the red block and cannot be moved directly.
Each move can place the block on another stack or on the table (creating a new stack of one).  For instance, you could move the red block to either the blue stack or the table.
**Important Note**: The order of the stacks doesn't matter in this game. Two images are considered equivalent as long as the stacks contain the same blocks, regardless of the order in which the stacks appear. For example, an image with stack A on the left and stack B on the right is equivalent to an image with stack B on the left and stack A on the right.

## Procedure and Output
Your output should follow this format:
1. First, analyze the starting and ending configurations, including the number of stacks and the blocks in each stack (similar to the example above).
2. Then, list the moves in a step-by-step manner using the format move(SOURCE, TARGET). Remember, "SOURCE" refers to the block being moved (always the top block of a stack), and "TARGET" refers to the destination (another stack or the table).

## Example Output
<Analysis> 
Starting state: there are three stacks:
- Stack 1: Purple block (alone)
- Stack 2: Blue block (alone)
- Stack 3: From bottom to top: Orange block, Red block
Ending state: there are three stacks:
- Stack 1: Purple block (alone)
- Stack 2: From bottom to top: Orange block, Blue block
- Stack 3: Red block (alone)
<Output>
1. move(red,table)
2. move(blue,orange)
'''
            prompt1_examples = []
            prompt2_examples = []
            prompt3_examples = []
            image1_examples = []
            image2_examples = []
            if in_context_example_num > 0:
                # prompt_examples.append("## Example:\n")
                example_indices = random.sample(range(8), in_context_example_num)
                for example_index in example_indices:
                    this_example = EXAMPLE_DICT[level][example_index]
                    image1_examples.append(PIL.Image.open(this_example["start_image_path"]))
                    image2_examples.append(PIL.Image.open(this_example["end_image_path"]))
                    prompt1_examples.append(this_example["question1"])
                    prompt2_examples.append(this_example["question2"])
                    prompt3_examples.append("\n<Output>\n" + this_example["answer"] + "\n")
                    # prompt_examples.append("\n" + this_example["question"] + "\n<Output>" + this_example["answer"] + "\n")
            prompt_input_4 = "\n\nNow please generate moving plan. The beginning state is:"
            prompt_input_5 = "\nThe end state is:"
            begin_img = PIL.Image.open('level%d/input_img/%d.jpg'%(level, curr_id))
            end_img = PIL.Image.open('level%d/output_img/%d.jpg'%(level, curr_id))
            # prompt_img_1 = PIL.Image.open('prompt-visual-images/system-figure-1.png')
            # prompt_img_2 = PIL.Image.open('prompt-visual-images/system-figure-2.png')
            model_input_seq = [prompt_input_1, prompt_input_2, example_img, prompt_input_3]
            if in_context_example_num > 0:
                # assert len(prompt_examples) == len(image1_examples) + 1
                # assert len(prompt_examples) == in_context_example_num + 1
                model_input_seq.append("## Example:")
                for example_index in range(in_context_example_num):
                    model_input_seq.append(prompt1_examples[example_index])
                    model_input_seq.append(image1_examples[example_index])
                    model_input_seq.append(prompt2_examples[example_index])
                    model_input_seq.append(image2_examples[example_index])
                    model_input_seq.append(prompt3_examples[example_index])
            model_input_seq += [prompt_input_4, begin_img, prompt_input_5, end_img]

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



