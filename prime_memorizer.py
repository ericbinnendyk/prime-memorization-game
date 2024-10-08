# A game that helps the player memorize prime numbers.
# Most recent changes: Make it so that the game starts with the smallest prime candidate the user has guessed in less than 3 consecutive streaks. Add instructions and stats.

from my_math import factorize
from random import random
from math import log

def is_prime(n):
    return len(factorize(n)) == 1

is_answer_valid = lambda s: len(s) > 0 and (s[0] in {'Y', 'y', 'N', 'n'} or s == 'exit')

residues = [1, 7, 11, 13, 17, 19, 23, 29]

prev_streak = 0

def next_prime_candidate(n):
    quotient = n // 30
    remainder = n % 30
    next_index = (residues.index(remainder) + 1) % 8
    remainder = residues[next_index]
    if next_index == 0:
        quotient += 1
    return quotient*30 + remainder

def prev_prime_candidate(n):
    if n == 7: return 7
    quotient = n // 30
    remainder = n % 30
    prev_index = (residues.index(remainder) - 1) % 8
    remainder = residues[prev_index]
    if prev_index == 7:
        quotient -= 1
    return quotient*30 + remainder

def generate_review_prime_candidate(start):
    num_cands_back = int(log(random())/log(2**-0.0375)) + 1
    num_thirty_ranges = num_cands_back // 8
    candidate = start
    candidate -= 30*num_thirty_ranges
    if candidate < 31:
        # try again
        return generate_review_prime_candidate(start)
    for i in range(num_cands_back % 8):
        candidate = prev_prime_candidate(candidate)
    if candidate < 31:
        # try again
        return generate_review_prime_candidate(start)
    return candidate

# ask the user whether n is prime, and return the correct answer and whether the user was correct
# or return None if the user exits
def ask_user(n):
    n_is_prime = is_prime(n)
    answer = input("Is {} prime? (Y/N, or 'exit' to exit) ".format(n))
    while not is_answer_valid(answer):
        answer = input("Invalid input. Try again: ")
    if answer == 'exit':
        return None
    answer_is_yes = len(answer) > 0 and answer[0] in {'Y', 'y'}
    correct = (n_is_prime == answer_is_yes)
    return (n_is_prime, correct)

# print to the screen whether the user's answer was right or wrong
def print_user_answer(n, n_is_prime, correct):
    if not correct:
        print("Wrong!")
    else:
        print("Correct!")
    if n_is_prime:
        print() # having this extra empty line makes all the lines line up
    else:
        # show the factors of the number if it's composite
        print("{} = {}".format(n, '*'.join(map(str, factorize(n)))))

# updates the dropoff list with the latest streak, hard to explain
def update_dropoff(dropoff, streak_end):
    index_to_add = -1
    for i, candidate in enumerate(dropoff):
        if candidate > streak_end:
            index_to_add = i
            break
    if index_to_add == -1:
        index_to_add = len(dropoff)
    dropoff.insert(index_to_add, streak_end)
    # delete the first stairstep, as the number of streaks has already become "at least 3", unless the new stairstep added is strictly earlier than all of the others, in which case all the future "reach counts" are bumped down by 1 and the last stairstep is deleted
    if index_to_add == 0:
        del dropoff[-1]
    else:
        del dropoff[0]

# reads the data from the last save file and returns it as a dict
def process_game_data(path):
    f = None
    try:
        f = open(path, 'r')
    except:
        return None
    lines_of_f = f.readlines()
    f.close()

    stats = dict()
    data_components = [[]] # a list for the different segments of data from the file, separated by blank lines
    for line in lines_of_f:
        line = line.strip()
        if line == '' and (len(data_components[-1]) > 0 or len(data_components) == 1):
            data_components.append([])
        elif line != '':
            data_components[-1].append(line)

    # process the threshold/dropoff values to tell what number to start the game on
    if len(data_components[0]) > 0:
        stats['dropoff'] = [int(line) for line in data_components[0]]

    # process the incorrect guess stats
    if len(data_components) > 1 and len(data_components[1]) > 0:
        stats['stats'] = dict()
        misguessed_info = data_components[1]
        for line in misguessed_info:
            info_in_line = line.split(' ')
            n = int(info_in_line[0])
            score = float(info_in_line[1])
            stats['stats'][n] = score

    return stats

# saves game data
def save_game_data(path, stats):
    f = None
    try:
        f = open(path, 'w')
    except:
        print("Error: could not save game data to file {}".format(path))
        return

    if 'dropoff' in stats:
        for n in stats['dropoff']:
            f.write(str(n) + '\n')
    f.write('\n')
    if 'stats' in stats:
        most_misguessed = stats['stats']
        for n in most_misguessed:
            f.write("{} {}\n".format(n, most_misguessed[n]))
    f.close()

def int_input(prompt, default=-1):
    try:
        return int(input(prompt))
    except:
        # user input can't be converted to an integer
        return default

def summarize_wrong_guesses(incorrect_guesses):
    print()
    print("Incorrect guesses (excluding review questions):")
    for n in incorrect_guesses:
        print(n, end='')
        print(" ", end='')
        if is_prime(n):
            print("(guessed composite, actually prime)")
        else:
            print("(guessed prime, actually {})".format('*'.join(map(str, factorize(n)))))

