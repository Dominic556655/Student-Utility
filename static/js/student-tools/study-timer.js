const completeSound = new Audio("/static/sounds/Alert-sound.mp3");

let timer = null;
let seconds = 1500;
let endTime = null;
let hasCompleted = false;

// =========================
// LOCAL STORAGE KEYS
// =========================
const END_TIME_KEY = "studyTimerEndTime";
const SAVED_KEY = "studyTimerSaved";

// Elements
const display = document.getElementById("timerDisplay");
const durationSelect = document.getElementById("duration");

// =========================
// 🔔 REQUEST NOTIFICATION PERMISSION (ADDED)
// =========================
if ("Notification" in window && Notification.permission !== "granted") {
    Notification.requestPermission();
}

// =========================
// 🔔 DESKTOP NOTIFICATION FUNCTION (ADDED)
// =========================
function sendNotification() {
    if ("Notification" in window && Notification.permission === "granted") {
        new Notification("🎉 Study Session Completed", {
            body: "Great job! Your session has been saved successfully.",
            icon: "/static/img/image_2.jpg"
        });
    }
}

// =========================
// UPDATE DISPLAY
// =========================
function updateDisplay() {
    let mins = Math.floor(seconds / 60);
    let secs = seconds % 60;

    display.textContent = `${mins}:${secs.toString().padStart(2, "0")}`;
}

// =========================
// SET TIMER FROM DROPDOWN
// =========================
function setDuration() {
    clearInterval(timer);
    seconds = parseInt(durationSelect.value) * 60;
    updateDisplay();
}

// =========================
// START TIMER
// =========================
document.getElementById("startBtn").addEventListener("click", () => {

    clearInterval(timer);

    hasCompleted = false;

    localStorage.setItem(SAVED_KEY, "false");

    // Set the finish time
    endTime = Date.now() + (seconds * 1000);

    // Save it
    localStorage.setItem(END_TIME_KEY, endTime);

    timer = setInterval(updateTimer, 1000);

    updateTimer();
});


// =========================
// UPDATE TIMER
// =========================

function updateTimer() {

    const remaining = Math.max(
        0,
        Math.floor((endTime - Date.now()) / 1000)
    );

    seconds = remaining;

    updateDisplay();

    if (remaining === 0) {

    clearInterval(timer);

    if (!hasCompleted &&
        localStorage.getItem(SAVED_KEY) !== "true") {

        hasCompleted = true;

        localStorage.setItem(SAVED_KEY, "true");

        localStorage.removeItem(END_TIME_KEY);

        completeSound.play().catch(()=>{});

        navigator.vibrate?.(200);

        showToast("🎉 Study Session Completed!");

        sendNotification();

        saveSession();
    }
}
}

// =========================
// PAUSE TIMER
// =========================
document.getElementById("pauseBtn").addEventListener("click", () => {

    clearInterval(timer);

    // Save remaining seconds
    seconds = Math.max(
        0,
        Math.floor((endTime - Date.now()) / 1000)
    );

    localStorage.setItem(END_TIME_KEY, endTime);

});

// =========================
// RESET TIMER
// =========================
document.getElementById("resetBtn").addEventListener("click", () => {

    clearInterval(timer);

    endTime = null;

    seconds = parseInt(durationSelect.value) * 60;

    updateDisplay();

    localStorage.removeItem(END_TIME_KEY);
    localStorage.removeItem(SAVED_KEY);

});

// =========================
// CHANGE DURATION
// =========================
durationSelect.addEventListener("change", setDuration);


// =========================
// SAVE SESSION (WITH NOTIFICATION)
// =========================
function saveSession() {

    console.log("Saving session...");

    const subject = document.getElementById("subject").value.trim();
    const goal = document.getElementById("goal").value.trim();
    const duration = document.getElementById("duration").value;

    if (!subject || !goal) {
        alert("Please enter subject and goal before saving!");
        return;
    }

    fetch("/save-study-session/", {

    method: "POST",

    credentials: "same-origin",

    headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
    },

    body: JSON.stringify({
        subject,
        goal,
        duration
    })

    })
    .then(res => res.json())
    .then(data => {

        console.log("Saved:", data);

        if (data.status === "success") {

            const table = document.querySelector("tbody");

            const newRow = `
                <tr>
                    <td>${subject}</td>
                    <td>${goal}</td>
                    <td>${duration} mins</td>
                    <td>Just now</td>
                    <td>
        <button
            class="btn btn-danger delete-session-btn"
            data-id="${data.id}">
            Delete
        </button>
    </td>
                </tr>
            `;

            table.insertAdjacentHTML("afterbegin", newRow);

            document.getElementById("subject").value = "";
            document.getElementById("goal").value = "";

            // 🔔 ADDED NOTIFICATION HERE TOO
            sendNotification();
        }
    })
    .catch(err => {
        console.error("Error saving session:", err);
    });
}

