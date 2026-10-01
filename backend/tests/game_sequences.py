"""Legal move sequences shared by the rules, service, and API tests.

Each is a list of (board, cell) pairs, numbered 0-8 row by row. Every sequence
was checked against the rules engine; the tests that use them would fail if it
stopped being legal.
"""

# X wins board A (0) with cells 3, 4, 5 (the middle row). O cooperates by always
# answering in cell 0, which sends X straight back to board A.
X_WINS_BOARD_A = [(0, 3), (3, 0), (0, 4), (4, 0), (0, 5)]

# X wins boards A, B, C (the top row of the big board) the same way: game over.
X_WINS_TOP_ROW = [
    *X_WINS_BOARD_A,
    (5, 1), (1, 3), (3, 1), (1, 4), (4, 1), (1, 5),  # X wins B; O wins nothing yet
    (5, 2), (2, 3), (3, 2), (2, 4), (4, 2), (2, 5),  # O wins D and E; X wins C -> game
]  # fmt: skip

# Board A fills up with no winner:   X O X / X O O / O X X
# The last move is X in cell 0 (cell 1 in the professor's naming), which would send
# O to board A, now full. Moves between board-A moves are relays through other boards.
DRAW_BOARD_A = [
    (0, 2), (2, 1), (1, 0), (0, 1), (1, 2), (2, 0), (0, 3), (3, 3), (3, 0),
    (0, 4), (4, 4), (4, 0), (0, 7), (7, 5), (5, 0), (0, 5), (5, 6), (6, 0),
    (0, 8), (8, 7), (7, 0), (0, 6), (6, 8), (8, 0), (0, 0),
]  # fmt: skip
