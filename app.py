from flask import Flask, request, jsonify
import io
import os
from docx import Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import Table
from docx.text.paragraph import Paragraph

app = Flask(__name__)

def is_instruction_text(text):
    instruction_starters = [
        "תאר ופרט", "יש להציג", "יש לפרט", "הנחיה למילוי",
        "ציין האם", "שים לב!", "ככל שרלוונטי, תאר", "ככל שרלוונטי, פרט",
        "הסבר כיצד", "יש להתייחס לנושאים"
    ]
    for starter in instruction_starters:
        if text.startswith(starter):
            return True
    if text.count("[1]") > 0 and text.count("[2]") > 0:
        return True
    return False

def extract_from_docx_binary(binary_data):
    docx_bytes = io.BytesIO(binary_data)
    doc = Document(docx_bytes)

    json_structure = {
        "executive_summary": {"question": "סיכום מנהלים"},
        "the_need": {"question": "הצורך"},
        "the_product": {"question": "המוצר"},
        "team_and_capabilities": {"question": "הצוות ויכולות המיזם, פערים ביכולות"},
        "intellectual_property": {"question": "קניין רוחני"},
        "technology_uniqueness_innovation": {"question": "הטכנולוגיה, ייחודיות וחדשנות, חסמי כניסה טכנולוגיים, אתגרים, מוצרי צד ג'"},
        "tasks_and_activities": {"question": "משימות ופעילויות במיזם זה"},
        "market_clients_competition_business_model": {"question": "שוק, לקוחות, תחרות ומודל עסקי"},
        "grant_contribution_to_success": {"question": "תרומת מענק תנופה להצלחת המיזם"},
        "royalties": {"question": "תמלוגים"},
        "economic_and_technological_contribution": {"question": "התרומה הטכנולוגית והתעסוקתית הצפויה של המיזם לכלכלה הישראלית"}
    }

    section_keywords = {
        "executive_summary": ["סיכום מנהלים"],
        "the_need": ["הצורך"],
        "the_product": ["המוצר"],
        "team_and_capabilities": ["הצוות", "פערים", "עובדי מוסד", "מסגרת תומכת"],
        "intellectual_property": ["קניין רוחני", "בעלות במוצרי", "קוד פתוח", "פטנט"],
        "technology_uniqueness_innovation": ["טכנולוגיה", "ייחודיות", "חדשנות", "אתגרים"],
        "tasks_and_activities": ["משימות"],
        "market_clients_competition_business_model": ["שוק", "לקוחות", "תיקוף שוק", "מודל עסקי", "תחרות", "מתחרים", "חסמי כניסה"],
        "grant_contribution_to_success": ["תרומת מענק", "מענק תנופה"],
        "royalties": ["תמלוגים"],
        "economic_and_technological_contribution": ["תרומה הטכנולוגית", "תרומה התעסוקתית", "תרומה"]
    }

    result = {key: {"question": value["question"], "answer": ""} for key, value in json_structure.items()}
    section_content = {key: [] for key in json_structure.keys()}

    for element in doc.element.body:
        content_text = None
        if isinstance(element, CT_P):
            para = Paragraph(element, doc)
            text = para.text.strip()
            if text and text != "הזן טקסט כאן..." and not is_instruction_text(text):
                content_text = text
        elif isinstance(element, CT_Tbl):
            table = Table(element, doc)
            for row in table.rows:
                for cell in row.cells:
                    text = cell.text.strip()
                    if text and text != "הזן טקסט כאן..." and not is_instruction_text(text):
                        content_text = text
                        break
                if content_text:
                    break

        if content_text:
            for section_key, keywords in section_keywords.items():
                if any(keyword in content_text for keyword in keywords):
                    section_content[section_key].append(content_text)
                    break

    for section_key, content_parts in section_content.items():
        if content_parts:
            seen = set()
            unique_parts = [
                part for part in content_parts
                if not (part in seen or seen.add(part))
            ]
            result[section_key]["answer"] = "\n\n".join(unique_parts)

    return result

@app.route("/extract", methods=["POST"])
def extract():
    try:
        if "file" in request.files:
            uploaded_file = request.files["file"]
            if not uploaded_file.filename:
                return jsonify({"error": "empty filename"}), 400
            file_data = uploaded_file.read()
            source = "request.files"
        else:
            file_data = request.data
            source = "request.data"

        if not file_data:
            return jsonify({"error": "no data received"}), 400

        return jsonify({
            "status": "ok",
            "source": source,
            "bytes": len(file_data)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Tnufa Extractor API is running"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
