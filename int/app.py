
from flask import Flask, render_template, request, jsonify
from gtts import gTTS
import pandas as pd
import os
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import time

# FIXED: Properly configure Flask with static folder
app = Flask(__name__, static_folder='static', static_url_path='/static')
UPLOAD_FOLDER = "uploads"
AUDIO_FOLDER = os.path.join(app.root_path, "static")  # Use absolute path
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)



load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def learn_names_from_csv(df):
    """
    Learn male and female names from the CSV by analyzing Father and Mother names
    """
    male_names = set()
    female_names = set()
    
    for index, row in df.iterrows():
        father_name = str(row.get("Father Name", "")).strip()
        mother_name = str(row.get("Mother Name", "")).strip()
        
        if father_name and father_name != "nan":
            # Extract first name from father's name and add to male names
            father_first_name = father_name.split()[0].lower()
            if father_first_name:
                male_names.add(father_first_name)
        
        if mother_name and mother_name != "nan":
            # Extract first name from mother's name and add to female names  
            mother_first_name = mother_name.split()[0].lower()
            if mother_first_name:
                female_names.add(mother_first_name)
    
    return male_names, female_names

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # ADDED: Debug information
        print(f"🔍 AUDIO_FOLDER path: {AUDIO_FOLDER}")
        print(f"🔍 AUDIO_FOLDER exists: {os.path.exists(AUDIO_FOLDER)}")
        print(f"🔍 Current working directory: {os.getcwd()}")
        
        csv_file = request.files["csv"]
        if csv_file:
            csv_path = os.path.join(UPLOAD_FOLDER, csv_file.filename)
            csv_file.save(csv_path)

            # ADDED: Better error handling for CSV reading
            try:
                df = pd.read_csv(csv_path)
                print(f"📊 CSV loaded successfully!")
                print(f"📋 Total students: {len(df)}")
                print(f"📝 Columns: {list(df.columns)}")
            except Exception as e:
                return f"❌ Error reading CSV: {str(e)}"
            
            # Learn names from CSV data
            male_names, female_names = learn_names_from_csv(df)
            print(f"👨 Learned {len(male_names)} male names from fathers: {list(male_names)[:10]}...")
            print(f"👩 Learned {len(female_names)} female names from mothers: {list(female_names)[:10]}...")
            print("=" * 60)
            
            count = 0
            audio_names = []
            call_results = []

            for index, row in df.iterrows():
                # ADDED: Better error handling for missing columns
                try:
                    name = str(row.get("Name", "")).strip()
                    roll_no = str(row.get("Roll No", "")).strip()
                    sem = str(row.get("Semester", "")).strip()
                    spi = str(row.get("SPI", "")).strip()
                    result = str(row.get("Result", "")).strip()
                    father = str(row.get("Father Name", "")).strip()
                    contact = str(row.get("Father Contact", "")).strip()
                    
                    if not all([name, roll_no, father, contact]):
                        print(f"⚠️ Skipping row {index + 1}: Missing required data")
                        continue
                        
                except Exception as e:
                    print(f"❌ Error processing row {index + 1}: {str(e)}")
                    continue

                print(f"\n🎓 Processing Student {index + 1}: {name} ({roll_no})")

                # Clean and format phone number
                phone_number = str(contact).strip()
                phone_number = phone_number.replace('+91-', '').replace('+91', '').replace('-', '').replace(' ', '')
                if not phone_number.startswith('+'):
                    phone_number = f"+91{phone_number}"

                print(f"📞 Calling: {phone_number}")

                # DYNAMIC GENDER DETECTION - NO HARDCODING
                first_name = name.split()[0].lower()
                
                if first_name in male_names:
                    relation = "son"
                elif first_name in female_names:
                    relation = "daughter"
                else:
                    # If name not found in learned names, make educated guess
                    relation = "son"  # Default fallback
                    
                    # Try to find similar names (first 3 characters match)
                    for male_name in male_names:
                        if len(first_name) >= 3 and len(male_name) >= 3:
                            if first_name[:3] == male_name[:3]:
                                relation = "son"
                                break
                    
                    for female_name in female_names:
                        if len(first_name) >= 3 and len(female_name) >= 3:
                            if first_name[:3] == female_name[:3]:
                                relation = "daughter"
                                break

                if str(result).strip().lower() == "pass":
                    msg = f"Hello Mr. {father}. This is a message from your child's college. Your {relation} {name} has passed semester {sem} with SPI {spi}. Thank you."
                else:
                    msg = f"Hello Mr. {father}. This is a message from your child's college. Your {relation} {name} has failed semester {sem}. Please contact the college. Thank you."

                print(f"🔊 Message: {msg}")
                print(f"👤 Relation: {relation} (detected from CSV names)")
                print(f"📊 Result: {result} (SPI: {spi})")

                # FIXED: Create MP3 with better error handling
                try:
                    print(f"🎵 Generating audio for: {name}")
                    
                    # Create safe filename
                    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    audio_file_name = f"{safe_name.replace(' ', '_')}.mp3"
                    audio_file_path = os.path.join(AUDIO_FOLDER, audio_file_name)
                    
                    print(f"🎵 Audio file path: {audio_file_path}")
                    
                    # Generate TTS
                    tts = gTTS(text=msg, lang="en", tld='co.in', slow=True)
                    tts.save(audio_file_path)
                    
                    # ADDED: Verify file was created
                    if os.path.exists(audio_file_path):
                        file_size = os.path.getsize(audio_file_path)
                        print(f"✅ Audio file created successfully: {audio_file_path} ({file_size} bytes)")
                        audio_names.append((name, audio_file_name))
                    else:
                        print(f"❌ Audio file was not created: {audio_file_path}")
                        
                except Exception as audio_error:
                    print(f"❌ Audio generation failed for {name}: {str(audio_error)}")
                    # Continue with call even if audio fails
                    pass

                # Make the call
                try:
                    print(f"🚀 Initiating call...")
                    call = client.calls.create(
                        twiml=f'<Response><Say voice="alice" rate="slow">{msg}</Say></Response>',
                        to=phone_number,
                        from_=TWILIO_PHONE_NUMBER
                    )
                    print(f"✅ Call created successfully: {call.sid}")
                    call_results.append({
                        'name': name,
                        'roll_no': roll_no,
                        'father': father,
                        'phone': phone_number,
                        'status': 'Call initiated',
                        'call_sid': call.sid,
                        'message': msg,
                        'result': result,
                        'spi': spi,
                        'relation': relation
                    })
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"❌ Call failed for {name}: {str(e)}")
                    call_results.append({
                        'name': name,
                        'roll_no': roll_no,
                        'father': father,
                        'phone': phone_number,
                        'status': f'Call failed: {str(e)}',
                        'call_sid': None,
                        'message': msg,
                        'result': result,
                        'spi': spi,
                        'relation': relation
                    })

                count += 1

            # ADDED: Debug static folder serving
            print(f"🔍 AUDIO_FOLDER absolute path: {os.path.abspath(AUDIO_FOLDER)}")
            print(f"🔍 Flask static folder: {app.static_folder}")
            print(f"🔍 Flask static URL path: {app.static_url_path}")
            
            # ADDED: List actual files in static folder
            static_files = os.listdir(AUDIO_FOLDER) if os.path.exists(AUDIO_FOLDER) else []
            print(f"🔍 Files in static folder: {static_files}")

            # Generate HTML response
            html_response = f"<h3>✅ Processed {count} students.</h3>"
            html_response += f"<p>👨 Learned from {len(male_names)} father names: {', '.join(list(male_names)[:5])}...</p>"
            html_response += f"<p>👩 Learned from {len(female_names)} mother names: {', '.join(list(female_names)[:5])}...</p>"
            
            # FIXED: Audio previews with better error handling
            html_response += "<h4>Generated Audio Messages:</h4>"
            if audio_names:
                for name, filename in audio_names:
                    file_path = os.path.join(AUDIO_FOLDER, filename)
                    if os.path.exists(file_path):
                        html_response += f"""
                        <p><strong>{name}</strong>:</p>
                        <audio controls>
                            <source src="/static/{filename}" type="audio/mpeg">
                            Your browser does not support the audio element.
                        </audio><br><br>
                        """
                    else:
                        html_response += f"<p><strong>{name}</strong>: ❌ Audio file not found</p>"
            else:
                html_response += "<p>❌ No audio files were generated</p>"

            # Call results
            html_response += "<h4>📞 Call Results:</h4>"
            html_response += "<table border='1' style='border-collapse: collapse; width: 100%; font-family: Arial;'>"
            html_response += "<tr style='background-color: #f2f2f2;'><th>Roll No</th><th>Student</th><th>Father</th><th>Relation</th><th>Result</th><th>SPI</th><th>Phone</th><th>Status</th></tr>"
            
            for result in call_results:
                status_color = "green" if "initiated" in result['status'] else "red"
                result_color = "green" if result['result'].lower() == 'pass' else "red"
                html_response += f"""
                <tr>
                    <td><strong>{result['roll_no']}</strong></td>
                    <td>{result['name']}</td>
                    <td>{result['father']}</td>
                    <td><strong>{result['relation']}</strong></td>
                    <td style='color: {result_color}; font-weight: bold;'>{result['result']}</td>
                    <td>{result['spi']}</td>
                    <td>{result['phone']}</td>
                    <td style='color: {status_color};'>{result['status']}</td>
                </tr>
                """
            html_response += "</table>"
            
            # Summary
            successful_calls = len([r for r in call_results if 'initiated' in r['status']])
            failed_calls = len(call_results) - successful_calls
            html_response += f"""
            <h4>📊 Summary:</h4>
            <p>✅ <strong>Successful calls:</strong> {successful_calls}</p>
            <p>❌ <strong>Failed calls:</strong> {failed_calls}</p>
            <p>🎵 <strong>Audio files generated:</strong> {len(audio_names)}</p>
            <p>🧠 <strong>Gender detection:</strong> Learned from CSV data (no hardcoding)</p>
            """

            return html_response

    return render_template("index.html")

