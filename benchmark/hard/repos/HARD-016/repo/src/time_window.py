def overlaps(left, right):
    left_start, left_end = left
    right_start, right_end = right
    return left_start <= right_end and right_start <= left_end
