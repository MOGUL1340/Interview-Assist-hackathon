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

def generate_additional_questions_for_topic(topic_name, num_questions, resume_analysis, job_details):
    """
    Generate additional interview questions for a specific topic.

    Args:
        topic_name (str): Name of the topic
        num_questions (int): Number of questions to generate
        resume_analysis (dict): Candidate's resume analysis
        job_details (dict): Job details

    Returns:
        list: List of question objects with question, what_to_look_for, and follow_up
    """
    logging.info(f"Generating {num_questions} additional questions for topic: {topic_name}")

    try:
        prompt = f"""
        Generate exactly {num_questions} interview questions for the topic: "{topic_name}"

        Context:
        - Job: {job_details.get('title', 'Technical Position')}
        - Job Requirements: {job_details.get('description', 'N/A')}
        - Candidate Skills: {', '.join(resume_analysis.get('skills', [])[:10])}

        CRITICAL: Return a JSON array with EXACTLY {num_questions} question objects.

        Each question object must have this structure:
        {{
            "question": "The interview question text",
            "what_to_look_for": "What the interviewer should look for in the answer",
            "follow_up": "A relevant follow-up question"
        }}

        Return ONLY the JSON array, no other text.
        Example format:
        [
            {{"question": "...", "what_to_look_for": "...", "follow_up": "..."}},
            {{"question": "...", "what_to_look_for": "...", "follow_up": "..."}}
        ]
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert technical interviewer. Generate interview questions in JSON format only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        logging.info(f"GPT-4 response for additional questions: {content[:200]}...")

        # Parse the response
        data = json.loads(content)

        # Handle different response formats
        questions = []
        if isinstance(data, list):
            questions = data
        elif 'questions' in data:
            questions = data['questions']
        elif 'question_list' in data:
            questions = data['question_list']
        else:
            # Try to find any array in the response
            for value in data.values():
                if isinstance(value, list) and value:
                    questions = value
                    break

        logging.info(f"Parsed {len(questions)} additional questions for topic '{topic_name}'")

        # Ensure we have the right structure
        validated_questions = []
        for q in questions[:num_questions]:
            if isinstance(q, dict) and 'question' in q:
                validated_questions.append({
                    "question": q.get("question", ""),
                    "what_to_look_for": q.get("what_to_look_for", ""),
                    "follow_up": q.get("follow_up", "")
                })

        return validated_questions

    except Exception as e:
        logging.error(f"Error generating additional questions: {str(e)}")
        # Return fallback questions if generation fails
        fallback_questions = []
        for i in range(num_questions):
            fallback_questions.append({
                "question": f"Question {i+1} about {topic_name}",
                "what_to_look_for": "Look for understanding of core concepts",
                "follow_up": "Can you provide a specific example?"
            })
        return fallback_questions

def generate_interview_plan(resume_analysis, meeting_insights, job_details, time_limit_minutes=30):
    """
    Generate a comprehensive interview plan based on all inputs.

    Args:
        resume_analysis (dict): Analysis of candidate's resume
        meeting_insights (dict): Insights extracted from client meeting
        job_details (dict): Job description and requirements
        time_limit_minutes (int): Interview duration in minutes

    Returns:
        dict: Structured interview plan with topics, questions, and evaluation criteria
    """
    logging.info("Generating interview plan")

    try:
        # Prepare context for GPT
        context = f"""
        You are an expert interview preparation assistant for senior technical positions.
        Generate a comprehensive, structured interview plan based on the following information:

        CANDIDATE RESUME ANALYSIS:
        {json.dumps(resume_analysis, indent=2)}

        CLIENT MEETING INSIGHTS:
        {json.dumps(meeting_insights, indent=2)}

        JOB DETAILS:
        {json.dumps(job_details, indent=2)}

        INTERVIEW DURATION: {time_limit_minutes} minutes

        Generate a detailed interview plan with the following structure:
        1. Interview Overview (objectives, key focus areas)
        2. Time Allocation (breakdown by section)
        3. Topics to Cover (prioritized list with time allocations)
        4. Specific Questions (categorized by topic, with follow-up questions)
        5. Evaluation Criteria (scoring rubric for each topic)
        6. Red Flags to Watch For
        7. Code Challenge Requirements (if applicable)
        8. Candidate Questions Section (anticipated questions from candidate)

        For each question, provide:
        - The question text
        - Why this question is important
        - What to look for in the answer
        - Follow-up questions
        - Scoring criteria (1-5 scale)

        Ensure the plan is:
        - Specific to the candidate's background
        - Aligned with client requirements
        - Realistic for the time constraint
        - Unbiased and professional
        - Focused on technical depth for senior roles

        Return the complete interview plan as a structured JSON object.
        """

        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4 for better quality
            messages=[
                {"role": "system", "content": "You are an expert technical recruiter and interview preparation specialist with deep knowledge of software engineering roles."},
                {"role": "user", "content": context}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        plan = json.loads(response.choices[0].message.content)
        logging.info("Interview plan generated successfully")

        # Log the full plan structure for debugging
        logging.info(f"Main plan keys: {list(plan.keys())}")
        logging.info(f"Main plan structure (first 1000 chars): {json.dumps(plan, indent=2)[:1000]}")

        # Extract candidate name from resume analysis
        candidate_name = "Unknown"
        if isinstance(resume_analysis, dict):
            # Log resume analysis structure to debug
            logging.info(f"Resume analysis keys for name extraction: {list(resume_analysis.keys())}")

            # Try different possible paths to candidate name
            candidate_name = (
                resume_analysis.get("analysis", {}).get("analysis", {}).get("key_info", {}).get("name") or
                resume_analysis.get("analysis", {}).get("key_info", {}).get("name") or
                resume_analysis.get("key_info", {}).get("name") or
                resume_analysis.get("name") or
                resume_analysis.get("candidate_name") or
                "Unknown"
            )
            logging.info(f"Extracted candidate name: {candidate_name}")

        # Add metadata
        job_title = job_details.get("title") or job_details.get("description", "Position")[:50] if job_details else "Position"

        from datetime import datetime
        plan["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "time_limit_minutes": time_limit_minutes,
            "candidate_name": candidate_name,
            "job_title": job_title
        }

        logging.info(f"Metadata created - job_title: {job_title}, candidate_name: {candidate_name}")

        return plan

    except Exception as e:
        logging.error(f"Error generating interview plan: {str(e)}")
        return {"error": f"Failed to generate interview plan: {str(e)}"}

def prioritize_topics(resume_analysis, meeting_insights, time_limit_minutes, job_details=None):
    """
    Prioritize topics based on importance and time available.

    Args:
        resume_analysis (dict): Candidate resume analysis
        meeting_insights (dict): Client meeting insights
        time_limit_minutes (int): Available interview time
        job_details (dict): Job requirements and details

    Returns:
        list: Prioritized list of topics with time allocations
    """
    logging.info("Prioritizing interview topics")

    try:
        # Calculate available time for topics (reserve time for intro, questions, wrap-up)
        reserved_time = 10  # 3 intro + 5 candidate questions + 2 wrap-up
        available_time = time_limit_minutes - reserved_time

        context = f"""
        Based on the following information, create a prioritized list of topics to cover in the interview.

        CANDIDATE BACKGROUND:
        {json.dumps(resume_analysis, indent=2)}

        CLIENT REQUIREMENTS:
        {json.dumps(meeting_insights, indent=2)}

        JOB DETAILS:
        {json.dumps(job_details, indent=2) if job_details else "N/A"}

        TOTAL INTERVIEW TIME: {time_limit_minutes} minutes
        AVAILABLE TIME FOR TOPICS: {available_time} minutes (after reserving {reserved_time} minutes for intro/outro)

        CRITICAL INSTRUCTIONS FOR TIME ALLOCATION:
        1. Generate 5-8 topics based on importance and relevance
        2. Allocate time to each topic so that the SUM of all allocated_time equals {available_time} minutes
        3. Higher priority topics should get more time
        4. Each topic should have at least 5 minutes and at most 15 minutes

        For EACH topic, you MUST provide:
        - topic_name: Name of the topic
        - priority: Priority level (1-5, where 5 is highest)
        - allocated_time: Time allocated in minutes (ensure total = {available_time})
        - rationale: Why this topic is important
        - questions: Array of 3-5 DIVERSE interview questions for THIS SPECIFIC TOPIC

        For EACH question in the questions array, provide:
        - question: The actual question text
        - what_to_look_for: What to evaluate in the candidate's answer
        - follow_up: Follow-up question or probe
        - scoring_criteria: How to score this question (1-5 scale)

        VALIDATION BEFORE RESPONDING:
        - Check that EVERY topic has a 'questions' array
        - Check that EVERY questions array has 3-5 questions (not less, not more)
        - Check that questions are specific and relevant to their topic
        - Check that SUM of all allocated_time equals {available_time} minutes
        - If validation fails, fix the issues before responding

        Return as JSON with a 'topics' array. Each topic MUST have 3-5 questions and correct time allocation.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert at planning efficient and effective interviews. You ALWAYS generate 3-5 questions for each topic without exception."},
                {"role": "user", "content": context}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        topics = result.get("topics", [])

        # Log topic structure for debugging
        if topics:
            first_topic = topics[0]
            logging.info(f"First topic structure: {json.dumps(first_topic, indent=2)[:500]}")

        # Validate time allocation
        total_allocated = sum(topic.get('allocated_time', 0) for topic in topics)
        logging.info(f"Total time allocated: {total_allocated} minutes (expected: {available_time} minutes)")

        if abs(total_allocated - available_time) > 5:
            logging.warning(f"Time allocation mismatch! Total: {total_allocated}, Expected: {available_time}")
            # Adjust time proportionally
            if total_allocated > 0:
                adjustment_factor = available_time / total_allocated
                for topic in topics:
                    original_time = topic.get('allocated_time', 0)
                    topic['allocated_time'] = max(5, round(original_time * adjustment_factor))
                logging.info(f"Adjusted time allocation to match {available_time} minutes")

        logging.info(f"Prioritized {len(topics)} topics successfully")
        return topics

    except Exception as e:
        logging.error(f"Error prioritizing topics: {str(e)}")
        return []

