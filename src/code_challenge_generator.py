import openai
import os
import logging
from dotenv import load_dotenv
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_code_challenge(job_details, candidate_experience_level, technology_stack, difficulty="medium", duration_minutes=30):
    """
    Generate a code challenge tailored to the job and candidate.

    Args:
        job_details (dict): Job description and requirements
        candidate_experience_level (str): 'junior', 'mid', 'senior', 'lead'
        technology_stack (list): List of technologies (e.g., ['.NET', 'C#', 'SQL'])
        difficulty (str): 'easy', 'medium', 'hard'
        duration_minutes (int): Time allocated for the challenge

    Returns:
        dict: Code challenge with problem, solution, test cases, and evaluation criteria
    """
    logging.info(f"Generating code challenge for {candidate_experience_level} level in {technology_stack}")

    try:
        prompt = f"""
        Create a practical code challenge for a live coding interview.

        JOB CONTEXT:
        {json.dumps(job_details, indent=2)}

        CANDIDATE LEVEL: {candidate_experience_level}
        TECHNOLOGY STACK: {', '.join(technology_stack)}
        DIFFICULTY: {difficulty}
        TIME LIMIT: {duration_minutes} minutes

        Generate a challenge that:
        1. Is realistic and relevant to the job
        2. Can be completed in the time limit
        3. Tests practical problem-solving, not just theory
        4. Has clear requirements and constraints
        5. Includes edge cases to consider

        Provide:
        - Problem description (clear and concise)
        - Input/Output examples
        - Constraints and requirements
        - Sample solution (well-commented)
        - Test cases (including edge cases)
        - Evaluation criteria (what to look for)
        - Common mistakes to watch for
        - Follow-up questions to deepen discussion
        - Hints (if candidate gets stuck)

        Return as structured JSON.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert technical interviewer specializing in creating effective code challenges."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            response_format={"type": "json_object"}
        )

        challenge = json.loads(response.choices[0].message.content)

        # Add metadata
        challenge["metadata"] = {
            "difficulty": difficulty,
            "duration_minutes": duration_minutes,
            "technology_stack": technology_stack,
            "candidate_level": candidate_experience_level
        }

        logging.info("Code challenge generated successfully")
        return challenge

    except Exception as e:
        logging.error(f"Error generating code challenge: {str(e)}")
        return {"error": f"Failed to generate code challenge: {str(e)}"}

def generate_multiple_challenges(job_details, candidate_experience_level, technology_stack, count=3):
    """
    Generate multiple code challenges of varying difficulty.

    Args:
        job_details (dict): Job details
        candidate_experience_level (str): Experience level
        technology_stack (list): Technologies to use
        count (int): Number of challenges to generate

    Returns:
        list: List of code challenges
    """
    logging.info(f"Generating {count} code challenges")

    difficulties = ["easy", "medium", "hard"]
    challenges = []

    for i in range(min(count, len(difficulties))):
        difficulty = difficulties[i]
        duration = 20 if difficulty == "easy" else 30 if difficulty == "medium" else 45

        challenge = generate_code_challenge(
            job_details,
            candidate_experience_level,
            technology_stack,
            difficulty,
            duration
        )

        if "error" not in challenge:
            challenges.append(challenge)

    logging.info(f"Generated {len(challenges)} challenges successfully")
    return challenges

def generate_system_design_challenge(job_details, candidate_experience_level):
    """
    Generate a system design challenge for senior/lead positions.

    Args:
        job_details (dict): Job details
        candidate_experience_level (str): Experience level

    Returns:
        dict: System design challenge
    """
    logging.info("Generating system design challenge")

    try:
        prompt = f"""
        Create a system design challenge for a {candidate_experience_level} level interview.

        JOB CONTEXT:
        {json.dumps(job_details, indent=2)}

        Generate a realistic system design problem that:
        1. Is relevant to the job domain
        2. Can be discussed in 30-45 minutes
        3. Tests architectural thinking
        4. Has multiple valid approaches
        5. Allows for trade-off discussions

        Provide:
        - Problem statement
        - Requirements (functional and non-functional)
        - Constraints (scale, performance, etc.)
        - Expected components/discussion points
        - Evaluation criteria
        - Key trade-offs to discuss
        - Red flags (poor design choices)
        - Follow-up questions

        Return as structured JSON.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in system design interviews for senior engineering positions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            response_format={"type": "json_object"}
        )

        challenge = json.loads(response.choices[0].message.content)
        challenge["challenge_type"] = "system_design"

        logging.info("System design challenge generated successfully")
        return challenge

    except Exception as e:
        logging.error(f"Error generating system design challenge: {str(e)}")
        return {"error": f"Failed to generate system design challenge: {str(e)}"}

