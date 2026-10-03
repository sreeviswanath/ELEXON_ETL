import pandas as pd

raw_df = pd.read_csv("v1_remit_production_unavailability.csv")

# Drop unwanted columns

print(raw_df.columns.to_list())

# print()

raw_df = raw_df.drop(columns=['dataset','messageType','messageHeading','participantId','unavailableCapacity','cause', 'affectedUnitEIC', 'affectedArea','durationUncertainty', 'relatedInformation', 'outageProfile'])

print("AFter dropping cols.....")

print(raw_df)








# i have a df where i need to create two columns namely startTimeSeries and EndTimeSeries based on the column eventStartTime and eventEndTime .
# The startTimeSeries and endTimeSeries should be a time series column based on event time
# columns , spliut into months
# eg:
# so in the df , you can see my eventStartTime havng the date 20-01-2024 and eventendTime having the date 15-01-2025
# i need startTimeseries and endTimeseries to have
# 20-01-2024 - 01-02-2024
# 01-02-2024 - 01-03-2024
# .
# .
# 01-12-2024 - 01-01-2025
# 01-01-2025 - 15-01-2025
# i need to retain every other column value as it is , so if availcapacity of 20-01-2024 to 15-01-2025 is 300, all the generated timeseries value should have 300 itself, (this should be applicable for all other columns)
# the following is a part of my data:
# id	dataset	mrid	revisionNumber	publishTime	createdTime	messageType	messageHeading	eventType	unavailabilityType	participantId	registrationCode	assetId	assetType	affectedUnit	biddingZone	normalCapacity	availableCapacity	unavailableCapacity	eventStatus	eventStartTime	eventEndTime	cause	affectedUnitEIC	affectedArea	fuelType	relatedInformation	outageProfile	durationUncertainty
# 50986	REMIT	0000000000000003-ELXP-RMT-00000003	8	12-01-2024 17:25	12-01-2024 17:24	UnavailabilitiesOfElectricityFacilities	New: N_NPSCP - Unavailability of 48W00000CRYRW-2L at 2023-12-17 10:34:00, expected to last until 2023-12-17 15:00:00	Production unavailability	Unplanned	N_NPSCP	48W00000CRYRW-2L	48W00000CRYRW-2L	Production	CRYRW-2	10YGB----------A	138	104	34	Active	17-12-2023 11:34	17-01-2024 18:00	CCT 5 fault and 5 x offline from CCT 4						
# 767073	REMIT	0000000000000051-ELXP-RMT-00000051	1	16-07-2024 07:36	16-07-2024 07:34	UnavailabilitiesOfElectricityFacilities	New: N_NPSCP - Unavailability of 48W00000CRYRW-2L at 2024-07-18 08:00:00, expected to last until 2024-07-19 17:00:00	Production unavailability	Planned	N_NPSCP	48W00000CRYRW-2L	48W00000CRYRW-2L	Production	CRYRW-2	10YGB----------A	138	0	140	Active	18-07-2024 10:00	19-07-2024 19:00	DNO maintenance on 400Kv SGT1.	48W00000CRYRW-2L	N	Wind Onshore			
# 767534	REMIT	0000000000000051-ELXP-RMT-00000051	1	19-07-2024 15:57	19-07-2024 15:54	UnavailabilitiesOfElectricityFacilities	New: N_NPSCP - Unavailability of 48W00000CRYRW-2L at 2024-07-18 08:00:00, expected to last until 2024-07-19 17:00:00	Production unavailability	Planned	N_NPSCP	48W00000CRYRW-2L	48W00000CRYRW-2L	Production	CRYRW-2	10YGB----------A	138	0	140	Active	18-07-2024 10:00	19-07-2024 16:55	DNO maintenance on 400Kv SGT1.	48W00000CRYRW-2L	N	Wind Onshore			
# 767535	REMIT	0000000000000051-ELXP-RMT-00000051	1	19-07-2024 15:59	19-07-2024 15:57	UnavailabilitiesOfElectricityFacilities	New: N_NPSCP - Unavailability of 48W00000CRYRW-2L at 2024-07-18 08:00:00, expected to last until 2024-07-19 17:00:00	Production unavailability	Planned	N_NPSCP	48W00000CRYRW-2L	48W00000CRYRW-2L	Production	CRYRW-2	10YGB----------A	138	0	140	Active	18-07-2024 10:00	19-07-2024 16:55	DNO maintenance on 400Kv SGT1.	48W00000CRYRW-2L	N	Wind Onshore			


# #create two new columns startTimeSeries and endTimeSeries based on eventStartTime and eventEndTime columns
# df["eventStartTime"] = pd.to_datetime(df["eventStartTime"])
# df["eventEndTime"] = pd.to_datetime(df["eventEndTime"])
# def create_monthly_timeseries(row):
#     start = row["eventStartTime"]
#     end = row["eventEndTime"]
#     periods = []
#     current_start = start
#     while current_start < end:
#         # First day of the month after current_start
#         next_month = (
#             current_start.replace(day=1)
#             + pd.offsets.MonthBegin(1)
#         )
#         # The next boundary cannot go beyond eventEndTime
#         current_end = min(next_month, end)
#         periods.append({
#             "startTimeSeries": current_start,
#             "endTimeSeries": current_end
#         })
#         current_start = current_end
#     return periods

# print(df)




# # #create a function to generate monthly time series intervals based on eventStartTime and eventEndTime
# # def create_monthly_timeseries(row):

# #     start = row["eventStartTime"]

# #     end = row["eventEndTime"]

# #     periods = []

# #     current_start = start

# #     while current_start < end:

# #         # First day of the month after current_start

# #         next_month = (

# #             current_start.replace(day=1)

# #             + pd.offsets.MonthBegin(1)

# #         )

# #         # The next boundary cannot go beyond eventEndTime

# #         current_end = min(next_month, end)

# #         periods.append({

# #             "startTimeSeries": current_start,

# #             "endTimeSeries": current_end

# #         })

# #         current_start = current_end

# #     return periods

# # # Create the monthly intervals
# # df["monthly_intervals"] = df.apply(create_monthly_timeseries, axis=1)

# # # Explode the list of dictionaries into separate rows
# # df = df.explode("monthly_intervals")    

# # # Create new columns for startTimeSeries and endTimeSeries
# # df["startTimeSeries"] = df["monthly_intervals"].apply(lambda x: x["startTimeSeries"] if pd.notnull(x) else None)
# # df["endTimeSeries"] = df["monthly_intervals"].apply(lambda x: x["endTimeSeries"] if pd.notnull(x) else None)

# # # Drop the temporary column
# # df = df.drop(columns=["monthly_intervals"])


# # #retain all other columns as they are and forward fill rest of row values for the generated time series intervals
# # df = df.ffill()


# # print(df)

# # df.to_csv("elexon_timeSeries_check.csv")
