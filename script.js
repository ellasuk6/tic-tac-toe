// ===== Page elements =====
const bigBoard = document.getElementById('big-board');
const statusEl = document.getElementById('status');
const resetBtn = document.getElementById('reset');

// ===== Game state =====
let state;

function newGameState() {
  return {
    cells: Array.from({ length: 9 }, () => Array(9).fill(null)), // cells[board][cell]
    boardWinners: Array(9).fill(null), // 'X' | 'O' | 'draw' | null
    currentPlayer: 'X',
    activeBoard: null,                 // null = free choice, 0–8 = forced board
    gameWinner: null,                  // 'X' | 'O' | 'draw' | null
  };
}

// ===== Build the 81 cells (runs once) =====
function buildBoard() {
  bigBoard.innerHTML = '';
  for (let b = 0; b < 9; b++) {
    const small = document.createElement('div');
    small.className = 'small-board';
    small.dataset.board = b;

    for (let c = 0; c < 9; c++) {
      const cell = document.createElement('button');
      cell.className = 'cell';
      cell.dataset.board = b;
      cell.dataset.cell = c;
      cell.setAttribute('aria-label', `Board ${b + 1}, cell ${c + 1}`);
      small.appendChild(cell);
    }
    bigBoard.appendChild(small);
  }
}

// ===== Draw the screen from the state =====
function render() {
  for (let b = 0; b < 9; b++) {
    for (let c = 0; c < 9; c++) {
      const cellEl = bigBoard.querySelector(`.cell[data-board="${b}"][data-cell="${c}"]`);
      const mark = state.cells[b][c];
      cellEl.textContent = mark ?? '';
      cellEl.classList.toggle('x', mark === 'X');
      cellEl.classList.toggle('o', mark === 'O');
    }
  }
  statusEl.textContent = `Player ${state.currentPlayer}'s turn`;
}

// ===== Handle a click on any cell =====
function handleClick(event) {
  const cellEl = event.target.closest('.cell');
  if (!cellEl) return; // clicked a gap, not a cell

  const b = Number(cellEl.dataset.board);
  const c = Number(cellEl.dataset.cell);

  if (state.cells[b][c] !== null) return; // cell already taken

  state.cells[b][c] = state.currentPlayer;
  state.currentPlayer = state.currentPlayer === 'X' ? 'O' : 'X';
  render();
}

// ===== Start / restart =====
function startGame() {
  state = newGameState();
  render();
}

buildBoard();
bigBoard.addEventListener('click', handleClick);
resetBtn.addEventListener('click', startGame);
startGame();