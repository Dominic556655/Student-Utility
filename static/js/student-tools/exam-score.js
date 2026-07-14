function getCookie(name) {

    let cookieValue = null;

    if (document.cookie &&document.cookie !== "") {

        const cookies =document.cookie.split(";");

        for (let i = 0;i < cookies.length;i++) {

            const cookie =cookies[i].trim();

            if (cookie.substring(0,name.length + 1) ===(name + "=")) {

                cookieValue =decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {

    console.log("✅ Exam Predictor Loaded");

    const gradingFormat =document.getElementById("gradingFormat");

    const caTotalInput =document.getElementById("caTotal");

    const examTotalInput =document.getElementById("examTotal");

    const predictionStatus =document.getElementById("predictionStatus");

    const requiredScoreEl =document.getElementById("requiredScore");
        const ctx = document.getElementById("examChart");

    renderExamHistory();

    document.getElementById("whatIfScore")
    .addEventListener("input", function () {

        const test =
            parseFloat(document.getElementById("testScore").value) || 0;

        const assignment =
            parseFloat(document.getElementById("assignmentScore").value) || 0;

        const attendance =
            parseFloat(document.getElementById("attendanceScore").value) || 0;

        const practical =
            parseFloat(document.getElementById("practicalScore").value) || 0;

        const examTotal =
            parseFloat(document.getElementById("examTotal").value) || 0;

        const currentCA =
            test + assignment + attendance + practical;

        whatIfScenario(currentCA, examTotal);
    });


    

            // =========================
            // CHART
            // =========================
let examChart = new Chart(ctx, {
    type: "bar",
    data: {
        labels: ["A", "B", "C", "D", "E"],
        datasets: [{
            label: "Grade Difficulty (Needed Score)",
            data: [0, 0, 0, 0, 0],
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: false
            }
        }
    }
});


    // =========================
    // GRADING FORMAT HANDLER
    // =========================
    gradingFormat.addEventListener("change", function () {

        const value = this.value;

        if (value === "30-70") {

            caTotalInput.value = 30;
            examTotalInput.value = 70;

            caTotalInput.readOnly = true;
            examTotalInput.readOnly = true;

        } else if (value === "40-60") {

            caTotalInput.value = 40;
            examTotalInput.value = 60;

            caTotalInput.readOnly = true;
            examTotalInput.readOnly = true;

        } else if (value === "50-50") {

            caTotalInput.value = 50;
            examTotalInput.value = 50;

            caTotalInput.readOnly = true;
            examTotalInput.readOnly = true;

        } else if (value === "custom") {

            caTotalInput.value = "";
            examTotalInput.value = "";

            caTotalInput.readOnly = false;
            examTotalInput.readOnly = false;
        }
    });


    // Buttons
    document.getElementById("predictBtn")
        .addEventListener("click", predictScore);

    document.getElementById("resetBtn")
        .addEventListener("click", resetFields);


    // =========================
    // MAIN PREDICT FUNCTION
    // =========================
    function predictScore() {

        const targetGrade =
            parseFloat(document.getElementById("targetGrade").value) || 0;

        const caTotal =
            parseFloat(caTotalInput.value) || 0;

        const examTotal =
            parseFloat(examTotalInput.value) || 0;

        const test =
            parseFloat(document.getElementById("testScore").value) || 0;

        const assignment =
            parseFloat(document.getElementById("assignmentScore").value) || 0;

        const attendance =
            parseFloat(document.getElementById("attendanceScore").value) || 0;

        const practical =
            parseFloat(document.getElementById("practicalScore").value) || 0;


        const currentCA =
            test + assignment + attendance + practical;


        // Validation
        if (!targetGrade) {
            alert("Please select target grade.");
            return;
        }

        if (!caTotal || !examTotal) {
            alert("Please select grading format.");
            return;
        }

        if (currentCA > caTotal) {
            alert(`CA exceeds allowed total (${caTotal})`);
            return;
        }

  

        // Show current CA
        document.getElementById("currentScore").textContent =
            currentCA.toFixed(2);


        // Needed score
        let neededScore =
            targetGrade - currentCA;

        if (neededScore < 0) {
            neededScore = 0;
        }
              generateAIInsight(
    currentCA,
    caTotal,
    examTotal,
    neededScore
);

saveExamHistory({
    course: document.getElementById("courseCode").value || "N/A",
    ca: currentCA.toFixed(2),
    examTotal: examTotal,
    target: targetGrade,
    required: neededScore.toFixed(2),
    result: neededScore <= examTotal ? "Possible" : "Impossible",
    date: new Date().toLocaleString()
});

        // Required score display
        if (neededScore <= examTotal) {

            requiredScoreEl.textContent =
                `${neededScore.toFixed(2)} / ${examTotal}`;

        } else {

            requiredScoreEl.textContent =
                "Impossible";
        }


        // SMART FEEDBACK (ONLY SYSTEM USED)
        getSmartFeedback(currentCA, examTotal, neededScore);

        // Grade table
        generateGradeTable(currentCA, examTotal);

        // WHAT IF
        whatIfScenario(currentCA, examTotal);

        // EXAM STRATEGY
        examStrategyEngine(currentCA, examTotal, neededScore);

        /* SAVE HISTORY TO DATABASE */
        fetch("/save-exam-history/", {

    method: "POST",

    headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
    },

    body: JSON.stringify({

        course_code:document.getElementById("courseCode").value,

        current_ca:currentCA,

        exam_total:examTotal,

        target_grade:targetGrade,

        required_score:neededScore,

        result:
            neededScore <= examTotal
                ? "Possible"
                : "Impossible",

        final_score:currentCA + neededScore
    })
});
    }



    // =========================
    // GRADE TABLE
    // =========================
    function generateGradeTable(currentCA, examTotal) {

        const gradeTable =
            document.getElementById("gradeTableBody");

        const grades = [
            { grade: "A", score: 70 },
            { grade: "B", score: 60 },
            { grade: "C", score: 50 },
            { grade: "D", score: 45 },
            { grade: "E", score: 40 },
            { grade: "F", score: 39 }
        ];

        gradeTable.innerHTML = "";

        grades.forEach(item => {

            let needed =
                item.score - currentCA;

            if (needed < 0) {
                needed = 0;
            }

            const result =
                needed <= examTotal
                    ? `${needed.toFixed(2)} / ${examTotal}`
                    : "Impossible";

            gradeTable.innerHTML += `
                <tr>
                    <td>${item.grade}</td>
                    <td>${result}</td>
                </tr>
            `;
            examChart.data.datasets[0].data = grades.map(item => {

    let needed = item.score - currentCA;

    if (needed < 0) needed = 0;

    return needed;
});

examChart.update();
        });
    }


    // =========================
    // RESET FUNCTION
    // =========================
    function resetFields() {

        document.getElementById("courseCode").value = "";
        document.getElementById("targetGrade").value = "";
        document.getElementById("gradingFormat").value = "";

        caTotalInput.value = "";
        examTotalInput.value = "";

        document.getElementById("testScore").value = "";
        document.getElementById("assignmentScore").value = "";
        document.getElementById("attendanceScore").value = "";
        document.getElementById("practicalScore").value = "";

        document.getElementById("currentScore").textContent = "0";
        requiredScoreEl.textContent = "-";
        predictionStatus.textContent = "-";

        document.getElementById("gradeTableBody").innerHTML = `
            <tr>
                <td colspan="2">Calculate to see prediction</td>
            </tr>
        `;
    }

});


// =========================
// SMART FEEDBACK ENGINE
// =========================
function getSmartFeedback(currentCA, examTotal, neededScore) {

    const maxPossible = currentCA + examTotal;

    const feedbackEl =
        document.getElementById("predictionStatus");

    if (maxPossible < 70) {
        feedbackEl.innerHTML =
            "A is no longer possible ❌ Best possible is B or lower";
        return;
    }

    if (neededScore <= examTotal * 0.3) {
        feedbackEl.innerHTML =
            "Strong position 💪 You only need a small score to succeed";
        return;
    }

    if (neededScore <= examTotal * 0.6) {
        feedbackEl.innerHTML =
            "You are on track 📊 Just need consistent preparation";
        return;
    }

    if (neededScore <= examTotal) {
        feedbackEl.innerHTML =
            "Difficult but possible ⚠️ Requires serious effort";
        return;
    }

    feedbackEl.innerHTML =
        "Not achievable ❌ Consider adjusting target grade";
}


// AI INSIGHT
function generateAIInsight(currentCA, caTotal, examTotal, neededScore) {

    const insightEl =
        document.getElementById("aiInsight");

    if (!insightEl) {
        console.error("AI Insight element not found");
        return;
    }

    const caPercentage =
        (currentCA / caTotal) * 100;

    const examPressure =
        (neededScore / examTotal) * 100;

    const totalPossible =
        currentCA + examTotal;

    let message = "";

    if (totalPossible < 70) {
        message =
            "❌ Target not achievable. Consider lowering expectations.";
    }

    else if (caPercentage >= 60 && examPressure <= 40) {
        message =
            "🟢 Strong performance. You are well positioned.";
    }

    else if (examPressure > 70) {
        message =
            "🔴 High risk. You rely heavily on exam performance.";
    }

    else if (caPercentage < 40) {
        message =
            "⚠️ Weak CA performance. Improve assignments & tests.";
    }

    else if (examPressure <= 60) {
        message =
            "🟡 Average standing. Stay consistent.";
    }

    else {
        message =
            "📊 Balanced performance. Keep pushing.";
    }

    insightEl.innerHTML = message;
}



// WHAT IF
function whatIfScenario(currentCA, examTotal) {

    const whatIfInput =
        document.getElementById("whatIfScore");

    const score =
        parseFloat(whatIfInput.value) || 0;

    const insightEl =
        document.getElementById("aiInsight");

    // Stop if empty
    if (!whatIfInput.value) return;

    // Validation
    if (score > examTotal) {

        insightEl.innerHTML =
            `❌ Exam score cannot exceed ${examTotal}`;
        return;
    }

    // Add exam score to current CA
    const finalScore =
        currentCA + score;

    let grade = "";

    if (finalScore >= 70) {
        grade = "A";
    }
    else if (finalScore >= 60) {
        grade = "B";
    }
    else if (finalScore >= 50) {
        grade = "C";
    }
    else if (finalScore >= 45) {
        grade = "D";
    }
    else if (finalScore >= 40) {
        grade = "E";
    }
    else {
        grade = "F";
    }

    // Show result
    insightEl.innerHTML = `
        📊 Your CA is <b>${currentCA.toFixed(2)}</b><br>
        📝 If you score <b>${score}/${examTotal}</b> in exam,<br>
        🎯 Final Score = <b>${finalScore.toFixed(2)}</b><br>
        🏆 Expected Grade = <b>${grade}</b>
    `;
}






// EXAM STRATEGY

function examStrategyEngine(currentCA, examTotal, neededScore) {

    const strategyEl =
        document.getElementById("strategyEngine");

    if (!strategyEl) return;

    const requiredPercent =
        (neededScore / examTotal) * 100;

    let message = "";

    if (requiredPercent <= 30) {
        message =
            "🟢 Easy target — revise past questions and stay consistent.";
    }

    else if (requiredPercent <= 60) {
        message =
            "🟡 Moderate target — focus on key topics and practice questions daily.";
    }

    else if (requiredPercent <= 80) {
        message =
            "⚠️ High target — prioritize exam questions and time management.";
    }

    else {
        message =
            "🔴 Very difficult — you need full focus + exam strategy + past questions.";
    }

    strategyEl.innerHTML = message;
}


// SAVE HISTORY
function saveExamHistory(data) {

    let history =
        JSON.parse(localStorage.getItem("examHistory")) || [];

    history.unshift(data); // newest first

    localStorage.setItem("examHistory", JSON.stringify(history));

    renderExamHistory();
}


// RENDER HISTORY TO PAGE
function renderExamHistory() {

    const historyEl =
        document.getElementById("examHistoryBody");

    if (!historyEl) return;

    let history =
        JSON.parse(localStorage.getItem("examHistory")) || [];

    historyEl.innerHTML = "";

    history.forEach((item, index) => {

        historyEl.innerHTML += `
            <tr>
                <td>${item.course}</td>
                <td>${item.ca}</td>
                <td>${item.examTotal}</td>
                <td>${item.target}</td>
                <td>${item.required}</td>
                <td>${item.result}</td>
                <td>${item.date}</td>
                <td>
                    <button class="btn btn-danger btn-sm"
                        onclick="deleteExamHistory(${index})">
                        Delete
                    </button>
                </td>
            </tr>
        `;
    });
}

// DELETE HISTORY
function deleteExamHistory(index) {

    let history =
        JSON.parse(localStorage.getItem("examHistory")) || [];

    history.splice(index, 1);

    localStorage.setItem("examHistory", JSON.stringify(history));

    renderExamHistory();
}

function clearExamHistory() {

    if (!confirm("Are you sure you want to delete all history?")) return;

    localStorage.removeItem("examHistory");

    renderExamHistory();
}