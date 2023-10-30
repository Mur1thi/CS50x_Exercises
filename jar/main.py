# Create a main function and test class Jar
# Make sure to call the main function so that your program runs.
from jar.jar import Jar


def main():
	# Create a new instance of Jar
	jar = Jar()

	# Test the capacity of the jar
	print(f"Capacity of the jar is: {jar.capacity}")

	# Test the __str__ function
	print(f"Jar contains: {jar} cookies")

	# Test the deposit function
	jar.deposit()
	print(f"The Jar now contains: {jar} cookies")

	# Test the withdraw function
	jar.withdraw()
	print(f"Jar contains: {jar} cookies")

# Call the main function
if __name__ == "__main__":
	main()