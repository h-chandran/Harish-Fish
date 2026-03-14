import sys

import chess


def main() -> None:
    board = chess.Board()

    while True:
        line = sys.stdin.readline()
        if not line:
            break

        command = line.strip()
        if command == "uci":
            print("id name FakeUciEngine")
            print("id author Harish-Fish Tests")
            print("option name Threads type spin default 1 min 1 max 16")
            print("option name Hash type spin default 16 min 1 max 2048")
            print("option name Skill Level type spin default 20 min 0 max 20")
            print("option name UCI_LimitStrength type check default true")
            print("option name UCI_Elo type spin default 2400 min 1320 max 3190")
            print("uciok")
            sys.stdout.flush()
            continue

        if command == "isready":
            print("readyok")
            sys.stdout.flush()
            continue

        if command.startswith("setoption"):
            continue

        if command == "ucinewgame":
            board = chess.Board()
            continue

        if command.startswith("position startpos"):
            board = chess.Board()
            if "moves" in command:
                moves = command.split("moves", 1)[1].strip().split()
                for move_uci in moves:
                    board.push_uci(move_uci)
            continue

        if command.startswith("position fen"):
            parts = command.split()
            fen = " ".join(parts[2:8])
            board = chess.Board(fen)
            if "moves" in command:
                moves = command.split("moves", 1)[1].strip().split()
                for move_uci in moves:
                    board.push_uci(move_uci)
            continue

        if command.startswith("go"):
            move = next(iter(board.legal_moves))
            print(f"bestmove {move.uci()}")
            sys.stdout.flush()
            continue

        if command == "quit":
            break


if __name__ == "__main__":
    main()
