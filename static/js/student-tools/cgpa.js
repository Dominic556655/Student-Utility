document.addEventListener("DOMContentLoaded", function () {

    // ---------------- CALCULATE CGPA ----------------
    function calculateCGPA() {

        let totalPoints = 0;
        let totalUnits = 0;

        const semesters = [];

        document.querySelectorAll("#cgpaBody tr").forEach((row, index) => {

            const gpa = Number(
                row.querySelector(".cgpa-gpa")?.value
            );

            const units = Number(
                row.querySelector(".cgpa-units")?.value
            );

            if (!isNaN(gpa) && !isNaN(units) && gpa > 0 && units > 0) {

                totalPoints += gpa * units;
                totalUnits += units;

                semesters.push({
                    semester: index + 1,
                    gpa: gpa,
                    units: units
                });
            }
        });

        const cgpa = totalUnits ? totalPoints / totalUnits: 0;

document.getElementById("cgpaResult").innerText = cgpa.toFixed(2);

// ---------------- CLASSIFICATION ----------------
let classification = "-";

if (cgpa >= 4.5) classification = "First Class";
else if (cgpa >= 3.5) classification = "Second Class Upper";
else if (cgpa >= 2.4) classification = "Second Class Lower";
else if (cgpa >= 1.5) classification = "Third Class";
else if (cgpa > 0) classification = "Pass";

document.getElementById("cgpaClass").innerText = classification;

const classEl = document.getElementById("cgpaClass");
if (classEl) {classEl.innerText = classification;}

saveCGPA(cgpa, totalUnits, classification, semesters);
    }


    // ---------------- SAVE CGPA ----------------
    function saveCGPA(cgpa, totalUnits, classification, semesters) {

        fetch("/save-cgpa/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                cgpa: cgpa,
                total_units: totalUnits,
                classification: classification,
                semesters: semesters
            })
        })
        .then(res => res.json())
        .then(data => {

            const record = data.data;
            const table = document.getElementById("cgpaHistoryBody");

            if (!table || !record) return;

            let rows = "";

            // Semester rows
            semesters.forEach((s, index) => {

    rows += `
        <tr data-record-id="${record.id}">
            <td>Semester ${s.semester}</td>
            <td>${s.gpa.toFixed(2)}</td>
            <td>${s.units}</td>

            <td>
                ${index === semesters.length - 1
                    ? record.cgpa.toFixed(2)
                    : ""}
            </td>

            

            <td>Just now</td>

            <td>
                ${index === semesters.length - 1
                    ? `
                    <button
                        class="btn btn-danger btn-sm delete-cgpa"
                        data-id="${record.id}">
                        Delete
                    </button>
                    `
                    : ""}
            </td>
        </tr>
    `;
            });

            // Remove "No records yet"
            const emptyRow = table.querySelector("td[colspan='6']");
            if (emptyRow) {
                emptyRow.closest("tr").remove();
            }

            table.insertAdjacentHTML("afterbegin", rows);

        })
        .catch(err => {
            console.error("❌ SAVE ERROR:", err);
        });
    }


    // ---------------- ADD SEMESTER ----------------
    document.getElementById("addSem")
        .addEventListener("click", function () {

        const count =
            document.querySelectorAll("#cgpaBody tr")
            .length + 1;

        const row = `
            <tr>
                <td>Semester ${count}</td>

                <td>
                    <input
                        type="number"
                        step="0.01"
                        class="form-control cgpa-gpa"
                        placeholder="e.g 4.20"
                    >
                </td>

                <td>
                    <input
                        type="number"
                        class="form-control cgpa-units"
                        placeholder="e.g 24"
                    >
                </td>

                <td>
                    <button class="btn btn-danger remove-sem">
                        Remove
                    </button>
                </td>
            </tr>
        `;

        document
            .getElementById("cgpaBody")
            .insertAdjacentHTML("beforeend", row);
    });


    // ---------------- REMOVE SEMESTER ----------------
    document.addEventListener("click", function (e) {

        if (e.target.classList.contains("remove-sem")) {

            const rows =
                document.querySelectorAll("#cgpaBody tr");

            if (rows.length > 1) {
                e.target.closest("tr").remove();
            }
        }
    });


    // ---------------- CALCULATE BUTTON ----------------
    document.getElementById("calcCgpa")
        .addEventListener("click", calculateCGPA);


    // ---------------- RESET ----------------
    document.getElementById("resetCgpa")
        .addEventListener("click", function () {

        document.getElementById("cgpaBody").innerHTML = `
            <tr>
                <td>Semester 1</td>

                <td>
                    <input
                        type="number"
                        step="0.01"
                        class="form-control cgpa-gpa"
                    >
                </td>

                <td>
                    <input
                        type="number"
                        class="form-control cgpa-units"
                    >
                </td>

                <td>
                    <button class="btn btn-danger remove-sem">
                        Remove
                    </button>
                </td>
            </tr>
        `;

        document.getElementById("cgpaResult")
            .innerText = "0.00";
    });

});


// ---------------- CSRF ----------------
function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (
                cookie.substring(
                    0,
                    name.length + 1
                ) === (name + "=")
            ) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }
        }
    }

    return cookieValue;
}


// ---------------- DELETE CGPA ----------------
document.addEventListener("click", function (e) {

    const btn = e.target.closest(".delete-cgpa");

    if (!btn) return;

    const recordId = btn.dataset.id;

    fetch(`/delete-cgpa/${recordId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        }
    })
    .then(res => res.json())
    .then(data => {

        if (data.id) {

            // remove all semester rows of this record
            document
                .querySelectorAll(
                    `[data-record-id="${recordId}"]`
                )
                .forEach(row => row.remove());
        }
    });
});