API_URL = "http://localhost:8000/"
GAME_ID = null
PIECES = []

function update_state(state) {

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
    
}

function delete_game() {

}

function delete_all() {

}