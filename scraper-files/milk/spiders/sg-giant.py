''' ====================================================== ''''''
| Data retrieved via directly scraping Giant.SG static webpages |
'''''' ====================================================== '''



import scrapy  # version ^2.6.1 at time of writing
import re
import pandas as pd
import datetime as dt
import pytz
from pathlib import Path
import csv
from rapidfuzz.process import extractOne
from rapidfuzz.fuzz import ratio


# Reflects local time
local_datetime = dt.datetime.now(pytz.timezone("Asia/Singapore"))


product_list_consolidated = []


# store keywords as keys and brand names as values in dictionary
with open("brands-milk.csv", mode="r") as brand_file:
	read_row = csv.reader(brand_file)
	header_row = next(read_row)

	# check if file is empty
	if header_row != None:
		
		# iterate over each row after the header row
		
		brand_dict = {rows[2]: rows[1] for rows in read_row} # {Name: Brand}

		# save Brand values as list after removing duplicates
		brand_list = list(set((brand_dict.values())))
		brand_list.sort()

	else:
		print("File is empty!")

brand_file.close()

print(f"\n\n\n{len(brand_dict)} items in Brand Dictionary:\n\n{brand_dict}\n\n")
print(f"\n\n\n{len(brand_list)} brands in Brand List:\n\n{brand_list}\n\n")




