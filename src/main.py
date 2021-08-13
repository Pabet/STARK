from channel import Channel
from field import FieldElement
from merkle import MerkleTree
from polynomial import Polynomial, interpolate_poly
from hashlib import sha256
from channel import serialize
from src.constraints import first_constraint, second_constraint, third_constraint, get_CP, CP_eval
from src.fri import next_fri_domain, next_fri_layer, fri_commit


# part 1: Statement, Low-Degree-Extension and Commitment functions

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

    # part2: Polynomial Constraints

    p0 = first_constraint(f)  # first rational function
    p1 = second_constraint(f, g)  # second rational function
    p2 = third_constraint(f, g)  # third rational function

    # print('deg p0 =', p0.degree())
    # print('deg p1 =', p1.degree())
    # print('deg p2 =', p2.degree())

    # channel = Channel()
    cp = get_CP(channel, p0, p1, p2)
    cp_eval = CP_eval(cp, eval_domain)
    cp_merkle = MerkleTree(cp_eval)

    # part3: FRI

    next_domain = next_fri_domain(eval_domain)

    # test fri layer generation:
    test_poly = Polynomial([FieldElement(2), FieldElement(3), FieldElement(0), FieldElement(1)])
    test_domain = [FieldElement(3), FieldElement(5)]
    beta = FieldElement(7)
    next_p, next_d, next_l = next_fri_layer(test_poly, test_domain, beta)
    assert next_p.poly == [FieldElement(23), FieldElement(7)]
    assert next_d == [FieldElement(9)]
    assert next_l == [FieldElement(86)]

    fri_polys, fri_domains, fri_layers, fri_merkles = fri_commit(cp, eval_domain, cp_eval, cp_merkle, channel)
    print(channel.proof)
