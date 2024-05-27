"""
The goal of this script is to always play the Little Prince chapters in the right order

However, there is a list of themes that can be displayed before each chapter, and the order of the themes is randomized.
We want to have 50% normal runs, and 50% runs with the themes displayed in a random order.

The themes handling is done using a txt file, where each line is a theme. The themes are read from the file, one of them is picked 
randomly, based of a random order generated at the beginning of the experiment.

The themes are displayed for 10 seconds, and the subject is asked to imagine about the theme.

The theme txt file is generated at the beginning of the experiment, with the subject number
We also need to save the answers of the subject about two questions:
- On a scale from 1 to 5, how easy was it for you to imagine about the given theme?
- On a scale from 1 to 5, how well do you think you managed to ignore the audio?

The answers are saved in a csv file, parametered with:
- the subject number,
- the run number,


We also need to be able to save the subject's answers to the questions about the LPP text in the same csv file.

The general executing pattern will be:

- Launch the python script using the subject and run number
- The script waits 10 seconds before starting the audio for the first run
- If it is a control run, the initial theme is displayed, instructions are given
- The script sends a trigger to the MEG system to indicate the start of the audio
- The audio is played
- The script sends a trigger to the MEG system to indicate the end of the audio
- The script then prompts the experiment for, in this order:
    - The subject's answer to the first question (theme imagination)
    - The subject's answer to the second question (audio ignoring)
    - The subject's answer to the third question (LPP text)

This is then saved for a given run, given subject

Note:

Handling if a run crashes in the middle / has to be restarted:
- The removal of the theme from the txt file has to be done at the very end!


Files:
- themes.txt: the list of themes: SIZE = NUMBER_OF_THEMES
- data/theme_{sub}.txt: the list of themes for the subject, SIZE = NUMBER_OF_THEMES
- data/is_random_{sub}.txt: the list of 0s and 1s to check whether it is a random run or not, size = len(chap_list)
- data/answers_{sub}.csv: the csv file with the answers of the subject, with the columns:
    - run number
    - theme imagination
    - audio ignoring
    - LPP text

"""

from expyriment import design, control, stimuli, io, misc
import meg_triggers
import sys
import os
import random
import pandas as pd


def generate_list(n):
    half_n = n // 2
    lst = [1] * half_n + [0] * half_n
    random.shuffle(lst)
    return lst

initialized = False

# Handle the arguments
if len(sys.argv) != 3:
    raise ValueError('The script needs two arguments: the subject number and the run number')

sub = int(sys.argv[1])
run = int(sys.argv[2])

THEME_NUMBERS = 13 ## ASSUMPTION: 27 chapters, 13 themes, 13 control runs

# TODO: Put the new chapter numbers, to 27
chap_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26"]

# AUDIO = f'wav/ch{chap_list[run]}.wav'##'wav/ch1-3.wav'
AUDIO = f'./../misc/ch1.wav'##'wav/ch1-3.wav'

# Check if the theme file exists (if not: run 1 for eg., generate it)
theme_file = f'themes.txt'
assert os.path.isfile(theme_file), f'The theme file does not exist'
# Check that there are enough themes for the runs
with open(theme_file, 'r') as f:
    lines = f.readlines()
    assert len(lines) >= len(chap_list)/2, f'There are not enough themes in the theme file'

# Same for the random / not random runs: it is a 50/50 chance, and we generate the random order at the beginning of the experiment
# Generate a list of 1s and 0s, 1 for random, 0 for not random, in a random order, with 50% of each

# Check if it exsits:
if not os.path.isfile(f'data/is_random_{sub}.txt'):
    # Generate the random order
    print(f'Generating random order for subject {sub}')
    with open(f'data/is_random_{sub}.txt', 'w') as f:
        # Generate a list of 0s and 1s, 50% of each
        for i in generate_list(len(chap_list)):
            f.write(str(i) + '\n')

# Same for theme order:
# Check if it exsits:
if not os.path.isfile(f'data/order_theme_{sub}.txt'):
    # Generate the random order
    with open(f'data/order_theme_{sub}.txt', 'w') as f:
        # Write a shuffled list of numbers from 0 to THEME_NUMBERS
        for i in random.sample(range(THEME_NUMBERS), THEME_NUMBERS):
            f.write(lines[i])

# Check that there is the same amount of lines in the random file as in the chapter list
# and there are only 0s and 1s in the file, and 50% of each

with open(f'data/is_random_{sub}.txt', 'r') as f:
    lines = f.readlines()
    if len(lines) != len(chap_list):
        raise ValueError('The random file does not have the right amount of lines')
    if not all([l in ['0\n', '1\n'] for l in lines]):
        raise ValueError('The random file does not have the right values')
    if len([l for l in lines if l == '0\n']) != THEME_NUMBERS or len([l for l in lines if l == '1\n']) != THEME_NUMBERS:
        raise ValueError('The random file does not have the right amount of 0s and 1s')
    
    random_order = [int(l) for l in lines]

RANDOM_RUN = random_order[run] == 1

if RANDOM_RUN:
    # Get the theme for the run
    with open(f'themes.txt', 'r') as f:
        with open(f'data/order_theme_{sub}.txt', 'r') as f2:
            lines = f.readlines()
            lines2 = f2.readlines()
            theme = lines2[run]

    print(f'\n Random run {run} \n')
    print(f'\n Theme: {theme} \n')

else:
    print(f'\n Normal run {run} \n')


print(f'\n Ready to play {AUDIO} \n')
exp = design.Experiment(name="Le_Petit_Prince")

control.set_develop_mode(False)
control.defaults.open_gl = 2

##
control.initialize(exp)

stim = stimuli.Audio(AUDIO)

fixcrossGreen = stimuli.FixCross(size=(45, 45), line_width=5,
                                 colour=(0, 255, 0))
fixcrossGreen.preload()
fixcrossGrey = stimuli.FixCross(size=(45, 45), line_width=3,
                                colour=(192, 192, 192))
fixcrossGrey.preload()


def clear_screen():
    exp.screen.clear()
    exp.screen.update()

def wait_for_MRI_synchro():
    fixcrossGreen.present(clear=True, update=True)
    exp.keyboard.wait_char('t')

control.start(exp)

stim.preload()
#wait_for_MRI_synchro()
p1 = meg_triggers.send_start(initialized)
initialized = True # to not have to recreate the parport
exp.clock.wait(50)
meg_triggers.send_stop(p1)

clear_screen()
fixcrossGrey.present(clear=True, update=True)
stim.present()
control.wait_end_audiosystem()

p1 = meg_triggers.send_start(initialized,p1)
exp.clock.wait(50)
meg_triggers.send_stop(p1)

io.Keyboard.process_control_keys()

control.end()

# Save the answers of the subject

# Ask for the answers directly in the command line
# On a scale from 1 to 5, how easy was it for you to imagine about the given theme?
# On a scale from 1 to 5, how well do you think you managed to ignore the audio?
# On a scale from 1 to 5, how well do you think you managed to understand the LPP text?

theme_imagination = int(input('On a scale from 1 to 5, how easy was it for you to imagine about the given theme? '))
audio_ignoring = int(input('On a scale from 1 to 5, how well do you think you managed to ignore the audio? '))

# Load the txt file with the questions about the LPP text
df_questions = pd.read_csv('questions_lpp.csv')

# TODO
lpp_text = int(input(df_questions.iloc[run]['question']))

with open(f'data/answers_{sub}.csv', 'a') as f:
    f.write(f'{sub},{run},{theme_imagination},{audio_ignoring},{lpp_text}\n')