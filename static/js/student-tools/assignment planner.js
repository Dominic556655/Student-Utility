function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


document.addEventListener("DOMContentLoaded", function () {

    // STATUS UPDATE
    document.querySelectorAll(".status-update").forEach(select => {

        select.addEventListener("change", function () {

            const id = this.dataset.id;
            const status = this.value;

            fetch(`/update-status/${id}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: `status=${status}`
            })
            .then(res => res.json())
            .then(data => {

                if (data.success) {
                    console.log("Updated:", data.status);
                }

            });

        });

    });

});


/* EDIT ASSIGNMENT */
document.querySelectorAll(".edit-btn")
.forEach(button => {

    button.addEventListener("click", function () {

        const id = this.dataset.id;

        // fill form
        document.getElementById("edit-title")
            .value = this.dataset.title;

        document.getElementById("edit-course")
            .value = this.dataset.course;

        document.getElementById("edit-category")
            .value = this.dataset.category;

        document.getElementById("edit-priority")
            .value = this.dataset.priority;

        document.getElementById("edit-status")
            .value = this.dataset.status;

        document.getElementById("edit-progress")
            .value = this.dataset.progress;

        document.getElementById("edit-date")
            .value = this.dataset.date;

        // IMPORTANT: update form action
        document.getElementById("editForm")
            .action = `/edit-assignment/${id}/`;
    });

});


/* SEARCH + FILTER */

const searchInput =
document.getElementById("searchAssignment");

const statusFilter =
document.getElementById("statusFilter");

const priorityFilter =
document.getElementById("priorityFilter");

function filterAssignments() {

    const search =
        searchInput.value.toLowerCase();

    const status =
        statusFilter.value;

    const priority =
        priorityFilter.value;

    const rows =
        document.querySelectorAll("tbody tr");

    rows.forEach(row => {

        const title =
            row.dataset.title || "";

        const course =
            row.dataset.course || "";

        const rowStatus =
            row.dataset.status || "";

        const rowPriority =
            row.dataset.priority || "";

        const matchSearch =
            title.includes(search) ||
            course.includes(search);

        const matchStatus =
            !status || rowStatus === status;

        const matchPriority =
            !priority || rowPriority === priority;

        if (
            matchSearch &&
            matchStatus &&
            matchPriority
        ) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }

    });

}

searchInput.addEventListener(
    "keyup",
    filterAssignments
);

statusFilter.addEventListener(
    "change",
    filterAssignments
);

priorityFilter.addEventListener(
    "change",
    filterAssignments
);

/* DELETE SINGLE ASSIGNMENT */

document.querySelectorAll(".delete-btn")
.forEach(button => {

    button.addEventListener("click", function () {

        const id = this.dataset.id;

        if (!confirm("Delete this assignment?")) return;

        fetch(`/delete-assignment/${id}/`, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            }
        })
        .then(res => res.json())
        .then(data => {

            if (data.success) {
                location.reload();
            } else {
                alert("Delete failed");
            }

        })
        .catch(err => {
            console.error(err);
        });

    });

});

/* CLEAR ALL HISTORY */
function clearAssignmentHistory() {

    if (!confirm("Delete all assignments?")) return;

    fetch("/delete-all-assignments/", {
        method: "POST",
        credentials: "same-origin",  // 🔥 IMPORTANT FIX
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({})
    })
    .then(res => res.json())
    .then(data => {

        console.log("SERVER RESPONSE:", data);

        if (data.success) {
            location.reload();
        } else {
            alert("Delete failed");
        }

    })
    .catch(err => {
        console.error("ERROR:", err);
    });
}