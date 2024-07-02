# Visual-Spatial-Planning Benchmark (VSP)

[Qiucheng Wu](https://wuqiuche.github.io/)<sup>1</sup>,
[Handong Zhao](https://hdzhao.github.io)<sup>2</sup>,
[Michael Saxon](https://saxon.me)<sup>1</sup>,
[Trung Bui](https://sites.google.com/site/trungbuistanford/)<sup>2</sup>,
[William Yang Wang](http://www.cs.ucsb.edu/~william/)<sup>1</sup>,
[Yang Zhang](https://mitibmwatsonailab.mit.edu/people/yang-zhang/)<sup>3</sup>,
[Shiyu Chang](https://code-terminator.github.io/)<sup>1</sup>
<br>
<sup>1</sup>UC, Santa Barbara, <sup>2</sup>Adobe Research, <sup>3</sup>MIT-IBM Watson AI Lab

This is the repo of the paper "VSP: Assessing the dual challenges of perception and reasoning in spatial planning tasks for VLMs".

## Introduction
Vision language models (VLMs) are an exciting emerging class of language models (LMs) that have merged classic LM capabilities with those of image processing systems. However, the ways that these capabilities combine are not always intuitive and warrant direct investigation. One understudied capability in VLMs is visual spatial planning ---the ability to comprehend the spatial arrangements of objects and devise action plans to achieve desired outcomes in visual scenes. In our study, we introduce VSP, a benchmark that 1) evaluates the spatial planning capability in these models in general, and 2) breaks down the visual planning task into finer-grained sub-tasks, including perception and reasoning, and measure the LMs capabilities in these sub-tasks. Our evaluation shows that both open-source and private VLMs fail to generate effective plans for even simple spatial planning tasks. Evaluations on the fine-grained analytical tasks further reveal fundamental deficiencies in the models’ visual perception and bottlenecks in reasoning abilities, explaining their worse performance in the general spatial planning tasks. We hope our work illuminates future directions for improving VLMs' abilities in spatial planning.

## Benchmark Access
Our benchmark consists of 10 tasks in 2 scenarios (maze navigation, blocks world). You can find the detailed tests under folder ```<SCENARIO>/task*```, where ```<SCENARIO>``` is one of "maze" and "blocks". For example, ```maze/task-main``` contains original test and evaluation files for the main task in the maze navigation scenario.

Each task includes the following contents:
1. ```maps```. This contains the original test data for the task, including mapped images and text inputs. They are organized by levels of difficulties.
2. ```prompt-text```. This includes the text part of the prompt.
3. ```prompt-visual-images```. This includes the image part of the prompt.
4. ```example```. This includes the in-context example used in the tasks.
5. ```test.py``` and ```eval.py```. These files are used as examples of testing and evaluation.

## Test on the Benchmark
Our benchmark is convenient for evaluation. We provide examples for testing on Gemini.
To run on Gemini, please first build the environment:
```bash
conda env create -f gemini.yaml
conda activate gemini
```
Alternatively, following Gemini official website to install necessary packages. After that, you may navigate to any task and run the test script. For example, the main task in maze navigation scenario:
```bash
cd maze/task-main
python test.py
```
Notice that you should include your Gemini API in the code.


## Acknowledgement
To implement the two scenarios, we utilize and enhance existing resources from two aspects. For the maze navigation scenario, we leverage [OpenAI's gym](https://gymnasium.farama.org) engine to generate input images. For the blocks world scenario, we sample input images from the [BIRD dataset](https://github.com/ASU-APG/BIRD_Code). The reference for the two works are listed below.
```
@misc{gokhale2019blocksworld, 
  title={Blocksworld Revisited: Learning and Reasoning to Generate Event-Sequences from Image Pairs}, 
  author={Tejas Gokhale and Shailaja Sampat and Zhiyuan Fang and Yezhou Yang and Chitta Baral}, 
  year={2019}, 
  eprint={1905.12042}, 
  archivePrefix={arXiv}, 
  primaryClass={cs.CV} 
}

@article{brockman2016openai,
  title={Openai gym},
  author={Brockman, Greg and Cheung, Vicki and Pettersson, Ludwig and Schneider, Jonas and Schulman, John and Tang, Jie and Zaremba, Wojciech},
  journal={arXiv preprint arXiv:1606.01540},
  year={2016}
}
```
