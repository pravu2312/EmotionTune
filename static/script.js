// script.js
const video = document.getElementById("video");
const emotionSpan = document.getElementById("emotion");
const musicLink = document.getElementById("music_link");

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => console.error("Error accessing webcam:", err));

function captureImage() {
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    const imageData = canvas.toDataURL("image/jpeg");

    fetch("/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: imageData })
    })
    .then(response => response.json())
    .then(data => {
        emotionSpan.textContent = data.emotion;
        musicLink.href = data.music_url;
        musicLink.textContent = `Listen to song for ${data.emotion}`;
    })
    .catch(err => console.error("Error:", err));
}
