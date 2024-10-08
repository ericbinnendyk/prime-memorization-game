# prime-memorization-game
A game to help the user memorize prime numbers.

## Installing

Requires Python 3, terminal access, and permissions to write and read arbitrary files.

* Open a terminal.
* Run `git clone https://github.com/ericbinnendyk/prime-memorization-game` into the folder of your choice.
* Navigate to `prime-memorization-game`.
* Run the program with `python3 prime_memorizer.py`.

## Instructions

The goal of this game is to help you memorize prime numbers as far as you can.

You will be given increasing numbers not divisible by 2, 3, or 5, and asked if each of them are prime.

### Normal playthrough mode

The game starts with the smallest prime candidate that has been reached on less than 3 streaks of correct answers starting from the previous starting value.

In the normal playthrough, you will be asked a review question every 10 questions. If you get the answer wrong, you will be reset back to that number and you will lose your highest streak.

In the normal mode, the game ends when 4 of the last 20 prime candidates have been guessed incorrectly. You can end the game early at any time by typing `exit`.

### Practice mode

The practice mode is useful if you want to learn primes starting from a different value, or if you want to play without the risk of damaging your progress.

In the practice mode, the game starts from an integer of your choice. The game continues indefinitely, regardless of your performance, until you type `exit`.

### Saving progress

Your progress is saved automatically into the file `prime_memorizer_progress.txt` at the end of each play, if possible. Note that if the program doesn't have permission to read and write files, you won't be able to save your progress.

### Statistics

You can also view user statistics. Currently, the following statistics are viewable:

* your three longest streaks (excluding streaks that have been removed after incorrect answers to review questions)
* your most frequently misguessed prime candidates (where more recent playthroughs get weighted more heavily)

## What about composite numbers that _are_ divisible by 2, 3, or 5?

Numbers divisible by 2 or 5 can be detected because their last digit is also divisible by 2 or 5, respectively. Numbers divisible by 3 have a digit sum divisible by 3.

Numbers not divisible by 2, 3, or 5 repeat the following values mod 30: 1, 7, 11, 13, 17, 19, 23, 29. If you want to recite primes quickly, I find it convenient to memorize this pattern and go through each prime candidate in your head, checking whether you remember it as prime or composite.
