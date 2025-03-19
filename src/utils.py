import json
import re

def generate_query_texts_fields(query):
    special_fields = ["ingredients", "instructions", "description", "name", "comments"]
    special_requirements = query.get("special_requirements", {})

    # Get the number of brands
    brand = special_requirements.get("brand", [])
    if brand is None:  # If brand is None, treat it as an empty list
        brand = []
    brand_count = len(brand)

    # If no brands are provided, return a default structure
    if brand_count == 0:
        return [[('Thành phần', 'description')]]

    # Normalize fields to match the number of brands
    normalized_values = [
        [
            (special_requirements.get(field, [None] * brand_count)[i] if i < len(special_requirements.get(field, [])) else None)
            for i in range(brand_count)
        ]
        for field in special_fields
    ]

    # Create list of grouped fields
    query_texts_fields = []
    for i in range(brand_count):
        group = []
        for j in range(len(special_fields)):
            value = normalized_values[j][i]
            if value is not None:
                # Format values if necessary (e.g., capitalize for 'ingredients')
                if special_fields[j] == "ingredients":
                    value = value.capitalize()
                group.append((value, special_fields[j]))
        query_texts_fields.append(group if group else [])
        
    # If all groups are empty, return the default structure
    if all(not group for group in query_texts_fields):
        query_texts_fields = [[('Thành phần', 'description')] for _ in range(brand_count)]

    return query_texts_fields



def generate_query_texts_fields_with_brand_check(query):
    special_fields = ["ingredients", "instructions", "description", "name", "comments"]
    special_requirements = query.get("special_requirements", {})
    brand_count = len(special_requirements.get("brand", []))

    if brand_count == 0:
        return []  # Không có thương hiệu nào, trả về danh sách rỗng

    # Tạo danh sách các giá trị cho từng trường, đảm bảo giá trị hợp lệ được duplicate
    values_list = [
        (
            [
                value if value is not None else next(
                    (v for v in special_requirements.get(field, []) if v is not None),
                    None
                )
                for value in (special_requirements.get(field, []) or [None])
            ]
            if special_requirements.get(field, [])
            else [None] * brand_count
        )
        for field in special_fields
    ]

    # Ensure every group corresponds to each brand
    query_texts_fields = []
    for i in range(brand_count):
        group = [
            (values_list[j][i], special_fields[j])
            for j in range(len(special_fields))
            if values_list[j][i] is not None
        ]
        query_texts_fields.append(group)

    # Nếu tất cả các nhóm đều rỗng, tạo danh sách mặc định
    if all(not group for group in query_texts_fields):
        query_texts_fields = [[('Thành phần', 'description')] for _ in range(brand_count)]

    return query_texts_fields


def parse_to_json(result):
    try:
        sanitized_response = result.strip().replace("```json", "").replace("```", "")
        return json.loads(sanitized_response)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return {} 

def adjust_and_ensure_json(input_json):
    """
    Adjusts the JSON input so that:
    1. If `brand` or `category` is None, treat it as a single `[None]`.
    2. Adjust the other fields to match the longer length of `brand` or `category`:
        - If `brand` is longer, `category` is duplicated to match its length.
        - If `category` is longer, `brand` and other fields are padded with `[None]`.
    3. Fields that already contain values remain unchanged.

    :param input_json: dict, the input JSON object to be adjusted.
    :return: dict, the adjusted JSON object.
    """
    special_requirements = input_json.get("special_requirements", {})
    
    # Ensure `brand` and `category` are lists, defaulting to `[None]` if missing or None
    brand = special_requirements.get("brand", [None])
    category = special_requirements.get("category", [None])

    if not isinstance(brand, list):
        brand = [brand]
    if not isinstance(category, list):
        category = [category]

    # Determine the longer count between `brand` and `category`
    max_count = max(len(brand), len(category))

    # Adjust `brand` and `category` to match the max_count
    if len(brand) < max_count:
        brand += [None] * (max_count - len(brand))
    if len(category) < max_count:
        category = category * (max_count // len(category)) + category[:max_count % len(category)]

    # Update `brand` and `category` in `special_requirements`
    special_requirements["brand"] = brand
    special_requirements["category"] = category

    # Adjust all other fields to match the max_count
    for key, value in special_requirements.items():
        if key not in ["brand", "category", "sale"]:  # Skip brand, category, and sale
            if value is None:  # If field is None, create a list of None
                value = [None] * max_count
            elif not isinstance(value, list):
                # Convert non-list fields to lists
                value = [value]

            # Ensure the list has enough elements by filling with None
            if len(value) < max_count:
                value = value + [None] * (max_count - len(value))

            # Update the field
            special_requirements[key] = value

    input_json["special_requirements"] = special_requirements
    return input_json

def change_to_json(result):
    def sanitize_input(raw_input):
        """
        Sanitize raw input by removing formatting artifacts like backticks and fixing common issues.
        """
        sanitized_input = re.sub(r"^```(?:json)?|```$", "", raw_input.strip(), flags=re.MULTILINE)
        return sanitized_input.strip()

    def replace_nulls(obj):
        """
        Recursively replace all occurrences of the string "null" or None-like strings with None.
        """
        if isinstance(obj, dict):
            return {k: replace_nulls(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_nulls(item) for item in obj]
        elif obj in ["null", None]:  # Replace "null" string or actual None with Python None
            return None
        return obj

    try:
        sanitized_result = sanitize_input(result)
        parsed_json = json.loads(sanitized_result)
        return replace_nulls(parsed_json)

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return {"error": "Invalid JSON format", "special_requirements": {}}