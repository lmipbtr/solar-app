import pandas as pd
import numpy as np
import streamlit as st
import sys
import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime
#from io import StringIO
from matplotlib.dates import MonthLocator, YearLocator, DateFormatter

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    #bytes_data = uploaded_file.getvalue()
    #st.write(bytes_data)

    # To convert to a string based IO:
    #stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    #st.write(stringio)

    # To read file as string:
    #string_data = stringio.read()
    #st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
    df_import_export=pd.read_excel(uploaded_file, sheet_name='Import_Export_kWhs')
    df_generation=pd.read_excel(uploaded_file, sheet_name='kWhs Generated')
    df_tariffs=pd.read_excel(uploaded_file, sheet_name='Tariffs')
    
    nmi=df_import_export.iloc[0,0]
    meter_number=df_import_export.iloc[1,1]
    if str(nmi)[0] == '1':
        currency = '€'
        
    elif str(nmi)[0] == '6':
        currency = '$'

    del df_import_export['NMI']
    del df_import_export['Meter Number']
    del df_import_export['Type']
    del df_tariffs['NMI']
    del df_tariffs['Meter Number']
    df_import_export['Date']= pd.to_datetime(df_import_export['Date'],format='%d/%m/%Y')
    df_tariffs['Date']= pd.to_datetime(df_tariffs['Date'],format='%d/%m/%Y')
    min_date=min(df_import_export['Date'])
    max_date=max(df_import_export['Date'])
 
    #st.write(df_import_export)
    #st.write(df_generation)
    #st.write(df_tariffs)
     
    start_date = st.date_input("Enter Start Date", today)
    st.write("Start Date is:", start_date)
    
    end_date = st.date_input("Enter End Date", today)
    st.write("End Date is:", end_date)
    
    no_of_days = ((end_date - start_date).days)+1
    
    df_daily_import_export_kWhs = df_import_export.copy()
    cols_to_sum = df_daily_import_export_kWhs.columns[ 2 : df_daily_import_export_kWhs.shape[1]]
    df_daily_import_export_kWhs['Daily Total kWhs'] = df_daily_import_export_kWhs[cols_to_sum].sum(axis=1)
    df_daily_import_export_kWhs = df_daily_import_export_kWhs.drop(df_daily_import_export_kWhs.iloc[:, 2:-1],axis = 1)

    df_daily_import_kWhs = df_daily_import_export_kWhs[(df_daily_import_export_kWhs['Direction'] == 'Consumption')]
    del df_daily_import_kWhs['Direction']
    df_daily_import_kWhs.rename({'Daily Total kWhs': 'Import_kWh'}, axis='columns', inplace=True)
    
    df_daily_import_kWhs = df_daily_import_kWhs.loc[df_daily_import_kWhs['Date'].dt.date >= start_date]
    df_daily_import_kWhs = df_daily_import_kWhs.loc[df_daily_import_kWhs['Date'].dt.date <= end_date]
    
    #df_daily_import_kWhs.set_index(['Date'], inplace=True)

    df_daily_export_kWhs = df_daily_import_export_kWhs[(df_daily_import_export_kWhs['Direction'] == 'Generation')]
    del df_daily_export_kWhs['Direction']
    df_daily_export_kWhs.rename({'Daily Total kWhs': 'Export_kWh'}, axis='columns', inplace=True)
    
    df_daily_export_kWhs = df_daily_export_kWhs.loc[df_daily_export_kWhs['Date'].dt.date >= start_date]
    df_daily_export_kWhs = df_daily_export_kWhs.loc[df_daily_export_kWhs['Date'].dt.date <= end_date]
    
    #df_daily_export_kWhs.set_index(['Date'], inplace=True)
    df_export = df_import_export.loc[df_import_export['Direction'].eq('Generation')]
    df_export['Direction'] = df_export['Direction'].str.replace('Generation','Export')
    df_export = df_export.loc[df_export['Date'].dt.date >= start_date]
    df_export = df_export.loc[df_export['Date'].dt.date <= end_date]
    df_import = df_import_export.loc[df_import_export['Direction'].eq('Consumption')]
    df_import['Direction'] = df_import['Direction'].str.replace('Consumption','Import')
    df_import = df_import.loc[df_import['Date'].dt.date >= start_date]
    df_import = df_import.loc[df_import['Date'].dt.date <= end_date]
    df_generation_all_total = df_generation.copy()
    df_generation = df_generation.loc[df_generation['Date'].dt.date >= start_date]
    df_generation = df_generation.loc[df_generation['Date'].dt.date <= end_date]
    df_generation['Date']= pd.to_datetime(df_generation['Date'],format='%d/%m/%Y')
    del df_generation['Type']
    del df_export['Direction']
    del df_import['Direction']
    df_generation_all = df_generation.copy()
    del df_generation_all_total['Type']
    
    df_export.set_index(['Date'],inplace=True)
    df_import.set_index(['Date'],inplace=True)
    df_generation.set_index(['Date'],inplace=True)
    
    df_daily_generated_kWhs = df_generation_all.copy()
    cols_to_sum = df_daily_generated_kWhs.columns[ 2 : df_daily_generated_kWhs.shape[1]-1]
    df_daily_generated_kWhs['Generation_kWh'] = df_daily_generated_kWhs[cols_to_sum].sum(axis=1)
    df_daily_generated_kWhs = df_daily_generated_kWhs.drop(df_daily_generated_kWhs.iloc[:, 1:-1],axis = 1)
    #df_daily_generated_kWhs.rename(columns={0: 'Date'}, inplace=True)
    #df_daily_generated_kWhs.set_index(['Date'], inplace=True)

    df_export_daily_profile = df_export.copy()
    #df_export_daily_profile.set_index('Date',inplace=True)
    df_export_daily_profile = df_export_daily_profile.mean()

    df_import_daily_profile = df_import.copy()
    #df_import_daily_profile.set_index('Date',inplace=True)
    df_import_daily_profile = df_import_daily_profile.mean()

    df_generation_daily_profile = df_generation.copy()
    #df_generation_daily_profile.set_index(['Date'], inplace=True)
    df_generation_daily_profile = df_generation_daily_profile.mean()
    
    df_load = df_import + df_generation - df_export
    df_load_daily_profile = df_load.copy()
    df_load_daily_profile = df_load_daily_profile.mean()
    
    df_daily_total_kWhs = df_daily_import_kWhs.merge(df_daily_export_kWhs.merge(df_daily_generated_kWhs, on='Date'),on='Date')
    df_daily_total_kWhs['Load_kWh'] = df_daily_total_kWhs.apply(lambda row: row['Import_kWh'] + (row['Generation_kWh'] - row['Export_kWh']), axis=1)
    
    #df_daily_import_kWhs
    #df_daily_export_kWhs
    #df_daily_generated_kWhs
    
    #df_daily_total_kWhs.set_index(['Date'], inplace=True)
    #df_daily_total_kWhs
    
    total_exports=df_daily_total_kWhs['Export_kWh'].sum()
    total_imports=df_daily_total_kWhs['Import_kWh'].sum()
    total_generated=df_daily_total_kWhs['Generation_kWh'].sum()
    total_load=df_daily_total_kWhs['Load_kWh'].sum()
    
    total_exports_float=total_exports
    total_imports_float=total_imports
    total_generated_float=total_generated
    total_load_float=total_load
    
    df_totals_max = df_daily_total_kWhs.idxmax()
    df_totals_min = df_daily_total_kWhs.idxmin()
    df_totals_mean = df_daily_total_kWhs.mean()
    
    df_totals_non_zero = df_daily_total_kWhs.drop(df_daily_total_kWhs[df_daily_total_kWhs.Export_kWh == 0].index)
    if df_totals_non_zero.empty:
        dummy_row=[start_date,0,0,0,0]
        df_totals_non_zero.loc[1] = dummy_row
        #df_totals_non_zero.append(dummy_row)
    df_totals_export_min = df_totals_non_zero.idxmin()
    export_max=df_daily_total_kWhs.iloc[df_totals_max.iloc[2]]
    export_min=df_daily_total_kWhs.iloc[df_totals_export_min.iloc[2]]
    
    import_max=df_daily_total_kWhs.iloc[df_totals_max.iloc[1]]
    import_min=df_daily_total_kWhs.iloc[df_totals_min.iloc[1]]
    generation_max=df_daily_total_kWhs.iloc[df_totals_max.iloc[3]]
    generation_min=df_daily_total_kWhs.iloc[df_totals_export_min.iloc[3]]
    load_max=df_daily_total_kWhs.iloc[df_totals_max.iloc[4]]
    load_min=df_daily_total_kWhs.iloc[df_totals_min.iloc[4]]

    export_max_date=str(export_max.iloc[0].strftime("%d-%b-%Y"))
    export_max_kWh=export_max.iloc[2]
    
    export_min_date=str(export_min.iloc[0].strftime("%d-%b-%Y"))
    export_min_kWh = export_min.iloc[2]
    export_mean_kWh = df_totals_non_zero['Export_kWh'].mean()#df_totals_mean.iloc[1]
    export_max_kWh = ("{0:.2f}".format(export_max_kWh))
    export_min_kWh = ("{0:.2f}".format(export_min_kWh))
    export_mean_kWh = ("{0:.2f}".format(export_mean_kWh))

    import_max_date=str(import_max.iloc[0].strftime("%d-%b-%Y"))
    import_max_kWh=import_max.iloc[1]
    import_min_date=str(import_min.iloc[0].strftime("%d-%b-%Y"))
    import_min_kWh = import_min.iloc[1]
    import_mean_kWh = df_totals_non_zero['Import_kWh'].mean()#df_totals_mean.iloc[1]
    #import_mean_kWh = df_totals_mean.iloc[1]
    import_max_kWh = ("{0:.2f}".format(import_max_kWh))
    import_min_kWh = ("{0:.2f}".format(import_min_kWh))
    import_mean_kWh = ("{0:.2f}".format(import_mean_kWh))

    generation_max_date=str(generation_max.iloc[0].strftime("%d-%b-%Y"))
    generation_max_kWh=generation_max.iloc[3]
    generation_min_date=str(generation_min.iloc[0].strftime("%d-%b-%Y"))
    generation_min_kWh = generation_min.iloc[3]
    generation_mean_kWh = df_totals_non_zero['Generation_kWh'].mean()#df_totals_mean.iloc[3]
    generation_max_kWh = ("{0:.2f}".format(generation_max_kWh))
    generation_min_kWh = ("{0:.2f}".format(generation_min_kWh))
    generation_mean_kWh = ("{0:.2f}".format(generation_mean_kWh))

    load_max_date=str(load_max.iloc[0].strftime("%d-%b-%Y"))
    load_max_kWh=load_max.iloc[4]
    load_min_date=str(load_min.iloc[0].strftime("%d-%b-%Y"))
    load_min_kWh = load_min.iloc[4]
    load_mean_kWh = df_totals_mean.iloc[4]
    load_max_kWh = ("{0:.2f}".format(load_max_kWh))
    load_min_kWh = ("{0:.2f}".format(load_min_kWh))
    load_mean_kWh_str = ("{0:.2f}".format(load_mean_kWh))

    df_tariffs_fit = df_tariffs.loc[df_tariffs['Direction'].eq('Generation')]
    df_tariffs_fit['Direction'] = df_tariffs_fit['Direction'].str.replace('Generation','Export')
    df_tariffs_fit=df_tariffs_fit.loc[df_tariffs_fit['Date'].dt.date >= start_date]
    df_tariffs_fit=df_tariffs_fit.loc[df_tariffs_fit['Date'].dt.date <= end_date]
    df_tariffs_fot = df_tariffs.loc[df_tariffs['Direction'].eq('Consumption')]
    df_tariffs_fot['Direction'] = df_tariffs_fot['Direction'].str.replace('Consumption','Import')
    df_tariffs_fot=df_tariffs_fot.loc[df_tariffs_fot['Date'].dt.date >= start_date]
    df_tariffs_fot=df_tariffs_fot.loc[df_tariffs_fot['Date'].dt.date <= end_date]

    df_import_all = df_import.copy()
    df_export_all = df_export.copy()
    
    connection_charge_no_gst = (df_tariffs_fit.iloc[:,2].sum())
    average_conn_fee = connection_charge_no_gst / float(no_of_days)
    connection_charge_no_gst_str = (currency+"{0:.2f}".format(connection_charge_no_gst))
    average_conn_fee = (currency+"{0:.2f}".format(average_conn_fee))
    total_bill_excl_gst = connection_charge_no_gst
    
    df_tariffs_fit.drop(df_tariffs_fit.iloc[:, 0:3], inplace=True, axis=1)
    #df_export_all.drop(df_export_all.iloc[:, 0:2], inplace=True, axis=1)

    df_export_value = df_tariffs_fit*df_export_all.values
    export_credit = df_export_value.values.sum() / 100
    average_export_credit = export_credit / float(no_of_days)
    total_bill_excl_gst = total_bill_excl_gst - export_credit
    total_export_kWhs = df_export_all.values.sum()
    average_kWh_exported = total_export_kWhs / float(no_of_days)
    fit = export_credit / total_export_kWhs
    total_export_kWhs = ("{0:,.2f}".format(total_export_kWhs))
    average_kWh_exported = ("{0:.2f}".format(average_kWh_exported))
    fit = (currency+"{0:.3f}".format(fit))
    average_export_credit = (currency+"{0:.2f}".format(average_export_credit))
    export_credit_str = (currency+"{0:.2f}".format(export_credit))

    df_tariffs_fot.drop(df_tariffs_fot.iloc[:, 0:3], inplace=True, axis=1)
    #df_import_all.drop(df_import_all.iloc[:, 0:2], inplace=True, axis=1)
    df_import_value = df_tariffs_fot*df_import_all.values
    import_charge = df_import_value.values.sum() / 100 #*1.1
    average_import_charge = import_charge / float(no_of_days)
    total_import_kWhs = df_import_all.values.sum()
    average_import_kWhs = total_import_kWhs / float(no_of_days)
    tariff=import_charge / total_import_kWhs
    total_bill_excl_gst = total_bill_excl_gst + import_charge
    average_total_bill = total_bill_excl_gst / float(no_of_days)
    import_charge_str = (currency+"{0:.2f}".format(import_charge))
    average_import_charge = (currency+"{0:.2f}".format(average_import_charge))
    total_import_kWhs = ("{0:,.2f}".format(total_import_kWhs))
    average_import_kWhs = ("{0:.2f}".format(average_import_kWhs))
    tariff_str = (currency+"{0:.3f}".format(tariff))
    average_total_bill = (currency+"{0:.2f}".format(average_total_bill))
    
    generated_exported=total_exports / total_generated
    generated_to_load=1-generated_exported
    load_imported=total_imports / total_load
    load_generated=1-load_imported
    generated_less_exports=(total_generated-total_exports)
    average_kWh_exported = total_exports / no_of_days
    average_kWh_exported=("{0:,.2f}".format(average_kWh_exported)+" kWh/day")
    total_exports=("{0:,.2f}".format(total_exports)+" kWhs")
    total_imports=("{0:,.2f}".format(total_imports)+" kWhs")
    total_load=("{0:,.2f}".format(total_load)+" kWhs")
    total_generated=("{0:,.2f}".format(total_generated)+" kWhs")
    generated_less_exports=("{0:,.2f}".format(generated_less_exports))
    period = str(start_date.strftime('%d-%b-%y')) + " to " + str(end_date.strftime('%d-%b-%y'))
    
    fig, (ax1,ax2) = plt.subplots(1,2,subplot_kw={'aspect':'equal'})
    fig.suptitle(f'For period {period}', fontsize=10, color = 'Red', y=0.8)
    #fig.tight_layout()
    
    fig.canvas.manager.set_window_title('Pie Charts')
    pie1_title=f"Total Generated {total_generated}"
    label_export='Exported\n'+total_exports
    label_load='Load\n'+generated_less_exports+" kWhs"
    pie1_labels=label_load, label_export
    pie1_data=[generated_to_load,generated_exported]
    ax1.set_title(pie1_title,fontsize=8)
    ax1.pie(pie1_data, labels=pie1_labels, autopct='%1.1f%%', textprops={'fontsize': 6})

    #fig.add_subplot(2,1,2)#plt.subplot(2,2,1)
    colors=['red','green']
    pie2_title=f"Total Load {total_load}"
    label_import='Imported\n'+total_imports
    label_gen='Generated\n'+generated_less_exports+" kWhs"
    pie2_labels=label_import, label_gen
    pie2_data=[load_imported,load_generated]
    ax2.set_title(pie2_title,fontsize=8)
    ax2.pie(pie2_data, labels=pie2_labels, autopct='%1.1f%%', colors=colors, textprops={'fontsize': 6})

    st.pyplot(fig)
    
    #del df_generation_all['Type']
    df_generation_non_zero = df_generation_all_total.copy()
    df_generation_non_zero['Date'] = pd.to_datetime(df_generation_non_zero['Date'],format='%d/%m/%Y')
    df_generation_non_zero[50] = df_generation_non_zero.iloc[:,2:49].sum(axis=1)
    df_generation_non_zero = df_generation_non_zero[df_generation_non_zero[50]!=0]
    df_generation_non_zero.drop(df_generation_non_zero.iloc[:,1:49], axis=1, inplace=True)
    df_generation_non_zero.columns=['Date', 'kWhs']

    df_monthly_sums = df_generation_non_zero.groupby(df_generation_non_zero.Date.dt.to_period('M')).sum(numeric_only=True)#.plot.bar()#rename('Year'),df_generation_non_zero['Date'].dt.month.name().rename('Month')])['kWhs'].sum().reset_index())
    df_annual_sums = df_generation_non_zero.groupby(df_generation_non_zero.Date.dt.to_period('Y')).sum(numeric_only=True)#.plot.bar()#rename('Year'),df_generation_non_zero['Date'].dt.month.name().rename('Month')])['kWhs'].sum().reset_index())

    fig=plt.figure(figsize=(18,12))
    bplot1 = plt.bar(df_daily_total_kWhs['Date'], df_daily_total_kWhs['Load_kWh'], color='magenta', width=0.5, edgecolor='gray', label='Load kWh')
    bplot2 = plt.bar(df_daily_total_kWhs['Date'], df_daily_total_kWhs['Import_kWh'], color='cyan', width=0.5, edgecolor='gray', label='Imported kWh')
    plt.xlabel('Date')
    plt.ylabel('kWh')
    plt.xticks(rotation=45)
    plt.title('Total Load and Imported kWhs')
    plt.bar_label(bplot1,color='black',fmt='%.1f',padding=-14)
    plt.bar_label(bplot2,color='black',fmt='%.1f',padding=-14)
    plt.legend()
    plt.grid(which='both', color='gray', linestyle='dashed', linewidth=0.5)

    st.pyplot(fig)
    #st.bar_chart(df_daily_total_kWhs, y = "Import_kWh", x_label="Date", y_label="Imported Kwhs", color="#0000ff")
    #st.bar_chart(df_daily_export_kWhs, x_label="Date", y_label="Exported Kwhs", color="#ff0000")
    #st.bar_chart(df_generation_non_zero, x_label="Date", y_label="Generated Kwhs", color="#00ff00")'''
    
    fig = plt.figure(figsize=(18,12))
    bplot1 = plt.bar(df_daily_total_kWhs['Date'], df_daily_total_kWhs['Export_kWh'], color='orange', width=0.5, edgecolor='gray', label='Exported kWh')
    bplot2 = plt.bar(df_daily_total_kWhs['Date'], df_daily_total_kWhs['Import_kWh'] * -1, color='purple', width=0.5, edgecolor='gray', label='Imported kWh')
    plt.xlabel('Date')
    plt.ylabel('kWh')
    plt.xticks(rotation=45)
    plt.title('Total Imported and Exported kWhs')
    plt.bar_label(bplot1,color='black',fmt='%.1f',padding=-14)
    plt.bar_label(bplot2,color='yellow',fmt='%.1f',padding=-14)
    plt.legend()
    plt.grid(which='both', color='gray', linestyle='dashed', linewidth=0.5)

    st.pyplot(fig)
    
    fig = plt.figure(figsize=(18,12))
    bplot1 = plt.bar(df_daily_total_kWhs['Date'], df_daily_total_kWhs['Generation_kWh'], color='yellow', width=0.5, edgecolor='gray', label='Generated kWh')
    bplot2 = plt.bar(df_daily_total_kWhs['Date'], df_daily_total_kWhs['Export_kWh'], color='lime', width=0.5, edgecolor='gray', label='Exported kWh')
    plt.xlabel('Date')
    plt.ylabel('kWh')
    plt.xticks(rotation=45)
    plt.title('Total Generated and Exported kWhs')
    plt.bar_label(bplot1,color='black',fmt='%.1f',padding=-14)
    plt.bar_label(bplot2,color='black',fmt='%.1f',padding=-14)
    plt.legend()
    plt.grid(which='both', color='gray', linestyle='dashed', linewidth=0.5)

    st.pyplot(fig)
    
    fig, ax = plt.subplots(figsize=(18,12))
    #fig.tight_layout()
    fig.canvas.manager.set_window_title('Monthly kWhs')
    bplot2=plt.bar(df_monthly_sums.index.to_timestamp(), df_monthly_sums.kWhs, width = 20)
    ax.xaxis.set_major_locator(MonthLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%b-%Y'))
    plt.xlabel('Month')
    plt.ylabel('kWhs')
    plt.xticks(rotation=45)
    plt.title('Monthly Generated kWhs')
    plt.bar_label(bplot2,color='black',fmt='%.0f')
    plt.grid(which='both', color='gray', linestyle='dashed')

    st.pyplot(fig)
    
    fig, ax = plt.subplots(figsize=(18,12))
    fig.canvas.manager.set_window_title('Annual kWhs')
    bplot2=plt.bar(df_annual_sums.index.to_timestamp(), df_annual_sums.kWhs, width = 100)
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%Y'))
    plt.xlabel('Year')
    plt.ylabel('kWhs')
    plt.xticks(rotation=45)
    plt.title('Annual Generated kWhs')
    plt.bar_label(bplot2,color='black',fmt='%.0f')
    plt.grid(which='both', color='gray', linestyle='dashed', linewidth=0.5)

    st.pyplot(fig)
     
    fig, ax = plt.subplots(figsize=(18,12))
    #fig=plt.figure()
    #fig.tight_layout()
    fig.canvas.manager.set_window_title('Daily Profiles')
    fig.add_subplot(2,2,1)#plt.subplot(2,2,1)
    #df_generation_daily_profile = df_generation_all.mean()
    df_generation_daily_profile.plot.bar(title = "Daily Generation kWh Profile")
    plt.xticks([])
    #plt.xticks(rotation=45)

    fig.add_subplot(2,2,2)#plt.subplot(2,2,2)
    #fig.tight_layout()
    df_import_daily_profile.plot.bar(title = "Daily Import kWh Profile")
    plt.xticks([])
    #plt.xticks(rotation=45)

    fig.add_subplot(2,2,3)#plt.subplot(2,2,3)
    #fig.tight_layout()
    df_export_daily_profile.plot.bar(title = "Daily Export kWh Profile")
    plt.xticks([])
    #plt.xticks(rotation=45)
    #plt.subplots_adjust(left=0.125, right=0.9, bottom=0.1, top=0.9, hspace=0.4)

    fig.add_subplot(2,2,4)
    #fig.tight_layout()
    df_load_daily_profile.plot.bar(title = "Daily Load kWh Profile")
    plt.xticks([])
    #plt.xticks(rotation=45)
    #pw.addPlot('Daily Profiles', fig)
    #plt.savefig(filepath+'Daily Profiles.png')
    #plt.tight_layout(pad=0.8, w_pad=0.8, h_pad=1.0)

    st.pyplot(fig)
    
    #del df_tariffs_fit['Direction']
    #del df_tariffs_fit['Standing Charge']
    #df_tariffs_fit.set_index(['Date'], inplace=True)
    #del df_tariffs_fot['Direction']
    #del df_tariffs_fot['Standing Charge']
    #df_tariffs_fot.set_index(['Date'], inplace=True)
    
    average_fit = df_tariffs_fit.mean().mean()
    average_fot = df_tariffs_fot.mean().mean()
    
    export_credit = (total_exports_float * average_fit) / 100
    imports_charge = (total_imports_float * average_fot) / 100
    load_charge = (total_load_float * average_fot) / 100
    tax1 = (imports_charge + connection_charge_no_gst) * 0.1
    tax2 = (load_charge + connection_charge_no_gst) * 0.1
    
    data1 = {"Consumption_Cost": [load_charge,imports_charge],"Feed_in_Tariff": [0, -export_credit],"Connection_Fee":[connection_charge_no_gst,connection_charge_no_gst],"Tax":[tax2,tax1]}
    df= pd.DataFrame(data1, index = ["Without_Solar", "With_Solar"])
    df["Total"]=df.sum(axis=1)
    
    total_savings=(df.iat[0,4] - df.iat[1,4] ) / df.iat[0,4]
    total_savings=("{0:.2%}".format(total_savings))
    period = str(start_date.strftime('%d-%b-%y')) + " to " + str(end_date.strftime('%d-%b-%y'))
    title = (f'Total savings for period {period}: {total_savings}')

    fig, ax = plt.subplots(figsize=(18,12))
    #fig, ax = plt.subplots()
    #bplot1 = plt.bar(df['Consumption_Cost'], df['Feed_in_Tariff'], df['Connection_Fee'], df['Tax'])
    #bplot2 = plt.bar(df.index, height=df['Total'], color='cyan', edgecolor='gray')
    ax.bar(df.index, df.Consumption_Cost, align='edge', width=0.3)
    ax.bar_label(ax.containers[0], label_type='center',fmt=currency+'{:,.2f}')
    ax.bar(df.index, df.Connection_Fee, align='edge', width=0.3, bottom=df.Consumption_Cost)
    ax.bar_label(ax.containers[1], label_type='center',fmt=currency+'{:,.2f}')
    ax.bar(df.index, df.Tax, align='edge', width=0.3, bottom=df.Consumption_Cost + df.Connection_Fee)
    ax.bar_label(ax.containers[2], label_type='center',fmt=currency+'{:,.2f}')
    ax.bar(df.index, df.Feed_in_Tariff, align='edge', width=0.3, bottom=0)#df.Consumption_Cost)
    ax.bar_label(ax.containers[3], label_type='center',fmt=currency+'{:,.2f}')
    ax.bar(df.index, df.Total, align='edge', width=-0.3)#df.Consumption_Cost)
    ax.bar_label(ax.containers[4], label_type='center',fmt=currency+'{:,.2f}')
    ax.legend(['Consumption Cost', 'Connection Fee', 'Tax', 'Feed-in-Tariff', 'Total'])
    ax.grid(which='both')
    ax.set_ylabel(currency)
    ax.set_title(title,fontsize=18, fontweight='bold', color='red')

    st.pyplot(fig)
    
    bill_w_o_solar=(load_mean_kWh*no_of_days*tariff)+connection_charge_no_gst
    average_bill_w_o_solar=(load_mean_kWh*tariff)+(connection_charge_no_gst/no_of_days)
    average_bill_w_o_solar=(currency+"{0:.2f}".format(average_bill_w_o_solar))
    net_savings = (bill_w_o_solar - total_bill_excl_gst) / bill_w_o_solar
    bill_w_o_solar=(currency+"{0:.2f}".format(bill_w_o_solar))
    total_bill_excl_gst = (currency+"{0:.2f}".format(total_bill_excl_gst))
    net_savings = ("{0:.2%}".format(net_savings))

    if str(nmi)[0] == '1':
        discount = 0
        tax = 0.09
        total_bill_incl_tax_disc=(((connection_charge_no_gst + import_charge) * (1 + tax)) * (1-discount))
        total_bill_incl_tax_disc_str = (currency+"{0:.2f}".format(total_bill_incl_tax_disc))
    elif str(nmi)[0] == '6':
        discount = 0.19
        tax = 0.1
        total_bill_incl_tax_disc=(((connection_charge_no_gst + import_charge) * (1 + tax)) * (1-discount)) - export_credit
        total_bill_incl_tax_disc_str=(currency+"{0:.2f}".format(total_bill_incl_tax_disc))

    title = "Billing Data for period from " + str(period) + "(" + str(no_of_days) + " days"")" + " MPRN:" + str(nmi)
    billing_text1 = "Total Connection Fee for period: "+"\t"+connection_charge_no_gst_str+"\t\t\t"+"("+average_conn_fee+" /day)"
    billing_text2 = "Total Exported Energy in period: "+"\t"+total_exports+"\t"+"("+average_kWh_exported+")"
    billing_text3 = "Total Exported Credit in period: "+"\t"+export_credit_str+"\t\t\t"+"("+average_export_credit+" /day)"+"\t\t"+"("+fit+" /kWh)"
    billing_text4 = "Total Imported Energy in period: "+"\t"+total_import_kWhs+" kWh\t\t"+"("+average_import_kWhs+" kWh/day)"
    billing_text5 = "Total Imported Cost in period: "+"\t\t"+import_charge_str+"\t\t\t"+"("+average_import_charge+" /day)"+"\t"+"("+tariff_str+" /kWh)"
    billing_text6 = "Total Bill (excl tax and discount): "+"\t"+total_bill_excl_gst+"\t\t\t"+"("+average_total_bill+" /day)"
    billing_text7 = "Total Bill (incl tax and discount): "+"\t"+total_bill_incl_tax_disc_str
    billing_text8 = "Total Bill (w/o solar or disc): "+"\t\t"+bill_w_o_solar+"\t\t\t"+"("+average_bill_w_o_solar+" /day)"
    billing_text9 = "Net savings:"+"\t\t\t\t\t\t"+net_savings
    
    kpi_export_text1 = "Total Exports:"+"\t\t\t\t"+total_exports
    kpi_export_text2 = "Maximum Daily Exports: "+"\t"+export_max_kWh+" kWh on "+export_max_date
    kpi_export_text3 = "Minimum Daily Exports: "+"\t"+export_min_kWh+" kWh on "+export_min_date
    kpi_export_text4 = "Average Daily Exports: "+"\t\t"+export_mean_kWh+ " kWh"
    
    kpi_import_text1 = "Total Imports:"+"\t\t\t\t"+total_imports
    kpi_import_text2 = "Maximum Daily Imports: "+"\t"+import_max_kWh+" kWh on "+import_max_date
    kpi_import_text3 = "Minimum Daily Imports: "+"\t"+import_min_kWh+" kWh on "+import_min_date
    kpi_import_text4 = "Average Daily Imports: "+"\t"+import_mean_kWh+ " kWh"
    
    kpi_generation_text1 = "Total Generated:"+"\t\t\t\t"+total_generated
    kpi_generation_text2 = "Maximum Daily Generation: "+"\t"+generation_max_kWh+" kWh on "+generation_max_date
    kpi_generation_text3 = "Minimum Daily Generation: "+"\t"+generation_min_kWh+" kWh on "+generation_min_date
    kpi_generation_text4 = "Average Daily Generation: "+"\t\t"+generation_mean_kWh+ " kWh"
    
    kpi_load_text1 = "Total Load:"+"\t\t\t\t\t"+total_load
    kpi_load_text2 = "Maximum Daily Load: "+"\t\t"+load_max_kWh+" kWh on "+load_max_date
    kpi_load_text3 = "Minimum Daily Load: "+"\t\t"+load_min_kWh+" kWh on "+load_min_date
    kpi_load_text4 = "Average Daily Load: "+"\t\t"+load_mean_kWh_str+ " kWh"
    
    st.header(title, divider = "red")
    st.text(billing_text1)
    st.text(billing_text2)
    st.text(billing_text3)
    st.text(billing_text4)
    st.text(billing_text5)
    st.text(billing_text6)
    st.text(billing_text7)
    st.text(billing_text8)
    st.text(billing_text9)
    st.subheader("", divider = True)
    
    title = "KPIs for period from " + str(period) + "(" + str(no_of_days) + " days"")" + " MPRN:" + str(nmi)
    
    st.header(title, divider = "red")
    st.subheader("Exports", divider = True)
    st.text(kpi_export_text1)
    st.text(kpi_export_text2)
    st.text(kpi_export_text3)
    st.text(kpi_export_text4)
    st.subheader("Imports", divider = True)
    st.text(kpi_import_text1)
    st.text(kpi_import_text2)
    st.text(kpi_import_text3)
    st.text(kpi_import_text4)
    st.subheader("Generation", divider = True)
    st.text(kpi_generation_text1)
    st.text(kpi_generation_text2)
    st.text(kpi_generation_text3)
    st.text(kpi_generation_text4)
    st.subheader("Load", divider = True)
    st.text(kpi_load_text1)
    st.text(kpi_load_text2)
    st.text(kpi_load_text3)
    st.text(kpi_load_text4)
    st.subheader("", divider = True)
    
