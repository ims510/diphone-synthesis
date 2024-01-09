def get_user_input():
    # Define the table as a list of lists
    table = [
        ["le chat noir grimpe", "le chien marron aboie", "le jeune garçon parle", "le chat beige saute", "la vieille femme glisse"],
        ["sur le toit", "sur le lit", "sur le sol"],
        ["en miaulant", "en sautant", "en riant", "en grattant", "en appuyant"],
        ["joyeusement", "bruyamment", "fortement", "les draps", "les rideaux"]
    ]

    # Get user input for each column
    choices = []
    for column in table:
        if len(choices) > 0:
            print(f"\nYour sentence so far: {' '.join(choices)}")
            print("-----------------------------------------------------------")

        print("\n".join(f"{i + 1}. {item}" for i, item in enumerate(column)))
        user_choice = input(f"Choose an element for your sentence (1-{len(column)}): ")
        print("-----------------------------------------------------------")
        # Validate user input
        while not user_choice.isdigit() or not (1 <= int(user_choice) <= len(column)):
            print("Invalid input. Please enter a valid number.")
            user_choice = input(f"Choose an element for your sentence (1-{len(column)}): ")

        # Append the chosen element to the choices list
        choices.append(column[int(user_choice) - 1])

    # Capitalize the first letter of the first choice and add a full stop at the end

    return choices

# Call the function and print the result
user_choices = get_user_input()
if user_choices:
    user_choices[0] = user_choices[0].capitalize()
    user_choices[len(user_choices)-1] =  user_choices[len(user_choices)-1] + "."
print("\nYour selected sentence:")
print(" ".join(user_choices))
