import os
import pickle
#pip install python-chess
#import chess
import chess.pgn
import psycopg2
from psycopg2 import sql


connection_params = {
    "dbname": "chessdb",
    "user": "postgres",    
    "password": "123456", # ALTER USER postgres PASSWORD '123456';
    "host": "localhost",
    "port": "5432"
}
conn = psycopg2.connect(**connection_params)
cur = conn.cursor()

piece_map = {
    'black_rook': 'r',
    'black_knight': 'n',
    'black_bishop': 'b',
    'black_queen': 'q',
    'black_king': 'k',
    'black_pawn': 'p',
    'white_rook': 'R',
    'white_knight': 'N',
    'white_bishop': 'B',
    'white_queen': 'Q',
    'white_king': 'K',
    'white_pawn': 'P',
}


def get_info(custom_board):
    fen_rows = []
    
    for rank in range(8, 0, -1):  # Loop ranks from 8 to 1
        fen_row = []
        empty_squares = 0
        for file in 'abcdefgh':  # Loop files 'a' to 'h'
            piece, _, _ = custom_board[file][rank]
            if piece:
                if empty_squares > 0:
                    fen_row.append(str(empty_squares))
                    empty_squares = 0
                fen_row.append(piece_map[piece])
            else:
                empty_squares += 1
        if empty_squares > 0:
            fen_row.append(str(empty_squares))
        fen_rows.append(''.join(fen_row))

    # Join rows with '/' to create FEN position part
    fen_position = '/'.join(fen_rows)

    # Add default FEN extras: active color, castling, en passant, halfmove clock, fullmove number
    fen = f"{fen_position} w KQkq - 0 1"

    # Create a chess.Board object
    board = chess.Board(fen=fen)
    position = str(board)
    table_name = "chess_positions"
    query = """
    SELECT 
        'result' AS type, result AS key, COUNT(*) AS count
    FROM 
        chess_positions
    WHERE 
        position = %s
    GROUP BY 
        result
    UNION ALL
    SELECT 
        'next_move' AS type, next_move AS key, COUNT(*) AS count
    FROM 
        chess_positions
    WHERE 
        position = %s
    GROUP BY 
        next_move;
    """
    
    cur.execute(query, (position, position))
    rows = cur.fetchall()
    
    # Format results into dictionaries
    results = {"result": {}, "next_move": {}}
    for row in rows:
        results[row[0]][row[1]] = row[2]
    return results
