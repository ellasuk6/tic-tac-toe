const bigBoard = document.getElementById('big-board');

function buildBoard() {
  bigBoard.innerHTML = '';
  for (let b = 0; b < 9; b++) {
    const small = document.createElement('div');
    small.className = 'small-board';
    small.dataset.board = b;

    for (let c = 0; c < 9; c++) {
      const cell = document.createElement('button');
      cell.className = 'cell';
      cell.dataset.board = b;   // which small board (0–8)
      cell.dataset.cell = c;    // which cell inside it (0–8)
      cell.setAttribute('aria-label', `Board ${b + 1}, cell ${c + 1}`);
      small.appendChild(cell);
    }
    bigBoard.appendChild(small);
  }
}

buildBoard();