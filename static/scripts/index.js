function search(text){
    document.getElementById("res-div").innerHTML = "<center><h4 style='font-size:40px;'>Loading...</h4></center>"
    fetch(`searchq=${text}`, {
        method:"GET"
    }).then((res) => {
        return res.json()
    }).then((data) => {
        document.getElementById("res-div").innerHTML = ""
        if(data == '"song not found"'){
            document.getElementById("res-div").innerHTML = "<center><h4 style='font-size:40px;'>Song Not Found</h4></center>"
            return ""
        }
        for(let i=0;i<Object.keys(data).length;i++){

            let div = document.createElement("div")
            div.innerText = Object.keys(data)[i]
            // div.style.background = `url(${data[Object.keys(data)[i]]['img']})`
            let imgId = data[Object.keys(data)[i]]['img'].split("/")[4]
            div.className = "song-div"
            div.id = i
            document.getElementById("res-div").appendChild(div)
            let br = document.createElement("br")
            document.getElementById(i).appendChild(br)
            let br324 = document.createElement("br")
            document.getElementById(i).appendChild(br324)
            let br3241= document.createElement("br")
            document.getElementById(i).appendChild(br3241)
            let img = document.createElement("img")
            img.src = data[Object.keys(data)[i]]['img']
            img.onclick = () => {
                window.location.href = `song$$img=${imgId}$$name=${Object.keys(data)[i]}`
            }
            document.getElementById(i).appendChild(img)
            br = document.createElement("br")
            document.getElementById(i).appendChild(br)
            let br2 = document.createElement("br")
            document.getElementById(i).appendChild(br2)
        }

    })
}
function add_playlist(text, playlistName){
    document.getElementById("res-div").innerHTML = "<center><h4 style='font-size:40px;'>Loading...</h4></center>"
    fetch(`/searchq=${text}`, {
        method:"GET"
    }).then((res) => {
        return res.json()
    }).then((data) => {
        document.getElementById("res-div").innerHTML = ""
        if(data == '"song not found"'){
            document.getElementById("res-div").innerHTML = "<center><h4 style='font-size:40px;'>Song Not Found</h4></center>"
            return ""
        }
        for(let i=0;i<Object.keys(data).length;i++){

            let div = document.createElement("div")
            div.innerText = Object.keys(data)[i]
            // div.style.background = `url(${data[Object.keys(data)[i]]['img']})`
            let imgId = data[Object.keys(data)[i]]['img'].split("/")[4]
            div.className = "song-div"
            div.id = i
            document.getElementById("res-div").appendChild(div)
            let br = document.createElement("br")
            document.getElementById(i).appendChild(br)
            let br324 = document.createElement("br")
            document.getElementById(i).appendChild(br324)
            let br3241= document.createElement("br")
            document.getElementById(i).appendChild(br3241)
            let img = document.createElement("img")
            img.src = data[Object.keys(data)[i]]['img']
            img.onclick = () => {
                window.location.href = `/add$$img=${imgId}$$name=${Object.keys(data)[i]}$$playlist=${playlistName}`
            }
            document.getElementById(i).appendChild(img)
            br = document.createElement("br")
            document.getElementById(i).appendChild(br)
            let br2 = document.createElement("br")
            document.getElementById(i).appendChild(br2)

        }

    })
}

var paused = false
function changeVol(val){
    document.getElementById("audio").volume = val/100
    localStorage.setItem("vol", `${val/100}`)
    // document.getElementById("vol-text").innerText = `Volume: ${val/10}/10`
}

function playSong(){
    setTimeout(() => {
        maxChanger()
    }, 1000)
    paused = !paused
    if(paused){
        document.getElementById("audio").play()
        document.getElementById("album-art").className = "active"
        document.getElementById("player-track").className = "active"
        document.getElementById("btn-player").innerHTML = `<i class="fas fa-pause"></i>`
        return ""
    }else{
        document.getElementById("audio").pause()
        document.getElementById("player-track").className = ""
        document.getElementById("album-art").className = ""
        document.getElementById("btn-player").innerHTML = `<i class="fas fa-play"></i>`
        return ""
    }
}
function skiper(n) {
    try{
        var player = document.getElementById('audio');
        player.currentTime = n;
    }catch{
        
    }
  
  }
