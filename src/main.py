from channel import Channel
from field import FieldElement
from merkle import MerkleTree
from polynomial import interpolate_poly, Polynomial
from hashlib import sha256
from channel import serialize

if __name__ == '__main__':
    a = [FieldElement(1), FieldElement(3141592)]  # first two elements of the trace
    while len(a) < 1023:
        a.append(a[-2] * a[-2] + a[-1] * a[-1])  # create execution trace

    assert len(a) == 1023  # The trace must consist of exactly 1023 elements.
    assert a[0] == FieldElement(1)  # The first element in the trace must be the unit element.
    for i in range(2, 1023):
        assert a[i] == a[i - 1] * a[i - 1] + a[i - 2] * a[
            i - 2]  # The FibonacciSq recursion rule does not apply for index {i}
    assert a[1022] == FieldElement(2338775057)  # Wrong last element!

    g = FieldElement.generator() ** (3221225472 / 1024)  # generator of the subgroup of size 1024
    G = [g ** i for i in range(1024)]  # subgroup

    # Checks that g and G are correct.
    assert g.is_order(1024)  # The generator g is of wrong order.
    b = FieldElement(1)
    for i in range(1023):
        assert b == G[i]  # The i-th place in G is not equal to the i-th power of g
        b = b * g
        assert b != FieldElement(1)  # f'g is of order {i + 1}

    if b * g != FieldElement(1):
        print('g is of order > 1024')

    # create the polynomial
    # G -> x_values, a -> y_values
    p = interpolate_poly(G[:-1], a)
    v = p(2)
    assert v == FieldElement(1302089273)

    # extent to a larger domain
    h = FieldElement.generator() ** (3221225472 / 8192)  # h generator of subgroup of size 8192
    H = [h ** i for i in range(8192)]
    w = FieldElement.generator()
    eval_domain = [w * i for i in H]

    assert len(set(eval_domain)) == len(eval_domain)
    w = FieldElement.generator()
    w_inv = w.inverse()
    assert '55fe9505f35b6d77660537f6541d441ec1bd919d03901210384c6aa1da2682ce' == sha256(str(H[1]).encode()).hexdigest(), \
        'H list is incorrect. H[1] should be h (i.e., the generator of H).'
    for i in range(8192):
        assert ((w_inv * eval_domain[1]) ** i) * w == eval_domain[i]

    # evaluation on the coset
    f_eval = [p(x) for x in eval_domain]
    assert '1d357f674c27194715d1440f6a166e30855550cb8cb8efeb72827f6a1bf9b5bb' == sha256(
        serialize(f_eval).encode()).hexdigest()

    # commitment to our evaluation of f on the extended domain
    f_merkle = MerkleTree(f_eval)
    assert f_merkle.root == '6c266a104eeaceae93c14ad799ce595ec8c2764359d7ad1b4b7c57a4da52be04'

    # channel <-> conversion to a non-interavtive proof by using the Fiat-Shamir-Heuristic
    channel = Channel()
    channel.send(f_merkle.root)

    print(channel.proof)

