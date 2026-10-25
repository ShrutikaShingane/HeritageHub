import os
import io
import markdown
import base64
import json
from io import BytesIO
from flask import Flask, request, render_template, jsonify, session, Response, stream_with_context, redirect, url_for, \
    send_file
from dotenv import load_dotenv
from groq import Groq
from PIL import Image
from auth import auth_bp
from database import get_db_connection

# PDF Generation Library
from xhtml2pdf import pisa

load_dotenv()
# Groq Client Setup
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)
app.secret_key = 'heritage_hub_super_secret_key_123'
app.register_blueprint(auth_bp)


@app.route('/')
def index():
    conn = get_db_connection()
    content = None
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT about_us, contact_us FROM site_content WHERE id = 1")
            content = cursor.fetchone()
            cursor.close()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()
    return render_template('index.html', content=content)


@app.route('/login')
def login_page():
    return render_template('auth.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return "You are not logged in. <a href='/login'>Login here</a>"
    return render_template('dashboard.html')


# ==========================================
# ROUTE 5: Logout
# ==========================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page', msg='logout_success'))


@app.route('/api/history', methods=['GET'])
def get_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title FROM chats WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
    chats = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(chats)


@app.route('/api/chat/<int:chat_id>', methods=['GET'])
def get_chat_messages(chat_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT sender, content, image_path FROM messages WHERE chat_id = %s ORDER BY created_at ASC",
                   (chat_id,))
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(messages)


@app.route('/api/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    user_text = request.form.get('text', '')
    image_file = request.files.get('image')
    chat_id = request.form.get('chat_id')
    is_module_click = request.form.get('is_module_click', 'false') == 'true'
    module_name = request.form.get('module_name', '')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Create new chat if not exists
    if not chat_id or chat_id == 'null' or chat_id == '':
        cursor.execute("INSERT INTO chats (user_id, title) VALUES (%s, %s)", (user_id, "New Chat"))
        conn.commit()
        chat_id = cursor.lastrowid

    # Save User Message
    img_b64 = None
    img_obj = None
    if image_file:
        img = Image.open(io.BytesIO(image_file.read()))
        img.thumbnail((800, 800))
        img_obj = img
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=70)
        img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    cursor.execute("INSERT INTO messages (chat_id, sender, content, image_path) VALUES (%s, %s, %s, %s)",
                   (chat_id, 'user', user_text, img_b64))
    conn.commit()

    # AI Prompt (Ultra-Detailed - 10-12 Paragraphs)
    if is_module_click:
        system_prompt = (
            f"You are Heritage Hub AI. The user wants specific info about: {module_name}. "
            "DO NOT re-identify the object. Provide highly detailed info for this module."
        )
    else:
        system_prompt = (
            "You are Heritage Hub AI, a world-class historian, archaeologist, and epigraphist. "
            "Your task is to provide an EXHAUSTIVE, museum-quality research report on the provided image. "
            "If the image is NOT a historical/heritage object, say 'This does not appear to be a heritage object' and briefly describe it.\n\n"
            "If it IS a heritage object, you MUST write a LONG and DETAILED response (minimum 10-12 paragraphs). "
            "Use the following structure, but expand heavily on every single point:\n\n"
            "1. **Basic Identification**: What exactly is it? Provide the specific name.\n"
            "2. **Origin & Creator**: Who created it? (King, dynasty, artisan). When was it created? (Exact year, century, or era).\n"
            "3. **Historical Context**: What was happening in history when this was made? Describe the political and social climate.\n"
            "4. **Purpose & Significance**: Why was it made? Who was it meant for? What was its primary use?\n"
            "5. **In-depth Description**: Describe the materials used, the size, the artistic style, and the craftsmanship.\n"
            "6. **Inscriptions & Scripts**: If there is any text, what language/script is it? (e.g., Modi, Devanagari, Sanskrit).\n"
            "7. **Detailed Translation/Meaning**: Translate the text line by line and explain its deep meaning.\n"
            "8. **Cultural Impact**: How did this object influence the culture or society of that time?\n"
            "9. **Current Status**: Where is it currently kept? (Museum, private collection, or lost?)\n"
            "10. **Interesting Facts**: Add any fascinating historical facts or mysteries related to this object.\n\n"
            "Do NOT be brief. Elaborate on every point. Use bold headings, bullet points, and write in a scholarly tone."
        )

    # Fetch context
    cursor.execute("SELECT sender, content FROM messages WHERE chat_id = %s ORDER BY created_at ASC LIMIT 5",
                   (chat_id,))
    history = cursor.fetchall()
    chat_context = "\n".join([f"{msg['sender']}: {msg['content']}" for msg in history])

    # Auto Title Generation (Uses Vision Model to see the image)
    cursor.execute("SELECT COUNT(*) as c FROM messages WHERE chat_id = %s", (chat_id,))
    if cursor.fetchone()['c'] <= 2:
        title_prompt = "Look at this image and text. Generate a very short 3-4 word title for this chat. Output ONLY the title, nothing else."
        try:
            title_messages = [{"role": "user", "content": [{"type": "text", "text": title_prompt}]}]
            if img_b64:
                title_messages[0]["content"].append(
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})
            if user_text:
                title_messages[0]["content"].append({"type": "text", "text": user_text})

            title_response = client.chat.completions.create(
                messages=title_messages,
                model="qwen/qwen3.8-27b",
                max_tokens=15
            )
            title = title_response.choices[0].message.content.strip().replace('"', '').replace('\n', '')
            cursor.execute("UPDATE chats SET title = %s WHERE id = %s", (title, chat_id))
            conn.commit()
        except Exception as e:
            print(f"Title Gen Error: {e}")

    def generate():
        full_response = ""

        model_name = "qwen/qwen3.8-27b"

        try:
            image_b64_string = None
            if img_b64:
                image_b64_string = f"data:image/jpeg;base64,{img_b64}"

            messages_content = [{"type": "text", "text": system_prompt + "\n\nUser Query: " + user_text}]

            if image_b64_string:
                messages_content.append({
                    "type": "image_url",
                    "image_url": {"url": image_b64_string}
                })

            if chat_context:
                messages_content.append({"type": "text", "text": f"Context:\n{chat_context}"})

            # Groq API call (Streaming with higher token limit)
            response_stream = client.chat.completions.create(
                messages=[{"role": "user", "content": messages_content}],
                model=model_name,
                stream=True,
                temperature=0.4,
                max_tokens=800  # Increased for longer output
            )

            for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    text_chunk = chunk.choices[0].delta.content
                    full_response += text_chunk
                    yield text_chunk

        except Exception as e:
            last_error = str(e)
            print(f"Groq Error: {last_error}")
            yield f"\n\n❌ **AI Error:** {last_error}"
            return

        # Database mein save karein
        formatted_html = markdown.markdown(full_response, extensions=['extra'])
        cursor.execute("INSERT INTO messages (chat_id, sender, content) VALUES (%s, %s, %s)",
                       (chat_id, 'ai', formatted_html))
        conn.commit()
        cursor.close()
        conn.close()

    headers = {'X-Chat-ID': str(chat_id)}
    return Response(stream_with_context(generate()), headers=headers, mimetype='text/plain')


