(function() {
    var toggle = document.querySelector('.nav-toggle');
    var navLinks = document.getElementById('navLinks');
    if (toggle && navLinks) {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            navLinks.classList.toggle('active');
        });
    }
})();
