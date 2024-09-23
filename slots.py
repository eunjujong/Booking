import ast

# def read_slots(filename='slots.txt'):
#     with open(filename, 'r') as file:
#         slots = [line.strip() for line in file if line.strip() and not line.startswith('#')]

#     return slots

def read_slots(filename='slots.txt'):
    with open(filename, 'r') as file:
        content = file.read()
        try:
            slots = ast.literal_eval(content)
        except (ValueError, SyntaxError):
            print(f"Error parsing slots from {filename}. Please check the format.")
            slots = []

    return slots



