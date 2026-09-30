// ===== Page elements =====
const bigBoard = document.getElementById('big-board');
const statusEl = document.getElementById('status');
const resetBtn = document.getElementById('reset');

// ===== Game state =====
let state;

// ===== Win detection (works for small boards AND the big board) =====
const WIN_LINES = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8], // rows
  [0, 3, 6], [1, 4, 7], [2, 5, 8], // columns
  [0, 4, 8], [2, 4, 6],            // diagonals
];

function checkWinner(cells) {
  for (const [a, b, c] of WIN_LINES) {
    const mark = cells[a];
    if ((mark === 'X' || mark === 'O') && mark === cells[b] && mark === cells[c]) {
      return mark;
    }
  }
  if (cells.every(cell => cell !== null)) return 'draw';
  return null; // still in play
}

// ===== Board rules =====
const BOARD_NAMES = [
  'top-left', 'top-center', 'top-right',
  'middle-left', 'center', 'middle-right',
  'bottom-left', 'bottom-center', 'bottom-right',
];

function isPlayableBoard(b) {
  if (state.gameWinner !== null) return false;    // game over
  if (state.boardWinners[b] !== null) return false; // board already decided
  return state.activeBoard === null || state.activeBoard === b;
}


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
    const smallEl = bigBoard.querySelector(`.small-board[data-board="${b}"]`);
    const result = state.boardWinners[b];
    const playable = isPlayableBoard(b);

    smallEl.classList.toggle('won-x', result === 'X');
    smallEl.classList.toggle('won-o', result === 'O');
    smallEl.classList.toggle('drawn', result === 'draw');
    smallEl.classList.toggle('playable', playable);

    for (let c = 0; c < 9; c++) {
      const cellEl = bigBoard.querySelector(`.cell[data-board="${b}"][data-cell="${c}"]`);
      const mark = state.cells[b][c];
      cellEl.textContent = mark ?? '';
      cellEl.classList.toggle('x', mark === 'X');
      cellEl.classList.toggle('o', mark === 'O');
      cellEl.disabled = !playable || mark !== null;
    }
  }
  
  const over = state.gameWinner !== null;
  statusEl.classList.toggle('game-over', over);
  statusEl.classList.toggle('win-x', state.gameWinner === 'X');
  statusEl.classList.toggle('win-o', state.gameWinner === 'O');

  if (state.gameWinner === 'X' || state.gameWinner === 'O') {
    statusEl.textContent = `Player ${state.gameWinner} wins! Click New Game to play again.`;
  } else if (state.gameWinner === 'draw') {
    statusEl.textContent = `It's a draw! Click New Game to play again.`;
  } else if (state.activeBoard === null) {
    statusEl.textContent = `Player ${state.currentPlayer}: choose any open board`;
  } else {
    statusEl.textContent = `Player ${state.currentPlayer}: play in the ${BOARD_NAMES[state.activeBoard]} board`;
  }
}

// ===== Handle a click on any cell =====
function handleClick(event) {
  const cellEl = event.target.closest('.cell');
  if (!cellEl) return; // clicked a gap, not a cell

  const b = Number(cellEl.dataset.board);
  const c = Number(cellEl.dataset.cell);

  if (!isPlayableBoard(b)) return;        // wrong board, board decided, or game over
  if (state.cells[b][c] !== null) return; // cell already taken

  const wasFreeMove = state.activeBoard === null;

  state.cells[b][c] = state.currentPlayer;
  state.boardWinners[b] = checkWinner(state.cells[b]);
  state.gameWinner = checkWinner(state.boardWinners);

  if (state.gameWinner !== null) {
    render(); // game over: don't pass the turn
    return;
  }

  if (wasFreeMove && state.boardWinners[b] === null) {
    state.activeBoard = b;    // free move → opponent must answer in this board
  } else {
    state.activeBoard = null; // forced move, or board just closed → opponent chooses
  }

  state.currentPlayer = state.currentPlayer === 'X' ? 'O' : 'X';
  render();
}

function startGame() {
  state = newGameState();
  render();
}

buildBoard();
bigBoard.addEventListener('click', handleClick);
resetBtn.addEventListener('click', startGame);
startGame();