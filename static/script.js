// Code for interaction
window.onload = function() {
    var dropdowns = document.getElementsByClassName('dropdown');
    for (var i = 0; i < dropdowns.length; i++) {
        dropdowns[i].addEventListener('mouseover', function() {
            this.children[1].style.display = 'block';
            this.children[1].style.opacity = '0';
            this.children[1].style.transition = 'opacity 0.5s';
            setTimeout(function() {
                this.children[1].style.opacity = '1';
            }.bind(this), 0);
        });
        dropdowns[i].addEventListener('mouseout', function() {
            this.children[1].style.opacity = '0';
            setTimeout(function() {
                if (this.children[1].style.opacity === '0') {
                    this.children[1].style.display = 'none';
                }
            }.bind(this), 500);
        });
    }

    // Get the modals
    var signInModal = document.getElementById('signInModal');
    var signUpModal = document.getElementById('signUpModal');

    // Get the buttons
    var signInButton = document.getElementById('signinButton');
    var signUpButton = document.getElementById('signupButton');

    // Get the <span> elements that close the modals
    var signInClose = signInModal.getElementsByClassName('close')[0];
    var signUpClose = signUpModal.getElementsByClassName('close')[0];

    // When the user clicks on the button, open the modal 
    signInButton.onclick = function() {
        signInModal.style.display = "block";
    }

    signUpButton.onclick = function() {
        signUpModal.style.display = "block";
    }

    // When the user clicks on <span> (x), close the modal
    signInClose.onclick = function() {
        signInModal.style.display = "none";
    }

    signUpClose.onclick = function() {
        signUpModal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == signInModal) {
            signInModal.style.display = "none";
        }
        if (event.target == signUpModal) {
            signUpModal.style.display = "none";
        }
    }

    // Add AJAX call to your sign in form
    document.querySelector('#signin-form').addEventListener('submit', function(e) {
        e.preventDefault();
        fetch('/signin', {
            method: 'POST',
            body: new URLSearchParams(new FormData(e.target)) // e.target is the form
        }).then(response => response.json())
        .then(data => {
            if (data.error) {
                // Show error message inside the modal
                document.querySelector('#signin-error-message').innerText = data.error;
            } else {
                // On success, redirect to the dashboard
                window.location.href = '/dashboard';
            }
        });
    });
};
