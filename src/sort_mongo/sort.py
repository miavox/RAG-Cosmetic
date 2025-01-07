import itertools
import re
import os
from dotenv import load_dotenv

load_dotenv()

class MongoSort:
    def __init__(self, task_data, mongo_handler):
        self.mongo_handler = mongo_handler  # Nhận MongoHandler từ bên ngoài
        self.collection_name = os.getenv("MONGO_DB_NAME")
        self.task = self.load_task(task_data)
        self.filtered_products = self.query(self.task)

    def load_task(self, task_data):
        return task_data

    def query(self, task):
        query_conditions = {}

        task = task["special_requirements"]
        
        for check in task:
            if task[check] == "null" or task[check] is None:
                task[check] = None

        def add_condition(field):
            if task.get(field) is not None:
                if isinstance(task[field], list):
                    task[field] = [item for item in task[field] if item is not None]  # Remove null values
                    if task[field]:
                        query_conditions[field] = {"$in": [re.compile(f"^{item}$", re.IGNORECASE) for item in task[field]]}
                else:
                    query_conditions[field] = re.compile(f"^{task[field]}$", re.IGNORECASE)

        # Check if size, category, or brand are null or a list containing only a single null value
        if (task.get("size") is None or (isinstance(task.get("size"), list) and len(task["size"]) == 1 and task["size"][0] is None)) and \
           (task.get("category") is None or (isinstance(task.get("category"), list) and len(task["category"]) == 1 and task["category"][0] is None)) and \
           (task.get("brand") is None or (isinstance(task.get("brand"), list) and len(task["brand"]) == 1 and task["brand"][0] is None)):
            # Only apply price condition
            if self.task.get("price") and self.task["price"] is not None:
                price_condition = task["price"]
                if price_condition.startswith("<"):
                    query_conditions["price"] = {"$lt": float(price_condition[1:])}
                elif price_condition.startswith(">"):
                    query_conditions["price"] = {"$gt": float(price_condition[1:])}
                elif "-" in price_condition:
                    min_price, max_price = map(float(price_condition.split("-")))
                    query_conditions["price"] = {"$gte": min_price, "$lte": max_price}
                else:
                    query_conditions["price"] = float(price_condition)
            return self.mongo_handler.query(collection_name=self.collection_name, query=query_conditions)

        # Check if all special requirements are empty or contain only null values
        if all(value is None or (isinstance(value, list) and all(item is None for item in value)) for value in task.values()):
            # Only apply price condition
            if task.get("price") and task["price"] is not None:
                price_condition = task["price"]
                if price_condition.startswith("<"):
                    query_conditions["price"] = {"$lt": float(price_condition[1:])}
                elif price_condition.startswith(">"):
                    query_conditions["price"] = {"$gt": float(price_condition[1:])}
                elif "-" in price_condition:
                    min_price, max_price = map(float(price_condition.split("-")))
                    query_conditions["price"] = {"$gte": min_price, "$lte": max_price}
                else:
                    query_conditions["price"] = float(price_condition)
            return self.mongo_handler.query(collection_name=self.collection_name, query=query_conditions)

        # Add skin_type condition based on category, brand, and size
        if task.get("category") and task.get("brand") and task.get("size") and task.get("skin_type"):
            category_brand_size_skin_type_pairs = list(zip(task["category"], task["brand"], task["size"], task["skin_type"]))
            query_conditions["$or"] = []
            for category, brand, size, skin_types in category_brand_size_skin_type_pairs:
                condition = {}
                if category:
                    if isinstance(category, list):
                        condition["category"] = {"$in": [re.compile(f"^{cat}$", re.IGNORECASE) for cat in category]}
                    else:
                        condition["category"] = re.compile(f"^{category}$", re.IGNORECASE)
                if brand:
                    if isinstance(brand, list):
                        condition["brand"] = {"$in": [re.compile(f"^{b}$", re.IGNORECASE) for b in brand]}
                    else:
                        condition["brand"] = re.compile(f"^{brand}$", re.IGNORECASE)
                if size is not None:
                    if isinstance(size, str):
                        if size.startswith("<"):
                            condition["volume_weight"] = {"$lt": float(size[1:])}
                        elif size.startswith(">"):
                            condition["volume_weight"] = {"$gt": float(size[1:])}
                        elif "-" in size:
                            min_size, max_size = map(float, size.split("-"))
                            condition["volume_weight"] = {"$gte": min_size, "$lte": max_size}
                        else:
                            condition["volume_weight"] = float(size)
                    else:
                        condition["volume_weight"] = float(size)
                if skin_types:
                    if isinstance(skin_types, list):
                        condition["skin_type"] = {"$in": [re.compile(f"^{skin_type}$", re.IGNORECASE) for skin_type in skin_types]}
                    else:
                        condition["skin_type"] = re.compile(f"^{skin_types}$", re.IGNORECASE)
                query_conditions["$or"].append(condition)

        # Add rating condition
        if task.get("rating") and task["rating"] is not None:
            query_conditions["rating"] = {"$gte": float(task["rating"])}

        # Add popularity condition
        if task.get("popularity") == "bán chạy":
            query_conditions["rating"] = {"$gte": 3, "$lte": 5}

        # Add color code range condition
        if task.get("color_code_range") and task["color_code_range"] is not None:
            min_color, max_color = task["color_code_range"]
            query_conditions["color_code"] = {"$gte": min_color, "$lte": max_color}

        # Query the database with the constructed conditions
        return self.mongo_handler.query(collection_name=self.collection_name, query=query_conditions)

    def create_combos(self):
            categories = self.group_by_category()
            special_requirements = self.task["special_requirements"]

            if (special_requirements.get("size") is None or (isinstance(special_requirements.get("size"), list) and len(special_requirements["size"]) == 1 and special_requirements["size"][0] is None)) and \
            (special_requirements.get("category") is None or (isinstance(special_requirements.get("category"), list) and len(special_requirements["category"]) == 1 and special_requirements["category"][0] is None)) and \
            (special_requirements.get("brand") is None or (isinstance(special_requirements.get("brand"), list) and len(special_requirements["brand"]) == 1 and special_requirements["brand"][0] is None)):
                return [[product] for product in self.filtered_products]
            if self.task["comparison"] == True:
                # Create combos from all products
                brands = self.group_by_brands()
                combos = list(itertools.product(*brands.values()))
                return combos
            else:
                # Handle cases where a category element is a list
                if any(isinstance(cat, list) for cat in special_requirements.get("category", [])):
                    combos = []
                    for combo in itertools.product(*categories.values()):
                        valid_combo = True
                        for i, cat in enumerate(special_requirements.get("category", [])):
                            if isinstance(cat, list):
                                if not any(re.match(f"^{sub_cat}$", combo[i]["category"], re.IGNORECASE) for sub_cat in cat):
                                    valid_combo = False
                                    break
                            else:
                                if not re.match(f"^{cat}$", combo[i]["category"], re.IGNORECASE):
                                    valid_combo = False
                                    break
                        if valid_combo:
                            combos.append(combo)
                    return combos
                else:
                    # Return each product as a separate combo
                    return list(itertools.product(*categories.values()))
    
    def group_by_category(self):
        categories = {}
        for product in self.filtered_products:
            category = product["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(product)
        return categories

    def group_by_brands(self):
        brands = {}
        for product in self.filtered_products:
            brand = product["brand"]
            if brand not in brands:
                brands[brand] = []
            brands[brand].append(product)
        return brands

    def filter_combos_by_budget(self, combos):
        valid_combos = []
        budget_condition = self.task["budget"]
        if budget_condition is None or budget_condition == "null":
            return list(combos)  # Return all combos if budget is null
        if budget_condition == "min":
            min_combo = min(combos, key=lambda combo: sum(item["price"] for item in combo))
            valid_combos.append(min_combo)
        elif budget_condition == "max":
            max_combo = max(combos, key=lambda combo: sum(item["price"] for item in combo))
            valid_combos.append(max_combo)
        else:
            for combo in combos:
                total_price = sum(item["price"] for item in combo)
                if budget_condition.startswith(">"):
                    if total_price > int(budget_condition[1:]):
                        valid_combos.append(combo)
                elif budget_condition.startswith("<"):
                    if total_price < int(budget_condition[1:]):
                        valid_combos.append(combo)
                elif "-" in budget_condition:
                    min_price, max_price = map(int, budget_condition.split("-"))
                    if min_price <= total_price <= max_price:
                        valid_combos.append(combo)
                else:
                    if total_price == int(budget_condition):
                        valid_combos.append(combo)
        return valid_combos

    def print_combos(self, combos):
        result = []
        for combo in combos:
            result.append([str(item['milvus_id']) for item in combo])  # Use milvus_id instead of _id
        return result[:4]

    def run(self):
        combos = self.create_combos()
        valid_combos = self.filter_combos_by_budget(combos)
        if valid_combos:
            result = self.print_combos(valid_combos)
            return {"combos": result, "result": True}
        else:
            # Find the closest combos to the budget condition
            closest_combos = sorted(combos, key=lambda combo: abs(sum(item["price"] for item in combo) - int(self.task["budget"].split("-")[0])))
            result = self.print_combos(closest_combos[:4])  # Return top 5 closest combos
            return {"combos": result, "result": False}

    def print_combo_product_names(self, combos):
        result = ""
        for combo in combos:
            result += "Combo:\n"
            total_price = 0
            for product_milvus_id in combo:
                # Find the product in filtered_products
                product = next((p for p in self.filtered_products if str(p['milvus_id']) == product_milvus_id), None)
                if product:
                    result += f"{product['name']}\n"
                    total_price += product['price']
                else:
                    result += f"Product with Milvus ID {product_milvus_id} not found.\n"
            result += f"Total price: {total_price}\n\n"
        return result