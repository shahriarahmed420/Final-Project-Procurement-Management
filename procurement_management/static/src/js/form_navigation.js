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

document.getElementById("supplier-form").addEventListener("submit", function(event) {
    let isValid = true;
    let fields = this.querySelectorAll("[required]");

    fields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add("is-invalid"); // Add Bootstrap invalid style
            isValid = false;
        } else {
            field.classList.remove("is-invalid"); // Remove error style if corrected
        }
    });

    if (!isValid) {
        event.preventDefault(); // Prevent form submission if validation fails
    }
});

document.getElementById("pdfUpload").addEventListener("change", function() {
        var file = this.files[0];
        if (file) {
            var allowedTypes = ["application/pdf"];
            if (!allowedTypes.includes(file.type)) {
                alert("Only PDF files are allowed!");
                this.value = ""; // Clear the file input
            }
        }
});