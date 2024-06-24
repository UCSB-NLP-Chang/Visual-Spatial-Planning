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
        curr_example_pack["image_path"] = "example/level%d/image_input/%d.jpg"%(level, example_id)
        with open("example/level%d/text_input/%d.txt"%(level, example_id), 'r') as f:
            curr_example_pack["question"] = f.read()
        with open("example/level%d/answer/%d.txt"%(level, example_id), 'r') as f:
            curr_example_pack["answer"] = f.read()
        EXAMPLE_DICT[level].append(curr_example_pack)

# import ipdb; ipdb.set_trace()
example_img = PIL.Image.open('prompt-visual-images/example0.jpg')        
for level in levels:
    os.makedirs(output_path + "level%d"%(level), exist_ok=True)
    os.makedirs(input_backup_path + "level%d"%(level), exist_ok=True)
    start_idx = 0
    end_idx = 100
    runned_term = 0
    input_img_path = "level%d/image_input/"%(level)
    input_txt_path = "level%d/text_input/"%(level)
    while True:
        try:
            curr_id = start_idx + runned_term
            if curr_id >= end_idx:
                break
            prompt_input_1 = '''
You are a robot that sorts and organizes colored blocks by adding and removing them to stacks.
You can move them between stacks to produce a desired end state.

In this task, you will see a photo of blocks. This photo shows the beginning state of the blocks. You will see a photo of blocks. This photo shows the beginning state of the blocks. Meanwhile, you will be provided an action sequence about moving blocks. Your task is to determine if the provided action plan can be successfully executed. Since coding is not within your skill set, your approach relies on logical reasoning of the map.

## Game Setup
- The block configuration is presented in the image. You must view and interpret the image in order to determine which blocks are in which stack and determine the consequence of moving.
- Each block has a unique color (blue, yellow, purple, orange, red, green).
- Blocks are stacked vertically in a stack, forming multiple stacks.
- A valid action can only move the top block of any stacks. Attempting to move lower blocks is considered an invalid move.
- For the destination, a valid move can either (a) move the top block to the top of another stack, or (b) place the top block on the table, creating a new stack with just one block.
'''

            prompt_input_2 = '''
We provide an example to further illustrate the rules:
'''
            
            prompt_input_3 = '''
The sequence of actions provided is:
1. move(red,table)
2. move(green,table)

In this example, there are four blocks in three stacks. The stacks are:
- Stack 1: Purple block (alone)
- Stack 2: Blue block (alone)
- Stack 3: From bottom to top: Orange block, Red block
It is valid to move the purple block, the blue block, and the red block, since they are at the top of a stack. It is invalid to move the orange block since it is not at the top of a stack (because it is covered by the red block).
Each move can place the block on top of another stack or on the table (creating a new stack of one).  For instance, you could move the red block to either the blue stack or the table.

## Procedure and Output
Your output should follow this format:
1. First, briefly analyze the block configuration, and check each action step by step to see if the provided step is valid as shown above.
2. Then, answer the question with the format "<Output> Yes" or "<Output> No" to indicate if the action sequence is valid.

Here is an example for the output:
<Analysis> In the image, there are three stacks:
- Stack 1: Purple block (alone)
- Stack 2: Blue block (alone)
- Stack 3: From bottom to top: Orange block, Red block
The first action "move(red,table)" is valid, because the red block is on top of a stack (stack 3 in this case), and the target is "table". After the first action, the state will become:
- Stack 1: Purple block (alone)
- Stack 2: Blue block (alone)
- Stack 3: Orange block (alone)
- Stack 4: Red block (alone)
The second action "move(green,table)" is invalid, because there is no green block.
Therefore, the provided action sequence is invalid.
<Output> No
'''
            prompt_examples = []
            image_examples = []
            if in_context_example_num > 0:
                prompt_examples.append("## Example:\n")
                example_indices = random.sample(range(8), in_context_example_num)
                for example_index in example_indices:
                    this_example = EXAMPLE_DICT[level][example_index]
                    image_examples.append(PIL.Image.open(this_example["image_path"]))
                    prompt_examples.append("\nThe action sequence is:\n" + this_example["question"] + "\n" + this_example["answer"] + "\n")
            prompt_input_4 = "\n\nNow please determine if the provided action sequence is valid given the following input state:"
            prompt_input_5 = "\nThe action sequence is:\n"
            begin_img = PIL.Image.open('level%d/image_input/%d.jpg'%(level, curr_id))
            with open(input_txt_path + "%d.txt"%(curr_id), 'r') as f:
                question = f.read()
            model_input_seq = [prompt_input_1, prompt_input_2, example_img, prompt_input_3]
            if in_context_example_num > 0:
                assert len(prompt_examples) == len(image_examples) + 1
                assert len(prompt_examples) == in_context_example_num + 1
                model_input_seq.append(prompt_examples[0])
                for example_index in range(in_context_example_num):
                    model_input_seq.append(image_examples[example_index])
                    model_input_seq.append(prompt_examples[example_index+1])
            model_input_seq += [prompt_input_4, begin_img, prompt_input_5, question]

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



