from itertools import combinations

"""
Prepare sudoku board and variables
"""

assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

index = 0
diagonal_units_1 = []
diagonal_units_2 = []
for row in rows:
    diagonal_units_1.append(row + cols[index:index+1])
    diagonal_units_2.append(row + cols[::-1][index:index+1])
    index += 1

diagonal_units = [diagonal_units_1, diagonal_units_2]

unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    for unit in unitlist:
        twin_candidates = {}
        for box in unit:
            if len(values[box]) == 2:
                twin_candidates[box] = values[box]
        # Eliminate the naked twins as possibilities for their peers
        if len(twin_candidates) >= 2:
            for a, b in combinations(twin_candidates, 2):
                if twin_candidates[a] == twin_candidates[b]:
                    for box in unit:
                        if box != a and box != b:
                            for digit in twin_candidates[a]:
                                if digit in values[box]:
                                    assign_value(values, box, values[box].replace(digit, ''))

    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    dict = {}
    index = 0
    for value in grid:
        if value == '.':
            value = '123456789'
        dict[boxes[index]] = value
        index += 1
    return dict

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def eliminate(values):
    """
    If a box has a value with only one digit, remove this digit from all peers of this box
    :param values: The sudoku in dictionary form
    :return: The sudoku in dictionary form after the elimination method
    """
    for key, value in values.items():
        if len(value) == 1:
            for peer in peers[key]:
                assign_value(values, peer, values[peer].replace(value,''))
    return values

def only_choice(values):
    """
    Check for all units, if there is a value, which can be assigned to one box in that unit only.
    If you find one, assign the value to this box.
    :param values: The sudoku in dictionary form
    :return: The sudoku in dictionary form after the only choice method
    """
    for unit in unitlist:
        numCount = [0] * 10
        numLastBox = [""] * 10
        for box in unit:
            for number in values[box]:
                numCount[int(number)] += 1
                numLastBox[int(number)] = box
        for idx, val in enumerate(numCount):
            if val == 1:
                assign_value(values, numLastBox[idx], str(idx))
    return values

def reduce_puzzle(values):
    """
    Try to solve the puzzle by applying the methods eliminate, only_choice and naked_twins.
    If the boards doesn't change anymore compared to the last iteration, return the board.
    :param values: The sudoku in dictionary form
    :return: The sudoku in dictionary form after applying all the solving methods multiple times
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        eliminate(values)

        # Your code here: Use the Only Choice Strategy
        only_choice(values)
        
        naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Using depth-first search and propagation, create a search tree and solve the sudoku.
    :param values: The sudoku in dictionary form
    :return: The sudoku in dictionary form after the depth-first search method
    """
    values = reduce_puzzle(values)
    
    if values == False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values
    
    minLen = 9
    minKey = 'A1'
    # Choose one of the unfilled squares with the fewest possibilities
    for key, val in values.items():
        if len(val) > 1 and minLen > len(val):
            minLen = len(val)
            minKey = key
        
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    if not (minLen == 9 and minKey == 'A1'):
        for number in values[minKey]:
            temp = values.copy()
            temp[minKey] = number
            result = search(temp)
            if result:
                return result

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
