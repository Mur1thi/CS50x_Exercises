class Jar:
    def __init__(self, capacity=12):
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("Capacity must be a positive integer.")
        self._capacity = capacity
        self.cookies = 0

    def __str__(self):
        # if null, return "no cookies"
        if self.cookies == 0:
            return "no"
        return "🍪" * self.cookies

    def deposit(self):
        n = input("Enter the number of cookies to deposit: ")
        try:
            n = int(n)
        except ValueError:
            print("Invalid input. Please enter a positive integer.")
            return
        if n < 1:
            print("Number of cookies to deposit must be a positive integer.")
            return
        if self.cookies + n > self._capacity:
            print("Depositing these many cookies would exceed the jar's capacity.")
            return
        self.cookies += n

    def withdraw(self):
        n = input("Enter the number of cookies to withdraw: ")
        try:
            n = int(n)
        except ValueError:
            print("Invalid input. Please enter a positive integer.")
            return
        if n < 1:
            print("Number of cookies to withdraw must be a positive integer.")
            return
        if self.cookies - n < 0:
            print("There are No enough cookies, only {} left.".format(self.cookies))
            return
        self.cookies -= n

    @property
    def capacity(self):
        return self._capacity

    @property
    def size(self):
            return self.cookies
