''' ====================================================== ''''''
| Data retrieved after rendering ShengSiong webpages in Firefox |
'''''' ====================================================== '''



# pip3 install scrapy
# pip3 install pandas
# pip3 install pytz
# pip3 install path
# pip3 install pathlib2
# pip3 install rapidfuzz
# pip3 install scrapy-playwright
# playwright install firefox

## https://github.com/scrapy-plugins/scrapy-playwright
## add DOWNLOAD_HANDLERS and TWISTED_REACTOR to settings.py
## optional: add PLAYWRIGHT_BROWSER_TYPE to specify browser



import scrapy  # version ^2.6.1 at time of writing
from scrapy_playwright.page import PageMethod
import csv
from rapidfuzz.process import extractOne
from rapidfuzz.fuzz import ratio
import re
import pandas as pd
import datetime as dt
import pytz
from pathlib import Path
import traceback


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




class SgOv8Spider(scrapy.Spider):
	
	name = "sg-ov8"


	allowed_domains = ["shengsiong.com.sg"]


	def start_requests(self):

		curls = [

			# Stage 1
			'''
			curl 'https://shengsiong.com.sg/mum-baby-kids/stage-1-milk-formula' \
				-H 'authority: shengsiong.com.sg' \
				-H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
				-H 'accept-encoding': 'gzip, deflate, br' \
				-H 'accept-language: en-GB,en;q=0.9' \
				-H 'cache-control: max-age=0' \
				-H 'dnt: 1' \
				-H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"' \
				-H 'sec-ch-ua-mobile: ?0' \
				-H 'sec-ch-ua-platform: "macOS"' \
				-H 'sec-fetch-dest: document' \
				-H 'sec-fetch-mode: navigate' \
				-H 'sec-fetch-site: same-origin' \
				-H 'sec-fetch-user: ?1' \
				-H 'upgrade-insecure-requests: 1' \
				-H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36' \
				--compressed
			''',

			# Stage 2
			'''
			curl 'https://shengsiong.com.sg/mum-baby-kids/stage-2-milk-formula' \
				-H 'authority: shengsiong.com.sg' \
				-H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
				-H 'accept-encoding': 'gzip, deflate, br' \
				-H 'accept-language: en-GB,en;q=0.9' \
				-H 'cache-control: max-age=0' \
				-H 'dnt: 1' \
				-H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"' \
				-H 'sec-ch-ua-mobile: ?0' \
				-H 'sec-ch-ua-platform: "macOS"' \
				-H 'sec-fetch-dest: document' \
				-H 'sec-fetch-mode: navigate' \
				-H 'sec-fetch-site: same-origin' \
				-H 'sec-fetch-user: ?1' \
				-H 'upgrade-insecure-requests: 1' \
				-H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36' \
				--compressed
			''',

			# Stage 3
			'''
			curl 'https://shengsiong.com.sg/mum-baby-kids/stage-3-milk-formula' \
				-H 'authority: shengsiong.com.sg' \
				-H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
				-H 'accept-encoding': 'gzip, deflate, br' \
				-H 'accept-language: en-GB,en;q=0.9' \
				-H 'cache-control: max-age=0' \
				-H 'dnt: 1' \
				-H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"' \
				-H 'sec-ch-ua-mobile: ?0' \
				-H 'sec-ch-ua-platform: "macOS"' \
				-H 'sec-fetch-dest: document' \
				-H 'sec-fetch-mode: navigate' \
				-H 'sec-fetch-site: same-origin' \
				-H 'sec-fetch-user: ?1' \
				-H 'upgrade-insecure-requests: 1' \
				-H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36' \
				--compressed
			''',

			# Stage 4 and above
			'''
			curl 'https://shengsiong.com.sg/mum-baby-kids/stage-4-above-milk-formula' \
				-H 'authority: shengsiong.com.sg' \
				-H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
				-H 'accept-encoding': 'gzip, deflate, br' \
				-H 'accept-language: en-GB,en;q=0.9' \
				-H 'cache-control: max-age=0' \
				-H 'dnt: 1' \
				-H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"' \
				-H 'sec-ch-ua-mobile: ?0' \
				-H 'sec-ch-ua-platform: "macOS"' \
				-H 'sec-fetch-dest: document' \
				-H 'sec-fetch-mode: navigate' \
				-H 'sec-fetch-site: same-origin' \
				-H 'sec-fetch-user: ?1' \
				-H 'upgrade-insecure-requests: 1' \
				-H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36' \
				--compressed
			'''
		]
		

		# urls = [

		# 	# Stage 1
		# 	"https://shengsiong.com.sg/mum-baby-kids/stage-1-milk-formula?sortBy=brand-A-to-Z",

		# 	# Stage 2
		# 	"https://shengsiong.com.sg/mum-baby-kids/stage-2-milk-formula?sortBy=brand-A-to-Z",

		# 	# Stage 3
		# 	"https://shengsiong.com.sg/mum-baby-kids/stage-3-milk-formula?sortBy=brand-A-to-Z",

		# 	# Stage 4 and above
		# 	"https://shengsiong.com.sg/mum-baby-kids/stage-4-above-milk-formula?sortBy=brand-A-to-Z"
		# ]

		# headers = {
		# 	'authority': 'shengsiong.com.sg',
		# 	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		# 	'accept-language': 'en-GB,en;q=0.9',
		# 	'cache-control': 'max-age=0',
		# 	'dnt': '1',
		# 	'referer': 'https://shengsiong.com.sg',
		# 	'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
		# 	'sec-ch-ua-mobile': '?0',
		# 	'sec-ch-ua-platform': '"macOS"',
		# 	'sec-fetch-dest': 'document',
		# 	'sec-fetch-mode': 'navigate',
		# 	'sec-fetch-site': 'none',
		# 	'sec-fetch-user': '?1',
		# 	'upgrade-insecure-requests': '1',
		# 	'user-agent': '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.
		# 	36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36''',
		# }
		

		try:			
			for curl in curls:
				yield scrapy.Request.from_curl(
					curl,
					# headers=headers,
					callback=self.parse,
					meta=dict(
						playwright=True,
						playwright_include_page=True,
						playwright_page_methods=[
							PageMethod("wait_for_selector", "div.card div.card-body"),
							PageMethod("wait_for_selector", "div.product-price > span"),
							PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
							PageMethod("wait_for_selector", "div.product-list > div > div:nth-child(16)"), # 15 per page
						],
						errback=self.errback
					)
				)

		except Exception:
			print(
			f'''
			  \n\n
			  ---
			  One or more errors occurred:
			  
			  {traceback.format_exc()}
			  ---
			  \n\n
			  '''
			)


	
			
	async def parse(self, response):

		try:
		
			page = response.meta["playwright_page"]
			await page.close()
	
			products = response.css("div.card div.card-body")
			product_list = []
	
			print("\n\n", len(products), " found for ", response.xpath(".//nav/ol/li[2]/text()").get(), "\n\n")
	
	
			for i in range(len(products)):
				# ------------------
				milk_name = products[i].css("div.product-name::text").get().replace("S26", "S-26")
				# |
				# |
	
				# ---------
				product = {}
				# |
	
				# ---
				if any(words in milk_name.lower() for words in ["stage 5", "step 5"]):
					stage = "Stage 5"
				elif any(words in milk_name.lower() for words in ["stage 4", "step 4"]):
					stage = "Stage 4"
				elif any(words in milk_name.lower() for words in ["stage 3", "step 3"]):
					stage = "Stage 3"
				elif any(words in milk_name.lower() for words in ["stage 2", "step 2"]):
					stage = "Stage 2"
				elif any(words in milk_name.lower() for words in ["stage 1", "step 1"]):
					stage = "Stage 1"
				else:
					stage = re.findall(r"Stage \d", response.xpath(".//nav/ol/li[2]/text()").get())[0]
				# |
				product["Stage"] = stage
				# ---
	
				# |
	
				# ---
				brand_from_list = extractOne(milk_name.split()[0], brand_list, scorer=ratio, score_cutoff=90)
				# |
				brand_from_dict = extractOne(milk_name, brand_dict.keys(), scorer=ratio, score_cutoff=80)
				# |
				if brand_from_list != None:
					brand = brand_from_list[0]
					# |
				elif brand_from_dict != None:
					brand = brand_dict[brand_from_dict[0]]
					# |
				else:
					del brand_from_dict
					brand_from_list = extractOne(milk_name.split()[0], brand_list, scorer=ratio, score_cutoff=80)
					# |
					if brand_from_list != None:
						brand = brand_from_list[0]
					# |
					else:
						brand = milk_name.split()[0]
				# |
				product["Brand"] = brand
				# ---
	
				# |
	
				# ---
				if brand not in milk_name:
					# Prepend Name with Brand, then delete duplicate substrings
					# Use reversed() method to keep last occurrence of duplicate
					a = (brand + " " + milk_name).split()
					b = dict(zip(reversed([x.lower()for x in a]), reversed(a)))
					name = " ".join(reversed(b.values()))
					# |
				else:
					name = milk_name
				# |
				product["Name"] = name
				# ---
	
				# |
	
				# ---
				nett_weight = products[i].css("div.product-packSize::text").get().lower().replace(" ", "")
				# |
				product["Nett Weight"] = nett_weight
				# ---
	
				# |
	
				# ---
				price = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", products[i].css("div.product-price > span::text").get())[0]
				# |
				product["Price (SGD)"] = price
				# ---
	
				# |
	
				# ---
				# Function to remove duplicate + and - operator symbols
				# Source: https://stackoverflow.com/questions/51069610/how-can-i-keep-only-the-given-operators-and-numbers
				def normalize_sign(m):
					return '-' if m.group().count('-') % 2 else '+'
				# |
				# Remove characters that are not digits or operators
				if nett_weight != None:
					tmp = re.sub(r'[^\dx/+-.]', '', nett_weight)
					# |
					# Replace multiple occurences of x, / or . by a single occurence
					# and remove heading occurences of + and -
					tmp = re.sub(r'[+\-]*([x/.])[x/.]*', r'\1', tmp)
					# |
					# Normalize sign when multiple + and - are encountered
					output = re.sub('[+\-]{2,}', normalize_sign, tmp)
					# |
					# |
					if "kg" in nett_weight:
						output = "1000 *" + output
					# |
					# Using a helper column to calculate Price per 100g
					weight_g = "%.0f" % int(eval(output.replace("x", "*")))
					unit_price = round((float(price) * 100 / float(weight_g)), 2)
				# |
				product["Weight (g)"] = weight_g
				product["Price per 100g"] = unit_price
				# ---
	
				# |
	
				# ---
				def in_stock():
					button_text = products[i].css("button.btn-primary::text").get().lower()
					# |
					oos_keywords = ["sold out", "out of stock", "no stock", "unavailable"]
					# |
					if any(words in button_text for words in oos_keywords):
						in_stock = "No"
					else:
						in_stock = "Yes"
					# |
				return in_stock
				# ---
	
				product["In Stock"] = in_stock()
	
				# |
	
				# ---
	
				product_list.append(product)
				# ---------
	
				# |
	
				# ---
				try:
					# ---
					milk_tag = products[i].xpath("..//div[@class='product-tag']/text()").get()
					# |
					promo = re.compile(r"Buy \d+ for (?:\$\d*\.\d+|\d+)")
					# |
					# |
					if bool(promo.search(milk_tag)):
						nums = re.findall(r"(?:\d*\.\d+|\d+)", milk_tag)
						# |
						product = {}
						product["Stage"] = stage
						product["Brand"] = brand
						product["Name"] = f"{name} ({milk_tag})"
						product["Nett Weight"] = f"{nums[0]}x{nett_weight}"
						product["Price (SGD)"] = nums[1]
						product["Weight (g)"] = int(nums[0]) * int(weight_g)
						product["Price per 100g"] = round((float(nums[1]) * 100 / product["Weight (g)"]), 2)
						# |
						product["In Stock"] = in_stock()
						# |
						# |
						product_list.append(product)
						# |
						print(f"\"{milk_tag}\" promo found for [{i+1}] {stage}: {name}.")
					# ---
				# |
				except:
					print(f"No promotions for [{i+1}] {stage}: {name}.")
				# |
				# ------------------
	
	
	
				product_list_consolidated.extend(product_list)
	
				product_list_df = pd.DataFrame(product_list_consolidated)
	
				product_list_df = product_list_df.sort_values(
					by=["Stage", "Name"],
					na_position="last"
				)
	
	
				# Function to move columns in DataFrame
				def movecol(df, cols_to_move=[], ref_col="", place="After"):
					# ---
					cols = df.columns.tolist()
					# |
					if place == "After":
						seg1 = cols[:list(cols).index(ref_col) + 1]
						seg2 = cols_to_move
					# |
					if place == "Before":
						seg1 = cols[:list(cols).index(ref_col)]
						seg2 = cols_to_move + [ref_col]
					# |
					seg1 = [i for i in seg1 if i not in seg2]
					seg3 = [i for i in cols if i not in seg1 + seg2]
					# |
					return(df[seg1 + seg2 + seg3])
					# ---
	
	
				product_list_df = movecol(
					product_list_df,
					cols_to_move=["Weight (g)"],
					ref_col="Price (SGD)",
					place="Before"
				)
	
	
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
	
	
				# successively insert 3 new columns from the left
				product_list_df.insert(
					loc=0,
					column="Country-Retailer",
					value="SG-ShengSiong"
				)
				product_list_df.insert(0, "Day", local_datetime.strftime("%a"))
				product_list_df.insert(0, "Date", local_datetime.strftime("%Y/%m/%d"))
				
				
				product_list_df.index = pd.RangeIndex(
					start=1,
					stop=(len(product_list_df.index) + 1),
					step=1
				)
	
	
	
				print("\n\n", product_list_df.to_string())
				print(f"Duplicates: \n\n\n{product_list_df[product_list_df.duplicated()]}\n")
	
	
				timestamp = str(local_datetime.strftime("[%Y-%m-%d %H:%M:%S]"))
				
				output_file = str(timestamp + " sg-ov8.csv")
				output_dir = Path("../scraped-data/sg-shengsiong")
				
				
				# Create directory as required; won't raise an error if directory already exists
				output_dir.mkdir(parents=True, exist_ok=True)
				
				
				product_list_df.to_csv(
					(output_dir / output_file),
					float_format="%.2f",
					encoding="utf-8"
				)
				
				# Output filename format: "[YYYY-MM-DD hh:mm:ss] sg-ov8.csv"

		
		except Exception:
			print(
			f'''
			  \n\n
			  ---
			  One or more errors occurred:
			  
			  {traceback.format_exc()}
			  ---
			  \n\n
			  '''
			)




	async def errback(self, failure):
		page = failure.request.meta["playwright_page"]
		print(
			'''\n\n
            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            One or more errors occurred, causing Playwright to close the page.
            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            \n\n'''
		)
		await page.close()