import openai
import os
import logging
from dotenv import load_dotenv
import tempfile

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(audio_file_path):
    """
    Transcribe audio/video file using OpenAI Whisper API.

    Args:
        audio_file_path (str): Path to the audio/video file

    Returns:
        dict: Transcription result with text and metadata
    """
    logging.info(f"Starting transcription for file: {audio_file_path}")

    try:
        with open(audio_file_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                language="en"  # Can be auto-detected if not specified
            )

        logging.info("Transcription completed successfully")

        return {
            "text": transcript.text,
            "language": transcript.language if hasattr(transcript, 'language') else "en",
            "duration": transcript.duration if hasattr(transcript, 'duration') else None,
            "segments": transcript.segments if hasattr(transcript, 'segments') else []
        }

    except Exception as e:
        logging.error(f"Error during transcription: {str(e)}")
        return {"error": f"Transcription failed: {str(e)}"}

def transcribe_from_base64(base64_content, file_extension="mp3"):
    """
    Transcribe audio from base64 encoded content.

    Args:
        base64_content (str): Base64 encoded audio content
        file_extension (str): File extension (mp3, wav, m4a, etc.)

    Returns:
        dict: Transcription result
    """
    import base64

    logging.info("Transcribing from base64 content")

    try:
        # Decode base64 content
        audio_data = base64.b64decode(base64_content)

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name

        # Transcribe
        result = transcribe_audio(temp_file_path)

        # Clean up temporary file
        os.unlink(temp_file_path)

        return result

    except Exception as e:
        logging.error(f"Error transcribing from base64: {str(e)}")
        return {"error": f"Failed to transcribe from base64: {str(e)}"}

def extract_meeting_insights(transcript_text):
    """
    Extract key insights from meeting transcript using GPT.

    Args:
        transcript_text (str): Full meeting transcript

    Returns:
        dict: Extracted insights including requirements, candidate expectations, etc.
    """
    logging.info("Extracting meeting insights from transcript")

    try:
        prompt = f"""
        Analyze the following meeting transcript between a client and recruiter about a job position.
        Extract and structure the following information:

        1. Job Requirements (technical skills, experience level, education)
        2. Candidate Expectations (soft skills, cultural fit, team dynamics)
        3. Interview Duration (if mentioned)
        4. Specific Topics to Cover (areas of focus during interview)
        5. Red Flags to Watch For (concerns mentioned by client)
        6. Code Challenge Requirements (if live coding is needed)

        Transcript:
        {transcript_text}

        Provide the response in JSON format with these keys:
        - job_requirements
        - candidate_expectations
        - interview_duration_minutes
        - topics_to_cover (array)
        - red_flags (array)
        - code_challenge_needed (boolean)
        - code_challenge_details (if applicable)
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing meeting transcripts and extracting structured information about job interviews."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        import json
        insights = json.loads(response.choices[0].message.content)
        logging.info("Meeting insights extracted successfully")

        return insights

    except Exception as e:
        logging.error(f"Error extracting meeting insights: {str(e)}")
        return {"error": f"Failed to extract insights: {str(e)}"}

def process_meeting_recording(audio_file_path_or_base64, is_base64=False, file_extension="mp3"):
    """
    Complete pipeline: transcribe meeting and extract insights.

    Args:
        audio_file_path_or_base64: File path or base64 content
        is_base64 (bool): Whether input is base64 encoded
        file_extension (str): File extension if using base64

    Returns:
        dict: Complete analysis with transcript and insights
    """
    logging.info("Starting meeting recording processing")

    # Transcribe
    if is_base64:
        transcription = transcribe_from_base64(audio_file_path_or_base64, file_extension)
    else:
        transcription = transcribe_audio(audio_file_path_or_base64)

    if "error" in transcription:
        return transcription

    # Extract insights
    insights = extract_meeting_insights(transcription["text"])

    result = {
        "transcript": transcription,
        "insights": insights
    }

    logging.info("Meeting recording processing completed")
    return result
