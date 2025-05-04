let offset = 0;
const limit = 5;

// Web Speech API for STT
let recognition;
function recordSpeech() {
  const status = document.getElementById("recordingStatus");
  if (!("webkitSpeechRecognition" in window)) {
    alert("Web Speech API not supported!");
    return;
  }
  recognition = new webkitSpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = "en-US";

  recognition.onstart = () => (status.innerText = "🎙 Listening...");
  recognition.onend = () => (status.innerText = "✅ Done Recording!");
  recognition.onerror = () => (status.innerText = "❌ Mic Error!");

  recognition.onresult = function (event) {
    const transcript = event.results[0][0].transcript;
    document.getElementById("voice-output").innerText =
      "You said: " + transcript;
    document.getElementById("ingredients").value = transcript;
  };
  recognition.start();
}

function searchRecipes(reset = true) {
  if (reset) {
    offset = 0;
    document.getElementById("results").innerHTML = "";
  }

  const ingredients = document
    .getElementById("ingredients")
    .value.split(",")
    .map((i) => i.trim());
  const cuisine = document.getElementById("cuisineFilter").value;
  const course = document.getElementById("courseFilter").value;
  const diet = document.getElementById("dietFilter").value;
  const prep_time = document.getElementById("prepTimeFilter").value;

  if (ingredients.length === 1 && ingredients[0] === "") {
    alert("Please enter at least one ingredient.");
    return;
  }

  fetch("https://tastemate-o2wx.onrender.com/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ingredients,
      cuisine,
      course,
      diet,
      prep_time,
      offset,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      const resultsDiv = document.getElementById("results");
      if (data.error) {
        resultsDiv.innerHTML = `<p class="text-red-500">${data.error}</p>`;
        return;
      }
      data.forEach((recipe) => {
        const recipeDiv = document.createElement("div");
        recipeDiv.classList.add(
          "recipe",
          "border",
          "p-4",
          "rounded-md",
          "shadow-md",
          "bg-white",
          "mt-4",
          "text-left",
          "max-w-2xl",
          "mx-auto"
        );
        recipeDiv.innerHTML = `
                <img src="${
                  recipe.image_url
                }" alt="Recipe Image" class="w-[400px] h-[280px] object-cover rounded-xl shadow-lg mb-4">
                <h3 class="text-2xl font-bold text-green-700 text-center">${
                  recipe.name
                }</h3>
                <p><strong>Cuisine:</strong> ${recipe.cuisine || "N/A"}</p>
                <p><strong>Course:</strong> ${recipe.course || "N/A"}</p>
                <p><strong>Diet:</strong> ${recipe.diet || "N/A"}</p>
                <p><strong>Prep Time:</strong> ${
                  recipe.prep_time || "N/A"
                } mins</p>
                <p><strong>Description:</strong> ${
                  recipe.description || "N/A"
                }</p>
                <p><strong>Ingredients:</strong> ${
                  Array.isArray(recipe.ingredients)
                    ? recipe.ingredients.join(", ")
                    : recipe.ingredients
                }</p>
                <p><strong>Instructions:</strong> ${recipe.instructions}</p>
            `;
        resultsDiv.appendChild(recipeDiv);
      });
      offset += limit;
      document.getElementById("exploreMore").classList.remove("hidden");
    });
}

// Image detection
function uploadImage(event) {
  event.preventDefault();
  const formData = new FormData();
  const imageFile = document.getElementById("imageInput").files[0];

  if (!imageFile) {
    alert("Please select an image!");
    return;
  }

  formData.append("image", imageFile);

  fetch("http://127.0.0.1:5000/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      // Extract "foodName" from response
      const foodNames = data.foodName || [];

      if (foodNames.length === 0) {
        document.getElementById("ingredients").value = "No food detected.";
      } else {
        document.getElementById("ingredients").value = foodNames.join(", ");
      }
    })
    .catch((error) => console.error("Error:", error));
}

function handleDragOver(event) {
  event.preventDefault();
  event.dataTransfer.dropEffect = 'copy';
}

function handleDrop(event) {
  event.preventDefault();
  const file = event.dataTransfer.files[0];
  if (file) {
    document.getElementById('imageInput').files = event.dataTransfer.files;
    previewImage({ target: { files: event.dataTransfer.files } });
  }
}

function previewImage(event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      document.getElementById('dropZone').style.backgroundImage = `url(${e.target.result})`;
      document.getElementById('dropZone').style.backgroundSize = 'cover';
      document.getElementById('dropZone').style.backgroundPosition = 'center';
    };
    reader.readAsDataURL(file);
  }
}

function openCamera() {
  const video = document.getElementById('cameraPreview');
  navigator.mediaDevices.getUserMedia({ video: true })
    .then((stream) => {
      video.srcObject = stream;
      video.classList.remove('hidden');
      video.play();
      const captureButton = document.createElement('button');
      captureButton.innerText = 'Capture Photo';
      captureButton.className = 'bg-red-600 text-white font-semibold py-2 px-4 rounded-lg mt-2';
      captureButton.onclick = capturePhoto;
      document.querySelector('.flex-col').appendChild(captureButton);
    })
    .catch((error) => console.error('Camera access denied', error));
}

function capturePhoto() {
  const video = document.getElementById('cameraPreview');
  const canvas = document.getElementById('capturedCanvas');
  const context = canvas.getContext('2d');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  video.srcObject.getTracks().forEach(track => track.stop());
  video.classList.add('hidden');
  canvas.classList.remove('hidden');
  canvas.toBlob((blob) => {
    const file = new File([blob], 'captured-image.png', { type: 'image/png' });
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    document.getElementById('imageInput').files = dataTransfer.files;
    previewImage({ target: { files: dataTransfer.files } });
  });
}

// async function scrapeRes(e) {
//   e.preventDefault(); // stop form from reloading page

//   const ingredients = document.querySelector('ingredients').value;
//   const formData = new FormData();
//   formData.append('ingredients', ingredients);

//   try {
//     const response = await fetch('/recipes', {
//       method: 'POST',
//       body: formData
//     });

//     if (!response.ok) throw new Error('Fetch error');

//     const html = await response.text();
//     document.querySelector('scrappedResults').innerHTML = html;

//   } catch (err) {
//     document.querySelector('scrappedResults').innerHTML = "<p>❌ Failed to fetch recipes</p>";
//     console.error(err);
//   }
// }
