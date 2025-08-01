import base64
import os
from mistralai import Mistral

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

def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None

# Retrieve the API key from environment variables
# api_key = "YOUR_API_KEY"

# Specify model
model = "pixtral-12b-2409"

# Initialize the Mistral client
client = Mistral(api_key=api_key)

levels = [6]
in_context_example_num = 0 # 0, 1, 2, 4, 8

if in_context_example_num > 0:
    assert 0
else:
    output_path = "your_output_path/"
    input_backup_path = "input-mistral/input_backup_img/"

os.makedirs(output_path, exist_ok=True)
os.makedirs(input_backup_path, exist_ok=True)
import ipdb; ipdb.set_trace()
for level in levels:
    with open("../maps/level%d/car-dir.txt"%(level), "r") as f:
        car_dirs = f.read().split('\n')
    with open("../maps/level%d/person-dir.txt"%(level), "r") as f:
        person_dirs = f.read().split('\n')
    with open("../maps/level%d/car-speed.txt"%(level), "r") as f:
        car_speeds = f.read().split('\n')
    with open("../maps/level%d/person-speed.txt"%(level), "r") as f:
        person_speeds = f.read().split('\n')
    os.makedirs(output_path + "level%d"%(level), exist_ok=True)
    os.makedirs(input_backup_path + "level%d"%(level), exist_ok=True)
    start_idx = 12
    end_idx = 100
    runned_term = 0
    example_image = encode_image("../prompt-visual-images/example.png")
    icon_image = encode_image("../prompt-visual-images/icon.png")
    while True:
        try:
            curr_id = start_idx + runned_term
            if curr_id >= end_idx:
                break
            test_id = curr_id
            test_image = encode_image("../maps/level%d/%d.png"%(level, test_id))
            prompt_1 = '''As a professional navigation agent, your task is to analyze a map and determine the time needed for the car and the person passing the goal.

## Game Setup
- The game presents a fully observable map. There is a person, a car, and a goal on the map.
- The game further specifies the moving direction of the person and car ("up", "down", "left", "right").
- Your goal is to determine the time needed for the car and the person passing the goal.
The following figure shows how the player, the car, and the goals look like.
'''

            prompt_2 = '''
We provide an example to further illustrate the rules.
'''
            prompt_3 = '''
The car is moving left with speed 1.0 grid per second, and the person is moving up with speed 0.5 grid per second.

In this provided example:
- The car is 2 grid away from the goal. Given it's time as 1.0 grid per second, the time needed is 2 / 1.0 = 2 seconds.
- The person is 1 grid away from the goal. Given it's time as 0.5 grid per second, the time needed is 1 / 0.5 = 2 seconds.

## Procedure and Output
Now you will answer for the following given map. To solve it, analyze the car and the person separately. Then, answer for them separately. For example:
Car: 2.0
Person: 2.0
means car and the person will need 2.0 seconds to pass the goal respectively.
Do not output any extra content after the above aggregated output.

Please analyze and determine the time needed for the car and the person passing the goal:
'''
            test_direction_prompt = "The car is moving %s with speed %s, and the person is moving %s with speed %s."%(car_dirs[test_id], car_speeds[test_id], person_dirs[test_id], person_speeds[test_id])
            prompt_examples = []
            image_examples = []

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_1
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{icon_image}"
                        },
                        {
                            "type": "text",
                            "text": prompt_2
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{example_image}"
                        },
                        {
                            "type": "text",
                            "text": prompt_3
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{test_image}"
                        },
                        {
                            "type": "text",
                            "text": test_direction_prompt
                        }
                    ]
                }
            ]
            # import ipdb; ipdb.set_trace()
            chat_response = client.chat.complete(
                model=model,
                messages=messages,
                max_tokens=1000
            )
            time.sleep(3)
            # import ipdb; ipdb.set_trace()
            print(chat_response.choices[0].message.content)
            with open(output_path + "level%d/%d.txt"%(level, curr_id), "w") as f:
                f.write(chat_response.choices[0].message.content)
            time.sleep(2)
            runned_term += 1
        except:
            print("error")
            time.sleep(2)
            pass
        # except:
        #     import ipdb; ipdb.set_trace()
        #     pass







