document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("current").addEventListener("click", function () {
        document.getElementById("active-projects").style.display = 'flex';
        document.getElementById("active-projects").style.flexDirection = 'column'
        document.getElementById("project-search-container").style.display = 'none';
        document.getElementById("on-going-container").style.display = 'none';
    });

    document.getElementById("find").addEventListener("click", function () {
        document.getElementById("active-projects").style.display = 'none';
        document.getElementById("on-going-container").style.display = 'none';
        document.getElementById("project-search-container").style.display = 'flex';
        document.getElementById("project-search-container").style.flexDirection = 'column';
        document.getElementById("project-search-container").style.visibility = 'visible';
    });

    document.getElementById("on-going").addEventListener("click", function () {
        document.getElementById("active-projects").style.display = 'none';
        document.getElementById("project-search-container").style.display = 'none';
        document.getElementById("on-going-container").style.display = 'flex';
        document.getElementById("on-going-container").style.flexDirection = 'column';
        document.getElementById("on-going-container").style.visibility = 'visible';
    });

    document.querySelectorAll(".view-btn").forEach(button => {
        button.addEventListener("click", function () {
            document.getElementById("popup").style.display = 'flex';
        });
    });

    document.querySelectorAll(".list-dropdown-btn").forEach(button => {
        button.addEventListener("click", function (e) {
            e.stopPropagation(); // prevents event bubbling
            const card = button.closest(".project-list-card");
            const dropdown = card.querySelector(".list-card-dropdown");

            if (dropdown) {
                dropdown.style.display = dropdown.style.display === "flex" ? "none" : "flex";
            }
        });
    });  

    document.querySelectorAll(".project-list-card").forEach(card => {
        card.addEventListener("click", function (e) {
            e.stopPropagation(); // prevents event bubbling
            const dropdown = card.querySelector(".list-card-dropdown");

            if (dropdown) {
                dropdown.style.display = dropdown.style.display === "flex" ? "none" : "flex";
            }
        });
    });  

    // document.querySelector(".bgOverlay").addEventListener("click", function () {
    //     document.getElementById("popup").style.display = 'none';
    // });

    // document.getElementById("popup-close").addEventListener("click", function () {
    //     document.getElementById("popup").style.display = 'none';
    // });

    async function projectSearch() {
        console.log("searching");
        const searchPage = document.getElementById("project-search-container");
        if(searchPage.style.display == 'flex') {
            const searchInput = document.getElementById("search-text").value.toLowerCase();
            console.log(searchInput);
            const projectList = document.querySelectorAll(".project-card");
            projectList.forEach(project => {
                const projectName = project.querySelector(".project-name").textContent.toLowerCase();
                if(projectName.includes(searchInput)) {
                    console.log(projectName);
                    project.style.display = 'flex';
                } else {
                    project.style.display = 'none';
                }
            });
        }
    }

    document.getElementById("search").addEventListener("click", projectSearch);
    document.getElementById("search-text").addEventListener("input", projectSearch);
    document.getElementById("search-bar").addEventListener("keyup", function(event) {
        if(event.key === "Enter") {
            projectSearch();
        }
    });
    document.getElementById("search-bar").addEventListener("input", function() {
        if(this.value === "") {
            document.querySelectorAll(".project-info").forEach(project => {
                project.style.display = 'flex';
            });
        }
    });

});
