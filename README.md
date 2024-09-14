## urls :
**for connect to chat**
*ws://127.0.0.1/ws/chat/{room_name}/*     

**for receive notifications**
*ws://127.0.0.1/ws/chat/listener/*

example of what you reveive from notification :
```javascript
{members_list:  ['username1', 'username2']
message: 
{__str__: 'username1', content: 'this is message', timestamp: '2024-03-09T13:04:33253530Z'}
roomName: "3212156deb2d49d698f8acdca5ba7900"
type: "chat_message"}
```

 

## examples :
*connect to a chatroom* :

```javascript
   const roomName = JSON.parse(document.getElementById('room-name').textContent);
    let username = {{ username }}
    document.getElementById("demo").innerHTML = username
    const chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/chat/'
        + roomName
        + '/'
    );
     chatSocket.onmessage = function (e) {
            const data = JSON.parse(e.data);

            if (data["command"] == "fetch_message") {
                for (let i = data["message"].length - 1; i >= 0; i--) {
                    document.querySelector('#chat-log').value += (data["message"][i]["content"] + '\n');
                }
            } else if (data["command"] == "new_message") {
                document.querySelector('#chat-log').value += (data["message"]["content"] + '\n');

            }

        };
      // this function is used for fetch previos messages 
        chatSocket.onopen = function (e) {
            chatSocket.send(JSON.stringify({
                'command': "fetch_message",
                'roomName': roomName
            }));
        }


        chatSocket.onclose = function (e) {
            console.error('Chat socket closed unexpectedly');
        };
```




example of what you revive from fech message :
```javascript
command: "fetch_message"
message: : 
{__str__: 'fff', content: 'dd', timestamp: '2024-03-09T13:04:33253530Z'} 
{__str__: 'fff', content: 'dddd', timestamp: '2024-03-06T07:32:13804463Z'} 
{__str__: 'zahra', content: 'ssss', timestamp: '2024-03-06T07:32:00252499Z'} 
{__str__: 'fff', content: 'ss', timestamp: '2024-03-06T07:19:23064145Z'}
```




*send message*

```javascript
 document.querySelector('#chat-message-submit').onclick = function (e) {
            const messageInputDom = document.querySelector('#chat-message-input');
            const message = messageInputDom.value;
            chatSocket.send(JSON.stringify({
                'content': message,
                'command': "new_message",
                'username': username,
                'roomName': roomName
            }));

            messageInputDom.value = '';
        };
```



tips
* --str-- is sender  
* you can fetch username and roomName from https://127.0.0.1/chat/api/join/(car id)
this is example of what you receive from above api

    ```javascript
    {
    "success": true,
    "roomName": [
        "3212156deb2d49d698f8acdca5ba7900"
    ],
    "username": "username1",
    "profile": {
        "id": 1,
        "email": "example@gmail.com",
        "picture": "https://s3.ir-tbz-sh1.arvanstorage.ir/django-car-ads/images/default.jpeg?AWSAccessKeyId=b9189c7f-1727-4604-ba04-71d2a053857d&Signature=%2FumxRNppd01uu9%2BLxastjgiiu8A%3D&Expires=1710004756",
        "city": "اصقهان",
        "first_name": "امیر",
        "last_name": "رنجبر",
        "gender": "مرد",
        "user": 2
    }
    }
    ```



*receive notifications*
```javascript
  const chatSocket2 = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/chat/'
        + 'listener'
        + '/'
    );

    chatSocket2.onmessage = function (e) {
        var data = JSON.parse(e.data)
        for (let i = data['members_list'].length - 1; i >= 0; i--) {
            if (data['members_list'][i] == username) {
                if (data['username'] != username) {
                    if (data['roomName'] != roomName) {
                        if (!("Notification" in window)) {
                            alert("This browser does not support desktop notification");
                        }
                        // Let's check whether notification permissions have already been granted
                        else if (Notification.permission === "granted") {
                            // If it's okay let's create a notification
                            var notification = new Notification(data['username'] + " : " + data['content']);
                        }
                        // Otherwise, we need to ask the user for permission
                        else if (Notification.permission !== "denied") {
                            Notification.requestPermission().then(function (permission) {
                                // If the user accepts, let's create a notification
                                if (permission === "granted") {
                                    var Notification = new Notification("Hi there!");
                                }
                            });
                        }
                    }
                }
            }
        }
        }
```