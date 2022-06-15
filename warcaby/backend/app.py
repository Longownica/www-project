import os
import pickle
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
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    #for piece in game.board.pieces:
    #    pprint(vars(piece))

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

def game_state_from_game(id: str, is_white:bool, game: Game) -> GameState:
    return GameState(
        id=id,
        pieces=get_pieces(game),
        finished=game.is_over(),
        you_white=is_white,
        whites_turn=game.board.player_turn == 1,
        possible_moves=game.board.get_possible_moves()
    )

@app.get("/start", response_model=GameState)
async def start_game():
    result = await games.find_one({'finished': {'$ne': True}})
    if result is None:
        # create new game
        game = Game()
        game_state_db = GameStateDb(pkl=Binary(pickle.dumps(game)), finished=False)
        inserted = await games.insert_one(game_state_db.dict())
        return game_state_from_game(str(inserted.inserted_id), True, game)
    # return existing game
    else:
        id = result['_id']
        game: Game = pickle.loads(result['pkl'])
        is_white = False
        return game_state_from_game(str(id), is_white, game)
        
@app.get("/{id}", response_model=GameState)
async def get_game(id: str, is_white: bool):
    game = await get_game_from_id(id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_state_from_game(id, is_white, game)

@app.put("/{id}/move", response_model=GameState)
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

    return game_state_from_game(id, is_white, game)

@app.delete("/all")
async def delete_all_games():
    pprint(dir(games))
    games.drop()
    pass

@app.delete("/{id}")
async def delete_game(id: str):
    result = await games.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