# --- CHAT DELETE API ---
@app.route('/api/delete_chat/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats WHERE id = %s AND user_id = %s", (chat_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Chat deleted'})


# --- PDF EXPORT API (Beautiful HTML to PDF) ---
@app.route('/api/export_pdf/<int:chat_id>', methods=['GET'])
def export_pdf(chat_id):
    if 'user_id' not in session:
        return "Unauthorized", 401
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT title FROM chats WHERE id = %s AND user_id = %s", (chat_id, session['user_id']))
    chat = cursor.fetchone()
    if not chat: return "Chat not found", 404

    cursor.execute("SELECT sender, content FROM messages WHERE chat_id = %s ORDER BY created_at ASC", (chat_id,))
    messages = cursor.fetchall()
    cursor.close()
    conn.close()

    # HTML Content taiyar karein PDF ke liye
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{ size: a4; margin: 2cm; }}
            body {{ font-family: Helvetica, sans-serif; color: #333; line-height: 1.6; }}
            h1 {{ color: #c59b63; text-align: center; border-bottom: 2px solid #c59b63; padding-bottom: 10px; }}
            h3 {{ color: #a67c52; margin-top: 20px; }}
            .user-msg {{ background-color: #f2e9df; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #a67c52; }}
            .ai-msg {{ background-color: #ffffff; padding: 10px; border-left: 4px solid #c59b63; margin-bottom: 20px; }}
            ul, ol {{ margin-left: 20px; }}
            strong {{ color: #000; }}
        </style>
    </head>
    <body>
        <h1>Heritage Hub Report: {chat['title']}</h1>
    """

    for msg in messages:
        if msg['sender'] == 'user':
            html_content += f'<div class="user-msg"><b>User:</b> {msg["content"]}</div>'
        else:
            html_content += f'<div class="ai-msg">{msg["content"]}</div>'

    html_content += "</body></html>"

    # PDF generate karein
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

    if pisa_status.err:
        return "Error generating PDF", 500

    pdf_buffer.seek(0)

    return send_file(pdf_buffer, as_attachment=True, download_name=f"{chat['title']}_HeritageHub.pdf",
                     mimetype='application/pdf')


# ==========================================
# ROUTE 7: Profile Page UI
# ==========================================
@app.route('/profile')
def profile_page():
    if 'user_id' not in session:
        return "Unauthorized", 401
    return render_template('profile.html')


# ==========================================
# ROUTE 8: Get Profile Data API
# ==========================================
@app.route('/api/get_profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
                   SELECT name,
                          email,
                          profile_pic,
                          role,
                          DATE_FORMAT(created_at, '%b %Y') as joined
                   FROM users
                   WHERE id = %s
                   """, (session['user_id'],))
    user = cursor.fetchone()

    if user:
        cursor.execute("SELECT COUNT(*) as total FROM chats WHERE user_id = %s", (session['user_id'],))
        user['total_chats'] = cursor.fetchone()['total']

        cursor.execute("""
                       SELECT COUNT(*) as total
                       FROM messages m
                                JOIN chats c ON m.chat_id = c.id
                       WHERE c.user_id = %s
                         AND m.image_path IS NOT NULL
                       """, (session['user_id'],))
        user['total_images'] = cursor.fetchone()['total']

        cursor.close()
        conn.close()
        return jsonify(user)

    cursor.close()
    conn.close()
    return jsonify({'error': 'User not found'}), 404


# ==========================================
# ROUTE 9: Update Profile API
# ==========================================
from werkzeug.security import generate_password_hash


@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    name = data.get('name')
    email = data.get('email')
    new_password = data.get('password')
    profile_pic = data.get('profile_pic')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if new_password and new_password.strip() != "":
            hashed_pass = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET name=%s, email=%s, password_hash=%s, profile_pic=%s WHERE id=%s",
                           (name, email, hashed_pass, profile_pic, session['user_id']))
        else:
            cursor.execute("UPDATE users SET name=%s, email=%s, profile_pic=%s WHERE id=%s",
                           (name, email, profile_pic, session['user_id']))

        conn.commit()
        session['user_name'] = name

        return jsonify({'message': 'Profile updated successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/delete_account', methods=['DELETE'])
def delete_account():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (session['user_id'],))
        conn.commit()
        session.clear()
        return jsonify({'message': 'Account deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ==========================================
# ADMIN DASHBOARD ROUTES
# ==========================================

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return "Access Denied. <a href='/login'>Login as Admin</a>"
    return render_template('admin.html')


@app.route('/api/admin/stats')
def admin_stats():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as c FROM users WHERE role = 'user'")
    users = cursor.fetchone()['c']

    cursor.execute("SELECT COUNT(*) as c FROM chats")
    chats = cursor.fetchone()['c']

    cursor.execute("SELECT COUNT(*) as c FROM messages WHERE image_path IS NOT NULL")
    images = cursor.fetchone()['c']

    cursor.close()
    conn.close()

    return jsonify({'users': users, 'chats': chats, 'images': images})


@app.route('/api/admin/users')
def admin_get_users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    search_query = request.args.get('search', '')
    role_filter = request.args.get('role', 'all')
    status_filter = request.args.get('status', 'all')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT id, name, email, role, is_blocked, DATE_FORMAT(created_at, '%d %b %Y') as joined FROM users WHERE 1=1"
    params = []

    if search_query:
        query += " AND (name LIKE %s OR email LIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    if role_filter != 'all':
        query += " AND role = %s"
        params.append(role_filter)

    if status_filter != 'all':
        is_blocked = True if status_filter == 'blocked' else False
        query += " AND is_blocked = %s"
        params.append(is_blocked)

    query += " ORDER BY id DESC"

    cursor.execute(query, tuple(params))
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)


@app.route('/api/admin/promote/<int:user_id>', methods=['POST'])
def admin_promote_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = 'admin' WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'User promoted to Admin'})


@app.route('/api/admin/chart_data')
def admin_chart_data():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
                   SELECT DATE (created_at) as date, COUNT (*) as count
                   FROM users
                   WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                   GROUP BY DATE (created_at)
                   ORDER BY date ASC
                   """)
    users_data = cursor.fetchall()

    cursor.execute("""
                   SELECT DATE (created_at) as date, COUNT (*) as count
                   FROM messages
                   WHERE image_path IS NOT NULL AND created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                   GROUP BY DATE (created_at)
                   ORDER BY date ASC
                   """)
    images_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({'users': users_data, 'images': images_data})


@app.route('/api/admin/toggle_block/<int:user_id>', methods=['POST'])
def admin_toggle_block(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT is_blocked FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if user:
        new_status = not user['is_blocked']
        cursor.execute("UPDATE users SET is_blocked = %s WHERE id = %s", (new_status, user_id))
        conn.commit()

    cursor.close()
    conn.close()
    return jsonify({'message': 'Status updated'})


@app.route('/api/admin/chats')
def admin_get_chats():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
                   SELECT c.id, c.title, u.name as user_name, DATE_FORMAT(c.created_at, '%d %b %Y') as date
                   FROM chats c JOIN users u
                   ON c.user_id = u.id
                   ORDER BY c.id DESC
                   """)
    chats = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(chats)


@app.route('/api/admin/get_content')
def get_site_content():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT about_us, contact_us FROM site_content WHERE id = 1")
    content = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(content)


@app.route('/api/admin/update_content', methods=['POST'])
def update_site_content():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE site_content SET about_us = %s, contact_us = %s WHERE id = 1",
                   (data.get('about_us'), data.get('contact_us')))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Content updated successfully'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)