var looping = false
function looper(){
    looping = !looping
    if(looping){
        document.getElementById("loop-i").style.color = "#FF4C29"
    }else{
        document.getElementById("loop-i").style.color = ""
    }
    
}
function like(img, songName){
    formdata = new FormData()
    fetch(`/like$$songname=${songName}$$img=${img}`, {
        method:"POST",
        body:formdata
    })
    if(document.getElementById("like-btn").style.color == "rgb(255, 76, 41)"){
        document.getElementById("like-btn").style.color = ""
        return
    }else{
        document.getElementById("like-btn").style.color = "rgb(255, 76, 41)"
        return
    }
    
}

function getNext(){

    fetch("/next-song", {
        method:"GET"
    }).then((res) => {
        return res.json()
    }).then((data) => {
        window.location.href = data['main']
    })
}

window.addEventListener('keydown', function(e) {
    if(e.keyCode == 32 && e.target == document.body) {
        e.preventDefault();
    }
});

window.addEventListener("load", () => {
    let userVol = localStorage.getItem("vol")
    setInterval(() => {
        document.getElementById("slider-range").value = document.getElementById('audio').currentTime


        if(document.getElementById('audio').currentTime == document.getElementById('audio').duration){
            document.getElementById('audio').currentTime = "0"
            if(looping){
                document.getElementById('audio').play()
            }
            if(!looping){
                if(document.getElementById("isplaylist").innerText = "yes"){
                    nextSongPlaylist()
                }else{
                    getNext()
                }
                
                // TODO : Next song
            }
        }


    }, 300);


    if(userVol != null){
        changeVol(parseFloat(userVol) * 100)
        document.getElementById("vol-range").value = (userVol * 100).toString()
    }
    if(document.getElementById("isplaylist").innerText != "yes"){
        playSong()
    }
    setInterval(() => {
        if(document.getElementById("audio").paused == paused){
            playSong()
        }
    }, 30);
})

window.onkeydown = (e) => {
    e = e.key.toLowerCase()
    if(e == " " && document.activeElement.id != "search-text"){
        document.getElementById("btn-player").click()
    }if(e == "l"){
        document.getElementById("play-next").click()
    }if(e == "enter" && document.activeElement.id == "search-text"){
        document.getElementById("search-btn").click()
    }
}

function hide(id){
    document.getElementById(id).style.display = "none"
}
function show(id){
    document.getElementById(id).style.display = "block"
}

function changeClass(classN, id){
    document.getElementById(id).className = classN
}

function switcher(mode){
    if(mode == "home"){
        show("home")
        hide("search")
        hide("library")

        changeClass("active-a", "home-a")
        changeClass("", "search-a")
        changeClass("", "library-a")
    }
    if(mode == "search"){
        hide("home")
        show("search")
        hide("library")
        changeClass("", "home-a")
        changeClass("active-a", "search-a")
        changeClass("", "library-a")
    }
    if(mode == "library"){
        hide("home")
        hide("search")
        show("library")
        changeClass("", "home-a")
        changeClass("", "search-a")
        changeClass("active-a", "library-a")
    }
}
function ly(song, artist){
    fetch(`/get-ly$$artist=${artist}$$songname=${song}`, {
        method:"GET"
    }).then((res) => {
        return res.json()
    }).then((data) => {
        data = data['data']
        document.getElementById("lyrics-text").innerText = data
    })
}

function maxChanger(){
    document.getElementById("slider-range").max = `${Math.round(document.getElementById('audio').duration)}`
}

var currPlaylistPlaying = ""
function playSongPlaylist(songName, src, img){
    document.getElementById("album-name").innerText = songName
    document.getElementById("_1").src = `https://i.scdn.co/image/${img}`
    document.getElementById("audio").src = src
    setTimeout(() => {
        maxChanger()
    }, 1000)
    currPlaylistPlaying = songName

    document.getElementById("web-icon").href = `https://i.scdn.co/image/${img}`
    document.getElementsByTagName("title")[0].innerText = "Kaloka - " + songName.split("{")[0]
    playSong()
    if(paused == false){
        playSong()
    }

    ly(songName.split("{")[0], songName.split("{")[1].split(",")[0].replace("}", ""))
}
function nextSongPlaylist(){
    for(let i = 0;i<document.getElementsByClassName("hidden-h4").length;i++){
        if(document.getElementsByClassName("song-div")[i].innerText.split("\n")[0] == currPlaylistPlaying){
            try{
                document.getElementsByClassName("song-div")[i+1].getElementsByTagName("img")[0].click()
            }catch{
                document.getElementsByClassName("song-div")[0].getElementsByTagName("img")[0].click()
            }
            return
        }
    }
}