def main_game(practice, start=0):
    stats = process_game_data('prime_memorizer_progress.txt')
    most_misguessed = dict()
    if stats != None and 'stats' in stats:
        most_misguessed = stats['stats'] # dictionary assigning a score to each number based on how often the user fails to guess it, with exponentially decaying weights for previous plays

    dropoff = [] # this new list represents the largest candidate that has been included in at least 3 streaks, 2 streaks, and 1 streak respectively

    # find the starting value
    initial_n = 0 # dummy value

    if practice:
        initial_n = start
        if initial_n < 7:
            initial_n = 7
        while initial_n % 30 not in residues:
            initial_n += 1
    else:
        if stats != None and 'dropoff' in stats:
            dropoff = stats['dropoff']
            # backwards compatibility
            if len(dropoff) == 1:
                dropoff = [dropoff[0], dropoff[0], dropoff[0]]

        if len(dropoff) > 0:
            # start with the smallest prime that's been in less than 3 of the user's streaks
            initial_n = next_prime_candidate(dropoff[0])
        else:
            initial_n = 7 # smallest valid value
            # no streaks yet
            dropoff = [1, 1, 1]

    n = initial_n
    last_unbroken_streak = prev_prime_candidate(n) # the last value v such that the user has answered correctly for all values from 7 up to v
    num_guesses = 0
    num_correct_guesses = 0
    incorrect_guesses = []
    last_20_guesses = []
    while True:
        answer = ask_user(n)
        if answer == None: # user wants to end the game
            break
        n_is_prime, correct = answer

        print_user_answer(n, n_is_prime, correct)

        num_guesses += 1
        if correct:
            num_correct_guesses += 1
            if last_unbroken_streak == prev_prime_candidate(n):
                last_unbroken_streak = n
        else:
            incorrect_guesses.append(n)
        last_20_guesses.append(correct)
        if len(last_20_guesses) > 20: del last_20_guesses[0]
        
        print("Correct guesses: {}/{} ({:.2f}%)".format(num_correct_guesses, num_guesses, 100*num_correct_guesses/num_guesses))

        # if the user got at least 4 of the last 20 non-review questions wrong, it's game over (except in practice mode)
        if not practice and len([x for x in last_20_guesses if x == False]) >= 4:
            print("At least four of the most recent 20 guesses were wrong.")
            print("Game over.")
            break

        n = next_prime_candidate(n)
        
        if not practice:
            if num_guesses % 10 == 0 and n > 100 and initial_n > 31:
                # pose a review question
                # if the user gets this question wrong, their streak is reset back to this number (unless it was set back to a smaller value by an earlier review question)
                print("Review:")
                review_n = generate_review_prime_candidate(initial_n)
                answer = ask_user(review_n)
                if answer == None: # user wants to end the game
                    break
                review_n_is_prime, correct = answer

                print_user_answer(review_n, review_n_is_prime, correct)

                if not correct:
                    last_unbroken_streak = min(last_unbroken_streak, prev_prime_candidate(review_n))

    last_n = n

    summarize_wrong_guesses(incorrect_guesses)

    if not practice:
        update_dropoff(dropoff, last_unbroken_streak)

        # update most_misguessed dict with new incorrect guesses
        most_misguessed = dict([(n, most_misguessed[n]) for n in most_misguessed if n > last_unbroken_streak])
        for n in most_misguessed:
            if last_unbroken_streak < n <= last_n and n not in incorrect_guesses:
                most_misguessed[n] = most_misguessed[n]*0.7
        for n in incorrect_guesses:
            if n not in most_misguessed:
                most_misguessed[n] = 0
            most_misguessed[n] = most_misguessed[n]*0.7 + 0.3

        save_game_data('prime_memorizer_progress.txt', {'dropoff': dropoff, 'stats': most_misguessed})

def print_instructions():
    print()
    print("Instructions")
    print()
    print("The goal of this game is to help you memorize all the prime numbers")
    print("up to a certain level.")
    print()
    print("You will be given increasing numbers not divisible by 2, 3, or 5,")
    print("and asked if each of them are prime.")
    print()
    print("The game starts with the smallest prime candidate that has been reached")
    print("on less than 3 streaks of correct answers starting from the previous")
    print("starting value.")
    print()
    print("In the normal playthrough, you will be asked a review question every")
    print("10 questions. If you get the answer wrong, you will be reset back to")
    print("that number and you will lose your highest streak.")
    print()
    print("In the normal mode, the game ends when 4 of the last 20 prime candidates")
    print("have been guessed incorrectly.")

def show_stats():
    stats = process_game_data('prime_memorizer_progress.txt')
    if stats == None or stats == dict():
        print("No stats to show yet.")
    if 'dropoff' in stats:
        print("Longest streaks: {}".format(', '.join([str(x) for x in stats['dropoff']])))
    if 'stats' in stats:
        most_misguessed_pairs = list(stats['stats'].items())
        most_misguessed_pairs.sort(key=lambda x: x[1])
        most_misguessed_pairs.reverse()
        print("Your most misguessed numbers are:")
        for n, freq in most_misguessed_pairs:
            print("{} (about {:.2f}%)".format(n, freq))

print("Welcome to Eric's Prime Memorization Game!")
while True:
    print()
    print("1. Play in normal mode")
    print("2. Play in practice mode (doesn't count towards score)")
    print("3. Instructions")
    print("4. Show stats")
    print("0. Exit")
    game_mode = int_input("Please enter a value: ")
    while game_mode not in {1, 2, 3, 4, 0}:
        game_mode = int_input("Invalid input. Try again: ")
    if game_mode == 1:
        main_game(practice=False)
    if game_mode == 2:
        print("Welcome to practice mode!")
        n = int_input("Enter integer to start quiz from: ", default=0)
        main_game(practice=True, start=n)
    if game_mode == 3:
        print_instructions()
    if game_mode == 4:
        show_stats()
    if game_mode == 0:
        print("Goodbye!")
        exit()
