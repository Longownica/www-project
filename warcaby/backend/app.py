import os
import pickle
import json
from pprint import pprint
from xmlrpc.client import Boolean
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from bson.binary import Binary
from typing import Optional, List
import motor.motor_asyncio
from checkers.game import Game
from checkers.board import Board

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.checkers
games = db['games']

class Piece(BaseModel):
    position: int
    is_white: bool
    is_king: bool

class GameState(BaseModel):
    id: str
    pieces: List[Piece]
    finished: bool
    you_white: bool
    whites_turn: bool
    possible_moves: List[List[int]]

class GameStateDb(BaseModel):
    pkl: Binary
    finished: bool




def get_pieces(game: Game) -> List[Piece]:
    pprint(vars(game))
    pprint(vars(game.board))
    for piece in game.board.pieces:
        pprint(vars(piece))

    pieces = []
    for piece in game.board.pieces:
        if piece.captured:
            continue
        new_piece = Piece(
            position=piece.position,
            is_white=piece.player == 1,
            is_king=piece.king
        )
        pieces.append(new_piece)

    return pieces

async def get_game_from_id(id: str) -> Optional[Game]:
    game_state_db = await games.find_one({'_id': ObjectId(id)})
    print(game_state_db)
    if game_state_db is None:
        return None

    game = pickle.loads(game_state_db['pkl'])
    return game

async def update_game_state(id: str, game: Game):
    new_state = GameStateDb(
        pkl=Binary(pickle.dumps(game)),
        finished=game.is_over()
    )
    await games.replace_one({'_id': ObjectId(id)}, new_state.dict())

@app.get("/start", response_model=GameState)
async def start_game():
    result = await games.find_one({'finished': {'$ne': True}})
    if result is None:
        # create new game
        game = Game()
        game_state_db = GameStateDb(pkl=Binary(pickle.dumps(game)), finished=False)
        inserted = await games.insert_one(game_state_db.dict())
        possible = game.get_possible_moves()
        response = GameState(id=str(inserted.inserted_id), pieces=get_pieces(game), finished=False, you_white=True, whites_turn=game.whose_turn() == 1, possible_moves=possible)
        return response
    # return existing game
    else:
        id = result['_id']
        game: Game = pickle.loads(result['pkl'])
        finished = result['finished']
        you_white = False
        whites_turn = game.whose_turn() == 1
        possible = game.get_possible_moves()
        return GameState(id=str(id), pieces=get_pieces(game), finished=finished, you_white=you_white, whites_turn=whites_turn, possible_moves=possible)
        
@app.put("/move", response_model=GameState)
async def move(id: str, is_white: bool, from_field: int, to_field: int):
    game: Game = await get_game_from_id(id)
    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    if game.whose_turn() == 1 and not is_white or game.whose_turn() == 2 and is_white:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="It's not your turn")
    possible_moves = game.get_possible_moves()
    if [from_field, to_field] not in possible_moves:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Move is not possible")
    game.move([from_field, to_field])
    await update_game_state(id, game)
    #update possible moves
    possible_moves = game.get_possible_moves()

    return GameState(id=id, pieces=get_pieces(game), finished=game.is_over(), you_white=is_white, whites_turn=game.whose_turn() == 1, possible_moves=possible_moves)

@app.delete("/{id}")
async def delete_game(id: str):
    result = await games.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

@app.delete("/all")
async def delete_all_games():
    pass