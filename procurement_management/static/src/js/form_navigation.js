// static/src/js/form_navigation.js
// JavaScript for handling form step navigation
document.getElementById("next-1").onclick = function() {
    document.getElementById("step-1").style.display = "none";
    document.getElementById("step-2").style.display = "block";
};

document.getElementById("prev-2").onclick = function() {
    document.getElementById("step-2").style.display = "none";
    document.getElementById("step-1").style.display = "block";
};

document.getElementById("next-2").onclick = function() {
    document.getElementById("step-2").style.display = "none";
    document.getElementById("step-3").style.display = "block";
};

document.getElementById("prev-3").onclick = function() {
    document.getElementById("step-3").style.display = "none";
    document.getElementById("step-2").style.display = "block";
};

document.getElementById("next-3").onclick = function() {
    document.getElementById("step-3").style.display = "none";
    document.getElementById("step-4").style.display = "block";
};

document.getElementById("prev-4").onclick = function() {
    document.getElementById("step-4").style.display = "none";
    document.getElementById("step-3").style.display = "block";
};

document.getElementById("next-4").onclick = function() {
    document.getElementById("step-4").style.display = "none";
    document.getElementById("step-5").style.display = "block";
};

document.getElementById("prev-5").onclick = function() {
    document.getElementById("step-5").style.display = "none";
    document.getElementById("step-4").style.display = "block";
};