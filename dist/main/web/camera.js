const createVideo = (id, width, height) => {
    const video = document.createElement("video");
    video.id = id;
    video.width = width;
    video.height = height;
    video.autoplay = true;
    video.controls = true;
    return video;
};

const createCanvas = (id, width, height) => {
    const canvas = document.createElement("canvas");
    canvas.id = id;
    canvas.width = width;
    canvas.height = height;
    canvas.style.borderRadius = "10px";
    canvas.style.borderStyle = "inset"
    return canvas;
};

const constraints = {
    audio: false,
    video: {
      facingMode: "user"
    }
};

const getCameraStream = video => {
    navigator.mediaDevices
      .getUserMedia(constraints)
      .then(function success(stream) {
        video.srcObject = stream;
      });
};

const getFrameFromVideo = (video, canvas) => {
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(video.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, video.width, video.height);
    ctx.restore();
    requestAnimationFrame(() => getFrameFromVideo(video, canvas));
};

const init = () => {
    const detectSightContainer = document.getElementById("detection_sight_container");

    const width = detectSightContainer.clientWidth - 1 - 50;
    const height = detectSightContainer.clientHeight - 1 - 50;

    const video = createVideo("vid", width, height);
    const canvas = createCanvas("canvas", video.width, video.height);

    getCameraStream(video);
    getFrameFromVideo(video, canvas);

    detectSightContainer.appendChild(canvas);
};
  
document.getElementById("detection_sight_container").onload = init();