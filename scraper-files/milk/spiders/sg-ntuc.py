''' ====================================================== ''''''
| Data retrieved via GET request to Fairprice Omni API endpoint |
'''''' ====================================================== '''



import scrapy  # version ^2.6.1 at time of writing
import json
import re
import pandas as pd
import datetime as dt
import pytz
from pathlib import Path


# Reflects local time
local_datetime = dt.datetime.now(pytz.timezone("Asia/Singapore"))


product_list_consolidated = []



class SgNtucSpider(scrapy.Spider):
	
	name = 'sg-ntuc'


	
	def start_requests(self):

		urls = [
			
			# Stages 1 and 2
			'''https://website-api.omni.fairprice.com.sg/api/product/v2?
			category=infant-formula--1&experiments=searchVariant-B%2CtimerVariant-Z
			%2CinlineBanner-A%2CsubstitutionBSVariant-A%2Cgv-B%2CSPI-Z%2CSNLI-A%2CSC-
			A%2Cshelflife-C%2CA%2CcSwitch-A&includeTagDetails=true&orderType
			=DELIVERY&page=1&pageType=category&slug=infant-formula--1&sorting=A-Z
			&storeId=165&url=infant-formula--1''',
			
			# Stage 3
			'''https://website-api.omni.fairprice.com.sg/api/product/v2?
			category=stage-3&ctaLocation=[object Object]&experiments=searchVariant-B,
			timerVariant-Z,inlineBanner-A,substitutionBSVariant-A,gv-A,SPI-Z,SNLI-B,
			SC-A,shelflife-B,D,cSwitch-A,ampEnabled-B,ds-Z&includeTagDetails=true&orderType
			=DELIVERY&page=1&pageType=category&slug=stage-3&sorting=A-Z
			&storeId=165&url=stage-3''',
			
			# Stages 4 and 5
			'''https://website-api.omni.fairprice.com.sg/api/product/v2?
			category=stage-4-above&ctaLocation=[object Object]&experiments=searchVariant-B,
			timerVariant-Z,inlineBanner-A,substitutionBSVariant-A,gv-A,SPI-Z,SNLI-B,SC-B,
			shelflife-A,D,cSwitch-B,ampEnabled-B,ds-Z&includeTagDetails=true&orderType
			=DELIVERY&page=1&pageType=category&slug=stage-4-above&sorting=A-Z
			&storeId=165&url=stage-4-above'''
		]

		headers = {
			'authority': 'website-api.omni.fairprice.com.sg',
			'accept': 'application/json',
			'accept-language': 'en',
			'content-type': 'application/json',
			'dnt': '1',
			'origin': 'https://www.fairprice.com.sg',
			'referer': 'https://www.fairprice.com.sg/',
			'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
			'sec-ch-ua-mobile': '?0',
			'sec-ch-ua-platform': '"macOS"',
			'sec-fetch-dest': 'empty',
			'sec-fetch-mode': 'cors',
			'sec-fetch-site': 'same-site',
			'user-agent': '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.
			36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36''',
		}

		for url in urls:
			yield scrapy.Request(url, headers=headers, callback=self.parse, meta={"req_h": headers})


	
	def parse(self, response):

		parsed_json = json.loads(response.body)["data"]
		product_list = []
		products = parsed_json["product"]

		stage_1_keywords = ["Stage 1", "Step 1", "Starter",
							"Infant", "Newborn", "Lebens 1", "0-6", "0-12"]
		
		stage_2_keywords = ["Stage 2", "Step 2", "Follow", "6-12"]
		
		stage_3_keywords = ["Stage 3", "Step 3", "Lebens 2", "Growing", "Kid",
							"Toddler", "1-3YR", "1-3 Years", "12-36", "Junior", "Mo Milk", "Dale & Cecil"]
		
		stage_4_keywords = ["Stage 4", "Step 4", "Lebens 3", "3-6YR",  "TripleSure",
							"Preschool", "Kendakids Vita-Boost Shake", "Ascenda"]
		
		stage_5_keywords = ["Stage 5", "Step 5", "School", "10+"]
		
		
		i = 1

		for milk in products:
			# ----------------
			
			# |
			
			# ---------
			product = {}
			# |
			
			# ---
			brand = milk["brand"]["name"].replace("'S", "'s").replace("S26", "S-26")
			
			product["Brand"] = brand
			# ---
			
			# |
			
			# ---
			# product["Name"] = (re.sub(r"(\(\W+\))|\-\Z", "", 
			# ((re.sub(r"(\d+ x \d+.\d+kg)|(\(\d+x\d+g\))|(\d+sx\d+.\d+kg\+free \d+g)|\d+g|(\d+.\d+kg)", "", 
			# (milk["name"].replace("S26", "S-26").lower()))).strip()))).strip()
			#
			
			name = milk["name"].replace("S26", "S-26")
			
			product["Name"] = name
			# ---
			
			# |
			
			# ---
			if any(words.lower() in product["Name"].lower() for words in stage_5_keywords[0:2]):
				stage = "Stage 5"
			
			elif any(words.lower() in product["Name"].lower() for words in stage_4_keywords[0:3]):
				stage = "Stage 4"
			
			elif any(words.lower() in product["Name"].lower() for words in stage_3_keywords[0:3]):
				stage = "Stage 3"
			
			elif any(words.lower() in product["Name"].lower() for words in stage_2_keywords[0:2]):
				stage = "Stage 2"
			
			elif any(words.lower() in product["Name"].lower() for words in stage_1_keywords):
				stage = "Stage 1"
			
			elif any(words.lower() in product["Name"].lower() for words in stage_2_keywords):
				stage = "Stage 2"
			
			elif any(words.lower() in product["Name"].lower() for words in stage_3_keywords):
				stage = "Stage 3"
			
			elif any(words.lower() in product["Name"].lower() for words in stage_4_keywords):
				stage = "Stage 4"
			
			elif any(words.lower() in product["Name"].lower() for words in stage_5_keywords):
				stage = "Stage 5"
			
			#
			product["Stage"] = stage
			# ---
			
			# |
			
			# ---
			# data.product[0].metaData["Unit Of Weight"]
			if "DisplayUnit" in milk["metaData"]:
				nett_weight = milk["metaData"]["DisplayUnit"].replace(" ", "").lower()
			else:
				# https://regex101.com/
				nett_weight = re.findall(
					r"\d+[x]\d+", milk["slug"])[0]
				if "Ready To Drink" in name:
					nett_weight = nett_weight + "ml"
			# |
			# Checking if webpage correctly displays Nett Weight for Twin Packs
			if any(words in name.lower() for words in ["tp", "twin pack"]):
				if bool("2x" in nett_weight) == False:
					nett_weight = "2x" + nett_weight
			# |
			product["Nett Weight"] = nett_weight
			# ---
			
			# |
			
			# ---
			price = float(milk["storeSpecificData"][0]["mrp"])
			# |
			if milk["storeSpecificData"][0]["discount"] is not None:
				discount = float(milk["storeSpecificData"][0]["discount"])
			# |
			else:
				discount = 0.00
			# |
			price = "%.2f" % (price - discount)
			# |
			product["Price (SGD)"] = price
			# ---
			
			# |
			
			# ---
			def normalize_sign(m):
				return '-' if m.group().count('-') % 2 else '+'
			
			# https://stackoverflow.com/questions/51069610/how-can-i-keep-only-the-given-operators-and-numbers
			# |
			# Remove characters that are not digits or operators
			if product["Nett Weight"] is not None:
				# |
				tmp = re.sub(r'[^\dx/+-.]', '', product["Nett Weight"])
				# |
				# Replace multiple occurences of x, / or . by a single occurence
				# and remove heading occurences of + and -
				tmp = re.sub(r'[+\-]*([x/.])[x/.]*', r'\1', tmp)
				# |
				# Normalize sign when multiple + and - are encountered
				output = re.sub('[+\-]{2,}', normalize_sign, tmp)
				# |
				if "kg" in product["Nett Weight"]:
					output = "1000 *" + output
				# |
				# Using a helper column to calculate Price per 100g
				weight_g = "%.0f" % int(
					eval(output.replace("x", "*"))
				)
				# |
				unit_price = round(
					(float(product["Price (SGD)"]) * 100 / float(weight_g)),
					2)
				# |
				product["Weight (g)"] = weight_g
				product["Price per 100g"] = unit_price
			# ---

			# |
			
			# ---
			def in_stock():
				stock_count = milk["storeSpecificData"][0]["stock"]
				# |
				if stock_count > 0:
					product["In Stock"] = "Yes"
				else:
					product["In Stock"] = "No"
			# ---
			
			in_stock()
			
			# |
			
			# ---
			def coo():
				product["Country of Origin"] = milk["metaData"]["Country of Origin"]
			# ---
			
			coo()
			
			# |

			# ---
			def diet():
				if "Dietary Attributes" in milk["metaData"]:
					diet = milk["metaData"]["Dietary Attributes"]
					# |
					if len(diet) > 0 and "Goat" in product["Name"]:
						product["Dietary Attributes"] = "Goat's Milk, " + ", ".join(diet)
					# |
					elif len(diet) > 0:
						product["Dietary Attributes"] = ", ".join(diet)
					# |
					elif "Goat" in product["Name"]:
						product["Dietary Attributes"] = "Goat's Milk"
				# |
				else:
					product["Dietary Attributes"] = None
			# ---
			diet()
			
			# |
			product_list.append(product)
			# ---------
			
			# |
			
			# ---
			# offers data.product[11].offers[0].description
			try:
				# ---
				offer_description = milk["offers"][0]["description"]
				promo = re.compile(r"Buy \d+ for (?:\$\d*\.\d+|\d+)")
				# |
				if bool(promo.search(offer_description)):
					nums = re.findall(r"(?:\d*\.\d+|\d+)", offer_description)
					# print(nums)
					# print(type(nums))
					# |
					product = {}
					product["Stage"] = stage
					product["Brand"] = brand
					product["Name"] = f"{name} ({offer_description})"
					product["Nett Weight"] = f"{nums[0]}x{nett_weight}"
					product["Price (SGD)"] = nums[1]
					product["Weight (g)"] = int(nums[0]) * int(weight_g)
					product["Price per 100g"] = round(
						(float(nums[1]) * 100 / product["Weight (g)"]),
						2)
					# |
					in_stock()
					coo()
					diet()
					# |
					# print(product)
					product_list.append(product)
					print(f"\"{offer_description}\" promo found for [{i}] {stage}: {name}.")
				# ---
			except:
				print(f"No direct promotions for [{i}] {stage}: {name}.")
			
			i += 1
			
			# ----------------



		product_list_consolidated.extend(product_list)
		
		product_list_df = pd.DataFrame(product_list_consolidated)
		
		# Function to move columns in Dataframe
		def movecol(df, cols_to_move=[], ref_col='', place='After'):
			# |
			cols = df.columns.tolist()
			if place == 'After':
				seg1 = cols[:list(cols).index(ref_col) + 1]
				seg2 = cols_to_move
			if place == 'Before':
				seg1 = cols[:list(cols).index(ref_col)]
				seg2 = cols_to_move + [ref_col]
			# |
			seg1 = [i for i in seg1 if i not in seg2]
			seg3 = [i for i in cols if i not in seg1 + seg2]
			# |
			return(df[seg1 + seg2 + seg3])
		
		product_list_df = movecol(product_list_df,
								  cols_to_move=["Stage"],
								  ref_col="Brand",
								  place="Before")
		
		product_list_df = movecol(product_list_df,
								  cols_to_move=["Weight (g)"],
								  ref_col="Price (SGD)",
								  place="Before")
		
		product_list_df = product_list_df.sort_values(
			by=["Stage", "Name"], na_position="last"
		)
		# "Stage", "Name",
		# "Price per 100g"
		
		# Optional: remove helper column; we don't need to display it
		# product_list_df = product_list_df.drop(
		#     columns=["Weight (g)"], axis=1)
		
		product_list_df.drop_duplicates(
			subset=None, keep='last', inplace=True, ignore_index=True)
		
		# successively insert 3 new columns from the left
		product_list_df.insert(
			loc=0,
			column="Country-Retailer",
			value="SG-Fairprice"
		)
		product_list_df.insert(0, "Day", local_datetime.strftime("%a"))
		product_list_df.insert(0, "Date", local_datetime.strftime("%Y/%m/%d"))
		
		product_list_df.index = pd.RangeIndex(
			start=1, stop=(len(product_list_df.index) + 1), step=1
		)
		
		
		page = int(parsed_json["pagination"]["page"])
		total_pages = int(parsed_json["pagination"]["total_pages"])
		
		headers = response.meta["req_h"]


		for p in range(page+1, total_pages+1):

			next_page_urls = [
				
				# Stages 1 and 2
				f'''https://website-api.omni.fairprice.com.sg/api/product/v2?
				category=infant-formula--1&experiments=searchVariant-B%2CtimerVariant-Z
				%2CinlineBanner-A%2CsubstitutionBSVariant-A%2Cgv-B%2CSPI-Z%2CSNLI-A%2CSC-
				A%2Cshelflife-C%2CA%2CcSwitch-A&includeTagDetails=true&orderType
				=DELIVERY&page={p}&pageType=category&slug=infant-formula--1&sorting=A-Z
				&storeId=165&url=infant-formula--1''',
				
				# Stage 3
				f'''https://website-api.omni.fairprice.com.sg/api/product/v2?
				category=stage-3&ctaLocation=[object Object]&experiments=searchVariant-B,
				timerVariant-Z,inlineBanner-A,substitutionBSVariant-A,gv-A,SPI-Z,SNLI-B,
				SC-A,shelflife-B,D,cSwitch-A,ampEnabled-B,ds-Z&includeTagDetails=true&orderType
				=DELIVERY&page={p}&pageType=category&slug=stage-3&sorting=A-Z
				&storeId=165&url=stage-3''',
				
				# Stages 4 and 5
				f'''https://website-api.omni.fairprice.com.sg/api/product/v2?
				category=stage-4-above&ctaLocation=[object Object]&experiments=searchVariant-B,
				timerVariant-Z,inlineBanner-A,substitutionBSVariant-A,gv-A,SPI-Z,SNLI-B,SC-B,
				shelflife-A,D,cSwitch-B,ampEnabled-B,ds-Z&includeTagDetails=true&orderType
				=DELIVERY&page={p}&pageType=category&slug=stage-4-above&sorting=A-Z
				&storeId=165&url=stage-4-above'''
			]

			for url in next_page_urls:
				yield scrapy.Request(url, headers=headers, callback=self.parse, meta={"req_h": headers})



	
		# print("\n\n", product_list_df.to_string())
		print("\n\n", product_list_df)
		print(f"\nPage {page} of {total_pages}")
		print(f"Duplicates: \n\n{product_list_df[product_list_df.duplicated()]}\n\n\n")

		
		timestamp = str(local_datetime.strftime("[%Y-%m-%d %H:%M:%S]"))
		
		output_file = str(timestamp + " sg-ntuc.csv")
		output_dir = Path("../scraped-data/sg-ntuc_fairprice")
		
		# Create directory as required; won't raise an error if directory already exists
		output_dir.mkdir(parents=True, exist_ok=True)
		
		product_list_df.to_csv(
			(output_dir / output_file),
			float_format="%.2f", encoding="utf-8"
		)
		
		# Output filename format: "[YYYY-MM-DD hh:mm:ss] sg-ntuc.csv"