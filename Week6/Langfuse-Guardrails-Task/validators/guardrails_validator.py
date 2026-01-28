from typing import Dict
import re
from guardrails.hub import ToxicLanguage


class GuardrailsValidator:
    """Guardrails AI using Hub ToxicLanguage validator"""

    def __init__(self):
        print("-> Loading Guardrails AI Hub validators...")
        try:
            # Use Hub ToxicLanguage validator for both input and output
            # Lower threshold = more sensitive (0.0-1.0)
            self.toxic_validator = ToxicLanguage(
                threshold=0.25,
                validation_method="sentence", 
                on_fail="exception"
            )
            
            # Topic restriction patterns
            self.invalid_patterns = [
                r"\bjoke\b", r"\btell.*joke\b", r"\bfunny\b",
                r"\bweather\b", r"\bsports?\b", r"\bmovies?\b", 
                r"\bmusic\b", r"\bgames?\b", r"\bentertain"
            ]
            
            # Greeting patterns (handled separately with friendly response)
            self.greeting_patterns = [
                r"^(hi|hello|hey|greetings?|good\s+(morning|afternoon|evening|day))[\s\.,!?]*$",
                r"\bhow\s+are\s+you\b", r"\bwhat'?s\s+up\b", r"\bhowdy\b"
            ]
            
            self.enabled = True
            print("-> Guardrails AI Hub loaded (ToxicLanguage + custom topic restriction)")
        except Exception as e:
            print(f"-> WARNING: Guardrails Hub validators not available: {e}")
            print("-> Continuing without guardrails")
            self.enabled = False

    def _check_greeting(self, text: str) -> bool:
        """Check if text is a greeting. Returns True if it's a greeting."""
        text_lower = text.lower().strip()
        
        for pattern in self.greeting_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _check_topic_restriction(self, text: str) -> bool:
        """Check if text violates topic restrictions. Returns True if allowed."""
        text_lower = text.lower()
        
        for pattern in self.invalid_patterns:
            if re.search(pattern, text_lower):
                return False
        
        return True

    def validate_input(self, user_input: str) -> Dict:
        if not self.enabled:
            return {"allowed": True, "message": None, "reason": None}
        
        try:
            # Check for greetings first
            if self._check_greeting(user_input):
                return {
                    "allowed": False,
                    "message": "Hello! I'm a research assistant designed to help you find information. How can I assist you with your research today?",
                    "reason": "greeting"
                }
            
            # Check topic restriction
            if not self._check_topic_restriction(user_input):
                return {
                    "allowed": False,
                    "message": "I'm designed to help with research. Please provide an appropriate research-related query.",
                    "reason": "topic_restriction"
                }
            
            # Check toxic language using Hub validator
            try:
                validated_output = self.toxic_validator.validate(user_input, metadata={})
                print(f"Validated Input: {validated_output}")
                if validated_output.get("outcome") == "fail":
                    return {"allowed": False, "message": f"I cannot process inappropriate content. {validated_output.get('error_message')}", "reason": "toxic_language"}
                return {"allowed": True, "message": None, "reason": None}
            except Exception as toxic_error:
                # Toxic language detected
                return {
                    "allowed": False,
                    "message": "I cannot process inappropriate content. Please rephrase your query.",
                    "reason": "toxic_language"
                }
            
        except Exception as e:
            print(f"Validation error: {e}")
            return {
                "allowed": False,
                "message": "I cannot process that request. Please provide a research-related query.",
                "reason": str(e)
            }

    def validate_output(self, output: str) -> Dict:
        if not self.enabled:
            return {"allowed": True, "modified_output": output, "reason": None}
        
        try:
            # Check toxic language in output using Hub validator
            try:
                validated_output = self.toxic_validator.validate(output, metadata={})
                if validated_output.get("outcome") == "fail":
                    raise ValueError("Toxic content detected in output")
                return {
                    "allowed": True,
                    "modified_output": output,
                    "reason": None
                }
            except Exception:
                # Toxic content in output
                return {
                    "allowed": False,
                    "modified_output": "I'm designed to help with research and information retrieval.",
                    "reason": "toxic_content_in_output"
                }
            
        except Exception as e:
            print(f"Output validation error: {e}")
            return {
                "allowed": False,
                "modified_output": "I'm designed to help with research and information retrieval.",
                "reason": str(e)
            }