def generate_debugging_challenge(technology_stack):
    """
    Generate a debugging challenge with intentional bugs.

    Args:
        technology_stack (list): Technologies to use

    Returns:
        dict: Debugging challenge with buggy code and solutions
    """
    logging.info("Generating debugging challenge")

    try:
        prompt = f"""
        Create a debugging challenge for technologies: {', '.join(technology_stack)}

        Generate code with 3-5 intentional bugs that:
        1. Are realistic mistakes developers make
        2. Range from syntax to logic errors
        3. Test understanding of the language/framework
        4. Can be found in 15-20 minutes

        Provide:
        - Buggy code snippet (with line numbers)
        - Expected behavior
        - Actual behavior (what goes wrong)
        - List of bugs with locations
        - Fixed code
        - Explanation of each bug
        - What to look for in candidate's approach

        Return as structured JSON.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at creating effective debugging exercises."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        challenge = json.loads(response.choices[0].message.content)
        challenge["challenge_type"] = "debugging"

        logging.info("Debugging challenge generated successfully")
        return challenge

    except Exception as e:
        logging.error(f"Error generating debugging challenge: {str(e)}")
        return {"error": f"Failed to generate debugging challenge: {str(e)}"}

def create_challenge_suite(job_details, resume_analysis, meeting_insights):
    """
    Create a complete suite of code challenges based on all inputs.

    Args:
        job_details (dict): Job details
        resume_analysis (dict): Candidate resume analysis
        meeting_insights (dict): Client meeting insights

    Returns:
        dict: Complete challenge suite with multiple types
    """
    logging.info("Creating complete challenge suite")

    try:
        # Extract candidate info
        candidate_level = resume_analysis.get("analysis", {}).get("key_info", {}).get("current_role", "mid")

        # Determine if senior/lead
        years_exp = resume_analysis.get("analysis", {}).get("key_info", {}).get("years_of_experience", 3)
        if years_exp >= 7:
            candidate_level = "senior"
        elif years_exp >= 10:
            candidate_level = "lead"

        # Extract technology stack from job details
        tech_stack = []
        job_title = job_details.get("title", "").lower()

        if ".net" in job_title or "c#" in job_title:
            tech_stack = [".NET", "C#", "SQL Server"]
        elif "java" in job_title:
            tech_stack = ["Java", "Spring", "SQL"]
        elif "python" in job_title:
            tech_stack = ["Python", "Django/Flask", "PostgreSQL"]
        elif "javascript" in job_title or "react" in job_title or "node" in job_title:
            tech_stack = ["JavaScript", "React", "Node.js"]
        else:
            tech_stack = ["General Programming"]

        suite = {
            "coding_challenges": [],
            "system_design": None,
            "debugging_challenge": None
        }

        # Check if code challenges are needed
        if meeting_insights.get("insights", {}).get("code_challenge_needed", True):
            # Generate coding challenges
            suite["coding_challenges"] = generate_multiple_challenges(
                job_details,
                candidate_level,
                tech_stack,
                count=2  # Generate 2 challenges to choose from
            )

            # Generate system design for senior+
            if candidate_level in ["senior", "lead"]:
                suite["system_design"] = generate_system_design_challenge(
                    job_details,
                    candidate_level
                )

            # Generate debugging challenge
            suite["debugging_challenge"] = generate_debugging_challenge(tech_stack)

        logging.info("Complete challenge suite created successfully")
        return suite

    except Exception as e:
        logging.error(f"Error creating challenge suite: {str(e)}")
        return {"error": f"Failed to create challenge suite: {str(e)}"}
