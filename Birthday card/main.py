# Get user input
recipient_name = input("Enter the recipient's name: ")
year_of_birth = int(input("Enter the year of birth: "))
message = input("Enter a personalized message: ")
sender_name = input("Enter the sender's name: ")

# Get current year
from datetime import datetime
current_year = datetime.now().year

# Calculate age
age = current_year - year_of_birth

# Print birthday card
print("\n--- Birthday Card ---\n")
print(f"{recipient_name}, let's celebrate your {age} years of awesomeness!")
print(f"Wishing you a day filled with joy and laughter as you turn {age}!\n")
print(message)
print("\nWith love and best wishes,")
print(sender_name)
