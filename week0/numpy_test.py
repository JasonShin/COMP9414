import numpy as np


def main():
    n = int(input("enter your number: "))
    matrix = np.random.randint(0, 100, (n, n))

    print("Generated Matrix:")
    print(matrix)
    print("\nSum of each row:", np.sum(matrix, axis=1))
    print("Sum of each column:", np.sum(matrix, axis=0))
    print("Overall sum:", np.sum(matrix))


if __name__ == "__main__":
    main()
