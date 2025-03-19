import os
from src.embeddings.multilingual_e5 import EmbeddingGenerator  
from src.database.mongo_handler import MongoHandler         
from src.database.milvus_handler import MilvusHandler        
from src.sort_mongo.sort import MongoSort
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()


class ProductSearch:
    def __init__(self, api_key=None, verbose=True):
        # Read collection names from .env
        self.mongo_collection = os.getenv("MONGO_DB_NAME")
        self.milvus_collection = os.getenv("MILVUS_COLLECTION_NAME")
        
        # Initialize components
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.embedding_generator = EmbeddingGenerator()
        self.mongo_handler = MongoHandler()
        self.milvus_handler = MilvusHandler(collection_name=self.milvus_collection, verbose=verbose)
        self.verbose = verbose

    def query_products_in_mongo(self, query_filters):
        """Query MongoDB and return milvus_ids."""
        mongo_sort = MongoSort(self.mongo_handler, query_filters)
        filtered_results = mongo_sort.run()
        
        # Flatten the list of combo milvus_ids
        milvus_ids = [milvus_id for combo in filtered_results["combos"] for milvus_id in combo if milvus_id]
        
        if self.verbose:
            print(f"Flattened Milvus IDs: {milvus_ids}")
        
        return milvus_ids

    def search_in_milvus(self, query_text, field_name, milvus_ids, limit=5):
        """
        Perform search in Milvus based on a query text, field name, and list of milvus_ids.

        Args:
            query_text (str): The query text to generate the embedding.
            field_name (str): The field to search in (e.g., "description", "ingredients").
            milvus_ids (list): List of Milvus IDs to filter the search.
            limit (int): Number of results to return.

        Returns:
            list: List of search results with Milvus IDs and similarities.
        """
        if not query_text:
            if self.verbose:
                print("Query text is empty. Skipping search.")
            return []

        # Generate embedding from query_text
        query_vector = self.embedding_generator.generate_embedding(query_text)

        # Format Milvus IDs into the expression
        if milvus_ids:
            milvus_expr = f"milvus_id in [{', '.join(map(str, milvus_ids))}]"
        else:
            milvus_expr = None  # No filter by Milvus IDs

        # Perform search in Milvus
        try:
            results = self.milvus_handler.search(
                vector=query_vector,
                field_name=field_name,
                limit=limit,
                expr=milvus_expr
            )
            if self.verbose:
                print(f"Milvus search for field '{field_name}' returned {len(results)} results.")
            return results
        except Exception as e:
            print(f"Error during Milvus search: {e}")
            return []


    def get_product_details(self, product_ids):
        """Retrieve product details from MongoDB."""
        product_details = self.mongo_handler.query(
            query={"milvus_id": {"$in": product_ids}},
            collection_name=self.mongo_collection
        )
        if self.verbose:
            print(f"Retrieved {len(product_details)} product details from MongoDB.")
        return product_details

    def search_combo_products(self, query_texts_fields, mongo_filter):
        """
        Search multiple combos of products based on different requirements.

        Args:
            query_texts_fields (list of list of tuples): List of combos where each combo contains (query_text, field_name) pairs.
            mongo_filter (dict): MongoDB filter.

        Returns:
            dict: Search results for all combos.
        """
        # Step 1: Query MongoDB for matching products
        mongo_sort = MongoSort(mongo_filter, self.mongo_handler)
        filtered_results = mongo_sort.run()
        print(filtered_results)

        combos = filtered_results["combos"]
        if not combos:
            return {"message": "Không tìm thấy sản phẩm nào phù hợp với yêu cầu của bạn.", "combos": []}

        results = []

        # Step 2: Process each combo
        for combo in combos:
            combo_results = []
            for idx, milvus_id in enumerate(combo):
                if milvus_id is None:
                    combo_results.append(None)
                    continue

                # Get the corresponding query_texts and fields for the current position
                current_query_texts = query_texts_fields[idx]
                current_results = []

                for query_text, field_name in current_query_texts:
                    # Perform search in Milvus for the current milvus_id
                    search_results = self.search_in_milvus(query_text, field_name, [milvus_id])

                    # Take the best result (lowest distance)
                    if search_results:
                        best_result = sorted(search_results, key=lambda x: x.distance)[0]
                        current_results.append({
                            "milvus_id": best_result.id,
                            "similarity": best_result.distance
                        })
                    else:
                        current_results.append(None)

                combo_results.append(current_results)

            results.append(combo_results)

        # Step 3: Retrieve product details for all found IDs
        all_product_ids = set(
            res["milvus_id"]
            for combo in results
            for res_list in combo if res_list
            for res in res_list if res
        )

        if not all_product_ids:
            return {"message": "Không tìm thấy sản phẩm nào phù hợp với yêu cầu của bạn.", "combos": []}

        product_details = self.mongo_handler.query(
            query={"milvus_id": {"$in": list(all_product_ids)}},
            collection_name=self.mongo_collection
        )

        # Step 4: Format results for each combo
        formatted_combos = []
        for combo, raw_results in zip(combos, results):
            formatted_combo = []
            for milvus_id, raw_result in zip(combo, raw_results):
                if raw_result:
                    # Match product details to Milvus IDs
                    products = []
                    similarity_sum = 0
                    similarity_count = 0

                    for res in raw_result:
                        product = next(
                            (p for p in product_details if p["milvus_id"] == res["milvus_id"]),
                            None
                        )
                        if product:
                            similarity_sum += res["similarity"]
                            similarity_count += 1
                            products.append({
                                "name": product.get("name"),
                                "price": product.get("price"),
                                "img": product.get("img"),
                                "link": product.get("link"),
                                "description": product.get("description"),
                                "milvus_id": res["milvus_id"],
                            })

                    # Tính average similarity
                    if similarity_count > 0:
                        average_similarity = similarity_sum / similarity_count
                        for product in products:
                            product["average_similarity"] = average_similarity

                    # Sort products in the combo by average_similarity
                    products.sort(key=lambda x: x["average_similarity"], reverse=False)
                    formatted_combo.append(products)
                else:
                    formatted_combo.append(None)
            formatted_combos.append(formatted_combo)
        
        # Step 5: Tính giá trị đại diện và sắp xếp combo
        def calculate_combo_similarity(combo):
            """Tính giá trị đại diện cho combo (ví dụ: trung bình các average_similarity trong combo)."""
            similarities = []
            for products in combo:
                if products:  # Nếu combo có sản phẩm
                    similarities.extend([p["average_similarity"] for p in products])
            return sum(similarities) / len(similarities) if similarities else float('inf')  # Giá trị lớn nhất nếu không có sản phẩm

        # Sắp xếp combo dựa trên average_similarity
        formatted_combos.sort(key=calculate_combo_similarity)

        return {"message": "Tìm thấy sản phẩm phù hợp.", "combos": formatted_combos}


    def transform_to_target_structure_fixed(self, query_texts_fields, mongo_filter):
        result = self.search_combo_products(query_texts_fields, mongo_filter)
        combos = result.get('combos', [])
        transformed_combos = []

        for combo_group in combos:
            group_items = []
            for inner_list in combo_group:
                if isinstance(inner_list, list) and inner_list:  # Ensure the inner list is valid
                    group_items.append(inner_list[0])  # Take the first element of each inner list
            if group_items:
                transformed_combos.append(group_items)

        # Update and return the transformed JSON
        return {
            "message": result.get("message", ""),
            "combos": transformed_combos
        }
        
    def rewrite_product_info_gpt(self, product_details, llm_client, query_text):
        """
        Rewrite product details using an LLM for better user presentation.

        Args:
            product_details (list): List of product details dictionaries.
            llm_client (ChatOpenAI): Instance of the ChatOpenAI class to call the LLM.

        Returns:
            list: List of rewritten product details dictionaries.
        """
        rewritten_details = []
        for product in product_details:
            try:
                # Prepare prompt for LLM
                prompt = f"""
                    Hãy viết lại thông tin sản phẩm dưới đây bằng văn phong thân thiện, dễ hiểu, hấp dẫn để giới thiệu tới người dùng theo dạng liệt kê các sản phẩm:
                    - Tên sản phẩm: {product.get('name', 'Không có thông tin')}
                    - Giá: {product.get('price', 'Không có thông tin')} VND
                    - Mô tả: {product.get('description', 'Không có thông tin')}

                    Yêu cầu từ người dùng: "{query_text}"
                """

                # Call LLM to rewrite
                rewritten_description = llm_client.analyze_request(
                    user_input=prompt,
                    prompt_function=lambda x: x,  # Direct prompt
                    model="gpt-3.5-turbo",  # Specify model
                    system_message="Bạn là trợ lý chuyên tư vấn mỹ phẩm cho người dùng, dựa vào yêu cầu người dùng và thông tin bạn có hãy trả lời cho người dùng.",
                    temperature=0.5
                )

                # Append rewritten product info
                rewritten_product = product.copy()
                rewritten_product["rewritten_description"] = rewritten_description
                rewritten_details.append(rewritten_product)

            except Exception as e:
                print(f"Error rewriting product info for {product.get('name')}: {e}")
                rewritten_details.append(product)  # Append original details if rewrite fails

        return rewritten_details
    
    def search_combo_products_with_rewriting_gpt(self, query_texts_fields, mongo_filter, llm_client, query_text):
        """
        Perform a product combo search and rewrite product details into a single response message.
        If Milvus returns empty results, fallback to MongoDB to retrieve product details.

        Args:
            query_texts_fields (list of list of tuples): List of combos where each combo contains (query_text, field_name) pairs.
            mongo_filter (dict): MongoDB filter.
            llm_client (ChatOpenAI): Instance of the ChatOpenAI class to rewrite descriptions.
            query_text (str): User query to customize the LLM response.

        Returns:
            dict: Search results with a single rewritten message and combos details.
        """
        # Perform the regular search
        search_results = self.search_combo_products(query_texts_fields, mongo_filter)

        # If no combos are found, return early
        if "combos" not in search_results or not search_results["combos"]:
            return {"message": "Không tìm thấy sản phẩm nào phù hợp với yêu cầu của bạn.", "combos": []}

        # Check if Milvus results are empty
        all_products = []
        is_milvus_empty = all(
            not product_list for combo in search_results["combos"] for product_list in combo
        )

        if is_milvus_empty:
            # Fallback to MongoDB directly if Milvus results are empty
            milvus_ids = self.query_products_in_mongo(mongo_filter)
            if not milvus_ids:
                return {"message": "Không tìm thấy sản phẩm nào phù hợp với yêu cầu của bạn.", "combos": [[] for _ in range(len(mongo_filter.get("brand", [])))]}

            # Retrieve product details from MongoDB using Milvus IDs
            product_details = self.get_product_details(milvus_ids)
            all_products.extend(product_details)
        else:
            # Consolidate all product details for rewriting
            for combo in search_results["combos"]:
                for product_list in combo:
                    if product_list:  # Only include non-empty product lists
                        all_products.extend(product_list)

        # Generate a single rewritten message for all products
        try:
            # Prepare the consolidated prompt for LLM
            product_info = "\n".join(
                f"- Tên sản phẩm: {product.get('name', 'Không có thông tin')}\n"
                f"  Giá: {product.get('price', 'Không có thông tin')} VND\n"
                f"  Mô tả: {product.get('description', 'Không có thông tin')}\n"
                for product in all_products
            )

            prompt = f"""
            Đối với các câu hỏi có giảm giá hay khuyến mãi không, câu trả lời luôn là có và lấy thông tin từ các sản phẩm thu thập đưa trả lời cho người dùng.
            Dựa trên thông tin các sản phẩm dưới đây và yêu cầu từ người dùng: "{query_text}",
            hãy tổng hợp lại thông tin, liệt kê ngắn gọn các sản phẩm dễ hiểu cho người dùng:
            {product_info}
            """

            rewritten_message = llm_client.analyze_request(
                user_input=prompt,
                prompt_function=lambda x: x,  # Direct prompt
                model="gpt-3.5-turbo",
                system_message="Bạn là trợ lý chuyên tổng hợp thông tin sản phẩm để tư vấn cho người dùng. Khi người dùng hỏi các chương trình khuyến mãi, phải luôn bảo là có.",
                temperature=0.5
            )

        except Exception as e:
            print(f"Error generating rewritten message: {e}")
            rewritten_message = "Không thể tạo nội dung tổng hợp sản phẩm vào lúc này. Vui lòng thử lại sau."

        # Return the results with the rewritten message
        return {
            "message": rewritten_message,
            "combos": search_results["combos"]
        }
        
    def search_combo_products_with_rewriting_gemini(self, query_texts_fields, mongo_filter, llm_client, query_text):
        """
        Perform a product combo search and rewrite product details into a single response message.
        If Milvus returns empty results, fallback to MongoDB to retrieve product details.

        Args:
            query_texts_fields (list of list of tuples): List of combos where each combo contains (query_text, field_name) pairs.
            mongo_filter (dict): MongoDB filter.
            llm_client (ChatOpenAI): Instance of the ChatOpenAI class to rewrite descriptions.
            query_text (str): User query to customize the LLM response.

        Returns:
            dict: Search results with a single rewritten message and combos details.
        """
        # Perform the regular search
        search_results = self.search_combo_products(query_texts_fields, mongo_filter)

        # If no combos are found, return early
        if "combos" not in search_results or not search_results["combos"]:
            return {"message": "Không tìm thấy sản phẩm nào phù hợp với yêu cầu của bạn.", "combos": []}

        # Check if Milvus results are empty
        all_products = []
        is_milvus_empty = all(
            not product_list for combo in search_results["combos"] for product_list in combo
        )

        if is_milvus_empty:
            # Fallback to MongoDB directly if Milvus results are empty
            milvus_ids = self.query_products_in_mongo(mongo_filter)
            if not milvus_ids:
                return {"message": "Không tìm thấy sản phẩm nào phù hợp với yêu cầu của bạn.", "combos": [[] for _ in range(len(mongo_filter.get("brand", [])))]}

            # Retrieve product details from MongoDB using Milvus IDs
            product_details = self.get_product_details(milvus_ids)
            all_products.extend(product_details)
        else:
            # Consolidate all product details for rewriting
            for combo in search_results["combos"]:
                for product_list in combo:
                    if product_list:  # Only include non-empty product lists
                        all_products.extend(product_list)

        # Generate a single rewritten message for all products
        try:
            # Prepare the consolidated prompt for LLM
            product_info = "\n".join(
                f"- Tên sản phẩm: {product.get('name', 'Không có thông tin')}\n"
                f"  Giá: {product.get('price', 'Không có thông tin')} VND\n"
                f"  Mô tả: {product.get('description', 'Không có thông tin')}\n"
                for product in all_products
            )

            prompt = f"""
            Đối với các câu hỏi có giảm giá hay khuyến mãi không, câu trả lời luôn là có và lấy thông tin từ các sản phẩm thu thập đưa trả lời cho người dùng.
            Dựa trên thông tin các sản phẩm dưới đây và yêu cầu từ người dùng: "{query_text}",
            hãy tổng hợp lại thông tin, liệt kê ngắn gọn các sản phẩm dễ hiểu cho người dùng:
            {product_info}
            """

            rewritten_message = llm_client.analyze_request(user_input=prompt)

        except Exception as e:
            print(f"Error generating rewritten message: {e}")
            rewritten_message = "Không thể tạo nội dung tổng hợp sản phẩm vào lúc này. Vui lòng thử lại sau."

        # Return the results with the rewritten message
        return {
            "message": rewritten_message,
            "combos": search_results["combos"]
        }