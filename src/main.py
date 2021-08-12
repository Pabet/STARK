from channel import Channel
from field import FieldElement
from merkle import MerkleTree
from polynomial import interpolate_poly, X, prod
from hashlib import sha256
from channel import serialize


def create_execution_trace():
    trace = [FieldElement(1), FieldElement(3141592)]  # first two elements of the trace
    while len(trace) < 1023:
        trace.append(trace[-2] * trace[-2] + trace[-1] * trace[-1])  # create execution trace

    assert len(trace) == 1023  # The trace must consist of exactly 1023 elements.
    assert trace[0] == FieldElement(1)  # The first element in the trace must be the unit element.
    for i in range(2, 1023):
        assert trace[i] == trace[i - 1] * trace[i - 1] + trace[i - 2] * trace[
            i - 2]  # The FibonacciSq recursion rule does not apply for index {i}
    assert trace[1022] == FieldElement(2338775057)  # Wrong last element!
    return trace


def find_sub_group():
    generator = FieldElement.generator() ** (3221225472 / 1024)  # generator of the subgroup of size 1024
    Group = [generator ** i for i in range(1024)]  # subgroup

    # Checks that g and G are correct.
    assert generator.is_order(1024)  # The generator g is of wrong order.
    b = FieldElement(1)
    for i in range(1023):
        assert b == Group[i]  # The i-th place in G is not equal to the i-th power of g
        b = b * generator
        assert b != FieldElement(1)  # f'g is of order {i + 1}

    if b * generator != FieldElement(1):
        print('g is of order > 1024')
    return generator, Group


def get_polynomial(x, y):
    # create the polynomial
    # G -> x_values, a -> y_values
    polynomial = interpolate_poly(x, y)
    v = polynomial(2)
    assert v == FieldElement(1302089273)
    return polynomial


def extend_domain():
    # extent to a larger domain
    h = FieldElement.generator() ** (3221225472 / 8192)  # h generator of subgroup of size 8192
    H = [h ** i for i in range(8192)]
    w = FieldElement.generator()
    e_d = [w * i for i in H]

    assert len(set(e_d)) == len(e_d)
    w = FieldElement.generator()
    w_inv = w.inverse()
    assert '55fe9505f35b6d77660537f6541d441ec1bd919d03901210384c6aa1da2682ce' == sha256(str(H[1]).encode()).hexdigest(), \
        'H list is incorrect. H[1] should be h (i.e., the generator of H).'
    for i in range(8192):
        assert ((w_inv * e_d[1]) ** i) * w == e_d[i]
    return e_d


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
    numer2 = fun(X*(g**2)) - (fun(g*X))**2 - fun**2
    print("Numerator at g^1020 is", numer2(g ** 1020))
    print("Numerator at g^1021 is", numer2(g ** 1021))
    denom2 = (X ** 1024 - 1) / ((X - g**1021) * (X - g**1022) * (X - g**1023))
    pol2 = numer2 / denom2
    assert pol2.degree() == 1023, f'The degree of the third constraint is {pol2.degree()} when it should be 1023.'
    assert pol2(31415) == 2090051528
    return pol2


def get_CP(channel, pol0, pol1, pol2):
    # create a random linear combination of the rational functions
    alpha0 = channel.receive_random_field_element()
    alpha1 = channel.receive_random_field_element()
    alpha2 = channel.receive_random_field_element()
    return alpha0*pol0 + alpha1*pol1 + alpha2*pol2


def CP_eval(channel, p0, p1, p2, domain):
    CP = get_CP(channel, p0, p1, p2)
    return [CP(d) for d in domain]


if __name__ == '__main__':
    # part 1: Statement, Low-Degree-Extension and Commitment

    a = create_execution_trace()

    g, G = find_sub_group()

    f = get_polynomial(G[:-1], a)

    eval_domain = extend_domain()

    # evaluation on the coset
    f_eval = [f(x) for x in eval_domain]
    assert '1d357f674c27194715d1440f6a166e30855550cb8cb8efeb72827f6a1bf9b5bb' == sha256(
        serialize(f_eval).encode()).hexdigest()

    # commitment to our evaluation of f on the extended domain
    f_merkle = MerkleTree(f_eval)
    assert f_merkle.root == '6c266a104eeaceae93c14ad799ce595ec8c2764359d7ad1b4b7c57a4da52be04'

    # channel <-> conversion to a non-interactive proof by using the Fiat-Shamir-Heuristic
    channel = Channel()
    channel.send(f_merkle.root)

    print(channel.proof)

    p0 = first_constraint(f)  # first rational function
    p1 = second_constraint(f, g)  # second rational function
    p2 = third_constraint(f, g)  # third rational function

    print('deg p0 =', p0.degree())
    print('deg p1 =', p1.degree())
    print('deg p2 =', p2.degree())

    test_channel = Channel()
    CP_test = get_CP(test_channel, p0, p1, p2)
    assert CP_test.degree() == 1023, f'The degree of cp is {CP_test.degree()} when it should be 1023.'
    assert CP_test(2439804) == 838767343, f'cp(2439804) = {CP_test(2439804)}, when it should be 838767343'

    channel = Channel()
    CP_merkle = MerkleTree(CP_eval(channel, p0, p1, p2, eval_domain))
    assert CP_merkle.root == 'a8c87ef9764af3fa005a1a2cf3ec8db50e754ccb655be7597ead15ed4a9110f1', 'Merkle tree root is wrong.'
    print('Success!')