class SgGiantSpider(scrapy.Spider):
	
	name = 'sg-giant'
	

	def start_requests(self):

		urls = [

			# Stage 1
			"https://giant.sg/mum-baby/infant-essentials/stage-1-infant-milk?order=5",

			# Stage 2
			"https://giant.sg/mum-baby/infant-essentials/stage-2-milk-powder?order=5",

			# Stage 3
			"https://giant.sg/mum-baby/baby-milk/stage-3-milk-powder?order=5",

			# Stage 4
			"https://giant.sg/mum-baby/baby-milk/stage-4-milk-powder?order=5",

			# Stage 5
			"https://giant.sg/mum-baby/baby-milk/stage-5-milk-powder?order=5"
		]

		headers = {
			'authority': 'giant.sg',
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'accept-language': 'en-GB,en;q=0.9',
			'dnt': '1',
			'referer': 'https://giant.sg/mum-baby/infant-essentials?order=5',
			'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
			'sec-ch-ua-mobile': '?0',
			'sec-ch-ua-platform': '"macOS"',
			'sec-fetch-dest': 'document',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-site': 'same-origin',
			'sec-fetch-user': '?1',
			'upgrade-insecure-requests': '1',
			'user-agent': '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.
			36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36''',
		}

		for url in urls:
			yield scrapy.Request(url, headers=headers, callback=self.parse_html)


	
	def parse_html(self, response):
		
		product_list = []
		products = response.css("div.product_box")

		for milk in products:
			# ------------
			# |
			product = {}
			# |
			# |
			milk_name = milk.css("div.product_name > a::text").get()
			# |

			# ---
			stage = re.findall(
				r"Stage \d",
				response.css("strong.active-color > span::text").get()
			)[0]
			# |
			product["Stage"] = stage
			# ---

			# |

			# ---
			brand_from_dict = extractOne(
				milk_name,
				brand_dict.keys(),
				scorer=ratio,
				score_cutoff=70
			) # returns tuple value if match is found
			# |
			if brand_from_dict != None:
				brand = brand_dict[brand_from_dict[0]]
			# |
			else:
				del brand_from_dict
				brand_from_site = milk.css(
					"div.category-name > a::text"
				).get().title().replace("'S", "'s")
				# |
				brand_from_list = extractOne(
					brand_from_site,
					brand_list,
					scorer=ratio,
					score_cutoff=80
				)
				# |
				if brand_from_list != None:
					brand = brand_from_list[0]
				else:
					brand = brand_from_site
			# |
			product["Brand"] = brand
			# ---

			# |

			# ---
			if brand not in milk_name:
				# prepend Name with Brand, then delete adjacent duplicate substrings
				# use reversed() method to keep last occurrence of duplicate
				a = (brand + " " + milk_name).split()
				b = dict(
					zip(
						reversed([x.lower() for x in a]),
						reversed(a)
					)
				)
				name = " ".join(reversed(b.values()))
			else:
				name = milk_name
			# |
			product["Name"] = name
			# ---

			# |

			# ---
			nett_weight = re.findall(
				r"\d+[g|G]|\d+.\d+[k|K][g|G]",
				milk.css("span.size::text").get()
			)[0].lower()
			# |
			# Making a helper column ["Weight (g)"] to calculate Price per 100g later
			num = float(
				re.findall(
					r"\d+.\d+|d+",
					nett_weight
				)[0]
			)
			# |
			if "kg" in nett_weight and num > 100:
				weight_g = num
				nett_weight = f"{weight_g / 1000}kg"
			elif "kg" in nett_weight:
				weight_g = num * 1000
			elif "g" in nett_weight:
				weight_g = num
			# |
			product["Nett Weight"] = nett_weight
			product["Weight (g)"] = int(weight_g)
			# ---

			# |

			# ---
			price = re.sub(
				r"[^\d+\.]",
				"",
				milk.css("div.content_price > div::text").get()
			)
			# |
			product["Price (SGD"] = price
			# ---

			# |

			# ---
			unit_price = round(
				(float(price) / weight_g * 100),
				2
			)
			# |
			product["Price per 100g"] = unit_price
			# ---

			# |

			# ---
			button_class = milk.css("div.btn.add-cart::attr(class)").get()
			# |
			oos_keywords = ["oos", "sold-out", "out-of-stock", "no-stock", "unavailable"]
			# |
			if any(words in button_class for words in oos_keywords):
				in_stock = "No"
			else:
				in_stock = "Yes"
			# |
			product["In Stock"] = in_stock
			# ---

			# |
			# |

			product_list.append(product)
			# ------------



		product_list_consolidated.extend(product_list)

		product_list_df = pd.DataFrame(product_list_consolidated)


		# Function to move columns in DataFrame
		# def movecol(df, cols_to_move=[], ref_col="", place="After"):
		# 	# ---
		# 	cols = df.columns.tolist()
		# 	# |
		# 	if place == "After":
		# 		seg1 = cols[:list(cols).index(ref_col) + 1]
		# 		seg2 = cols_to_move
		# 	# |
		# 	if place == "Before":
		# 		seg1 = cols[:list(cols).index(ref_col)]
		# 		seg2 = cols_to_move + [ref_col]
		# 	# |
		# 	seg1 = [i for i in seg1 if i not in seg2]
		# 	seg3 = [i for i in cols if i not in seg1 + seg2]
		# 	# |
		# 	return(df[seg1 + seg2 + seg3])
		# 	# ---


		# product_list_df = movecol(
		# 	product_list_df,
		# 	cols_to_move=["Stage"],
		# 	ref_col="Brand",
		# 	place="Before"
		# )


		product_list_df = product_list_df.sort_values(
			by=["Stage", "Name"],
			na_position="last"
		)


		# Optional: remove helper column; we don't need to display it
		# product_list_df = product_list_df.drop(
		# 	columns=["Weight (g)"],
		# 	axis=1
		# )


		product_list_df.drop_duplicates(
			subset=None,
			keep="last",
			inplace=True,
			ignore_index=True
		)


		# Successively insert 3 new columns from the left
		product_list_df.insert(
			loc=0,
			column="Country-Retailer",
			value="SG-Giant"
		)
		product_list_df.insert(0, "Day", local_datetime.strftime("%a"))
		product_list_df.insert(0, "Date", local_datetime.strftime("%Y/%m/%d"))


		product_list_df.index = pd.RangeIndex(
			start=1,
			stop=(len(product_list_df.index) + 1),
			step=1
		)


		# For Debugging
		# print("---------\n")
		# print(product["Stage"])
		# print(product["Brand"])
		# print(i, product["Name"])
		# print(f'Price: {product["Price (SGD)"]}')
		# print(f'Weight: {product["Nett Weight"]}')
		# print(f'Weight (g): {product["Weight (g)"]}')
		# print(f'Price per 100g: {product["Price per 100g"]}')
		# print("\n---------")


		# print("\n\n", product_list_df.to_string())
		print("\n\n", product_list_df)
		print(
			"\n\n\n",
			f"Duplicates: \n{product_list_df[product_list_df.duplicated()]}",
			"\n\n"
		)


		
		timestamp = str(local_datetime.strftime("[%Y-%m-%d %H:%M:%S]"))

		output_file = str(timestamp + " sg-giant.csv")
		output_dir = Path("../scraped-data/sg-giant")


		# Create directory as required; won't raise an error if directory already exists
		output_dir.mkdir(parents=True, exist_ok=True)


		product_list_df.to_csv(
			(output_dir / output_file),
			float_format="%.2f",
			encoding="utf-8"
		)

		# Output filename format: "[YYYY-MM-DD hh:mm:ss] sg-giant.csv"