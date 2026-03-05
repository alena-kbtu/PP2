import re
import json

f = open("raw.txt", encoding="utf-8")
text = f.read()

items = re.findall(r"\d+\.\n(.*?)\n.*?[\d\s]{3}([\d\s]+,\d{2})\nСтоимость", text)

date_match = re.search(r"\d{2}\.\d{2}\.\d{4}", text)
time_match = re.search(r"\d{2}:\d{2}:\d{2}", text)
total = re.search(r"ИТОГО:\n([\d\s]+,\d{2})", text)
payment = "Банковская карта" if "Банковская карта" in text else "Наличные"
product_list = []
print(items)
for name, price in items:
    product_list.append({
        "name": name.strip(),
        "price": price.strip()
    })
                

data = {
    "receipt_info": {
        "date": date_match.group() if date_match else None,
        "time": time_match.group() if time_match else None,
        "payment_method": payment,
        "total_amount": total.group(1).strip() if total else None
    },
    "products": product_list
    
}

json_output = json.dumps(data, ensure_ascii=False, indent=4)
print(json_output)

with open("result.json", "w", encoding="utf-8") as f:
    f.write(json_output)