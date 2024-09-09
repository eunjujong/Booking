def read_slots(filename='slots.txt'):
    with open(filename, 'r') as file:
        slots = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    return slots