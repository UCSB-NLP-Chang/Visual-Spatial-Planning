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

levels = [3,4,5]
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
    3: [],
    4: [],
    5: [],
}
for level in levels:
    for example_id in range(8):
        curr_example_pack = {}
        curr_example_pack["image_path"] = "example/level%d/image_input/%d.jpg"%(level, example_id)
        with open("example/level%d/text_input/%d.txt"%(level, example_id), 'r') as f:
            curr_example_pack["question"] = f.read()
        with open("example/level%d/answer/%d.txt"%(level, example_id), 'r') as f:
            curr_example_pack["answer"] = f.read()
        EXAMPLE_DICT[level].append(curr_example_pack)

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
            prompt_input_1 = '''In this task, you will analyze an image containing several stacks of blocks. Later, you will be presented with four choices, each offering a textual representation of a block configuration. You will need to choose the configuration that exactly reflects the contents of the given image.

## Game Setup
- Each block has a unique color (blue, yellow, purple, orange, red, green).
- Blocks are stacked vertically in a stack, forming multiple stacks.

This is an image input example:\n
'''

            prompt_input_2 = '''
This example features four blocks arranged in three stacks:
- Stack 1: Purple block (alone)
- Stack 2: Blue block (alone)
- Stack 3: From bottom to top: Orange block, Red block

Here are examples of textual representations:

(A)
- Stack with red block, yellow block, from bottom to top
- Stack with orange block, purple block, green block, from bottom to top

(B)
- Stack with purple block
- Stack with blue block
- Stack with orange block, red block, from bottom to top

(C)
- Stack with orange block
- Stack with purple block
- Stack with blue block
- Stack with green block, yellow block, from bottom to top

(D)
- Stack with green block
- Stack with yellow block, blue block, from bottom to top
- Stack with red block, orange block, from bottom to top

We can analyze which text representation exactly reflects the configurations in the image accordingly. In this example:
- The input image has 3 stacks, while Candidate A only has 2 stacks. Therefore, Candidate A is not the correct answer.
- Similarly, Candidate C has 4 stacks, which also cannot be correct.
- For Candidate B, the blocks in each stack match what's shown in the image. This is the correct answer.
- For Candidate D, the blocks in each stack do not match the image. For example, stack 1 in the image has a purple block, and there is no any purple block in Candidate D. So this is incorrect.
- Therefore, the final answer is B.

## Procedure and Output
Your output should follow this format:
1. First, analyze the block configuration in the image and candidates as shown above;
2. Then, answer the question with the format <Output> <Choice>, where <Choice> is one of {A,B,C,D}. For example, "<Output> A".
'''

            prompt_examples = []
            image_examples = []
            if in_context_example_num > 0:
                prompt_examples.append("## Example:\n")
                example_indices = random.sample(range(8), in_context_example_num)
                for example_index in example_indices:
                    this_example = EXAMPLE_DICT[level][example_index]
                    image_examples.append(PIL.Image.open(this_example["image_path"]))
                    prompt_examples.append(this_example["question"] + "\n" + this_example["answer"] + "\n")
            prompt_input_3 = "\n\nNow please choose the correct textual representation based on the given image below:\n"
            prompt_input_4 = "\nHere are the textual candidates:\n"
            with open(input_txt_path + "%d.txt"%(curr_id), 'r') as f:
                candidates = f.read()
            input_img = PIL.Image.open(input_img_path + "%d.jpg"%(curr_id))
            model_input_seq = [prompt_input_1, example_img, prompt_input_2]
            if in_context_example_num > 0:
                assert len(prompt_examples) == len(image_examples) + 1
                assert len(prompt_examples) == in_context_example_num + 1
                model_input_seq.append(prompt_examples[0])
                for example_index in range(in_context_example_num):
                    model_input_seq.append(image_examples[example_index])
                    model_input_seq.append(prompt_examples[example_index+1])
            model_input_seq += [prompt_input_3, input_img, prompt_input_4, candidates]
            # , prompt_input_3, input_img, prompt_input_4, candidates]
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


