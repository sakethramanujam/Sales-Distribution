import pandas as pd
import sys
import os

target_file = os.path.join("./",sys.argv[1])
stores_file = os.path.join("./",sys.argv[2])
sales_file = os.path.join("./",sys.argv[3])
output_file = os.path.join("./",sys.argv[4])

target = pd.read_csv(target_file)
stores = pd.read_csv(stores_file)
sales = pd.read_csv(sales_file)

def add_city_column(sales,stores):
    """Takes Stores Data and Sales Data to add an additional column w.r.t city to sales"""
    stores_cities = pd.DataFrame({"stores":sales["store"]})
    replacer = stores.set_index('store').to_dict()['city']
    cities = stores_cities.replace(replacer)
    sales = sales.assign(city=cities)
    return sales

def targets(target):
    target_cities,target_sales = [],[]
    for i in range(len(target)):
        target_cities.append(target['city'][i])
        target_sales.append(target['amount'][i])
    return dict(zip(target_cities,target_sales))

def start_date(target):
    target_cities,dates = [],[]
    for i in range(len(target)):
        target_cities.append(target['city'][i])
        dates.append(target['date'][i])
    return dict(zip(target_cities,dates))
    

def get_days(proportions,target_amount):
    prop_sum = sum(proportions)
    days = round(target_amount/prop_sum)
    return (days)

def fillsales(start_date,period,dictofprops):
    start_date = str(start_date)
    period = int(period)
    dataframe = pd.DataFrame()
    for storename in dictofprops:
        store = [storename for i in range(period)]
        sales = [dictofprops[storename] for j in range(period)]
        dates = pd.date_range(start=start_date,periods=period,freq='D')
        sales_df = pd.DataFrame(data=dates,columns=["Date"])
        sales_df = sales_df.assign(Store_Name=store,Sale_Value=sales)
        dataframe = dataframe.append(sales_df,ignore_index=True)
    return dataframe

def get_city_wise_group(sales):
    """
    - Takes in Sales Dataframe and groups stores by city as key
    - for each city returns sale targets of the store datewise
    """
    target_sales= pd.DataFrame()
    city_wise_store_group = sales.groupby('city')
    target_dict = targets(target)
    target_dates = start_date(target)
    for name,group in city_wise_store_group:
        dataframe = city_wise_store_group.get_group(name)
        #Creating a set of stores with amount as the identifier 
        unique_sales = dataframe["amount"].unique() 
        #calculating total sales by different stores to ultimately find sale proportions
        total_sale_per_day = sum(unique_sales)
        ratios,proportions = [],[]
        store_names = []
        for i in range(len(unique_sales)):
            ratio = unique_sales[i]/total_sale_per_day
            ratios.append(ratio)
            proportions.append(unique_sales[i]*ratio)
            indices = dataframe[dataframe["amount"]==unique_sales[i]].index.values.astype(int)
            index = indices[0]
            store_names.append(dataframe["store"][index])
        proportion_dict = dict(zip(store_names,proportions))
        #days needed to complete target
        days_to_complete = get_days(proportions,target_dict[name])
        city_wise_sales = fillsales(target_dates[name],days_to_complete,proportion_dict)
        target_sales = target_sales.append(city_wise_sales,ignore_index=True)
    print(sys.argv[4],"Generated at ",output_file)
    return target_sales

sales = add_city_column(sales,stores) 
answer=get_city_wise_group(sales)
answer.to_csv(output_file,index=False)
