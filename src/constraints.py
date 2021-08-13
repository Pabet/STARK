from polynomial import X
from src.channel import Channel


def first_constraint(fun):
    numer0 = fun - 1
    denom0 = X - 1
    assert numer0(1) == 0  # f(x)-1 in divisible by (x-1)
    assert numer0 % denom0 == 0  # the division yields a polynomial
    pol0 = numer0 / denom0
    assert pol0(2718) == 2509888982
    return pol0


def second_constraint(fun, g):
    numer1 = fun - 2338775057
    denom1 = X - g ** 1022
    # assert numer1(2338775057) == 0  # f(x)-2338775057 in divisible by (x-2338775057)
    assert numer1 % denom1 == 0  # the division yields a polynomial
    pol1 = numer1 / denom1
    assert pol1(5772) == 232961446
    return pol1


def third_constraint(fun, g):
    numer2 = fun(X * (g ** 2)) - (fun(g * X)) ** 2 - fun ** 2
    # print("Numerator at g^1020 is", numer2(g ** 1020))
    # print("Numerator at g^1021 is", numer2(g ** 1021))
    denom2 = (X ** 1024 - 1) / ((X - g ** 1021) * (X - g ** 1022) * (X - g ** 1023))
    pol2 = numer2 / denom2
    assert pol2.degree() == 1023, f'The degree of the third constraint is {pol2.degree()} when it should be 1023.'
    assert pol2(31415) == 2090051528
    return pol2


def get_CP(channel, pol0, pol1, pol2):
    # create a random linear combination of the rational functions
    alpha0 = channel.receive_random_field_element()
    alpha1 = channel.receive_random_field_element()
    alpha2 = channel.receive_random_field_element()
    return alpha0 * pol0 + alpha1 * pol1 + alpha2 * pol2


def CP_eval(CP, domain):
    return [CP(d) for d in domain]


def cp_test(p0, p1, p2):
    test_channel = Channel()
    CP_test = get_CP(test_channel, p0, p1, p2)
    assert CP_test.degree() == 1023, f'The degree of cp is {CP_test.degree()} when it should be 1023.'
    assert CP_test(2439804) == 838767343, f'cp(2439804) = {CP_test(2439804)}, when it should be 838767343'