document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#multi-step-form");

    if (!form) {
        console.warn("⚠️ Form element not found. Check if `id="multi-step-form"` exists in your HTML.");
        return;
    }

    const steps = document.querySelectorAll(".form-step");
    let currentStep = 0;

    function showStep(stepIndex) {
        steps.forEach((step, index) => {
            step.style.display = index === stepIndex ? "block" : "none";
        });
    }

    function nextStep() {
        if (currentStep < steps.length - 1) {
            currentStep++;
            showStep(currentStep);
        }
    }

    function prevStep() {
        if (currentStep > 0) {
            currentStep--;
            showStep(currentStep);
        }
    }

    function safeAddEventListener(selector, event, handler) {
        const element = document.querySelector(selector);
        if (element) {
            element.addEventListener(event, handler);
        } else {
            console.warn(`⚠️ Element not found: ${selector}`);
        }
    }

    safeAddEventListener("#next-1", "click", nextStep);
    safeAddEventListener("#prev-2", "click", prevStep);
    safeAddEventListener("#next-2", "click", nextStep);
    safeAddEventListener("#prev-3", "click", prevStep);
    safeAddEventListener("#next-3", "click", nextStep);
    safeAddEventListener("#prev-4", "click", prevStep);
    safeAddEventListener("#next-4", "click", nextStep);
    safeAddEventListener("#prev-5", "click", prevStep);

    showStep(currentStep);

    // ✅ Remove "required" from hidden fields before form submission
    form.addEventListener("submit", function (event) {
        document.querySelectorAll("input[required], select[required]").forEach(field => {
            if (field.offsetParent === null) { // If the field is hidden
                field.removeAttribute("required");
            }
        });
    });

    // ✅ Validate Required Fields Before Submitting
    form.addEventListener("submit", function (event) {
        let isValid = true;
        let fields = this.querySelectorAll("[required]");

        fields.forEach(function (field) {
            if (!field.value.trim()) {
                field.classList.add("is-invalid");
                isValid = false;
            } else {
                field.classList.remove("is-invalid");
            }
        });

        if (!isValid) {
            event.preventDefault();
        }
    });
});