def generate_evaluation_rubric(topics):
    """
    Generate scoring rubric for interview evaluation.

    Args:
        topics (list): List of topics to be covered

    Returns:
        dict: Evaluation rubric with scoring guidelines
    """
    logging.info("Generating evaluation rubric")

    try:
        prompt = f"""
        Create a comprehensive evaluation rubric for an interview covering these topics:
        {json.dumps(topics, indent=2)}

        For each topic, provide:
        - Scoring scale (1-5)
        - What each score means (detailed descriptors)
        - Key indicators for each score level
        - Weight/importance (percentage)

        Also include:
        - Overall evaluation guidelines
        - Decision framework (hire/no-hire thresholds)
        - Special considerations

        Return as structured JSON.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at creating fair and effective evaluation criteria."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        rubric = json.loads(response.choices[0].message.content)
        logging.info("Evaluation rubric generated successfully")
        logging.info(f"Rubric keys: {list(rubric.keys()) if isinstance(rubric, dict) else 'Not a dict'}")
        logging.info(f"Rubric structure (first 500 chars): {json.dumps(rubric, indent=2)[:500]}")

        # Unwrap if GPT wrapped it in evaluation_rubric key
        if "evaluation_rubric" in rubric and len(rubric) == 1:
            rubric = rubric["evaluation_rubric"]
            logging.info("Unwrapped evaluation_rubric from response")

        # Ensure decision_framework exists with correct structure
        if "decision_framework" not in rubric:
            logging.warning("decision_framework missing from rubric, adding default")
            rubric["decision_framework"] = {
                "hire_threshold": 70,
                "no_hire_threshold": 50
            }
        else:
            # Validate threshold values
            df = rubric["decision_framework"]
            if "hire_threshold" not in df or not isinstance(df.get("hire_threshold"), (int, float)):
                logging.warning("hire_threshold missing or invalid, setting to 70")
                df["hire_threshold"] = 70
            if "no_hire_threshold" not in df or not isinstance(df.get("no_hire_threshold"), (int, float)):
                logging.warning("no_hire_threshold missing or invalid, setting to 50")
                df["no_hire_threshold"] = 50

        return rubric

    except Exception as e:
        logging.error(f"Error generating evaluation rubric: {str(e)}")
        return {}

def create_complete_interview_plan(resume_analysis, meeting_insights, job_details, time_limit_minutes=30):
    """
    Create a complete interview plan with all components.

    Args:
        resume_analysis (dict): Resume analysis
        meeting_insights (dict): Meeting insights
        job_details (dict): Job details
        time_limit_minutes (int): Interview duration

    Returns:
        dict: Complete interview plan ready for export
    """
    logging.info("Creating complete interview plan")

    try:
        # Log resume analysis structure for debugging candidate name extraction
        logging.info(f"Resume analysis keys: {list(resume_analysis.keys()) if isinstance(resume_analysis, dict) else 'Not a dict'}")
        if isinstance(resume_analysis, dict):
            logging.info(f"Resume analysis structure (first 500 chars): {json.dumps(resume_analysis, indent=2)[:500]}")

        # Generate main plan
        main_plan = generate_interview_plan(resume_analysis, meeting_insights, job_details, time_limit_minutes)

        if "error" in main_plan:
            return main_plan

        # Prioritize topics
        prioritized_topics = prioritize_topics(resume_analysis, meeting_insights, time_limit_minutes, job_details)

        # Generate evaluation rubric
        rubric = generate_evaluation_rubric(prioritized_topics)

        # Log the raw main_plan structure first
        logging.info("=" * 80)
        logging.info("RAW MAIN_PLAN STRUCTURE FROM GPT-4:")
        logging.info(f"Main plan keys: {list(main_plan.keys()) if isinstance(main_plan, dict) else 'Not a dict'}")
        if 'prioritized_topics' in main_plan:
            logging.info(f"prioritized_topics in main_plan: YES, count={len(main_plan['prioritized_topics'])}")
            if main_plan['prioritized_topics']:
                first_topic = main_plan['prioritized_topics'][0]
                logging.info(f"First topic from main_plan: {json.dumps(first_topic, indent=2)[:800]}")
        else:
            logging.info("prioritized_topics in main_plan: NO")
        logging.info("=" * 80)

        # Normalize the structure for frontend compatibility
        # Convert camelCase keys from GPT to snake_case/expected format
        # GPT sometimes returns {interviewPlan: {...}} and sometimes returns data directly
        if 'interviewPlan' in main_plan:
            interview_plan_data = main_plan['interviewPlan']
        elif 'interview_overview' in main_plan:
            interview_plan_data = main_plan['interview_overview']
        else:
            # Data is directly in main_plan
            interview_plan_data = main_plan

        logging.info(f"Interview plan data type: {type(interview_plan_data)}")
        logging.info(f"Interview plan data keys: {list(interview_plan_data.keys()) if isinstance(interview_plan_data, dict) else 'Not a dict'}")
        if isinstance(interview_plan_data, dict):
            logging.info(f"Interview plan data structure (first 500 chars): {json.dumps(interview_plan_data, indent=2)[:500]}")

        # Extract interview overview (objectives)
        interview_overview = interview_plan_data.get('interviewOverview') or interview_plan_data.get('interview_overview') or {}
        logging.info(f"Extracted interview_overview keys: {list(interview_overview.keys()) if isinstance(interview_overview, dict) else 'Not a dict'}")

        # Validate and normalize questions in prioritized_topics
        # Questions should already be generated by prioritize_topics() function
        for idx, topic in enumerate(prioritized_topics):
            topic_name = topic.get('topic_name') or topic.get('topic') or ''
            logging.info(f"Processing topic #{idx}: '{topic_name}'")

            # Check if topic has questions from GPT
            questions = topic.get('questions', [])
            if not isinstance(questions, list):
                questions = []
                topic['questions'] = questions

            logging.info(f"Topic '{topic_name}' has {len(questions)} questions from GPT")

            # Validate that we have 3-5 questions per topic
            if len(questions) < 3:
                logging.error(f"ERROR: Topic '{topic_name}' has only {len(questions)} questions! Expected 3-5.")
                # Generate fallback questions if GPT failed
                logging.info(f"Generating {3 - len(questions)} fallback questions for topic '{topic_name}'")
                for i in range(3 - len(questions)):
                    questions.append({
                        "question": f"Can you discuss your experience with {topic_name.lower()}?",
                        "what_to_look_for": "Depth of experience, specific examples, problem-solving approach",
                        "follow_up": "Can you provide a specific example from your work?",
                        "scoring_criteria": "1=No experience, 3=Some experience, 5=Expert level with concrete examples"
                    })
            elif len(questions) > 5:
                logging.warning(f"Topic '{topic_name}' has {len(questions)} questions, keeping first 5")
                topic['questions'] = questions[:5]

            logging.info(f"Final: topic '{topic_name}' has {len(topic['questions'])} questions")

            # Normalize time field - GPT might return allocated_time instead of allocated_time_minutes
            if 'allocated_time' in topic and 'allocated_time_minutes' not in topic:
                topic['allocated_time_minutes'] = topic['allocated_time']

            # Ensure time is in correct format
            if 'allocated_time_minutes' in topic:
                try:
                    topic['allocated_time_minutes'] = int(topic['allocated_time_minutes'])
                except (ValueError, TypeError):
                    topic['allocated_time_minutes'] = 0
            else:
                topic['allocated_time_minutes'] = 0

            # Normalize question structure if needed
            if 'questions' in topic and topic['questions']:
                logging.info(f"Topic '{topic_name}' has {len(topic['questions'])} questions")
                for i, question in enumerate(topic['questions']):
                    # Ensure question has expected fields
                    if isinstance(question, str):
                        # If question is just a string, convert to object
                        topic['questions'][i] = {
                            'question': question,
                            'what_to_look_for': '',
                            'scoring_criteria': ''
                        }
                        logging.info(f"Converted question {i+1} from string to object")
            else:
                logging.warning(f"Topic '{topic_name}' has no questions!")

        # Combine everything
        complete_plan = {
            "metadata": main_plan.get("metadata", {}),
            "interview_overview": interview_overview if isinstance(interview_overview, dict) else {"objectives": []},
            "prioritized_topics": prioritized_topics,
            "topics_to_cover": prioritized_topics,  # Alias for compatibility
            "evaluation_rubric": rubric,
            "red_flags": interview_plan_data.get("redFlags") or interview_plan_data.get("red_flags") or [],
            "candidate_questions": interview_plan_data.get("candidateQuestionsSection") or interview_plan_data.get("candidate_questions") or []
        }

        logging.info("Complete interview plan created successfully")
        logging.info("=" * 80)
        logging.info("FINAL COMPLETE PLAN STRUCTURE:")
        logging.info(f"Final complete plan - interview_overview has objectives: {'objectives' in complete_plan['interview_overview']}")
        if 'objectives' in complete_plan['interview_overview']:
            logging.info(f"Objectives count: {len(complete_plan['interview_overview']['objectives']) if isinstance(complete_plan['interview_overview']['objectives'], list) else 'Not a list'}")
        logging.info(f"Topics count: {len(prioritized_topics)}")
        if prioritized_topics:
            logging.info(f"First topic keys: {list(prioritized_topics[0].keys())}")
            logging.info(f"First topic has questions: {'questions' in prioritized_topics[0]}")
            if 'questions' in prioritized_topics[0]:
                logging.info(f"First topic questions count: {len(prioritized_topics[0]['questions'])}")
                if prioritized_topics[0]['questions']:
                    logging.info(f"First question: {json.dumps(prioritized_topics[0]['questions'][0], indent=2)[:300]}")
        logging.info("=" * 80)
        return complete_plan

    except Exception as e:
        logging.error(f"Error creating complete interview plan: {str(e)}")
        return {"error": f"Failed to create complete plan: {str(e)}"}
