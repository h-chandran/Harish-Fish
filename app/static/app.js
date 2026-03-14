const PIECES = {
    P: "♙",
    N: "♘",
    B: "♗",
    R: "♖",
    Q: "♕",
    K: "♔",
    p: "♟",
    n: "♞",
    b: "♝",
    r: "♜",
    q: "♛",
    k: "♚",
};

const files = ["a", "b", "c", "d", "e", "f", "g", "h"];
const ranks = ["8", "7", "6", "5", "4", "3", "2", "1"];

const state = {
    gameId: null,
    currentFen: null,
    moves: [],
    selectedSquares: [],
    lastBotMove: null,
    botThinking: false,
};

const boardEl = document.getElementById("board");
const gameIdEl = document.getElementById("game-id");
const fenDisplayEl = document.getElementById("fen-display");
const moveListEl = document.getElementById("move-list");
const statusOutputEl = document.getElementById("status-output");
const blackMoveInputEl = document.getElementById("black-move-input");
const selectedSquaresEl = document.getElementById("selected-squares");
const turnIndicatorEl = document.getElementById("turn-indicator");
const botMoveDisplayEl = document.getElementById("bot-move-display");
const botSourceDisplayEl = document.getElementById("bot-source-display");
const botProbabilityDisplayEl = document.getElementById("bot-probability-display");
const submitBlackBtn = document.getElementById("submit-black-btn");

document.getElementById("new-game-btn").addEventListener("click", createNewGame);
document.getElementById("reset-game-btn").addEventListener("click", resetGame);
document.getElementById("health-btn").addEventListener("click", fetchHealth);
submitBlackBtn.addEventListener("click", submitBlackMove);

renderBoardFromFen("8/8/8/8/8/8/8/8 w - - 0 1");
updateStatus("Ready.");

async function apiRequest(url, payload = null) {
    const options = {
        method: payload ? "POST" : "GET",
        headers: { "Content-Type": "application/json" },
    };

    if (payload) {
        options.body = JSON.stringify(payload);
    }

    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || "Request failed.");
    }
    return data;
}

async function fetchHealth() {
    try {
        const data = await apiRequest("/health");
        updateStatus(JSON.stringify(data, null, 2));
    } catch (error) {
        updateStatus(error.message);
    }
}

async function createNewGame() {
    const botMoveFirst = document.getElementById("bot-first").checked;
    try {
        const data = await apiRequest("/api/new-game", { bot_move_first: botMoveFirst });
        state.gameId = data.game_id;
        state.currentFen = data.current_fen;
        state.moves = [];
        state.selectedSquares = [];
        state.lastBotMove = null;
        state.botThinking = false;

        if (data.bot_move) {
            state.moves.push({
                side: "White",
                move: data.bot_move,
                source: data.source,
                probability: data.book_probability_used,
            });
            state.lastBotMove = {
                move: data.bot_move,
                source: data.source,
                probability: data.book_probability_used,
            };
        }

        syncUi();
        updateStatus(JSON.stringify(data, null, 2));
    } catch (error) {
        updateStatus(error.message);
    }
}

async function resetGame() {
    if (!state.gameId) {
        updateStatus("Create a game first.");
        return;
    }

    const botMoveFirst = document.getElementById("bot-first").checked;
    try {
        const data = await apiRequest("/api/reset-game", {
            game_id: state.gameId,
            bot_move_first: botMoveFirst,
        });

        state.currentFen = data.current_fen;
        state.moves = [];
        state.selectedSquares = [];
        state.lastBotMove = null;
        state.botThinking = false;

        if (data.bot_move) {
            state.moves.push({
                side: "White",
                move: data.bot_move,
                source: data.source,
                probability: data.book_probability_used,
            });
            state.lastBotMove = {
                move: data.bot_move,
                source: data.source,
                probability: data.book_probability_used,
            };
        }

        syncUi();
        updateStatus(JSON.stringify(data, null, 2));
    } catch (error) {
        updateStatus(error.message);
    }
}

async function submitBlackMove() {
    if (!state.gameId) {
        updateStatus("Create a game first.");
        return;
    }

    const move = blackMoveInputEl.value.trim();
    if (!move) {
        updateStatus("Enter a Black move in UCI.");
        return;
    }

    try {
        const data = await apiRequest("/api/player-move", {
            game_id: state.gameId,
            move,
        });

        state.currentFen = data.current_fen;
        state.moves.push({ side: "Black", move, source: "human", probability: null });
        state.selectedSquares = [];
        blackMoveInputEl.value = "";
        syncUi();
        updateStatus(JSON.stringify(data, null, 2));
        await requestBotMove();
    } catch (error) {
        updateStatus(error.message);
    }
}

