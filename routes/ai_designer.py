# routes/ai_designer.py

from flask import Blueprint, request, jsonify
import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "habitlab"

def init_routes(app, db):
    bp = Blueprint("ai_designer", __name__)

    @bp.route("/designer", methods=["POST"])
    def designer():
        """
        This route receives a habit + goal from the frontend,
        sends them to the local Ollama model, and returns:
        - Strategy A
        - Strategy B
        - A measurable metric
        - A recommended duration
        """

        habit = request.json.get("habit", "").strip()
        goal = request.json.get("goal", "").strip()

        if not habit and not goal:
            return jsonify({
                "error": "Please enter at least a habit or a goal before generating."
            }), 400

        if not habit and goal:
            habit = f"A habit that helps with: {goal}"

        if habit and not goal:
            goal = f"Improve the habit: {habit}"

        prompt = f"habit: {habit}\ngoal: {goal}"

        def call_model():
            r = requests.post(OLLAMA_URL, json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            })
            return r.json().get("response", "").strip()

        def strategies_too_similar(a, b):
            if not a or not b:
                return True
            words_a = set(a.lower().split())
            words_b = set(b.lower().split())
            overlap = len(words_a & words_b) / max(len(words_a), len(words_b), 1)
            return overlap > 0.6

        raw = call_model()
        # Retry up to 2 more times if strategies are too similar
        for _ in range(2):
            # Parse quick check before full parse
            a_line = next((l for l in raw.replace("\\n","\n").splitlines() if l.lower().startswith("strategy a:")), "")
            b_line = next((l for l in raw.replace("\\n","\n").splitlines() if l.lower().startswith("strategy b:")), "")
            if not strategies_too_similar(a_line, b_line):
                break
            raw = call_model()
        print("=== RAW MODEL OUTPUT ===")
        print(repr(raw))
        print("========================")

        # Extract only the 4 lines we need
        # Handle both real newlines and literal \n characters
        raw = raw.replace("\\n", "\n")
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        result = {}
        for i, line in enumerate(lines):
            def get_value(line, prefix):
                # Value may be on same line or next line
                val = line.split(":", 1)[1].strip()
                if not val and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if not any(next_line.lower().startswith(k) for k in ["strategy a", "strategy b", "metric", "duration"]):
                        val = next_line
                return val

            if line.lower().startswith("strategy a:") and "strategy_a" not in result:
                result["strategy_a"] = get_value(line, "strategy a:")
            elif line.lower().startswith("strategy b:") and "strategy_b" not in result:
                result["strategy_b"] = get_value(line, "strategy b:")
            elif line.lower().startswith("metric:") and "metric" not in result:
                result["metric"] = get_value(line, "metric:")
            elif line.lower().startswith("duration:") and "duration" not in result:
                result["duration"] = get_value(line, "duration:")

        # Clean duration — extract just the number of days
        raw_duration = result.get('duration', '')
        duration_num = None
        # Look for a plain number first
        nums = re.findall(r'\d+', raw_duration)
        if nums:
            duration_num = nums[0]
        else:
            # Convert common text to days
            text_map = {
                'one week': '7', 'a week': '7', 'two weeks': '14',
                'three weeks': '21', 'a month': '30', 'one month': '30',
                'two months': '60', 'three days': '3', 'five days': '5',
                'ten days': '10', 'two days': '2', 'four days': '4'
            }
            for phrase, days in text_map.items():
                if phrase in raw_duration.lower():
                    duration_num = days
                    break
        duration_clean = duration_num if duration_num else '7'

        # Clean metric — strip any existing scale and always use 1-10
        raw_metric = result.get('metric', '')
        raw_metric = re.sub(r'\s*(from\s+(1|one)\b.*|on\s+a\s+scale\b.*|\(\s*(1|one)\b.*|\d+\s*[-–]\s*\d+.*)', '', raw_metric, flags=re.IGNORECASE).strip().rstrip('.,')


        # Format as clean text matching original output shape
        output = (
            f"Strategy A: {result.get('strategy_a', '')}\n"
            f"Strategy B: {result.get('strategy_b', '')}\n"
            f"Metric: {raw_metric.strip()}\n"
            f"Duration: {duration_clean}"
        )

        return jsonify({
            "habit": habit,
            "goal": goal,
            "experiment": output,
            "strategy_a": result.get("strategy_a", ""),
            "strategy_b": result.get("strategy_b", ""),
            "metric": raw_metric,
            "duration": duration_clean
        })

    app.register_blueprint(bp, url_prefix="/ai")
