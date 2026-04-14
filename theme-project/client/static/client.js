const WS_URL = 'ws://localhost:8082/ws'

let ws = null;

const connectionStatusH2 = document.getElementById('connection-status');
const sendButton = document.getElementById('send-btn');
const messageArea = document.getElementById('message-area');
const sendMessage = document.getElementById('send-message');


function updateStatus(connected) {
    if (connected){
        connectionStatusH2.textContent = 'Соединение установлено!'
        sendButton.disabled = false
    } else {
        connectionStatusH2.textContent = 'Соединение не установлено!'
        sendButton.disabled = true
    }

}
function displayMessage(message) {
    messageArea.innerHTML = ''; 
    messageArea.textContent = message
}

function connectWebSocket() {
    try {
        ws = new WebSocket(WS_URL)
        ws.onopen = () => updateStatus(true)
        ws.onclose = () => updateStatus(false)
        ws.onmessage = (event) => displayMessage(event.data)
    } 
    catch (e) {
        console.log(e)
        updateStatus(false)
        setTimeout(()=>connectWebSocket(), 2000)
    }
}

function SendUniqueMessage() {
    messages = ['Классная тема!', 'Интересная тема!','Ты гений!']
    if (ws && ws.readyState === WebSocket.OPEN)
        message = messages[Math.floor(Math.random() * messages.length)]
        sendMessage.innerHTML = '';
        sendMessage.textContent = "Сообщение: " + message
        ws.send(message)

}


sendButton.addEventListener('click', SendUniqueMessage);

connectWebSocket();