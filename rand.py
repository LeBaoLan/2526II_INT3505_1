import random

# lucky_number = random.randint(1, 100)
# print(lucky_number)
# guess = int(input("enter your guess (1-100): "))

# previous_guess = None
# while guess != lucky_number:

#     if guess < lucky_number:
#         print("too low")
#         previous_guess = guess
#         guess = int(input(
#             f"enter your guess ({guess}-{previous_guess if previous_guess != None else 100}): "))
#     else:
#         print("too high")
#         previous_guess = guess
#         guess = int(input(
#             f"enter your guess ({previous_guess if previous_guess != None else 0}-{guess}): "))


# print("you win")


options = ["rock", "paper", "scissors"]
print("BO5 of rock, paper, scissors")
user_score = 0
computer_score = 0

for i in range(5):
    user_choice = input("enter rock, paper or scissors: ").lower()
    while user_choice not in options:
        user_choice = input("invalid choice, enter rock, paper or scissors: ").lower()
    computer_choice = random.choice(options)
    
    print(f"computer chose {computer_choice}")

    if user_choice == computer_choice:
        print("it's a tie")
    elif ((user_choice == "rock" and computer_choice == "scissors") or
          (user_choice == "scissors" and computer_choice == "paper") or
          (user_choice == "paper" and computer_choice == "rock")):
        print("you win")
        user_score += 1
    else:
        print("computer wins")
        computer_score += 1


print(f"Final score: you {user_score} - {computer_score} computer")

print("you win!" if user_score > computer_score else "computer wins!" if computer_score > user_score else "it's a tie!")    