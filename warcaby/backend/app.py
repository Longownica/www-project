import os
import pickle
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

class GameState(BaseModel):
    id: str
    board: List[int]
    finished: bool
    you_white: bool
    whites_turn: bool

class GameStateDb(BaseModel):
    pkl: Binary
    finished: bool


def get_board_state(Game) -> List[int]:
    return []

def get_game_from_id(id: str) -> Optional[Game]:
    game_state_db = games.find_one({'_id': ObjectId(id)})
    if game_state_db is None:
        game = pickle.loads(game_state_db['pickle'])
        return game

def update_game_state(id: str, game: Game):
    new_state = GameStateDb(
        pkl=Binary(pickle.dumps(game)),
        finished=game.is_over()
    )
    games.replace_one({'_id': ObjectId(id)}, new_state)

@app.get("/start", response_model=GameState)
async def start_game():
    result = await games.find_one({'finished': {'$ne': True}})
    if result is None:
        # create new game
        game = Game()
        game_state_db = GameStateDb(pkl=Binary(pickle.dumps(game)), finished=False)
        inserted = await games.insert_one(game_state_db.dict())
        response = GameState(id=str(inserted.inserted_id), board=get_board_state(game), finished=False, you_white=True, whites_turn=game.whose_turn() == 1)
        return response
    # return existing game
    else:
        id = result['_id']
        game = pickle.loads(result['pkl'])
        finished = result['finished']
        you_white = False
        whites_turn = game.whose_turn() == 1
        return GameState(id=str(id), board=get_board_state(game), finished=finished, you_white=you_white, whites_turn=whites_turn)
        
@app.put("/move", response_model=GameState)
async def move(id: str, is_white: bool, from_field: str, to_field: str):
    game: Game = get_game_from_id(id)
    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    if game.whose_turn() == 1 and not is_white or game.whose_turn() == 2 and is_white:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="It's not your turn")
    possible_moves = game.get_possible_moves()
    if [from_field, to_field] not in possible_moves:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Move is not possible")
    game.move([from_field, to_field])
    update_game_state(id, game)
    return GameState(id=id, board=get_board_state(game), finished=game.is_over(), you_white=is_white, whites_turn=game.whose_turn() == 1)

