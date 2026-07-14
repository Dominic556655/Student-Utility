// ================= GPA JS CLEAN VERSION =================
  function getCookie(name) {
        let cookieValue = null;

        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");

            for (let cookie of cookies) {
                cookie = cookie.trim();

                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );
                    break;
                }
            }
        }
        return cookieValue;
    }

document.addEventListener("DOMContentLoaded", function () {

    console.log("✅ GPA SCRIPT LOADED");

    function calculateGPA() {

        console.log("✅ calculateGPA running");

        let totalPoints = 0;
        let totalUnits = 0;

        const rows = document.querySelectorAll("#courseBody tr");

        // ✅ FIX: define courses array
        let courses = [];

        rows.forEach(row => {

    const name = row.querySelector(".course-name")?.value.trim();
    const unit = Number(row.querySelector(".course-unit")?.value);
    const grade = Number(row.querySelector(".course-grade")?.value);

    // 🚨 STRICT VALIDATION (ALL MUST BE VALID)
    if (!name || isNaN(unit) || isNaN(grade)) {
        return; // skip completely
    }

    courses.push({
        course: name,
        unit: unit,
        grade: grade
    });

    totalPoints += unit * grade;
    totalUnits += unit;
});

        const gpa = totalUnits ? (totalPoints / totalUnits) : 0;

        document.getElementById("gpaResult").innerText = gpa.toFixed(2);

        let classification = "-";

        if (gpa >= 4.5) classification = "First Class";
        else if (gpa >= 3.5) classification = "Second Class Upper";
        else if (gpa >= 2.4) classification = "Second Class Lower";
        else if (gpa >= 1.5) classification = "Third Class";
        else if (gpa > 0) classification = "Pass";

        document.getElementById("gpaClass").innerText = classification;

        const unitEl = document.getElementById("totalUnits");
        if (unitEl) unitEl.innerText = totalUnits;

        saveGPA(gpa, totalUnits, classification, courses);
    }

    function saveGPA(gpa, totalUnits, classification, courses) {

        console.log("🔥 saveGPA triggered");

        fetch("/save-gpa/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                courses: courses,
                gpa: gpa,
                total_units: totalUnits,
                classification: classification
            })
        })
        .then(res => res.json())
        .then(data => {

            const record = data.data;
            const table = document.getElementById("gpaHistoryBody");

            if (!record || !table) return;

            // convert courses to readable HTML
            let courseHTML = courses.map(c =>
                `${c.course} - (${c.unit})`
            ).join("<br>");

            const row = `
                <tr>
                    <td>${courseHTML}</td>
                    <td>${record.gpa.toFixed(2)}</td>
                    <td>${record.total_units}</td>
                    <td>${record.classification}</td>
                    <td>Just now</td>
                    <td>
                        <button class="btn btn-danger btn-sm delete-gpa"
                                data-id="${record.id}">
                            Delete
                        </button>
                    </td>
                </tr>
            `;

            table.insertAdjacentHTML("afterbegin", row);
        })
        .catch(err => console.error("❌ ERROR:", err));
    }

    // ================= EVENTS =================

    document.getElementById("calculateBtn")
        ?.addEventListener("click", calculateGPA);

    document.getElementById("addCourseBtn")
        ?.addEventListener("click", function () {

            const row = `
                <tr>
                    <td><input type="text" class="form-control course-name"></td>
                    <td><input type="number" class="form-control course-unit"></td>
                    <td>
                        <select class="form-select course-grade">
                            <option value="">Select Grade</option>
                            <option value="5">A</option>
                            <option value="4">B</option>
                            <option value="3">C</option>
                            <option value="2">D</option>
                            <option value="1">E</option>
                            <option value="0">F</option>
                        </select>
                    </td>
                    <td><button class="btn btn-danger remove-row">Remove</button></td>
                </tr>
            `;

            document.getElementById("courseBody")
                ?.insertAdjacentHTML("beforeend", row);
        });

    document.addEventListener("click", function (e) {

        if (e.target.classList.contains("remove-row")) {
            e.target.closest("tr")?.remove();
        }

        const btn = e.target.closest(".delete-gpa");
        if (!btn) return;

        fetch(`/delete-gpa/${btn.dataset.id}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.id) btn.closest("tr")?.remove();
        });
    });

    document.getElementById("resetBtn")
        ?.addEventListener("click", function () {
            document.getElementById("courseBody").innerHTML = "";
        });

});


document.addEventListener("click", function (e) {

    const btn = e.target.closest(".delete-gpa");
    if (!btn) return;

    fetch(`/delete-gpa/${btn.dataset.id}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.id) {
            btn.closest("tr").remove();
        }
    });
});



