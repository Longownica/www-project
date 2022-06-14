API_URL = "http://localhost:8000/"
GAME_ID = null
PIECES = []

function update_state(state) {
    $("#moves").text(JSON.stringify(state.possible_moves))
    $("#you").text(state.you_white ? "white" : "black")
    $("#turn").text(state.turn ? "white" : "black")
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
        }
        else {
            $("#x" + i).removeClass("white_checker");
            $("#x" + i).removeClass("black_checker");
        }
    }
}

function move() {
    var xhr = new XMLHttpRequest();
    var url = API_URL + "move"
    xhr.open("PUT?", url, false);
    xhr.send(null)
    response = JSON.parse(xhr.responseText)
    console.log(response)
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

}

function delete_all() {

}