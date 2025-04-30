document.addEventListener("DOMContentLoaded", function () {
    function setTagline() {
        const tagline = document.getElementById("tagline");
        var taglineText = "";
        const user = "freelancer"; //get user type
        if (user === "employer") {
            taglineText = "From Project to Pay—Made Seamless.";
        } else if (user === "freelancer") {
            taglineText = "Payments Made Easy, So You Can Focus on Work."
        } else {
            taglineText = "Monitor Payments, Ensure Transparency."
        }
        let index = 0;

        function type() {
            if (index < taglineText.length) {
                tagline.innerHTML += taglineText.charAt(index);
                index++;
                setTimeout( type, 100);
            }
        }
        type();
    }
    setTagline();
    function paymentbtn() {
        const paymentbtn = document.getElementById("payment-btn");
        var btntext = "";
        const user = "XXXXXXXXXX"; //get user type
        if (user === "employer") {
            btntext = "Send Payment";
        } else if (user === "freelancer") {
            btntext = "Request Payment"
        } 
        paymentbtn.innerHTML = btntext;
    }
    // paymentbtn();

    document.querySelectorAll(".payment-btn").forEach(button => {
        button.addEventListener("click", function () {
            document.getElementById("popup").style.display = 'flex';
        });
    });

    document.querySelector(".bgOverlay").addEventListener("click", function () {
        document.getElementById("popup").style.display = 'none';
    });

    document.getElementById("popup-close").addEventListener("click", function () {
        document.getElementById("popup").style.display = 'none';
    });
})