# ADDED: Custom route to serve audio files (backup solution)
@app.route('/static/<filename>')
def serve_static(filename):
    """Custom static file serving for debugging"""
    try:
        file_path = os.path.join(AUDIO_FOLDER, filename)
        if os.path.exists(file_path):
            from flask import send_file
            print(f"✅ Serving file: {file_path}")
            return send_file(file_path)
        else:
            print(f"❌ File not found: {file_path}")
            return f"File not found: {filename}", 404
    except Exception as e:
        print(f"❌ Error serving file {filename}: {str(e)}")
        return f"Error serving file: {str(e)}", 500
@app.route("/test_audio")
def test_audio():
    try:
        test_msg = "Hello, this is a test message from your college."
        tts = gTTS(text=test_msg, lang="en", tld='co.in', slow=True)
        audio_path = os.path.join(AUDIO_FOLDER, "test_audio.mp3")
        tts.save(audio_path)
        
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            return f"✅ Test audio created at: {audio_path} ({file_size} bytes)<br><audio controls><source src='/static/test_audio.mp3' type='audio/mpeg'></audio>"
        else:
            return "❌ Test audio file not found"
    except Exception as e:
        return f"❌ Test audio failed: {str(e)}"

@app.route("/call_status/<call_sid>")
def call_status(call_sid):
    """Check the status of a specific call"""
    try:
        call = client.calls(call_sid).fetch()
        return jsonify({
            'status': call.status,
            'duration': call.duration,
            'start_time': call.start_time,
            'end_time': call.end_time
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route("/make_single_call", methods=["POST"])
def make_single_call():
    """Make a single call for testing"""
    data = request.json
    phone_number = data.get('phone')
    message = data.get('message')
    
    # Clean and format phone number
    phone_number = phone_number.strip().replace('+91-', '').replace('+91', '').replace('-', '').replace(' ', '')
    if not phone_number.startswith('+'):
        phone_number = f"+91{phone_number}"
    
    print(f"🧪 Test call to: {phone_number}")
    print(f"💬 Message: {message}")
    
    try:
        call = client.calls.create(
            twiml=f'<Response><Say voice="alice" rate="slow">{message}</Say></Response>',
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER
        )
        print(f"✅ Test call successful: {call.sid}")
        return jsonify({
            'success': True,
            'call_sid': call.sid,
            'status': 'Call initiated'
        })
    except Exception as e:
        print(f"❌ Test call failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == "__main__":
    app.run(debug=True)


