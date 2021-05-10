from __future__ import division

import os, time
import sys
from os import path
from datetime import date, timedelta, datetime
import wget


japanese_population = 126300000


medical_workers_data_url = 'https://www.kantei.go.jp/jp/content/IRYO-vaccination_data.xlsx'
elderly_data_url = 'https://www.kantei.go.jp/jp/content/KOREI-vaccination_data.xlsx'

if os.path.exists('/Users/cianglenfield/Desktop/japan_vaccine_data/medical_workers_data_excel.xlsx') == True:
	os.system('rm /Users/cianglenfield/Desktop/japan_vaccine_data/medical_workers_data_excel.xlsx')
	os.system('rm /Users/cianglenfield/Desktop/japan_vaccine_data/medical_workers_data_converted.csv')

if os.path.exists('/Users/cianglenfield/Desktop/japan_vaccine_data/elderly_data_excel.xlsx') == True:
	os.system('rm /Users/cianglenfield/Desktop/japan_vaccine_data/elderly_data_excel.xlsx')
	os.system('rm /Users/cianglenfield/Desktop/japan_vaccine_data/elderly_data_converted.csv')

wget.download(medical_workers_data_url, '/Users/cianglenfield/Desktop/japan_vaccine_data/medical_workers_data_excel.xlsx')
os.system('ssconvert medical_workers_data_excel.xlsx medical_workers_data_converted.csv')

wget.download(elderly_data_url, '/Users/cianglenfield/Desktop/japan_vaccine_data/elderly_data_excel.xlsx')
os.system('ssconvert elderly_data_excel.xlsx elderly_data_converted.csv')

print("")

medical_workers_file = open("medical_workers_data_converted.csv")
elderly_file = open("elderly_data_converted.csv")
MHLW_data_file = open("japan_vaccine_MHLW_data.txt")

MHLW_data_file.readline()

coordinated_vaccine_data = {}

for line in medical_workers_file:
	if "2021" in line:
		data_date, day, daily_total_medical, daily_first_shot_medical, daily_second_shot_medical = line.rstrip().split(",")
		date_time = datetime.strptime(data_date, '%Y/%m/%d')
		new_date = datetime.strftime(date_time, '%m/%d')
		coordinated_vaccine_data[new_date] = [int(daily_total_medical), int(daily_first_shot_medical), int(daily_second_shot_medical)]

for line in elderly_file:
	if "2021" in line:
		data_date, day, daily_total_elderly, daily_first_shot_elderly, daily_second_shot_elderly = line.rstrip().split(",")
		date_time = datetime.strptime(data_date, '%Y/%m/%d')
		new_date = datetime.strftime(date_time, '%m/%d')
		if new_date not in coordinated_vaccine_data:
			coordinated_vaccine_data[new_date] = [0, 0, 0]
		daily_total_comma = "{:,}".format(int(daily_total_elderly)+coordinated_vaccine_data[new_date][0])
		new_daily_total = int(daily_total_elderly)+coordinated_vaccine_data[new_date][0]
		new_daily_first_shot = int(daily_first_shot_elderly)+coordinated_vaccine_data[new_date][1]
		new_daily_second_shot = int(daily_second_shot_elderly)+coordinated_vaccine_data[new_date][2]
		coordinated_vaccine_data[new_date] = [new_daily_total, new_daily_first_shot, new_daily_second_shot, daily_total_comma]


for line in MHLW_data_file:
	new_date, daily_total, daily_first_shots, daily_second_shots, daily_total_comma = line.rstrip().split("\t")
	old_date = datetime.strptime(new_date, '%a, %b %d')
	new_date = datetime.strftime(old_date, '%m/%d')
	coordinated_vaccine_data[new_date] = [int(daily_total), int(daily_first_shots), int(daily_second_shots), daily_total_comma]


sdate = date(2021, 2, 17)
edate = datetime.date(datetime.now())

delta = edate - sdate

date_list = []

for i in range(delta.days):
	day = sdate + timedelta(days=i)
	new_format = datetime.strftime(day, '%m/%d')
	date_list += [new_format]

for day in date_list:
	if day not in coordinated_vaccine_data:
		coordinated_vaccine_data[day] = [0, 0, 0, " "]

graph_data_file = open("japan_vaccine_data_for_graph.txt", "w")
vaccine_data_summary_file = open("/Volumes/Macintosh HD/Users/cianglenfield/Desktop/japan_vaccine_data/japan_vaccine_data_summaries.txt", "w")

graph_data_file.write("Date\tTotal daily doses given\tFirst doses given\tFollow-up doses given\tBasic doses given total\n")


overall_total = 0
first_dose_total = 0
second_dose_total = 0


for day in date_list:
	graph_data_file.write("%s\t%s\t%s\t%s\t%s\n" % (day, coordinated_vaccine_data[day][0], coordinated_vaccine_data[day][1], coordinated_vaccine_data[day][2], coordinated_vaccine_data[day][3]))
	overall_total += coordinated_vaccine_data[day][0]
	first_dose_total += coordinated_vaccine_data[day][1]
	second_dose_total += coordinated_vaccine_data[day][2]


overall_population_coverage = round((overall_total/(japanese_population*2))*100, 2)
first_shot_coverage = round((first_dose_total/japanese_population)*100, 2)
second_shot_coverage = round((second_dose_total/japanese_population)*100, 2)

total_coverage_comma = "{:,}".format(overall_total)

vaccine_data_summary_file.write("%s\t%s\t%s\t%s\n" % (total_coverage_comma, str(overall_population_coverage), str(first_shot_coverage), str(second_shot_coverage)))


elderly_file.close()
medical_workers_file.close()
MHLW_data_file.close()
graph_data_file.close()
vaccine_data_summary_file.close()

os.system("Rscript japan_vaccine_graphs.R")

os.system("cp japan_vaccine_data.py japan_vaccine_graphs.R japan_vaccination_rate_plot.png japan_vaccine_data_for_graph.txt japan_vaccine_data_summaries.txt japan-covid19-vaccination-data/")

os.system("cd japan-covid19-vaccination-data/; git add . ; git commit -m \"Updated %s\"; git push origin main" % edate)