// Code related to Three.js
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
var renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

var geometry = new THREE.BoxGeometry();
var material = new THREE.MeshBasicMaterial({color: 0x00ff00});
var cube = new THREE.Mesh(geometry, material);
scene.add(cube);

camera.position.z = 5;

function animate() {
    requestAnimationFrame(animate);
    cube.rotation.x += 0.01;
    cube.rotation.y += 0.01;
    renderer.render(scene, camera);
}
animate();

// Code for interaction
window.onload = function() {
    // Existing code...

    var signInButton = document.getElementById('signinButton');
    var signUpButton = document.getElementById('signupButton');
    var signInModal = document.getElementById('signInModal');
    var signUpModal = document.getElementById('signUpModal');
    var signInClose = signInModal.getElementsByClassName('close')[0];
    var signUpClose = signUpModal.getElementsByClassName('close')[0];
    var signInForm = signInModal.getElementsByTagName('form')[0];
    var messageElement = document.getElementById('signInMessage');
    var loginStatus = document.getElementById('loginStatus');
    // When the user clicks on the button, open the modal 
    // Existing code...
    
    signInButton.onclick = function() {
        signInModal.style.display = "block";
    }

    signInClose.onclick = function() {
        signInModal.style.display = "none";
    }

// This adds an event listener for form submission
// This adds an event listener for form submission
signInForm.addEventListener('submit', function(event) {
    event.preventDefault();

    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/login', true);

    xhr.onload = function() {
        if (this.status == 200) {
            var response = JSON.parse(this.responseText);
        
            console.log(response); // Add this line to print the response to the console

            if (response.success) {
                loginStatus.innerText = 'Logged in as ' + response.username;  // Update loginStatus
                signInModal.style.display = "none";
                // Handle successful login here
            } else {
                loginStatus.innerText = 'Login failed';  // Update loginStatus
                // Handle failed login here
            }
        } else {
            console.log("Request failed with status: " + this.status);
        }
    };

    xhr.onerror = function() {
        console.log("Request error");
    };

    var formData = new FormData(signInForm);
    xhr.send(formData);
});

}