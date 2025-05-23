import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import streamlit as st
from matplotlib.dates import MonthLocator, YearLocator, DateFormatter
from dateutil.relativedelta import relativedelta

with st.container(border=True):
    st.write("You only need to press Submit if you change any of the default values")
    with st.form(key='Input_form', clear_on_submit = False):
        batt_size = st.number_input(label='Enter battery size in kWh', value = 10)
        batt_dod = st.number_input(label='Enter Depth of Discharge', min_value = 0.0, max_value = 1.0, value = 0.8)
        batt_eff = st.number_input(label='Enter Round Trip Efficiency', min_value = 0.0, max_value = 1.0, value = 0.9)
        inv_eff = st.number_input(label='Enter Inverter Efficiency', min_value = 0.0, max_value = 1.0, value = 0.95)
        submit_button = st.form_submit_button(label='Submit')
    
with st.container(border=True):
    st.write("Choose an input file by clicking Browse Files or dragging and dropping a file into shaded area")
    uploaded_file = st.file_uploader("")
if uploaded_file is not None:
    df=pd.read_excel(uploaded_file, sheet_name='Import_Export_kWhs')
    del df['Type']
    df['Date']= pd.to_datetime(df['Date'],format='%d/%m/%Y')
    max_date=max(df['Date'])
    default_date = max_date - relativedelta(months=1)
  
    df1=pd.read_excel(uploaded_file, sheet_name='Tariffs')
    df1['Date']= pd.to_datetime(df1['Date'],format='%d/%m/%Y')

    df2=pd.read_excel(uploaded_file, sheet_name='kWhs Generated')
    df2['Date']= pd.to_datetime(df2['Date'],format='%d/%m/%Y')
    min_date=min(df2['Date'])
    
    with st.container(border=True):
        st.write("Default dates are the last month of the valid smart meter data.  These dates can be changed while the app is running by clicking on them and selecting a date from the drop-down calendar")
        start_date = st.date_input("Enter Start Date", value = default_date, min_value = min_date, max_value = max_date)
        start_date = datetime.combine(start_date, datetime.min.time())

        end_date = st.date_input("Enter End Date", min_value = min_date, max_value = max_date)
        end_date = datetime.combine(end_date, datetime.min.time())

    no_of_days = ((end_date - start_date).days)+1
    period = str(start_date.strftime('%d-%b-%y')) + " to " + str(end_date.strftime('%d-%b-%y'))
    
    df_export = df.loc[df['Direction'].eq('Generation')]
    df_export = df_export.loc[df_export['Date'] >= start_date]
    df_export = df_export.loc[df_export['Date'] <= end_date]
    df_import = df.loc[df['Direction'].eq('Consumption')]
    df_import = df_import.loc[df_import['Date'] >= start_date]
    df_import = df_import.loc[df_import['Date'] <= end_date]

    df_export_tariff = df1.loc[df1['Direction'].eq('Generation')]
    df_export_tariff = df_export_tariff.loc[df_export_tariff['Date'] >= start_date]
    df_export_tariff = df_export_tariff.loc[df_export_tariff['Date'] <= end_date]
    df_import_tariff = df1.loc[df1['Direction'].eq('Consumption')]
    df_import_tariff = df_import_tariff.loc[df_import_tariff['Date'] >= start_date]
    df_import_tariff = df_import_tariff.loc[df_import_tariff['Date'] <= end_date]

    df_standing_charge = df1.loc[df1['Direction'].eq('Consumption')]
    df_standing_charge = df_standing_charge.loc[df_standing_charge['Date'] >= start_date]
    df_standing_charge = df_standing_charge.loc[df_standing_charge['Date'] <= end_date]
    del df_standing_charge['NMI']
    del df_standing_charge['Meter Number']
    df_standing_charge = df_standing_charge.iloc[:, :-48]
    total_standing_charge = df_standing_charge['Standing Charge'].sum() * 100
    
    def soc_calc(batt_size):
        global batt_soc,start_date,outputs,df_soc
        rows = df_export.shape[0]
        cols = df_export.shape[1]
        batt_soc=batt_size
        soc = []
        outputs = []
        new_export = []
        new_import = []
        new_export_credit = []
        new_import_cost = []
        new_net_costs = []
        old_export = []
        old_import = []
        old_export_credit = []
        old_import_cost = []
        old_net_costs = []
        dates = []
        condition = []
        for i in range (rows):
            for j in range (4, cols):
                exports = df_export.iloc[i,j]
                imports = df_import.iloc[i,j]
                exports_tariff = df_export_tariff.iloc[i,j+1]
                imports_tariff = df_import_tariff.iloc[i,j+1]
                net_energy = exports/inv_eff - imports/inv_eff/batt_eff
                batt_soc = batt_soc + net_energy
                if(batt_soc >= batt_size):
                    batt_soc = batt_size
                    new_exports = exports - imports
                    new_imports = 0
                    cond = 'A'
                elif(batt_soc <= (batt_size * (1 - batt_dod))):
                    batt_soc = (batt_size * (1 - batt_dod))
                    new_exports = exports
                    new_imports = imports
                    cond = 'B'
                else:
                    batt_soc = batt_soc
                    new_exports = 0
                    new_imports = 0
                    cond = 'C'
                old_exports_tariff = exports * exports_tariff
                old_imports_tariff = imports * imports_tariff
                old_net_cost = old_imports_tariff - old_exports_tariff
                new_exports_tariff = new_exports * exports_tariff
                new_imports_tariff = new_imports * imports_tariff
                new_net_cost = new_imports_tariff - new_exports_tariff
                        
                soc.append(batt_soc)
                old_export.append(exports)
                old_import.append(imports)
                old_export_credit.append(old_exports_tariff)
                old_import_cost.append(old_imports_tariff)
                old_net_costs.append(old_net_cost)
                new_export.append(new_exports)
                new_import.append(new_imports)
                new_export_credit.append(new_exports_tariff)
                new_import_cost.append(new_imports_tariff)
                new_net_costs.append(new_net_cost)
                condition.append(cond)
                start_date = start_date + timedelta(days = 1/48)
                dates.append(start_date)
        #start_date=date_0
        
        df_soc = pd.DataFrame({'Date':dates,'SoC':soc,'Exports':old_export,'Imports':old_import,'Exports_Value':old_export_credit,'Imports_Cost':old_import_cost,'Net_Cost':old_net_costs,'Exports1':new_export,'Imports1':new_import,'Exports_Value1':new_export_credit,'Imports_Cost1':new_import_cost,'Net_Cost1':new_net_costs,'Condition':condition})
        df_soc = df_soc.set_index('Date')
        total_exports = round(df_soc['Exports'].sum(),2)
        total_exports=("{0:,.2f}".format(total_exports)+" kWhs")
        total_imports = round(df_soc['Imports'].sum(),2)
        total_imports=("{0:,.2f}".format(total_imports)+" kWhs")
        total_exports_value = round(df_soc['Exports_Value'].sum(),2)
        total_exports_value = ("${0:,.2f}".format(total_exports_value / 100))
        total_imports_cost = round(df_soc['Imports_Cost'].sum(),2)
        total_imports_cost = ("${:,.2f}".format(total_imports_cost / 100))
        total_net_cost = round(df_soc['Net_Cost'].sum(),2) + total_standing_charge
        
        total_new_exports = round(df_soc['Exports1'].sum(),2)
        total_new_exports = ("{0:,.2f}".format(total_new_exports)+" kWhs")
        total_new_imports = round(df_soc['Imports1'].sum(),2)
        total_new_imports = ("{0:,.2f}".format(total_new_imports)+" kWhs")
        total_new_exports_value = round(df_soc['Exports_Value1'].sum(),2)
        total_new_exports_value = ("${0:,.2f}".format(total_new_exports_value / 100))
        total_new_imports_cost = round(df_soc['Imports_Cost1'].sum(),2)
        total_new_imports_cost = ("${:,.2f}".format(total_new_imports_cost / 100))
        total_new_net_cost = round(df_soc['Net_Cost1'].sum(),2) + total_standing_charge
        dollar_saving = (total_net_cost - total_new_net_cost)
        percent_saving = ((total_net_cost - total_new_net_cost) / total_net_cost) * 100
        dollar_saving = ("${:,.2f}".format(dollar_saving / 100))
        percent_saving = ("{:,.1f}%".format(percent_saving))
        total_new_net_cost = ("${:,.2f}".format(total_new_net_cost / 100))
        total_net_cost = ("${:,.2f}".format(total_net_cost / 100))
        
        title1 = "Data for period from " + str(period) + " (" + str(no_of_days) + " days"")"
        output_text1 = "Exports:" + "\t\t\t" + total_exports
        output_text2 = "Imports:" + "\t\t\t" + total_imports
        output_text3 = "Exports credit:" + "\t\t" + total_exports_value
        output_text4 = "Imports cost:" + "\t\t" + total_imports_cost
        output_text5 = "Total Bill:" + "\t\t\t" + total_net_cost + "\t\t" + "including standing charge of " + "${:,.2f}".format(total_standing_charge / 100) + "  but excluding tax"
        output_text6 = "Exports:" + "\t\t\t" + total_new_exports
        output_text7 = "Imports:" + "\t\t\t" + total_new_imports
        output_text8 = "Exports credit:" + "\t\t" + total_new_exports_value
        output_text9 = "Imports cost:" + "\t\t" + total_new_imports_cost
        output_text10 = "Total Bill:" + "\t\t\t" + total_new_net_cost + "\t\t" + "including standing charge of " + "${:,.2f}".format(total_standing_charge / 100) + "  but excluding tax"
        
        output_text11 = "Total $ Savings for period " + "\t\t" + dollar_saving
        output_text12 = "Total $ Savings for period " + "\t\t" + percent_saving
        
        with st.container(border=True):
            st.subheader(title1)
            st.subheader("Without Battery", divider = True)
            st.text(output_text1)
            st.text(output_text2)
            st.text(output_text3)
            st.text(output_text4)
            st.text(output_text5)
            st.subheader("With Battery", divider = True)
            st.text(output_text6)
            st.text(output_text7)
            st.text(output_text8)
            st.text(output_text9)
            st.text(output_text10)
            st.subheader("Savings", divider = True)
            st.text(output_text11)
            st.text(output_text12)
        
        title2 = "Battery SoC for period from " + str(period) + " (" + str(no_of_days) + " days"")"
        st.subheader(title2)
    
    soc_calc(batt_size)
    f1=plt.figure(figsize=(18,12))
    plt.plot(df_soc['SoC'])
    plt.title(f'Battery Size {batt_size} kWh')
    plt.grid(which='both')
    plt.xticks(rotation=45)
    plt.ylabel('kWhs')
    plt.xlabel('Date')
    plt.ylim(0, batt_size*1.1)
    st.pyplot(f1)
    
         

