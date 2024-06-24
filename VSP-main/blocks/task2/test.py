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
            prompt_input_1 = '''In this task, you will see a photo of blocks. You will analyze the block configuration and then answer a question regarding the spatial relation of two specified blocks. Since coding is not within your skill set, your approach relies on logical reasoning.

## Game Setup
- Each block has a unique color (blue, yellow, purple, orange, red, green).
- Blocks are stacked vertically in a stack, forming multiple stacks.
- The possible relations of two blocks include: (A) One block is directly above another block, and they are at the same stack; (B) One block is directly below another block, and they are at the same stack; (C) Two blocks are at different blocks; (D) At least one of the asked blocks does not exist in the image.

We provide an example to further illustrate the rules:
'''

            prompt_input_2 = '''
In this example, there are four blocks in three stacks. From left to right:
- Stack 1: Purple block (alone)
- Stack 2: Blue block (alone)
- Stack 3: From bottom to top: Orange block, Red block

We can answer the questiosn regarding the spatial relations accordingly. 
For example, for the question "What is the spatial relation between the purple block and blue block?", since the purple block and the blue block are at different stacks, we should choose the choice indicating they are at different stacks.

## Procedure and Output
Your output should follow this format: 
1. First, analyze the block configuration;
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
            prompt_input_3 = "\n\nNow please answer the following question based on the given image below:\n"
            with open(input_txt_path + "%d.txt"%(curr_id), 'r') as f:
                question = f.read()
            input_img = PIL.Image.open(input_img_path + "%d.jpg"%(curr_id))
            model_input_seq = [prompt_input_1, example_img, prompt_input_2]
            if in_context_example_num > 0:
                assert len(prompt_examples) == len(image_examples) + 1
                assert len(prompt_examples) == in_context_example_num + 1
                model_input_seq.append(prompt_examples[0])
                for example_index in range(in_context_example_num):
                    model_input_seq.append(image_examples[example_index])
                    model_input_seq.append(prompt_examples[example_index+1])
            model_input_seq += [prompt_input_3, input_img, question]


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


