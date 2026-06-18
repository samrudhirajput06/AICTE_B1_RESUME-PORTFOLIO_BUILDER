from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
import google.generativeai as genai
import io
from dotenv import load_dotenv
import os

app = Flask(__name__)

generated_resume = ""

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(
    api_key=api_key
)

model = genai.GenerativeModel("gemini-2.5-flash")


@app.route("/", methods=["GET", "POST"])
def home():

    resume = ""

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        education = request.form["education"]
        skills = request.form["skills"]
        projects = request.form["projects"]
        achievements = request.form["achievements"]

        template = request.form.get("template", "Professional")
        action = request.form.get("action", "resume")

        # ---------------- RESUME ----------------
        if action == "resume":

            prompt = f"""
            Create a {template} ATS-friendly professional resume.

            Rules:
            - No markdown symbols.
            - No placeholders.
            - Use only supplied information.

            Sections:
            CONTACT
            SUMMARY
            EDUCATION
            SKILLS
            PROJECTS
            ACHIEVEMENTS

            Name: {name}
            Email: {email}
            Education: {education}
            Skills: {skills}
            Projects: {projects}
            Achievements: {achievements}
            """

        # ---------------- COVER LETTER ----------------
        elif action == "cover":

            prompt = f"""
            Create a professional cover letter.

            Name: {name}
            Email: {email}
            Education: {education}
            Skills: {skills}
            Projects: {projects}
            Achievements: {achievements}

            Write a formal cover letter suitable for internships
            and fresher job applications.
            """

        # ---------------- PORTFOLIO ----------------
        elif action == "portfolio":

            prompt = f"""
            Create a professional portfolio.

            Include these sections:

            ABOUT ME
            EDUCATION
            SKILLS
            PROJECTS
            ACHIEVEMENTS
            CONTACT

            Name: {name}
            Email: {email}
            Education: {education}
            Skills: {skills}
            Projects: {projects}
            Achievements: {achievements}

            Format it like a personal portfolio website.
            """

        response = model.generate_content(prompt)

        resume = response.text

        global generated_resume
        generated_resume = resume

    return render_template(
        "index.html",
        resume=resume
    )


@app.route("/download_pdf")
def download_pdf():

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)

    width, height = 595, 842

    # Title
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, 800, "AI Generated Resume")

    # Line below title
    pdf.line(50, 790, 540, 790)

    y = 760

    for line in generated_resume.split("\n"):

        line = line.strip()

        if not line:
            y -= 10
            continue

        # Detect headings
        if (
            line.upper() == line
            and len(line) < 30
        ):
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(50, y, line)

            y -= 22

            pdf.setFont("Helvetica", 11)

        else:
            pdf.drawString(60, y, line[:110])

            y -= 16

        if y < 50:
            pdf.showPage()

            y = 800

            pdf.setFont("Helvetica", 11)

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="AI_Document.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)