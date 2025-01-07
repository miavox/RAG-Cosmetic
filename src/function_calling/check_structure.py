class CheckStructure:
    def __init__(self):
        self.required_fields = ["product_type", "budget"]  
        self.required_subfields = ["popularity", "description", "brand", "name", "skin_tone", "size", "sale", "color_code"]  

    def check_missing_fields(self, extracted_data):
        """
        Kiểm tra các trường chính và các trường con trong dữ liệu trích xuất.
        :param extracted_data: Dữ liệu trích xuất (dictionary).
        :return: Dictionary với thông tin các trường bị thiếu.
        """
        missing = {
            "main_fields": [],
            "subfields": []
        }
        
        # Kiểm tra các trường chính
        for field in self.required_fields:
            if field not in extracted_data or not extracted_data[field]:
                missing["main_fields"].append(field)
        
        # Kiểm tra các trường con trong special_requirements
        special_requirements = extracted_data.get("special_requirements", {})
        for subfield in self.required_subfields:
            if subfield not in special_requirements or not special_requirements[subfield]:
                missing["subfields"].append(subfield)
        
        return missing

    def request_additional_data(self, missing_fields):
        """
        Create a request for additional data based on the missing fields.
        :param missing_fields: Dictionary containing the missing fields.
        :return: Request for additional data.
        """
        messages = []
        
        # Notification about missing main fields
        if "product_type" in missing_fields["main_fields"]:
            messages.append("Vui lòng cho biết loại sản phẩm bạn đang tìm kiếm (ví dụ: sữa rửa mặt, son môi, kem nền, v.v.).")
        if "budget" in missing_fields["main_fields"]:
            messages.append("Vui lòng cung cấp mức ngân sách bạn mong muốn (ví dụ: từ 200,000 VNĐ).")
        
        # # Notification about missing subfields
        # for subfield in missing_fields["subfields"]:
        #     messages.append(f"Vui lòng cung cấp thông tin về {subfield.replace('_', ' ').capitalize()} (nếu cần).")
        
        return " ".join(messages)

    def process_request(self, extracted_data):
        """
        Check the data and return a request for additional data if needed.
        :param extracted_data: Extracted data (dictionary).
        :return: Request for additional data or confirmation of complete information.
        """
        missing_fields = self.check_missing_fields(extracted_data)
        # if missing_fields["main_fields"] or missing_fields["subfields"]:
        if missing_fields["main_fields"]:
            return self.request_additional_data(missing_fields)
        return "Thông tin đã đầy đủ. Chúng tôi sẽ tiến hành xử lý yêu cầu của bạn."