async function requestBotMove() {
    if (!state.gameId) return;
    const turn = state.currentFen && state.currentFen.split(" ")[1] === "w";
    if (!turn) return;

    state.botThinking = true;
    if (submitBlackBtn) submitBlackBtn.disabled = true;
    try {
        updateStatus("Bot thinking…");
        const data = await apiRequest("/api/bot-move", { game_id: state.gameId });
        state.currentFen = data.resulting_fen;
        state.moves.push({
            side: "White",
            move: data.chosen_move_san,
            source: data.source,
            probability: data.book_probability_used,
        });
        state.lastBotMove = {
            move: `${data.chosen_move_san} (${data.chosen_move_uci})`,
            source: data.source,
            probability: data.book_probability_used,
        };
        syncUi();
        updateStatus(JSON.stringify(data, null, 2));
    } catch (error) {
        updateStatus(error.message);
    } finally {
        state.botThinking = false;
        if (submitBlackBtn) submitBlackBtn.disabled = false;
    }
}

function syncUi() {
    gameIdEl.textContent = state.gameId || "No game yet";
    fenDisplayEl.textContent = state.currentFen || "No position loaded.";
    renderBoardFromFen(state.currentFen || "8/8/8/8/8/8/8/8 w - - 0 1");
    renderMoveList();
    renderSelection();
    renderTurn();
    renderLastBotMove();
}

function renderMoveList() {
    moveListEl.innerHTML = "";
    state.moves.forEach((entry) => {
        const item = document.createElement("li");
        const parts = [`${entry.side}: ${entry.move}`];
        if (entry.source && entry.source !== "human") {
            parts.push(`source=${entry.source}`);
        }
        if (entry.probability !== null && entry.probability !== undefined) {
            parts.push(`p=${entry.probability}`);
        }
        item.textContent = parts.join(" | ");
        moveListEl.appendChild(item);
    });
}

function renderLastBotMove() {
    if (!state.lastBotMove) {
        botMoveDisplayEl.textContent = "none";
        botSourceDisplayEl.textContent = "none";
        botProbabilityDisplayEl.textContent = "n/a";
        return;
    }

    botMoveDisplayEl.textContent = state.lastBotMove.move;
    botSourceDisplayEl.textContent = state.lastBotMove.source || "none";
    botProbabilityDisplayEl.textContent =
        state.lastBotMove.probability === null || state.lastBotMove.probability === undefined
            ? "n/a"
            : String(state.lastBotMove.probability);
}

function renderTurn() {
    if (state.botThinking) {
        turnIndicatorEl.textContent = "Bot thinking…";
        return;
    }
    if (!state.currentFen) {
        turnIndicatorEl.textContent = "Waiting for game";
        return;
    }
    const turn = state.currentFen.split(" ")[1] === "w" ? "White to move" : "Black to move";
    turnIndicatorEl.textContent = turn;
}

function renderSelection() {
    selectedSquaresEl.textContent = state.selectedSquares.length
        ? state.selectedSquares.join(" -> ")
        : "none";
}

function renderBoardFromFen(fen) {
    boardEl.innerHTML = "";
    const boardPart = fen.split(" ")[0];
    const rows = boardPart.split("/");

    for (let visualRow = 0; visualRow < 8; visualRow += 1) {
        const logicalRow = 7 - visualRow;
        const row = rows[logicalRow];
        let fileIndex = 0;
        for (const char of row) {
            if (/\d/.test(char)) {
                const count = Number(char);
                for (let i = 0; i < count; i += 1) {
                    const square = createSquare(logicalRow, fileIndex, "");
                    boardEl.appendChild(square);
                    fileIndex += 1;
                }
            } else {
                const square = createSquare(logicalRow, fileIndex, char);
                boardEl.appendChild(square);
                fileIndex += 1;
            }
        }
    }
}

function createSquare(logicalRowIndex, fileIndex, pieceCode) {
    const square = document.createElement("button");
    square.type = "button";
    square.className = `square ${(logicalRowIndex + fileIndex) % 2 === 0 ? "light" : "dark"}`;
    const coordinate = `${files[fileIndex]}${ranks[logicalRowIndex]}`;
    square.dataset.square = coordinate;
    square.textContent = PIECES[pieceCode] || "";
    square.title = coordinate;

    if (state.selectedSquares.includes(coordinate)) {
        square.classList.add("selected");
    }

    square.addEventListener("click", () => handleSquareClick(coordinate));
    return square;
}

function handleSquareClick(square) {
    if (!state.gameId) {
        updateStatus("Create a game first.");
        return;
    }

    if (state.selectedSquares.length === 2) {
        state.selectedSquares = [];
    }

    state.selectedSquares.push(square);

    if (state.selectedSquares.length === 2) {
        blackMoveInputEl.value = `${state.selectedSquares[0]}${state.selectedSquares[1]}`;
    }

    syncUi();
}

function updateStatus(message) {
    statusOutputEl.textContent = message;
}
