from pyfinite import ffield


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    F = ffield.FField(5)  # create the field GF(2^5)
    a = 7  # field elements are denoted as integers from 0 to 2^5-1
    b = 15
    F.ShowPolynomial(a)  # show the polynomial representation of a
    c = F.Multiply(a, b)  # multiply a and b modulo the field generator
    F.ShowPolynomial(c)
