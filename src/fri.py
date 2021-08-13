from src.channel import Channel
from src.field import FieldElement
from src.merkle import MerkleTree
from src.polynomial import Polynomial


def next_fri_domain(fri_domain):
    return [(x ** 2) for x in fri_domain[:len(fri_domain) // 2]]


# slice operator-> string[start:end:step]
def next_fri_polynomial(poly, beta):
    even_coefficients = poly.poly[::2]  # take every second coefficient starting from the constant
    odd_coefficients = poly.poly[1::2]  # take every second coefficient starting from the second element
    even = Polynomial(even_coefficients)
    odd = beta * Polynomial(odd_coefficients)
    return odd + even


def next_fri_layer(poly, domain, beta):
    next_poly = next_fri_polynomial(poly, beta)
    next_domain = next_fri_domain(domain)
    next_layer = [next_poly(x) for x in next_domain]
    return next_poly, next_domain, next_layer


def fri_commit(cp, domain, cp_eval, cp_merkle, channel):
    fri_polys = [cp]
    fri_domains = [domain]
    fri_layers = [cp_eval]
    fri_merkles = [cp_merkle]
    while fri_polys[-1].degree() > 0:
        beta = channel.receive_random_field_element()
        next_poly, next_domain, next_layer = next_fri_layer(fri_polys[-1], fri_domains[-1], beta)
        fri_polys.append(next_poly)
        fri_domains.append(next_domain)
        fri_layers.append(next_layer)
        fri_merkles.append(MerkleTree(next_layer))
        channel.send(fri_merkles[-1].root)
    channel.send(str(fri_polys[-1].poly[0]))
    return fri_polys, fri_domains, fri_layers, fri_merkles


def test(cp, eval_domain, cp_eval, cp_merkle):
    test_channel = Channel()
    fri_polys, fri_domains, fri_layers, fri_merkles = fri_commit(cp, eval_domain, cp_eval, cp_merkle, test_channel)
    assert len(fri_layers) == 11, f'Expected number of FRI layers is 11, whereas it is actually {len(fri_layers)}.'
    assert len(fri_layers[-1]) == 8, f'Expected last layer to contain exactly 8 elements, it contains {len(fri_layers[-1])}.'
    assert all([x == FieldElement(-1138734538) for x in fri_layers[-1]]), f'Expected last layer to be constant.'
    assert fri_polys[-1].degree() == 0, 'Expacted last polynomial to be constant (degree 0).'
    assert fri_merkles[-1].root == '1c033312a4df82248bda518b319479c22ea87bd6e15a150db400eeff653ee2ee', 'Last layer Merkle root is wrong.'
    assert test_channel.state == '61452c72d8f4279b86fa49e9fb0fdef0246b396a4230a2bfb24e2d5d6bf79c2e', 'The channel state is not as expected.'

