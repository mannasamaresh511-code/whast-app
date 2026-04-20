// Toggle between Login and Signup on the index page
function toggleForm() {
    const title = document.getElementById('form-title');
    const actionInput = document.getElementById('action-type');
    const submitBtn = document.getElementById('submit-btn');
    const toggleText = document.querySelector('p');

    if (actionInput.value === 'login') {
        title.innerText = 'Sign Up';
        actionInput.value = 'signup';
        submitBtn.innerText = 'Create Account';
        toggleText.innerText = 'Already have an account? Login';
    } else {
        title.innerText = 'Login';
        actionInput.value = 'login';
        submitBtn.innerText = 'Login';
        toggleText.innerText = 'Need an account? Sign up';
    }
}

// Auto-scroll chat box to the bottom
window.onload = function() {
    const chatBox = document.getElementById('chat-box');
    if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}