// =========================
// INITIAL LOAD
// =========================
setDuration();

// =========================
// RESTORE TIMER AFTER REFRESH / PHONE SLEEP
// =========================
window.addEventListener("load", () => {

    const savedEnd = Number(localStorage.getItem(END_TIME_KEY));

    const alreadySaved =
        localStorage.getItem(SAVED_KEY) === "true";

    if (!savedEnd) return;

    endTime = savedEnd;

    if (Date.now() >= endTime) {

        seconds = 0;

        updateDisplay();

        if (!alreadySaved) {

            hasCompleted = true;

            localStorage.setItem(SAVED_KEY, "true");

            localStorage.removeItem(END_TIME_KEY);

            showToast("🎉 Study Session Completed!");

            sendNotification();

            saveSession();
        }

    } else {

        timer = setInterval(updateTimer, 1000);

        updateTimer();
    }
});


// =========================
// PHONE WAKES FROM SLEEP
// =========================
document.addEventListener("visibilitychange", () => {

    if (document.visibilityState !== "visible")
        return;

    const savedEnd = Number(localStorage.getItem(END_TIME_KEY));

    const alreadySaved =
        localStorage.getItem(SAVED_KEY) === "true";

    if (!savedEnd || alreadySaved)
        return;

    if (Date.now() >= savedEnd) {

        clearInterval(timer);

        seconds = 0;

        updateDisplay();

        hasCompleted = true;

        localStorage.setItem(SAVED_KEY, "true");

        localStorage.removeItem(END_TIME_KEY);

        showToast("🎉 Study Session Completed!");

        sendNotification();

        saveSession();

    } else {

        endTime = savedEnd;

        clearInterval(timer);

        timer = setInterval(updateTimer, 1000);

        updateTimer();
    }
});
// =========================
// TOAST MESSAGE
// =========================
function showToast(message) {

    const toast = document.getElementById("toast");

    if (!toast) {
        alert(message);
        return;
    }

    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}

// =========================
// CSRF HELPER
// =========================
function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

// =========================
// DELETE SINGLE SESSION
// =========================
document.addEventListener("click", function (e) {

    if (e.target.classList.contains("delete-session-btn")) {

        const id = e.target.dataset.id;

        if (!id) return;

        if (!confirm("Delete this study session?")) return;

        fetch(`/delete-study-session/${id}/`, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) location.reload();
            else alert(data.error || "Delete failed");
        })
        .catch(console.error);
    }
});

