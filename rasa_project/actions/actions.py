from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from sarvamai import SarvamAI
import openai
import os
import logging
import re
import random
from email_utils import send_reset_email

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize SarvamAI and OpenAI
client = SarvamAI(api_subscription_key="b5d9635d-8168-411e-9ed8-0c2e33114f5a")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Email validation function
def is_valid_email(email: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

# Supported intents
INTENTS = {
    "login_issue": "Please try resetting your password. Do you need help?",
    "password_reset": "Please provide your registered email to receive the reset link.",
    "still_issue": "Sorry about that. I’ll escalate this issue to support.",
    "issue_not_fixed": "Understood. I’ll collect more details for support.",
    "need_human_support": "I’m connecting you to a support agent.",
    "thank_you": "You're welcome!",
    "greet": "Hello!",
    "goodbye": "Goodbye! Have a great day!",
    "how_are_you": "I'm doing great, thank you for asking!",
    "bot_name": "I'm your multilingual assistant.",
    "affirm": "Awesome!",
    "deny": "Alright, let me know if you need anything else.",
    "fallback": "Sorry, I didn’t understand that. \n Can you rephrase?",
    "work": "It should be working now! 😊\n But if you still face any issues, let me know — I’ll escalate it to human support for you."
}

FOLLOW_UPS = {
    "login_issue": ["Can you confirm your email or username for password reset?"],
    "password_reset": [
        "Please wait while we process the reset.",
        "Is there anything else I can help you with?"
    ],
    "still_issue": ["Did you receive any error message?", "Should I escalate this to support?"],
    "issue_not_fixed": ["Can you share your phone type or OS version?", "Do you see any error messages?"],
    "need_human_support": ["Connecting you now...", "Please stay online."],
    "thank_you": ["Happy to help!", "Feel free to ask anything anytime."],
    "goodbye": ["Talk to you soon.", "Hope your issue is resolved."],
    "greet": ["Nice to meet you!", "How can I assist you today?"],
    "how_are_you": ["Hope you're doing well too!", "Let me know how I can assist."],
    "fallback": ["Try asking in a different way.", "I'm learning constantly – help me improve!"]
}

class ActionMultilingualResponse(Action):
    def name(self) -> Text:
        return "action_multilingual_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("text", "")
        detected_intent = tracker.latest_message.get("intent", {}).get("name", "")
        lang_code = tracker.get_slot("user_lang") or "hi-IN"

        logger.info(f"[Action] Received: {user_message}")
        logger.info(f"[Action] Intent (initial): {detected_intent}")
        logger.info(f"[Action] Lang: {lang_code}")

        try:
            if detected_intent not in INTENTS:
                logger.info("[Action] Unknown intent – using OpenAI to classify.")
                translation = client.text.translate(
                    input=user_message,
                    source_language_code="auto",
                    target_language_code="en",
                    speaker_gender="Male",
                    mode="classic-colloquial",
                    model="mayura:v1",
                    enable_preprocessing=False
                )
                translated_input = translation.translated_text or user_message

                openai_prompt = (
                    "You are an intent classification assistant.\n"
                    f"The user said: \"{translated_input}\"\n"
                    "Which of the following intents best matches the user message?\n"
                    + ", ".join(INTENTS.keys()) + "\n"
                    "Return only the intent name."
                )

                gpt_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": openai_prompt}],
                    temperature=0
                )

                predicted_intent = gpt_response.choices[0].message['content'].strip()
                logger.info(f"[Action] GPT predicted intent: {predicted_intent}")
                intent = predicted_intent if predicted_intent in INTENTS else "fallback"
            else:
                intent = detected_intent

            if intent == "password_reset":
                email = tracker.get_slot("user_email")

                if not email or not is_valid_email(email):
                    prompt = "Please provide your registered email to send the password reset link."
                    translated_prompt = client.text.translate(
                        input=prompt,
                        source_language_code="auto",
                        target_language_code=lang_code,
                        speaker_gender="Male",
                        mode="classic-colloquial",
                        model="mayura:v1",
                        enable_preprocessing=False
                    )
                    dispatcher.utter_message(text=translated_prompt.translated_text or prompt)
                    return []
                else:
                    success = send_reset_email(email)
                    confirmation = (
                        "We’ve sent a password reset link to your email." if success
                        else "Failed to send reset email. Please try again later."
                    )
                    translated_confirm = client.text.translate(
                        input=confirmation,
                        source_language_code="auto",
                        target_language_code=lang_code,
                        speaker_gender="Male",
                        mode="classic-colloquial",
                        model="mayura:v1",
                        enable_preprocessing=False
                    )
                    dispatcher.utter_message(text=translated_confirm.translated_text or confirmation)
                    return []

            base_response = INTENTS[intent]
            translated_response = client.text.translate(
                input=base_response,
                source_language_code="auto",
                target_language_code=lang_code,
                speaker_gender="Male",
                mode="classic-colloquial",
                model="mayura:v1",
                enable_preprocessing=False
            )
            dispatcher.utter_message(text=translated_response.translated_text or base_response)

            followups = FOLLOW_UPS.get(intent, [])
            if followups:
                prompt = random.choice(followups)
                followup_translation = client.text.translate(
                    input=prompt,
                    source_language_code="auto",
                    target_language_code=lang_code,
                    speaker_gender="Male",
                    mode="classic-colloquial",
                    model="mayura:v1",
                    enable_preprocessing=False
                )
                dispatcher.utter_message(text=followup_translation.translated_text or prompt)

        except Exception as e:
            logger.error(f"[Action] Error in multilingual response: {e}")
            dispatcher.utter_message(text="Sorry, something went wrong while processing your request.")

        return []

class ActionSendResetEmail(Action):
    def name(self) -> Text:
        return "action_send_reset_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        lang_code = tracker.get_slot("user_lang") or "hi-IN"
        email = tracker.get_slot("user_email")

        if not email or not is_valid_email(email):
            message = "Invalid or missing email. Please provide a valid registered email."
        else:
            success = send_reset_email(email)
            message = (
                "We’ve sent a password reset link to your email."
                if success else
                "Failed to send reset email. Please try again later."
            )

        try:
            translation = client.text.translate(
                input=message,
                source_language_code="auto",
                target_language_code=lang_code,
                speaker_gender="Male",
                mode="classic-colloquial",
                model="mayura:v1",
                enable_preprocessing=False
            )
            dispatcher.utter_message(text=translation.translated_text or message)
        except Exception as e:
            logger.error(f"[ActionSendResetEmail] Translation or send failed: {e}")
            dispatcher.utter_message(text=message)

        return []