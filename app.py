from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global variable to store rules
rules = []
rule_counter = 1  # To keep track of rule IDs

def evaluate_condition(condition, data):
    """Evaluate a single condition against provided data."""
    try:
        parts = condition.split()
        if len(parts) != 3:  # Ensure there are exactly 3 parts
            print(f"Invalid condition format: '{condition}'")
            return False
        
        attribute, operator, value = parts
        value = int(value) if value.isdigit() else value.strip("'")

        # Debugging: Check the values being evaluated
        print(f"Evaluating condition: {attribute} {operator} {value} against data: {data}")

        # Use data.get() to handle missing attributes gracefully
        if operator == ">":
            return data.get(attribute, float('-inf')) > value
        elif operator == "<":
            return data.get(attribute, float('inf')) < value
        elif operator == ">=":
            return data.get(attribute, float('-inf')) >= value
        elif operator == "<=":
            return data.get(attribute, float('inf')) <= value
        elif operator == "==":
            return data.get(attribute) == value
        elif operator == "!=":
            return data.get(attribute) != value
    except (IndexError, KeyError, ValueError) as e:
        print(f"Error evaluating condition '{condition}': {e}")
        return False  # Return False if there's an error

def evaluate_rule(rule, data):
    """Evaluate the rule against the provided data."""
    conditions = rule.split(" AND ")
    results = []
    
    for condition in conditions:
        stripped_condition = condition.strip()
        if stripped_condition:  # Ignore empty conditions
            result = evaluate_condition(stripped_condition, data)
            results.append(result)
            # Debugging: Log the result of each condition evaluation
            print(f"Condition: '{stripped_condition}' evaluated to: {result}")

    return all(results)  # Return True if all conditions are True

@app.route('/create_rule', methods=['POST'])
def create_new_rule():
    """Create a new rule and return its ID."""
    global rule_counter
    rule_string = request.json.get('rule_string')
    rules.append({"id": rule_counter, "rule": rule_string})
    rule_counter += 1
    return jsonify({"id": rule_counter - 1, "rule": rule_string}), 201

@app.route('/combine_rules', methods=['POST'])
def combine_rules_endpoint():
    """Combine multiple rules into one and return the combined rule."""
    global rule_counter  # Declare rule_counter as global
    rule_ids = request.json.get('rule_ids')
    
    # Validate rule_ids
    if not isinstance(rule_ids, list):
        return jsonify({"error": "rule_ids must be a list"}), 400

    combined_rule = " AND ".join([
        rules[int(rule_id) - 1]["rule"] 
        for rule_id in rule_ids 
        if isinstance(rule_id, int) and 1 <= rule_id < rule_counter
    ])
    
    # If no valid rules were combined, return an error
    if not combined_rule:
        return jsonify({"error": "No valid rule IDs provided"}), 400

    rules.append({"id": rule_counter, "rule": combined_rule})
    rule_counter += 1  # Increment for the next rule ID
    return jsonify({"id": rule_counter - 1, "rule": combined_rule}), 201

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_endpoint():
    """Evaluate a rule against provided data."""
    rule_id = request.json.get('rule_id')
    data = request.json.get('data')
    
    if rule_id is None or not data:
        return jsonify({"error": "Rule ID and data are required"}), 400
    
    try:
        rule = rules[int(rule_id) - 1]["rule"]
    except IndexError:
        return jsonify({"error": "Invalid rule ID"}), 400
    
    result = evaluate_rule(rule, data)
    return jsonify({"result": result}), 200

@app.route('/get_rules', methods=['GET'])
def get_rules():
    """Return a list of all rules."""
    return jsonify(rules), 200

if __name__ == '__main__':
    app.run(debug=True)
