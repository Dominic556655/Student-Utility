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



function downloadPDF() {
    const format = document.getElementById("timeFormat").value;
    window.location.href = `/download-timetable/?time_format=${format}`;
}


/* DELETE SINGLE ASSIGNMENT */

document.addEventListener("click", function (e) {

    if (e.target.classList.contains("delete-btn")) {

        const id = e.target.dataset.id;

        if (!id) {
            console.error("Missing timetable ID");
            return;
        }

        if (!confirm("Delete this timetable entry?")) return;

        fetch(`/delete-timetable/${id}/`, {
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
                alert(data.error || "Delete failed");
            }

        })
        .catch(err => console.error(err));
    }

});

/* CLEAR ALL HISTORY */

function clearTimeTable() {

    if (!confirm("Delete ALL timetable entries?")) return;

    fetch("/delete-all-timetable/", {
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
            alert(data.error || "Delete failed");
        }

    })
    .catch(err => console.error(err));
}