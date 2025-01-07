class CTP:
    @staticmethod
    def generate_overview(query):
        return f"""
            **Hướng dẫn:**  
            Phân tích kỹ nội dung tin nhắn của người dùng và xác định tất cả các trường được đề cập trong yêu cầu. Kiểm tra tất cả các trường dưới đây và đảm bảo không bỏ sót thông tin nào. Trả kết quả dưới dạng đối tượng JSON chứa `true/false` cho từng trường nếu thông tin đó được đề cập rõ ràng trong tin nhắn.  

            **Tin nhắn của người dùng:**  
            "{query}"  

            **Các trường cần kiểm tra và trả về:**  
            [ 'budget', 'product_popularity', 'product_ingredients', 'usage_instructions', 'product_descriptions', 'skin_types', 'skin_tones', 'product_sizes', 'discount_value', 'product_categories', 'brand_names', 'product_names', 'color_codes', 'comparison']  

            **Yêu cầu:**  
            - Đối với mỗi trường, trả về `true` nếu thông tin đó được đề cập rõ ràng; nếu không, không trả về trường đó.  
            - Không suy diễn thông tin mà chỉ dựa vào nội dung tin nhắn.  
            - Đối với `budget`, kiểm tra từ khóa như "giá khoảng", "tầm", "target".  
            - Đối với `comparison`, trả về `true` nếu người dùng yêu cầu so sánh sản phẩm.  

            **Định dạng đầu ra:**  
            {{
                "field_name_1": true,
                "field_name_2": true,
                ...
            }}
        """

    @staticmethod
    def generate_description(query):
        return f"""
            **Hướng dẫn:**  
            Phân tích nội dung tin nhắn của người dùng để trích xuất mô tả chi tiết cho từng sản phẩm. Trả kết quả dưới dạng mảng JSON, trong đó mỗi phần tử là mô tả của một sản phẩm.  

            **Tin nhắn của người dùng:**  
            "{query}"  

            **Yêu cầu:**  
            - Xác định từng sản phẩm được đề cập và trích xuất mô tả cụ thể, bao gồm các đặc điểm chính (nếu có).  
            - Nếu không có thông tin, trả về `"null"` cho sản phẩm đó.  
            - Đảm bảo mô tả từng sản phẩm luôn nằm trong một phần tử riêng biệt trong mảng JSON.  

            **Định dạng đầu ra:**  
            [
                "Các mô tả của sản phẩm đầu tiên",
                ...
            ]
        """

    @staticmethod
    def generate_instructions(query):
        return f"""
            **Hướng dẫn:**  
            Phân tích nội dung tin nhắn của người dùng để trích xuất **chính xác** hướng dẫn sử dụng cho sản phẩm. Trả kết quả dưới dạng mảng JSON, trong đó mỗi phần tử tương ứng với một sản phẩm được đề cập.  

            **Tin nhắn của người dùng:**  
            "{query}"  

            **Yêu cầu:**  
            - Xác định thông tin cụ thể về hướng dẫn sử dụng được người dùng cung cấp (nếu có).  
            - Chỉ trích xuất phần liên quan đến hướng dẫn sử dụng (ví dụ: cách dùng, thời điểm dùng).  
            - Không lặp lại mô tả hoặc các thông tin không liên quan đến hướng dẫn sử dụng, không bao gồm .  
            - Nếu không có thông tin hướng dẫn sử dụng, trả về `"null"`.  

            **Định dạng đầu ra:**  
            [
                "Hướng dẫn sử dụng của sản phẩm"
            ]
        """

    @staticmethod
    def generate_ingredients(query):
        return f"""
            **Hướng dẫn:**  
            Phân tích nội dung tin nhắn của người dùng để trích xuất **thành phần cụ thể** của từng sản phẩm. Trả kết quả dưới dạng mảng JSON, trong đó mỗi phần tử tương ứng với thành phần của một sản phẩm.  

            **Tin nhắn của người dùng:**  
            "{query}"  

            **Yêu cầu:**  
            - Trích xuất thông tin rõ ràng về thành phần của sản phẩm (nếu được cung cấp).  
            - Không lặp lại thông tin không liên quan hoặc suy diễn.  
            - Nếu chỉ có một sản phẩm và thông tin thành phần được cung cấp, trả về mảng với một phần tử duy nhất.  
            - Nếu không có thông tin thành phần, trả về `"null"`.  

            **Định dạng đầu ra:**  
            [
                "Các thành phần của sản phẩm đầu tiên"
            ]
        """

    @staticmethod
    def generate_budget(query):
        return f"""
            **Hướng dẫn:**  
            Phân tích nội dung tin nhắn của người dùng để trích xuất thông tin ngân sách dự kiến cho sản phẩm.  

            **Tin nhắn của người dùng:**  
            "{query}"  

            **Yêu cầu:**  
            - Nếu người dùng muốn giá rẻ nhất (ví dụ: "càng rẻ càng tốt", "rẻ nhất có thể"), trả về giá trị tối thiểu khả dụng (ví dụ: `"300000"`).  
            - Nếu người dùng muốn giá đắt nhất (ví dụ: "càng đắt càng tốt", "đắt nhất có thể"), trả về giá trị tối đa khả dụng (ví dụ: `"3000000"`).  
            - Nếu người dùng cung cấp khoảng giá (ví dụ: "200000 - 500000"), trả về dưới dạng `"200000-500000"`.  
            - Nếu người dùng cung cấp một số tiền cụ thể (ví dụ: "300000", "khoảng 300000", "tầm 300000"), trả về khoảng giá ±50,000 từ giá trị đó (ví dụ: `"250000-350000"`).  
            - Nếu người dùng yêu cầu giá nhỏ hơn hoặc lớn hơn một giá trị (ví dụ: "dưới 3000000", "trên 500000", "target 300000"), trả về giá trị chính xác (ví dụ: `"300000"` cho trường hợp cụ thể hoặc `"500000"` cho các điều kiện lớn hơn/nhỏ hơn).  
            - Đảm bảo giá trị luôn được định dạng là số (không có dấu cách, dấu phẩy, chữ "đồng", "k", hoặc các ký tự không cần thiết).  
            - Xử lý các trường hợp người dùng viết tắt giá trị (ví dụ: "500", "500k", "0.5 triệu") và đưa về định dạng chuẩn `xxxxxx`.  

            **Định dạng đầu ra:**  
            Chỉ trả về một trong các định dạng dưới đây, không kèm theo bất kỳ văn bản nào khác:  
            - `"xxxxxx"` (một giá trị cụ thể)  
            - `"xxxxxx-xxxxxx"` (khoảng giá)  

            **Ví dụ kết quả hợp lệ:**  
            - `"300000"`  
            - `"250000-350000"`
        """
