function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }

    return cookieValue;
}


// =========================
// SUMMARIZE NOTES
// =========================

async function runAI(tool) {

    const text = document.getElementById("notesInput").value;

    if (!text.trim()) {
        alert("Enter text first");
        return;
    }

    const btnId = tool === "summarize" ? "summarizeBtn" : "explainBtn";
    setLoading(btnId, "Loading...", true);

    const url = tool === "summarize"
        ? "/summarize-notes/"
        : "/explain-topic/";

    const payload = tool === "summarize"
        ? { notes: text }
        : { topic: text };

    try {
        const res = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (data.status === "success") {

            document.getElementById("aiOutput").innerHTML =
                tool === "summarize"
                    ? `<h4>Summary</h4>${data.summary}`
                    : `<h4>Explanation</h4>${data.explanation}`;
        } else {
            alert(data.message || "Error");
        }

    } catch (err) {
        console.error(err);
    } finally {
        setLoading(btnId, tool === "summarize" ? "Summarize" : "Explain", false);
    }
}
// =========================
// GENERATE QUIZ
// =========================
document.getElementById("quizBtn").addEventListener("click", generateQuiz);

function generateQuiz() {

    const notes = document.getElementById("notesInput").value;

    if (!notes.trim()) {
        alert("Enter notes first");
        return;
    }

    setLoading("quizBtn", "Generate Quiz", true);
    fetch("/generate-quiz/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ notes: notes })
    })
    .then(res => res.json())
    .then(data => {

        if (data.quiz) {
            document.getElementById("quizOutput").innerHTML = `
                <h4>Generated Quiz</h4>
                <pre>${data.quiz}</pre>
            `;
        } else {
            alert(data.message);
        }
    })
    .catch(err => console.error(err))

    .finally(() => {
        setLoading("quizBtn", "Generate Quiz", false);
    });
}

function setLoading(buttonId, text, loading=true) {
    const btn = document.getElementById(buttonId);

    if (loading) {
        btn.disabled = true;
        btn.innerText = "Processing...";
    } else {
        btn.disabled = false;
        btn.innerText = text;
    }
}

    //-------------------------
    //      STUDY PLANNER
    // -------------------------

async function generateStudyPlan() {
    const subject = document.getElementById("subject").value;
    const duration = document.getElementById("duration").value;
    const goal = document.getElementById("goal").value;

    const res = await fetch("/generate-study-plan/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            subject,
            duration,
            goal
        })
    });

    const data = await res.json();

    if (data.status === "success") {
        document.getElementById("studyPlanOutput").innerHTML = data.plan;
    } else {
        alert(data.message);
    }
}


   
// =========================
// CLEAR ALL HISTORY
// =========================
function clearaihistory() {

    if (!confirm("Delete ALL History?")) return;

    fetch("/clear_aihistory/", {
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
    .catch(console.error);
}