// =========================
// CLEAR ALL HISTORY
// =========================
function clearStudyHistory() {

    if (!confirm("Delete ALL study sessions?")) return;

    fetch("/clear-study-sessions/", {
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
            const tbody = document.querySelector("tbody");

            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4">No study sessions yet</td>
                    </tr>
                `;
            }

            alert("All study history cleared!");
        } else {
            alert(data.error || "Delete failed");
        }

    })
    .catch(console.error);
}

// const completeSound = new Audio("/static/sounds/Alert-sound.mp3");

// let timer = null;
// let seconds = 1500;
// let endTime = null;
// let hasCompleted = false;

// // Elements
// const display = document.getElementById("timerDisplay");
// const durationSelect = document.getElementById("duration");

// // =========================
// // 🔔 REQUEST NOTIFICATION PERMISSION (ADDED)
// // =========================
// if ("Notification" in window && Notification.permission !== "granted") {
//     Notification.requestPermission();
// }

// // =========================
// // 🔔 DESKTOP NOTIFICATION FUNCTION (ADDED)
// // =========================
// function sendNotification() {
//     if ("Notification" in window && Notification.permission === "granted") {
//         new Notification("🎉 Study Session Completed", {
//             body: "Great job! Your session has been saved successfully.",
//             icon: "/static/img/image_2.jpg"
//         });
//     }
// }

// // =========================
// // UPDATE DISPLAY
// // =========================
// function updateDisplay() {
//     let mins = Math.floor(seconds / 60);
//     let secs = seconds % 60;

//     display.textContent = `${mins}:${secs.toString().padStart(2, "0")}`;
// }

// // =========================
// // SET TIMER FROM DROPDOWN
// // =========================
// function setDuration() {
//     clearInterval(timer);
//     seconds = parseInt(durationSelect.value) * 60;
//     updateDisplay();
// }

// // =========================
// // START TIMER
// // =========================
// document.getElementById("startBtn").addEventListener("click", () => {

//     clearInterval(timer);
//     hasCompleted = false;

//     // Set the time the countdown should finish
//     endTime = Date.now() + (seconds * 1000);

//     timer = setInterval(updateTimer, 1000);

//     updateTimer();
// });

// function updateTimer() {

//     const remaining = Math.max(
//         0,
//         Math.floor((endTime - Date.now()) / 1000)
//     );

//     seconds = remaining;

//     updateDisplay();

//     if (remaining === 0) {

//         clearInterval(timer);

//         if (!hasCompleted) {

//             hasCompleted = true;

//             completeSound.play();
//             navigator.vibrate?.(200);

//             showToast("🎉 Study Session Completed!");
//             sendNotification();

//             saveSession();
//         }
//     }
// }

// // =========================
// // PAUSE TIMER
// // =========================
// document.getElementById("pauseBtn").addEventListener("click", () => {

//     clearInterval(timer);

//     // Save remaining seconds
//     seconds = Math.max(
//         0,
//         Math.floor((endTime - Date.now()) / 1000)
//     );

// });

// // =========================
// // RESET TIMER
// // =========================
// document.getElementById("resetBtn").addEventListener("click", () => {

//     clearInterval(timer);

//     endTime = null;

//     seconds = parseInt(durationSelect.value) * 60;

//     updateDisplay();

// });

// // =========================
// // CHANGE DURATION
// // =========================
// durationSelect.addEventListener("change", setDuration);

// // =========================
// // INITIAL LOAD
// // =========================
// setDuration();

// // =========================
// // SAVE SESSION (WITH NOTIFICATION)
// // =========================
// function saveSession() {

//     console.log("Saving session...");

//     const subject = document.getElementById("subject").value.trim();
//     const goal = document.getElementById("goal").value.trim();
//     const duration = document.getElementById("duration").value;

//     if (!subject || !goal) {
//         alert("Please enter subject and goal before saving!");
//         return;
//     }

//     fetch("/save-study-session/", {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json",
//             "X-CSRFToken": getCookie("csrftoken")
//         },
//         body: JSON.stringify({
//             subject: subject,
//             goal: goal,
//             duration: duration
//         })
//     })
//     .then(res => res.json())
//     .then(data => {

//         console.log("Saved:", data);

//         if (data.status === "success") {

//             const table = document.querySelector("tbody");

//             const newRow = `
//                 <tr>
//                     <td>${subject}</td>
//                     <td>${goal}</td>
//                     <td>${duration} mins</td>
//                     <td>Just now</td>
//                 </tr>
//             `;

//             table.insertAdjacentHTML("afterbegin", newRow);

//             document.getElementById("subject").value = "";
//             document.getElementById("goal").value = "";

//             // 🔔 ADDED NOTIFICATION HERE TOO
//             sendNotification();
//         }
//     })
//     .catch(err => {
//         console.error("Error saving session:", err);
//     });
// }

// // =========================
// // TOAST MESSAGE
// // =========================
// function showToast(message) {

//     const toast = document.getElementById("toast");

//     if (!toast) {
//         alert(message);
//         return;
//     }

//     toast.textContent = message;
//     toast.classList.add("show");

//     setTimeout(() => {
//         toast.classList.remove("show");
//     }, 3000);
// }

// // =========================
// // CSRF HELPER
// // =========================
// function getCookie(name) {
//     let cookieValue = null;

//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');

//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();

//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }

//     return cookieValue;
// }

// // =========================
// // DELETE SINGLE SESSION
// // =========================
// document.addEventListener("click", function (e) {

//     if (e.target.classList.contains("delete-session-btn")) {

//         const id = e.target.dataset.id;

//         if (!id) return;

//         if (!confirm("Delete this study session?")) return;

//         fetch(`/delete-study-session/${id}/`, {
//             method: "POST",
//             credentials: "same-origin",
//             headers: {
//                 "Content-Type": "application/json",
//                 "X-CSRFToken": getCookie("csrftoken")
//             }
//         })
//         .then(res => res.json())
//         .then(data => {
//             if (data.success) location.reload();
//             else alert(data.error || "Delete failed");
//         })
//         .catch(console.error);
//     }
// });

// // =========================
// // CLEAR ALL HISTORY
// // =========================
// function clearStudyHistory() {

//     if (!confirm("Delete ALL study sessions?")) return;

//     fetch("/clear-study-sessions/", {
//         method: "POST",
//         credentials: "same-origin",
//         headers: {
//             "Content-Type": "application/json",
//             "X-CSRFToken": getCookie("csrftoken")
//         }
//     })
//     .then(res => res.json())
//     .then(data => {

//         if (data.success) {
//             const tbody = document.querySelector("tbody");

//             if (tbody) {
//                 tbody.innerHTML = `
//                     <tr>
//                         <td colspan="4">No study sessions yet</td>
//                     </tr>
//                 `;
//             }

//             alert("All study history cleared!");
//         } else {
//             alert(data.error || "Delete failed");
//         }

//     })
//     .catch(console.error);
// }
