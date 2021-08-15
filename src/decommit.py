def decommit_on_fri_layers(idx, channel, fri_layers, fri_merkles):
    for layer, merkle in zip(fri_layers[:-1], fri_merkles[:-1]):
            length = len(layer)
            idx = idx % length
            idx_sibling = (idx + length // 2) % length
            channel.send(str(layer[idx]))
            channel.send(str(merkle.get_authentication_path(idx)))
            channel.send(str(layer[idx_sibling]))
            channel.send(str(merkle.get_authentication_path(idx_sibling)))
    channel.send(str(fri_layers[-1][0]))


def decommit_on_query(idx, channel, f_eval, f_merkle, fri_layers, fri_merkle):
    channel.send(str(f_eval[idx]))
    channel.send(str(f_merkle.get_authentication_path(idx)))
    channel.send(str(f_eval[idx + 8]))
    channel.send(str(f_merkle.get_authentication_path(idx + 8)))
    channel.send(str(f_eval[idx + 16]))
    channel.send(str(f_merkle.get_authentication_path(idx + 16)))
    decommit_on_fri_layers(idx, channel, fri_layers, fri_merkle)


def decommit_fri(channel, f_eval, f_merkle, fri_layers, fri_merkle):
    for query in range(3):
        idx = channel.receive_random_int(0, 8191-16)
        decommit_on_query(idx, channel, f_eval, f_merkle, fri_layers, fri_merkle)
