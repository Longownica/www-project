API_URL = "http://localhost:8000/"
GAME_ID = null
IS_WHITE = null
WHITES_TURN = null
FINISHED = false
PIECES = []
FROM = null
TO = null

EMPTY_STATE = {
    id: null,
    you_white: null,
    whites_turn: null,
    pieces: [],
    possible_moves: [],
    finished: false
}

function update_state(state) {
    $("#moves").text(JSON.stringify(state.possible_moves))
    $("#you").text(state.you_white ? "white" : "black")
    $("#turn").text(state.whites_turn ? "white" : "black")
    $("#finished").text(state.finished ? "true" : "false")
    for (var i = 1; i <= 32; i++) {
        piece = state.pieces.find((p) => p.position == i)

        if(piece) {
            if (piece.is_white) {
                $("#x" + i).removeClass("black_checker");
                $("#x" + i).addClass("white_checker");
            }
            else {
                $("#x" + i).removeClass("white_checker");
                $("#x" + i).addClass("black_checker");
            }
            if(piece.is_king) {
                $("#x" + i).addClass("king");
            }
        }
        else {
            $("#x" + i).removeClass("white_checker");
            $("#x" + i).removeClass("black_checker");
            $("#x" + i).removeClass("king");

        }
    }
    GAME_ID = state.id
    IS_WHITE = state.you_white
    WHITES_TURN = state.whites_turn
    PIECES = state.pieces
    FINISHED = false
}

function handle_click(id_str) {
    var id = Number(id_str.substring(1));
    if(FROM === null) {
        FROM = id;
    }
    else {
        TO = id;
        try {
            move()
        } catch {

        }
        FROM = null
        TO = null
    }
    $("#from").text(FROM)
    $("#to").text(TO)
}

function move() {
    var xhr = new XMLHttpRequest();
    var url = API_URL + `${GAME_ID}/move?is_white=${IS_WHITE}&from_field=${FROM}&to_field=${TO}`
    xhr.open("PUT", url, false);
    xhr.send(null)
    if(xhr.status != 200) {
        $("#error-msg").text(xhr.responseText)
        return
    }
    response = JSON.parse(xhr.responseText)
    console.log(response)
    update_state(response)
}

function start() {
    var xhr = new XMLHttpRequest();
    var url = API_URL + "start"
    xhr.open("GET", url, false);
    xhr.send(null)
    response = JSON.parse(xhr.responseText)
    console.log(response)
    update_state(response)
}

function delete_game() {
    var xhr = new XMLHttpRequest();
    var url = API_URL + `${GAME_ID}`
    xhr.open("DELETE", url, false);
    xhr.send(null)
    update_state(EMPTY_STATE)
}

function delete_all() {
    var xhr = new XMLHttpRequest();
    var url = API_URL + 'all'
    xhr.open("DELETE", url, false);
    xhr.send(null)
    update_state(EMPTY_STATE)
}

function refresh() {
    if (GAME_ID === null) {
        return
    }
    var xhr = new XMLHttpRequest();
    var url = API_URL + `${GAME_ID}?is_white=${IS_WHITE}`
    xhr.open("GET", url, false);
    xhr.send(null)
    response = JSON.parse(xhr.responseText)
    console.log(response)
    update_state(response)
}

setInterval(refresh, 1000)