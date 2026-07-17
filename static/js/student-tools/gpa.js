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

// ================= GRADING SYSTEM =================

const gradingSystems = {
    5: {
        max: 5,
        grades: [
            { letter: "A", point: 5 },
            { letter: "B", point: 4 },
            { letter: "C", point: 3 },
            { letter: "D", point: 2 },
            { letter: "E", point: 1 },
            { letter: "F", point: 0 }
        ]
    },

    4: {
        max: 4,
        grades: [
            { letter: "A", point: 4 },
            { letter: "B", point: 3 },
            { letter: "C", point: 2 },
            { letter: "D", point: 1 },
            { letter: "F", point: 0 }
        ]
    }
};

function loadGradeOptions(select) {

    const scale = document.getElementById("gradingScale").value;
    const grades = gradingSystems[scale].grades;

    select.innerHTML = '<option value="">Select Grade</option>';

    grades.forEach(g => {
        select.innerHTML += `
            <option value="${g.point}">
                ${g.letter} (${g.point})
            </option>
        `;
    });
}

function refreshAllGradeDropdowns() {

    document.querySelectorAll(".course-grade").forEach(select => {
        loadGradeOptions(select);
    });

}

document.addEventListener("DOMContentLoaded", function () {

    refreshAllGradeDropdowns();

document.getElementById("gradingScale")
    .addEventListener("change", refreshAllGradeDropdowns);

    console.log("✅ GPA SCRIPT LOADED");

    function calculateGPA() {

    console.log("✅ calculateGPA running");

    let totalPoints = 0;
    let totalUnits = 0;

    // Selected grading scale (4 or 5)
    const scale = Number(document.getElementById("gradingScale").value);

    const rows = document.querySelectorAll("#courseBody tr");

    let courses = [];

    rows.forEach(row => {

        const name = row.querySelector(".course-name")?.value.trim();
        const unit = Number(row.querySelector(".course-unit")?.value);
        const grade = Number(row.querySelector(".course-grade")?.value);

        if (!name || isNaN(unit) || isNaN(grade)) {
            return;
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

    // Display GPA with grading scale
    document.getElementById("gpaResult").innerText =
        `${gpa.toFixed(2)} / ${scale.toFixed(1)}`;

   

    const unitEl = document.getElementById("totalUnits");
    if (unitEl) unitEl.innerText = totalUnits;

    saveGPA(gpa, totalUnits, courses, scale);

}

    function saveGPA(gpa, totalUnits, courses, scale) {

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
            
            grading_scale: scale
        })
    })
    .then(res => res.json())
    .then(data => {

        const record = data.data;
        const table = document.getElementById("gpaHistoryBody");

        if (!record || !table) return;

        let courseHTML = courses.map(c =>
            `${c.course} - (${c.unit})`
        ).join("<br>");

        const row = `
            <tr>
                <td>${courseHTML}</td>
                <td>${record.gpa.toFixed(2)} / ${scale.toFixed(1)}</td>
                <td>${record.total_units}</td>
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
                        <select class="form-select course-grade"></select>
                    </td>
                    <td><button class="btn btn-danger remove-row">Remove</button></td>
                </tr>
            `;

            document.getElementById("courseBody")
                ?.insertAdjacentHTML("beforeend", row);
                
                const newSelect = document.querySelector(
    "#courseBody tr:last-child .course-grade"
);

loadGradeOptions(newSelect);
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



