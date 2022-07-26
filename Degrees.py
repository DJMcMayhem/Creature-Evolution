def shortest_move(a1: float, a2: float) -> float:
    dist_positive = (a2 - a1) % 360.0
    dist_negative = (a1 - a2) % 360.0

    if dist_positive <= dist_negative:
        return dist_positive

    return 0 - dist_negative


def angle_lerp(a1: float, a2: float, amt: float) -> float:
    return a1 + (shortest_move(a1, a2) * amt) % 360.0


def rotate_towards(a1: float, a2: float, max_rot: float) -> float:
    turn = shortest_move(a1, a2)

    if turn < 0:
        return (a1 + max(-max_rot, turn)) % 360.0

    return (a1 + min(max_rot, turn)) % 360.0
